"""Subscription system troubleshooting and monitoring.

This module provides diagnostic tools for WebSocket connection testing,
subscription system monitoring, and detailed status reporting for
development and debugging purposes.
"""

import asyncio
import contextlib
import json
import re
from datetime import UTC, datetime
from typing import Any

import websockets
from fastmcp import FastMCP
from websockets.typing import Subprotocol

from ..config.logging import logger
from ..config.settings import UNRAID_API_KEY, UNRAID_API_URL
from ..core.exceptions import ToolError
from .manager import subscription_manager
from .resources import ensure_subscriptions_started
from .utils import build_ws_ssl_context, build_ws_url


_ALLOWED_SUBSCRIPTION_NAMES = frozenset(
    {
        "logFileSubscription",
        "containerStatsSubscription",
        "cpuSubscription",
        "memorySubscription",
        "arraySubscription",
        "networkSubscription",
        "dockerSubscription",
        "vmSubscription",
    }
)

# Pattern: must start with "subscription" and contain only a known subscription name.
# _FORBIDDEN_KEYWORDS rejects any query that contains standalone "mutation" or "query"
# as distinct words. Word boundaries (\b) ensure "mutationField"-style identifiers are
# not rejected — only bare "mutation" or "query" operation keywords are blocked.
_SUBSCRIPTION_NAME_PATTERN = re.compile(r"^\s*subscription\b[^{]*\{\s*(\w+)", re.IGNORECASE)
_FORBIDDEN_KEYWORDS = re.compile(r"\b(mutation|query)\b", re.IGNORECASE)


def _validate_subscription_query(query: str) -> str:
    """Validate that a subscription query is safe to execute.

    Only allows subscription operations targeting whitelisted subscription names.
    Rejects any query containing mutation/query keywords.

    Returns:
        The extracted subscription name.

    Raises:
        ToolError: If the query fails validation.
    """
    if _FORBIDDEN_KEYWORDS.search(query):
        raise ToolError("Query rejected: must be a subscription, not a mutation or query.")

    match = _SUBSCRIPTION_NAME_PATTERN.match(query)
    if not match:
        raise ToolError(
            "Query rejected: must start with 'subscription' and contain a valid "
            "subscription operation. Example: subscription { logFileSubscription { ... } }"
        )

    sub_name = match.group(1)
    if sub_name not in _ALLOWED_SUBSCRIPTION_NAMES:
        raise ToolError(
            f"Subscription '{sub_name}' is not allowed. "
            f"Allowed subscriptions: {sorted(_ALLOWED_SUBSCRIPTION_NAMES)}"
        )

    return sub_name


def register_diagnostic_tools(mcp: FastMCP) -> None:
    """Register diagnostic tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def test_subscription_query(subscription_query: str) -> dict[str, Any]:
        """Test a GraphQL subscription query directly to debug schema issues.

        Use this to find working subscription field names and structure.
        Only whitelisted subscriptions are allowed (logFileSubscription,
        containerStatsSubscription, cpuSubscription, memorySubscription,
        arraySubscription, networkSubscription, dockerSubscription,
        vmSubscription).

        Args:
            subscription_query: The GraphQL subscription query to test

        Returns:
            Dict containing test results and response data
        """
        # Validate before any network I/O
        sub_name = _validate_subscription_query(subscription_query)

        try:
            logger.info(f"[TEST_SUBSCRIPTION] Testing validated subscription '{sub_name}'")

            try:
                ws_url = build_ws_url()
            except ValueError as e:
                raise ToolError(str(e)) from e

            ssl_context = build_ws_ssl_context(ws_url)

            # Test connection
            async with websockets.connect(
                ws_url,
                subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
                ssl=ssl_context,
                open_timeout=10,
                ping_interval=30,
                ping_timeout=10,
            ) as websocket:
                # Send connection init (using standard X-API-Key format)
                await websocket.send(
                    json.dumps(
                        {
                            "type": "connection_init",
                            "payload": {"headers": {"X-API-Key": UNRAID_API_KEY}},
                        }
                    )
                )

                # Wait for ack
                response = await websocket.recv()
                init_response = json.loads(response)

                if init_response.get("type") != "connection_ack":
                    return {"error": f"Connection failed: {init_response}"}

                # Send subscription
                await websocket.send(
                    json.dumps(
                        {"id": "test", "type": "start", "payload": {"query": subscription_query}}
                    )
                )

                # Wait for response with timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    result = json.loads(response)

                    logger.info(f"[TEST_SUBSCRIPTION] Response: {result}")
                    return {"success": True, "response": result, "query_tested": subscription_query}

                except TimeoutError:
                    return {
                        "success": True,
                        "response": "No immediate response (subscriptions may only send data on changes)",
                        "query_tested": subscription_query,
                        "note": "Connection successful, subscription may be waiting for events",
                    }

        except Exception as e:
            logger.error(f"[TEST_SUBSCRIPTION] Error: {e}", exc_info=True)
            return {"error": str(e), "query_tested": subscription_query}

    @mcp.tool()
    async def diagnose_subscriptions() -> dict[str, Any]:
        """Comprehensive diagnostic tool for subscription system.

        Shows detailed status, connection states, errors, and troubleshooting info.

        Returns:
            Dict containing comprehensive subscription system diagnostics
        """
        # Ensure subscriptions are started before diagnosing
        await ensure_subscriptions_started()

        try:
            logger.info("[DIAGNOSTIC] Running subscription diagnostics...")

            # Get comprehensive status
            status = await subscription_manager.get_subscription_status()

            # Initialize connection issues list with proper type
            connection_issues: list[dict[str, Any]] = []

            # Add environment info with explicit typing
            diagnostic_info: dict[str, Any] = {
                "timestamp": datetime.now(UTC).isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "unraid_api_url": UNRAID_API_URL[:50] + "..." if UNRAID_API_URL else None,
                    "api_key_configured": bool(UNRAID_API_KEY),
                    "websocket_url": None,
                },
                "subscriptions": status,
                "summary": {
                    "total_configured": len(subscription_manager.subscription_configs),
                    "auto_start_count": sum(
                        1
                        for s in subscription_manager.subscription_configs.values()
                        if s.get("auto_start")
                    ),
                    "active_count": len(subscription_manager.active_subscriptions),
                    "with_data": len(subscription_manager.resource_data),
                    "in_error_state": 0,
                    "connection_issues": connection_issues,
                },
            }

            # Calculate WebSocket URL (stays None if UNRAID_API_URL not configured)
            with contextlib.suppress(ValueError):
                diagnostic_info["environment"]["websocket_url"] = build_ws_url()

            # Analyze issues
            for sub_name, sub_status in status.items():
                runtime = sub_status.get("runtime", {})
                connection_state = runtime.get("connection_state", "unknown")

                if connection_state in ["error", "auth_failed", "timeout", "max_retries_exceeded"]:
                    diagnostic_info["summary"]["in_error_state"] += 1

                if runtime.get("last_error"):
                    connection_issues.append(
                        {
                            "subscription": sub_name,
                            "state": connection_state,
                            "error": runtime["last_error"],
                        }
                    )

            # Add troubleshooting recommendations
            recommendations: list[str] = []

            if not diagnostic_info["environment"]["api_key_configured"]:
                recommendations.append(
                    "CRITICAL: No API key configured. Set UNRAID_API_KEY environment variable."
                )

            if diagnostic_info["summary"]["in_error_state"] > 0:
                recommendations.append(
                    "Some subscriptions are in error state. Check 'connection_issues' for details."
                )

            if diagnostic_info["summary"]["with_data"] == 0:
                recommendations.append(
                    "No subscriptions have received data yet. Check WebSocket connectivity and authentication."
                )

            if (
                diagnostic_info["summary"]["active_count"]
                < diagnostic_info["summary"]["auto_start_count"]
            ):
                recommendations.append(
                    "Not all auto-start subscriptions are active. Check server startup logs."
                )

            diagnostic_info["troubleshooting"] = {
                "recommendations": recommendations,
                "log_commands": [
                    "Check server logs for [WEBSOCKET:*], [AUTH:*], [SUBSCRIPTION:*] prefixed messages",
                    "Look for connection timeout or authentication errors",
                    "Verify Unraid API URL is accessible and supports GraphQL subscriptions",
                ],
                "next_steps": [
                    "If authentication fails: Verify API key has correct permissions",
                    "If connection fails: Check network connectivity to Unraid server",
                    "If no data received: Enable DEBUG logging to see detailed protocol messages",
                ],
            }

            logger.info(
                f"[DIAGNOSTIC] Completed. Active: {diagnostic_info['summary']['active_count']}, With data: {diagnostic_info['summary']['with_data']}, Errors: {diagnostic_info['summary']['in_error_state']}"
            )
            return diagnostic_info

        except Exception as e:
            logger.error(f"[DIAGNOSTIC] Failed to generate diagnostics: {e}")
            raise ToolError(f"Failed to generate diagnostics: {e!s}") from e

    logger.info("Subscription diagnostic tools registered successfully")
