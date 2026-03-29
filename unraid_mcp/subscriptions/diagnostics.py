"""Subscription system troubleshooting and monitoring.

This module provides diagnostic tools for WebSocket connection testing,
subscription system monitoring, and detailed status reporting for
development and debugging purposes.
"""

import asyncio
import json
import re
from datetime import UTC, datetime
from typing import Any

import websockets
from fastmcp import FastMCP
from websockets.typing import Subprotocol

from ..config import settings as _settings
from ..config.logging import logger
from ..core.exceptions import ToolError
from ..core.utils import safe_display_url
from .manager import subscription_manager
from .resources import ensure_subscriptions_started
from .utils import (
    _analyze_subscription_status,
    build_connection_init,
    build_ws_ssl_context,
    build_ws_url,
)


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
        field_name = _validate_subscription_query(subscription_query)

        try:
            logger.info(f"[TEST_SUBSCRIPTION] Testing validated subscription field '{field_name}'")

            try:
                ws_url = build_ws_url()
            except ValueError as e:
                logger.error("[TEST_SUBSCRIPTION] Invalid WebSocket URL configuration: %s", e)
                raise ToolError(
                    "Subscription test failed: invalid WebSocket URL configuration."
                ) from e

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
                # Send connection init
                await websocket.send(json.dumps(build_connection_init()))

                # Wait for ack
                response = await websocket.recv()
                init_response = json.loads(response)

                if init_response.get("type") != "connection_ack":
                    logger.error(
                        "[TEST_SUBSCRIPTION] Connection not acknowledged: %s",
                        init_response,
                    )
                    raise ToolError(
                        "Subscription test failed: WebSocket connection was not acknowledged."
                    )

                # Use the negotiated subprotocol to pick the correct message type.
                # graphql-transport-ws uses "subscribe"; legacy graphql-ws uses "start".
                selected_proto = websocket.subprotocol or ""
                start_type = "subscribe" if selected_proto == "graphql-transport-ws" else "start"

                # Send subscription
                await websocket.send(
                    json.dumps(
                        {"id": "test", "type": start_type, "payload": {"query": subscription_query}}
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
            logger.error("[TEST_SUBSCRIPTION] Error: %s", e, exc_info=True)
            raise ToolError(
                "Subscription test failed: an unexpected error occurred. Check server logs for details."
            ) from e

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

            # Analyze connection issues and error counts via shared helper.
            # Gates connection_issues on current failure state (Bug 5 fix).
            error_count, connection_issues = _analyze_subscription_status(status)

            # Calculate WebSocket URL — apply safe_display_url to avoid leaking
            # credentials (user:pass@host) or the raw API key embedded in the URL.
            ws_url_display: str | None = None
            if _settings.UNRAID_API_URL:
                try:
                    ws_url_display = safe_display_url(build_ws_url())
                except ValueError:
                    ws_url_display = None

            # Add environment info with explicit typing
            diagnostic_info: dict[str, Any] = {
                "timestamp": datetime.now(UTC).isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "unraid_api_url": safe_display_url(_settings.UNRAID_API_URL),
                    "api_key_configured": bool(_settings.UNRAID_API_KEY),
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
            logger.error("[DIAGNOSTIC] Failed to generate diagnostics: %s", e, exc_info=True)
            raise ToolError(
                "Failed to generate diagnostics: an unexpected error occurred. Check server logs for details."
            ) from e

    logger.info("Subscription diagnostic tools registered successfully")
