"""Health monitoring and diagnostics.

Provides the `unraid_health` tool with 3 actions for system health checks,
connection testing, and subscription diagnostics.
"""

import datetime
import time
from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..config.settings import (
    UNRAID_API_URL,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
    VERSION,
)
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


HEALTH_ACTIONS = Literal["check", "test_connection", "diagnose"]

# Severity ordering: only upgrade, never downgrade
_SEVERITY = {"healthy": 0, "warning": 1, "degraded": 2, "unhealthy": 3}


def _server_info() -> dict[str, Any]:
    """Return the standard server info block used in health responses."""
    return {
        "name": "Unraid MCP Server",
        "version": VERSION,
        "transport": UNRAID_MCP_TRANSPORT,
        "host": UNRAID_MCP_HOST,
        "port": UNRAID_MCP_PORT,
    }


def register_health_tool(mcp: FastMCP) -> None:
    """Register the unraid_health tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_health(
        action: HEALTH_ACTIONS,
    ) -> dict[str, Any]:
        """Monitor Unraid MCP server and system health.

        Actions:
          check - Comprehensive health check (API latency, array, notifications, Docker)
          test_connection - Quick connectivity test (just checks { online })
          diagnose - Subscription system diagnostics
        """
        if action not in ("check", "test_connection", "diagnose"):
            raise ToolError(
                f"Invalid action '{action}'. Must be one of: check, test_connection, diagnose"
            )

        try:
            logger.info(f"Executing unraid_health action={action}")

            if action == "test_connection":
                start = time.time()
                data = await make_graphql_request("query { online }")
                latency = round((time.time() - start) * 1000, 2)
                return {
                    "status": "connected",
                    "online": data.get("online"),
                    "latency_ms": latency,
                }

            if action == "check":
                return await _comprehensive_check()

            if action == "diagnose":
                return await _diagnose_subscriptions()

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_health action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute health/{action}: {e!s}") from e

    logger.info("Health tool registered successfully")


async def _comprehensive_check() -> dict[str, Any]:
    """Run comprehensive health check against the Unraid system."""
    start_time = time.time()
    health_severity = 0  # Track as int to prevent downgrade
    issues: list[str] = []

    def _escalate(level: str) -> None:
        nonlocal health_severity
        health_severity = max(health_severity, _SEVERITY.get(level, 0))

    try:
        query = """
        query ComprehensiveHealthCheck {
          info {
            machineId time
            versions { unraid }
            os { uptime }
          }
          array { state }
          notifications {
            overview { unread { alert warning total } }
          }
          docker {
            containers(skipCache: true) { id state status }
          }
        }
        """
        data = await make_graphql_request(query)
        api_latency = round((time.time() - start_time) * 1000, 2)

        health_info: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "api_latency_ms": api_latency,
            "server": _server_info(),
        }

        if not data:
            health_info["status"] = "unhealthy"
            health_info["issues"] = ["No response from Unraid API"]
            return health_info

        # System info
        info = data.get("info", {})
        if info:
            health_info["unraid_system"] = {
                "status": "connected",
                "url": UNRAID_API_URL,
                "machine_id": info.get("machineId"),
                "version": info.get("versions", {}).get("unraid"),
                "uptime": info.get("os", {}).get("uptime"),
            }
        else:
            _escalate("degraded")
            issues.append("Unable to retrieve system info")

        # Array
        array_info = data.get("array", {})
        if array_info:
            state = array_info.get("state", "unknown")
            health_info["array_status"] = {
                "state": state,
                "healthy": state in ("STARTED", "STOPPED"),
            }
            if state not in ("STARTED", "STOPPED"):
                _escalate("warning")
                issues.append(f"Array in unexpected state: {state}")
        else:
            _escalate("warning")
            issues.append("Unable to retrieve array status")

        # Notifications
        notifications = data.get("notifications", {})
        if notifications and notifications.get("overview"):
            unread = notifications["overview"].get("unread", {})
            alerts = unread.get("alert", 0)
            health_info["notifications"] = {
                "unread_total": unread.get("total", 0),
                "unread_alerts": alerts,
                "unread_warnings": unread.get("warning", 0),
            }
            if alerts > 0:
                _escalate("warning")
                issues.append(f"{alerts} unread alert(s)")

        # Docker
        docker = data.get("docker", {})
        if docker and docker.get("containers"):
            containers = docker["containers"]
            health_info["docker_services"] = {
                "total": len(containers),
                "running": len([c for c in containers if c.get("state") == "running"]),
                "stopped": len([c for c in containers if c.get("state") == "exited"]),
            }

        # Latency assessment
        if api_latency > 10000:
            _escalate("degraded")
            issues.append(f"Very high API latency: {api_latency}ms")
        elif api_latency > 5000:
            _escalate("warning")
            issues.append(f"High API latency: {api_latency}ms")

        # Resolve final status from severity level
        severity_to_status = {v: k for k, v in _SEVERITY.items()}
        health_info["status"] = severity_to_status.get(health_severity, "healthy")
        if issues:
            health_info["issues"] = issues
        health_info["performance"] = {
            "api_response_time_ms": api_latency,
            "check_duration_ms": round((time.time() - start_time) * 1000, 2),
        }

        return health_info

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "error": str(e),
            "server": _server_info(),
        }


async def _diagnose_subscriptions() -> dict[str, Any]:
    """Import and run subscription diagnostics."""
    try:
        from ..subscriptions.manager import subscription_manager
        from ..subscriptions.resources import ensure_subscriptions_started

        await ensure_subscriptions_started()

        status = subscription_manager.get_subscription_status()
        connection_issues: list[dict[str, Any]] = []

        diagnostic_info: dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "environment": {
                "auto_start_enabled": subscription_manager.auto_start_enabled,
                "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                "api_url_configured": bool(UNRAID_API_URL),
            },
            "subscriptions": status,
            "summary": {
                "total_configured": len(subscription_manager.subscription_configs),
                "active_count": len(subscription_manager.active_subscriptions),
                "with_data": len(subscription_manager.resource_data),
                "in_error_state": 0,
                "connection_issues": connection_issues,
            },
        }

        for sub_name, sub_status in status.items():
            runtime = sub_status.get("runtime", {})
            conn_state = runtime.get("connection_state", "unknown")
            if conn_state in ("error", "auth_failed", "timeout", "max_retries_exceeded"):
                diagnostic_info["summary"]["in_error_state"] += 1
            if runtime.get("last_error"):
                connection_issues.append({
                    "subscription": sub_name,
                    "state": conn_state,
                    "error": runtime["last_error"],
                })

        return diagnostic_info

    except ImportError:
        return {
            "error": "Subscription modules not available",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        }
    except Exception as e:
        raise ToolError(f"Failed to generate diagnostics: {e!s}") from e
