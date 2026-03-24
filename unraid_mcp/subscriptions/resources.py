"""MCP resources that expose subscription data.

This module defines MCP resources that bridge between the subscription manager
and the MCP protocol, providing fallback queries when subscription data is unavailable.
"""

import asyncio
import json
import os
from collections.abc import Callable, Coroutine
from typing import Any, Final

import anyio
from fastmcp import FastMCP

from ..config.logging import logger
from .manager import subscription_manager
from .queries import SNAPSHOT_ACTIONS
from .snapshot import subscribe_once


# Global flag to track subscription startup
_subscriptions_started = False
_startup_lock: Final[asyncio.Lock] = asyncio.Lock()

_terminal_states = frozenset({"failed", "auth_failed", "max_retries_exceeded"})


async def ensure_subscriptions_started() -> None:
    """Ensure subscriptions are started, called from async context."""
    global _subscriptions_started

    # Fast-path: skip lock if already started
    if _subscriptions_started:
        return

    # Slow-path: acquire lock for initialization (double-checked locking)
    async with _startup_lock:
        if _subscriptions_started:
            return

        logger.info("[STARTUP] First async operation detected, starting subscriptions...")
        try:
            await autostart_subscriptions()
            _subscriptions_started = True
            logger.info("[STARTUP] Subscriptions started successfully")
        except Exception as e:
            logger.error(f"[STARTUP] Failed to start subscriptions: {e}", exc_info=True)


async def autostart_subscriptions() -> None:
    """Auto-start all subscriptions marked for auto-start in SubscriptionManager."""
    logger.info("[AUTOSTART] Initiating subscription auto-start process...")

    try:
        # Use the SubscriptionManager auto-start method
        await subscription_manager.auto_start_all_subscriptions()
        logger.info("[AUTOSTART] Auto-start process completed successfully")
    except Exception as e:
        logger.error(f"[AUTOSTART] Failed during auto-start process: {e}", exc_info=True)
        raise  # Propagate so ensure_subscriptions_started doesn't mark as started

    # Optional log file subscription
    log_path = os.getenv("UNRAID_AUTOSTART_LOG_PATH")
    if log_path is None:
        # Default to syslog if available
        default_path = "/var/log/syslog"
        if await anyio.Path(default_path).exists():
            log_path = default_path
            logger.info(f"[AUTOSTART] Using default log path: {default_path}")

    if log_path:
        try:
            logger.info(f"[AUTOSTART] Starting log file subscription for: {log_path}")
            config = subscription_manager.subscription_configs.get("logFileSubscription")
            if config:
                await subscription_manager.start_subscription(
                    "logFileSubscription", str(config["query"]), {"path": log_path}
                )
                logger.info(f"[AUTOSTART] Log file subscription started for: {log_path}")
            else:
                logger.error("[AUTOSTART] logFileSubscription config not found")
        except Exception as e:
            logger.error(f"[AUTOSTART] Failed to start log file subscription: {e}", exc_info=True)
    else:
        logger.info("[AUTOSTART] No log file path configured for auto-start")


def register_subscription_resources(mcp: FastMCP) -> None:
    """Register all subscription resources with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register resources with
    """

    @mcp.resource("unraid://logs/stream")
    async def logs_stream_resource() -> str:
        """Real-time log stream data from subscription."""
        await ensure_subscriptions_started()
        data = await subscription_manager.get_resource_data("logFileSubscription")
        if data is not None:
            return json.dumps(data, indent=2)
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues.",
            }
        )

    def _make_resource_fn(action: str) -> Callable[[], Coroutine[Any, Any, str]]:
        async def _live_resource() -> str:
            await ensure_subscriptions_started()
            data = await subscription_manager.get_resource_data(action)
            if data is not None:
                return json.dumps(data, indent=2)
            # Surface permanent errors only when the connection is in a terminal failure
            # state — if the subscription has since reconnected, ignore the stale error.
            last_error = subscription_manager.last_error.get(action)
            conn_state = subscription_manager.connection_states.get(action, "")
            if last_error and conn_state in _terminal_states:
                return json.dumps(
                    {
                        "status": "error",
                        "message": f"Subscription '{action}' failed: {last_error}",
                    }
                )
            # When auto-start is disabled, fall back to a one-shot fetch so the
            # resource returns real data instead of a perpetual "connecting" placeholder.
            if not subscription_manager.auto_start_enabled:
                try:
                    query_info = SNAPSHOT_ACTIONS.get(action)
                    if query_info is not None:
                        fallback_data = await subscribe_once(query_info)
                        return json.dumps(fallback_data, indent=2)
                except Exception as e:
                    logger.warning("[RESOURCE] On-demand fallback for '%s' failed: %s", action, e)
            return json.dumps(
                {
                    "status": "connecting",
                    "message": f"Subscription '{action}' is starting. Retry in a moment.",
                }
            )

        _live_resource.__name__ = f"{action}_resource"
        _live_resource.__doc__ = (
            f"Real-time {action.replace('_', ' ')} data via WebSocket subscription."
        )
        return _live_resource

    for _action in SNAPSHOT_ACTIONS:
        mcp.resource(f"unraid://live/{_action}")(_make_resource_fn(_action))

    logger.info("Subscription resources registered successfully")
