"""Subscription system troubleshooting and monitoring.

This module provides the diagnostic handlers behind the consolidated `unraid`
tool's `subscriptions` action — WebSocket connection testing, subscription
system monitoring, and detailed status reporting for development and debugging.

The handlers are exposed via :func:`_handle_subscriptions`, which the `unraid`
tool routes ``action="subscriptions"`` to (subactions ``diagnose`` and
``test_query``).
"""

import asyncio
import json
import re
from datetime import UTC, datetime
from typing import Any

from ..config import settings as _settings
from ..config.logging import logger
from ..core.exceptions import ToolError
from ..core.utils import safe_display_url
from .manager import subscription_manager
from .protocol import ProtocolError, graphql_ws_session
from .resources import ensure_subscriptions_started
from .utils import (
    _analyze_subscription_status,
    build_ws_ssl_context,
    build_ws_url,
)


# Schema field names that appear inside the selection set of allowed subscriptions.
# The regex _SUBSCRIPTION_NAME_PATTERN extracts the first identifier after the
# opening "{", so we list the actual field names used in queries (e.g. "logFile"),
# NOT the operation-level names (e.g. "logFileSubscription").
_ALLOWED_SUBSCRIPTION_FIELDS = frozenset(
    {
        "containerStats",
        "cpu",
        "dockerContainerStats",
        "memory",
        "array",
        "network",
        "docker",
        "systemMetricsTemperature",
        "vm",
        "displaySubscription",
        "notificationsWarningsAndAlerts",
        "pluginInstallUpdates",
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
            "subscription field. Example: subscription { cpu { used idle system } }"
        )

    field_name = match.group(1)
    if field_name not in _ALLOWED_SUBSCRIPTION_FIELDS:
        raise ToolError(
            f"Subscription field '{field_name}' is not allowed. "
            f"Allowed fields: {sorted(_ALLOWED_SUBSCRIPTION_FIELDS)}"
        )

    return field_name


async def test_subscription_query(subscription_query: str) -> dict[str, Any]:
    """Test a GraphQL subscription query directly to debug schema issues.

    Use this to find working subscription field names and structure.
    Only whitelisted schema fields are permitted (containerStats,
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
            raise ToolError("Subscription test failed: invalid WebSocket URL configuration.") from e

        ssl_context = build_ws_ssl_context(ws_url)

        # Shared handshake: connect -> connection_init -> connection_ack -> subscribe.
        # ack_timeout=None keeps the historical bare recv() (no deadline) on the ack;
        # ping_interval=30 matches the original probe configuration.
        try:
            async with graphql_ws_session(
                ws_url,
                subscription_query,
                sub_id="test",
                ssl_context=ssl_context,
                open_timeout=10,
                ack_timeout=None,
                ping_interval=30,
                ping_timeout=10,
            ) as session:
                # Wait for the first response with a timeout. The probe deliberately
                # does NOT normalize the frame — it returns whatever the server sent
                # first so a developer can inspect the raw subscription response.
                try:
                    response = await asyncio.wait_for(session.ws.recv(), timeout=5.0)
                    result = json.loads(response)

                    logger.info(f"[TEST_SUBSCRIPTION] Response: {result}")
                    return {
                        "success": True,
                        "response": result,
                        "query_tested": subscription_query,
                    }

                except TimeoutError:
                    return {
                        "success": True,
                        "response": "No immediate response (subscriptions may only send data on changes)",
                        "query_tested": subscription_query,
                        "note": "Connection successful, subscription may be waiting for events",
                    }
        except ProtocolError as e:
            logger.error("[TEST_SUBSCRIPTION] Connection not acknowledged: %s", e)
            raise ToolError(
                "Subscription test failed: WebSocket connection was not acknowledged."
            ) from e

    except ToolError:
        raise
    except Exception as e:
        logger.error("[TEST_SUBSCRIPTION] Error: %s", e, exc_info=True)
        raise ToolError(
            "Subscription test failed: an unexpected error occurred. Check server logs for details."
        ) from e


async def diagnose_subscriptions() -> dict[str, Any]:
    """Comprehensive diagnostics for the subscription system.

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

        # Aggregate counts/config via the manager's locked accessor — never
        # reach into its internal state (active_subscriptions / resource_data /
        # subscription_configs / connection_states) directly (arch-L1).
        summary = await subscription_manager.get_summary()

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
                "auto_start_enabled": summary["auto_start_enabled"],
                "max_reconnect_attempts": summary["max_reconnect_attempts"],
                "unraid_api_url": safe_display_url(_settings.UNRAID_API_URL),
                "api_key_configured": bool(_settings.UNRAID_API_KEY),
                "websocket_url": ws_url_display,
            },
            "subscriptions": status,
            "summary": {
                "total_configured": summary["total_configured"],
                "auto_start_count": summary["auto_start_count"],
                "active_count": summary["active_count"],
                "with_data": summary["with_data"],
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


# Subactions exposed via the `unraid` tool's `subscriptions` action.
_SUBSCRIPTIONS_SUBACTIONS: set[str] = {"diagnose", "test_query"}


async def _handle_subscriptions(subaction: str, subscription_query: str | None) -> dict[str, Any]:
    """Route `action="subscriptions"` subactions to their handlers.

    Subactions:
        diagnose    — full diagnostic dump of the WebSocket subscription system.
        test_query  — probe a raw GraphQL subscription (requires subscription_query).
    """
    from ..core.utils import validate_subaction

    validate_subaction(subaction, _SUBSCRIPTIONS_SUBACTIONS, "subscriptions")

    if subaction == "diagnose":
        return await diagnose_subscriptions()

    # test_query
    if not subscription_query:
        raise ToolError(
            "subscription_query is required for subscriptions/test_query. "
            'Example: unraid(action="subscriptions", subaction="test_query", '
            'subscription_query="subscription { cpu { used idle system } }")'
        )
    return await test_subscription_query(subscription_query)
