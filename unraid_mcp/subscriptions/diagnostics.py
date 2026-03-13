"""Subscription system troubleshooting and monitoring.

This module provides diagnostic tools for WebSocket connection testing,
subscription system monitoring, and detailed status reporting for
development and debugging purposes.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Any

import websockets
from fastmcp import FastMCP
from websockets.typing import Subprotocol

from ..config.logging import logger
from ..config.settings import UNRAID_API_KEY, UNRAID_API_URL
from ..core.exceptions import ToolError
from .manager import subscription_manager
from .resources import ensure_subscriptions_started
from .utils import _analyze_subscription_status, build_ws_ssl_context, build_ws_url


# Schema field names that appear inside the selection set of allowed subscriptions.
# The regex _SUBSCRIPTION_NAME_PATTERN extracts the first identifier after the
# opening "{", so we list the actual field names used in queries (e.g. "logFile"),
# NOT the operation-level names (e.g. "logFileSubscription").
_ALLOWED_SUBSCRIPTION_FIELDS = frozenset(
    {
        "logFile",
        "containerStats",
        "cpu",
        "memory",
        "array",
        "network",
        "docker",
        "vm",
    }
)

# Pattern: must start with "subscription" keyword, then extract the first selected
# field name (the word immediately after "{").
_SUBSCRIPTION_NAME_PATTERN = re.compile(r"^\s*subscription\b[^{]*\{\s*(\w+)", re.IGNORECASE)
# Reject any query that contains a bare "mutation" or "query" operation keyword.
_FORBIDDEN_KEYWORDS = re.compile(r"\b(mutation|query)\b", re.IGNORECASE)


def _validate_subscription_query(query: str) -> str:
    """Validate that a subscription query is safe to execute.

    Only allows subscription operations targeting whitelisted schema field names.
    Rejects any query containing mutation/query keywords.

    Returns:
        The extracted field name (e.g. "logFile").

    Raises:
        ToolError: If the query fails validation.
    """
    if _FORBIDDEN_KEYWORDS.search(query):
        raise ToolError("Query rejected: must be a subscription, not a mutation or query.")

    match = _SUBSCRIPTION_NAME_PATTERN.match(query)
    if not match:
        raise ToolError(
            "Query rejected: must start with 'subscription' and contain a valid "
            'subscription field. Example: subscription { logFile(path: "/var/log/syslog") { content } }'
        )

    field_name = match.group(1)
    if field_name not in _ALLOWED_SUBSCRIPTION_FIELDS:
        raise ToolError(
            f"Subscription field '{field_name}' is not allowed. "
            f"Allowed fields: {sorted(_ALLOWED_SUBSCRIPTION_FIELDS)}"
        )

    return field_name


def register_diagnostic_tools(mcp: FastMCP) -> None:
    """Register diagnostic tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def test_subscription_query(subscription_query: str) -> dict[str, Any]:
        """Test a GraphQL subscription query directly to debug schema issues.

        Use this to find working subscription field names and structure.
        Only whitelisted schema fields are permitted (logFile, containerStats,
        cpu, memory, array, network, docker, vm).

        Args:
            subscription_query: The GraphQL subscription query to test

        Returns:
            Dict containing test results and response data
        """
        # Validate before any network I/O (Bug 1 fix)
        field_name = _validate_subscription_query(subscription_query)

        try:
            logger.info(f"[TEST_SUBSCRIPTION] Testing validated subscription field '{field_name}'")

            # Build WebSocket URL — raises ValueError on invalid/missing scheme (Bug 4 fix)
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

        except ToolError:
            raise
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
            status = subscription_manager.get_subscription_status()

            # Analyze connection issues and error counts via shared helper.
            # Gates connection_issues on current failure state (Bug 5 fix).
            error_count, connection_issues = _analyze_subscription_status(status)

            # Calculate WebSocket URL
            ws_url_display: str | None = None
            if UNRAID_API_URL:
                try:
                    ws_url_display = build_ws_url()
                except ValueError:
                    ws_url_display = None

            # Add environment info with explicit typing
            diagnostic_info: dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "unraid_api_url": UNRAID_API_URL[:50] + "..." if UNRAID_API_URL else None,
                    "api_key_configured": bool(UNRAID_API_KEY),
                    "websocket_url": ws_url_display,
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
                    "in_error_state": error_count,
                    "connection_issues": connection_issues,
                },
            }

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
