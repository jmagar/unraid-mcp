"""MCP resources that expose subscription data.

This module defines MCP resources that bridge between the subscription manager
and the MCP protocol, providing fallback queries when subscription data is unavailable.
"""

import json
import os

import anyio
from fastmcp import FastMCP

from ..config.logging import logger
from .manager import subscription_manager


# Global flag to track subscription startup
_subscriptions_started = False


async def ensure_subscriptions_started() -> None:
    """Ensure subscriptions are started, called from async context."""
    global _subscriptions_started

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
        # Use the new SubscriptionManager auto-start method
        await subscription_manager.auto_start_all_subscriptions()
        logger.info("[AUTOSTART] Auto-start process completed successfully")
    except Exception as e:
        logger.error(f"[AUTOSTART] Failed during auto-start process: {e}", exc_info=True)

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
        if data:
            return json.dumps(data, indent=2)
        return json.dumps(
            {
                "status": "No subscription data yet",
                "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues.",
            }
        )

    logger.info("Subscription resources registered successfully")
