"""Health domain constants and helpers for the Unraid MCP tool.

The _handle_health function lives in unraid.py (not here) because tests patch
elicit_and_configure at unraid_mcp.tools.unraid — keeping the handler there
ensures patches resolve correctly without circular imports.
"""

import datetime
import time
from typing import Any

import httpx

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import CredentialsNotConfiguredError


# Import system online query to avoid duplication — used by setup and test_connection


# ===========================================================================
# HEALTH
# ===========================================================================

_HEALTH_SUBACTIONS: set[str] = {"check", "test_connection", "diagnose", "setup"}
_HEALTH_QUERIES: dict[str, str] = {
    "comprehensive_health": (
        "query ComprehensiveHealthCheck {"
        " info { machineId time versions { core { unraid } } os { uptime } }"
        " array { state }"
        " notifications { overview { unread { alert warning total } } }"
        " docker { containers(skipCache: true) { id state status } }"
        " }"
    ),
}
_SEVERITY = {"healthy": 0, "warning": 1, "degraded": 2, "unhealthy": 3}


async def _comprehensive_health_check() -> dict[str, Any]:
    from ..config.settings import (
        UNRAID_API_URL,
        UNRAID_MCP_HOST,
        UNRAID_MCP_PORT,
        UNRAID_MCP_TRANSPORT,
        VERSION,
    )
    from ..core.utils import safe_display_url

    start_time = time.time()
    health_severity = 0
    issues: list[str] = []

    def _escalate(level: str) -> None:
        nonlocal health_severity
        health_severity = max(health_severity, _SEVERITY.get(level, 0))

    try:
        data = await _client.make_graphql_request(_HEALTH_QUERIES["comprehensive_health"])
        api_latency = round((time.time() - start_time) * 1000, 2)

        health_info: dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "api_latency_ms": api_latency,
            "server": {
                "name": "Unraid MCP Server",
                "version": VERSION,
                "transport": UNRAID_MCP_TRANSPORT,
                "host": UNRAID_MCP_HOST,
                "port": UNRAID_MCP_PORT,
            },
        }

        if not data:
            health_info["status"] = "unhealthy"
            health_info["issues"] = ["No response from Unraid API"]
            return health_info

        info = data.get("info") or {}
        if info:
            health_info["unraid_system"] = {
                "status": "connected",
                "url": safe_display_url(UNRAID_API_URL),
                "machine_id": info.get("machineId"),
                "version": ((info.get("versions") or {}).get("core") or {}).get("unraid"),
                "uptime": (info.get("os") or {}).get("uptime"),
            }
        else:
            _escalate("degraded")
            issues.append("Unable to retrieve system info")

        array_info = data.get("array") or {}
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

        notifications = data.get("notifications") or {}
        if notifications and notifications.get("overview"):
            unread = notifications["overview"].get("unread") or {}
            alerts = unread.get("alert", 0)
            health_info["notifications"] = {
                "unread_total": unread.get("total", 0),
                "unread_alerts": alerts,
                "unread_warnings": unread.get("warning", 0),
            }
            if alerts > 0:
                _escalate("warning")
                issues.append(f"{alerts} unread alert(s)")

        docker = data.get("docker") or {}
        if docker and docker.get("containers"):
            containers = docker["containers"]
            health_info["docker_services"] = {
                "total": len(containers),
                "running": len(
                    [c for c in containers if (c.get("state") or "").upper() == "RUNNING"]
                ),
                "stopped": len(
                    [c for c in containers if (c.get("state") or "").upper() == "EXITED"]
                ),
            }

        if api_latency > 10000:
            _escalate("degraded")
            issues.append(f"Very high API latency: {api_latency}ms")
        elif api_latency > 5000:
            _escalate("warning")
            issues.append(f"High API latency: {api_latency}ms")

        severity_to_status = {v: k for k, v in _SEVERITY.items()}
        health_info["status"] = severity_to_status.get(health_severity, "healthy")
        if issues:
            health_info["issues"] = issues
        health_info["performance"] = {
            "api_response_time_ms": api_latency,
            "check_duration_ms": round((time.time() - start_time) * 1000, 2),
        }
        return health_info

    except CredentialsNotConfiguredError:
        raise  # Let tool_error_handler convert to setup instructions
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "error": str(e),
        }
