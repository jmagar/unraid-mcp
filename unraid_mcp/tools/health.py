"""Comprehensive health monitoring tools.

This module provides tools for comprehensive health checks of the Unraid MCP server
and the underlying Unraid system, including performance metrics, system status,
notifications, Docker services, and API responsiveness.
"""

import datetime
import time
from typing import Any

from fastmcp import FastMCP

from unraid_mcp.config.logging import logger
from unraid_mcp.config.settings import (
    UNRAID_API_URL,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
)
from unraid_mcp.core.client import make_graphql_request

_PROCESS_START_TIME = time.time()

# Performance thresholds for health assessment
API_LATENCY_WARNING_MS = 5000
API_LATENCY_DEGRADED_MS = 10000

# Severity ranking for health status aggregation
_SEVERITY_RANK = {
    "healthy": 0,
    "warning": 1,
    "degraded": 2,
    "unhealthy": 3,
    "critical": 3,
}  # critical reserved for future use


def _update_health_status(current: str, new: str) -> str:
    """Update status only if the new status is more severe."""
    if _SEVERITY_RANK.get(new, 0) > _SEVERITY_RANK.get(current, 0):
        return new
    return current


def register_health_tools(mcp: FastMCP) -> None:
    """Register all health tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def health_check() -> dict[str, Any]:
        """Returns comprehensive health status of the Unraid MCP server and system for monitoring purposes."""
        start_time = time.time()
        process_start_time = _PROCESS_START_TIME  # snapshot for consistent timing
        health_status = "healthy"
        issues = []

        try:
            # Enhanced health check with multiple system components
            comprehensive_query = """
            query ComprehensiveHealthCheck {
              info {
                machineId
                time
                versions { core { unraid } }
                os { uptime }
              }
              array {
                state
              }
              notifications {
                overview {
                  unread { alert warning total }
                }
              }
              docker {
                containers(skipCache: true) {
                  id
                  state
                  status
                }
              }
            }
            """

            response_data = await make_graphql_request(comprehensive_query)
            api_latency = round((time.time() - start_time) * 1000, 2)  # ms

            # Base health info
            health_info = {
                "status": health_status,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "api_latency_ms": api_latency,
                "server": {
                    "name": "Unraid MCP Server",
                    "version": "0.1.0",
                    "transport": UNRAID_MCP_TRANSPORT,
                    "host": UNRAID_MCP_HOST,
                    "port": UNRAID_MCP_PORT,
                    "process_uptime_seconds": round(time.time() - process_start_time, 2),
                },
            }

            if not response_data:
                health_status = "unhealthy"
                issues.append("No response from Unraid API")
                health_info["status"] = health_status
                health_info["issues"] = issues
                return health_info

            # System info analysis
            info = response_data.get("info", {})
            if info:
                health_info["unraid_system"] = {
                    "status": "connected",
                    "url": UNRAID_API_URL,
                    "machine_id": info.get("machineId"),
                    "time": info.get("time"),
                    "version": info.get("versions", {}).get("core", {}).get("unraid"),
                    "uptime": info.get("os", {}).get("uptime"),
                }
            else:
                health_status = _update_health_status(health_status, "degraded")
                issues.append("Unable to retrieve system info")

            # Array health analysis
            array_info = response_data.get("array", {})
            if array_info:
                array_state = array_info.get("state", "unknown")
                health_info["array_status"] = {
                    "state": array_state,
                    "healthy": array_state in ["STARTED", "STOPPED"],
                }
                if array_state not in ["STARTED", "STOPPED"]:
                    health_status = _update_health_status(health_status, "warning")
                    issues.append(f"Array in unexpected state: {array_state}")
            else:
                health_status = _update_health_status(health_status, "warning")
                issues.append("Unable to retrieve array status")

            # Notifications analysis
            notifications = response_data.get("notifications", {})
            if notifications and notifications.get("overview"):
                unread = notifications["overview"].get("unread", {})
                alert_count = unread.get("alert", 0)
                warning_count = unread.get("warning", 0)
                total_unread = unread.get("total", 0)

                health_info["notifications"] = {
                    "unread_total": total_unread,
                    "unread_alerts": alert_count,
                    "unread_warnings": warning_count,
                    "has_critical_notifications": alert_count > 0,
                }

                if alert_count > 0:
                    health_status = _update_health_status(health_status, "warning")
                    issues.append(f"{alert_count} unread alert notification(s)")

            # Docker services analysis
            docker_info = response_data.get("docker", {})
            if docker_info and docker_info.get("containers"):
                containers = docker_info["containers"]
                running_containers = [c for c in containers if c.get("state") == "running"]
                stopped_containers = [c for c in containers if c.get("state") == "exited"]

                health_info["docker_services"] = {
                    "total_containers": len(containers),
                    "running_containers": len(running_containers),
                    "stopped_containers": len(stopped_containers),
                    "containers_healthy": len(
                        [c for c in containers if c.get("status", "").startswith("Up")]
                    ),
                }

            # API performance assessment
            if api_latency > API_LATENCY_DEGRADED_MS:  # > 10 seconds
                health_status = _update_health_status(health_status, "degraded")
                issues.append(f"Very high API latency: {api_latency}ms")
            elif api_latency > API_LATENCY_WARNING_MS:  # > 5 seconds
                health_status = _update_health_status(health_status, "warning")
                issues.append(f"High API latency: {api_latency}ms")

            # Final status determination
            health_info["status"] = health_status
            if issues:
                health_info["issues"] = issues

            # Add performance metrics
            health_info["performance"] = {
                "api_response_time_ms": api_latency,
                "health_check_duration_ms": round((time.time() - start_time) * 1000, 2),
            }

            return health_info

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "error": str(e),
                "api_latency_ms": round((time.time() - start_time) * 1000, 2),
                "server": {
                    "name": "Unraid MCP Server",
                    "version": "0.1.0",
                    "transport": UNRAID_MCP_TRANSPORT,
                    "host": UNRAID_MCP_HOST,
                    "port": UNRAID_MCP_PORT,
                },
            }

    logger.info("Health tools registered successfully")
