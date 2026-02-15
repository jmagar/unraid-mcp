"""Subscription system troubleshooting and monitoring.

This module provides diagnostic tools for WebSocket connection testing,
subscription system monitoring, and detailed status reporting for
development and debugging purposes.
"""

import asyncio
import json
import ssl
from datetime import datetime
from typing import Any

import websockets
from fastmcp import FastMCP
from websockets.typing import Subprotocol

from ..config.logging import logger
from ..config.settings import UNRAID_API_KEY, UNRAID_API_URL, UNRAID_VERIFY_SSL
from ..core.exceptions import ToolError
from .manager import subscription_manager
from .resources import ensure_subscriptions_started


def register_diagnostic_tools(mcp: FastMCP) -> None:
    """Register diagnostic tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def test_subscription_query(subscription_query: str) -> dict[str, Any]:
        """
        Test a GraphQL subscription query directly to debug schema issues.
        Use this to find working subscription field names and structure.

        Args:
            subscription_query: The GraphQL subscription query to test

        Returns:
            Dict containing test results and response data
        """
        try:
            logger.info(f"[TEST_SUBSCRIPTION] Testing query: {subscription_query}")

            # Build WebSocket URL
            if not UNRAID_API_URL:
                raise ToolError("UNRAID_API_URL is not configured")
            ws_url = UNRAID_API_URL.replace("https://", "wss://").replace("http://", "ws://") + "/graphql"

            # Build SSL context for wss:// connections
            ssl_context = None
            if ws_url.startswith("wss://"):
                if isinstance(UNRAID_VERIFY_SSL, str):
                    ssl_context = ssl.create_default_context(cafile=UNRAID_VERIFY_SSL)
                elif UNRAID_VERIFY_SSL:
                    ssl_context = ssl.create_default_context()
                else:
                    ssl_context = ssl._create_unverified_context()

            # Test connection
            async with websockets.connect(
                ws_url,
                subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
                ssl=ssl_context,
                ping_interval=30,
                ping_timeout=10
            ) as websocket:

                # Send connection init (using standard X-API-Key format)
                await websocket.send(json.dumps({
                    "type": "connection_init",
                    "payload": {
                        "headers": {
                            "X-API-Key": UNRAID_API_KEY
                        }
                    }
                }))

                # Wait for ack
                response = await websocket.recv()
                init_response = json.loads(response)

                if init_response.get("type") != "connection_ack":
                    return {"error": f"Connection failed: {init_response}"}

                # Send subscription
                await websocket.send(json.dumps({
                    "id": "test",
                    "type": "start",
                    "payload": {"query": subscription_query}
                }))

                # Wait for response with timeout
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    result = json.loads(response)

                    logger.info(f"[TEST_SUBSCRIPTION] Response: {result}")
                    return {
                        "success": True,
                        "response": result,
                        "query_tested": subscription_query
                    }

                except asyncio.TimeoutError:
                    return {
                        "success": True,
                        "response": "No immediate response (subscriptions may only send data on changes)",
                        "query_tested": subscription_query,
                        "note": "Connection successful, subscription may be waiting for events"
                    }

        except Exception as e:
            logger.error(f"[TEST_SUBSCRIPTION] Error: {e}", exc_info=True)
            return {
                "error": str(e),
                "query_tested": subscription_query
            }

    @mcp.tool()
    async def diagnose_subscriptions() -> dict[str, Any]:
        """
        Comprehensive diagnostic tool for subscription system.
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

            # Initialize connection issues list with proper type
            connection_issues: list[dict[str, Any]] = []

            # Add environment info with explicit typing
            diagnostic_info: dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "unraid_api_url": UNRAID_API_URL[:50] + "..." if UNRAID_API_URL else None,
                    "api_key_configured": bool(UNRAID_API_KEY),
                    "websocket_url": None
                },
                "subscriptions": status,
                "summary": {
                    "total_configured": len(subscription_manager.subscription_configs),
                    "auto_start_count": sum(1 for s in subscription_manager.subscription_configs.values() if s.get("auto_start")),
                    "active_count": len(subscription_manager.active_subscriptions),
                    "with_data": len(subscription_manager.resource_data),
                    "in_error_state": 0,
                    "connection_issues": connection_issues
                }
            }

            # Calculate WebSocket URL
            if UNRAID_API_URL:
                if UNRAID_API_URL.startswith('https://'):
                    ws_url = 'wss://' + UNRAID_API_URL[len('https://'):]
                elif UNRAID_API_URL.startswith('http://'):
                    ws_url = 'ws://' + UNRAID_API_URL[len('http://'):]
                else:
                    ws_url = UNRAID_API_URL
                if not ws_url.endswith('/graphql'):
                    ws_url = ws_url.rstrip('/') + '/graphql'
                diagnostic_info["environment"]["websocket_url"] = ws_url

            # Analyze issues
            for sub_name, sub_status in status.items():
                runtime = sub_status.get("runtime", {})
                connection_state = runtime.get("connection_state", "unknown")

                if connection_state in ["error", "auth_failed", "timeout", "max_retries_exceeded"]:
                    diagnostic_info["summary"]["in_error_state"] += 1

                if runtime.get("last_error"):
                    connection_issues.append({
                        "subscription": sub_name,
                        "state": connection_state,
                        "error": runtime["last_error"]
                    })

            # Add troubleshooting recommendations
            recommendations: list[str] = []

            if not diagnostic_info["environment"]["api_key_configured"]:
                recommendations.append("CRITICAL: No API key configured. Set UNRAID_API_KEY environment variable.")

            if diagnostic_info["summary"]["in_error_state"] > 0:
                recommendations.append("Some subscriptions are in error state. Check 'connection_issues' for details.")

            if diagnostic_info["summary"]["with_data"] == 0:
                recommendations.append("No subscriptions have received data yet. Check WebSocket connectivity and authentication.")

            if diagnostic_info["summary"]["active_count"] < diagnostic_info["summary"]["auto_start_count"]:
                recommendations.append("Not all auto-start subscriptions are active. Check server startup logs.")

            diagnostic_info["troubleshooting"] = {
                "recommendations": recommendations,
                "log_commands": [
                    "Check server logs for [WEBSOCKET:*], [AUTH:*], [SUBSCRIPTION:*] prefixed messages",
                    "Look for connection timeout or authentication errors",
                    "Verify Unraid API URL is accessible and supports GraphQL subscriptions"
                ],
                "next_steps": [
                    "If authentication fails: Verify API key has correct permissions",
                    "If connection fails: Check network connectivity to Unraid server",
                    "If no data received: Enable DEBUG logging to see detailed protocol messages"
                ]
            }

            logger.info(f"[DIAGNOSTIC] Completed. Active: {diagnostic_info['summary']['active_count']}, With data: {diagnostic_info['summary']['with_data']}, Errors: {diagnostic_info['summary']['in_error_state']}")
            return diagnostic_info

        except Exception as e:
            logger.error(f"[DIAGNOSTIC] Failed to generate diagnostics: {e}")
            raise ToolError(f"Failed to generate diagnostics: {str(e)}") from e

    logger.info("Subscription diagnostic tools registered successfully")
