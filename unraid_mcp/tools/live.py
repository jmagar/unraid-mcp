"""Real-time subscription snapshot tool.

Provides the `unraid_live` tool with 11 actions — one per GraphQL
subscription. Each action opens a transient WebSocket, receives one event
(or collects events for `collect_for` seconds), then closes.

Use `subscribe_once` actions for current-state reads (cpu, memory, array_state).
Use `subscribe_collect` actions for event streams (notification_feed, log_tail).
"""

from __future__ import annotations

import os
from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.exceptions import ToolError, tool_error_handler
from ..subscriptions.snapshot import subscribe_collect, subscribe_once


_ALLOWED_LOG_PREFIXES = ("/var/log/", "/boot/logs/", "/mnt/")

SNAPSHOT_ACTIONS = {
    "cpu": """
        subscription { systemMetricsCpu { id percentTotal cpus { percentTotal percentUser percentSystem percentIdle } } }
    """,
    "memory": """
        subscription { systemMetricsMemory { id total used free available active buffcache percentTotal swapTotal swapUsed swapFree percentSwapTotal } }
    """,
    "cpu_telemetry": """
        subscription { systemMetricsCpuTelemetry { id totalPower power temp } }
    """,
    "array_state": """
        subscription { arraySubscription { id state capacity { kilobytes { free used total } } parityCheckStatus { status progress speed errors } } }
    """,
    "parity_progress": """
        subscription { parityHistorySubscription { date status progress speed errors correcting paused running } }
    """,
    "ups_status": """
        subscription { upsUpdates { id name model status battery { chargeLevel estimatedRuntime health } power { inputVoltage outputVoltage loadPercentage } } }
    """,
    "notifications_overview": """
        subscription { notificationsOverview { unread { info warning alert total } archive { info warning alert total } } }
    """,
    "owner": """
        subscription { ownerSubscription { username url avatar } }
    """,
    "server_status": """
        subscription { serversSubscription { id name status guid wanip lanip localurl remoteurl } }
    """,
}

COLLECT_ACTIONS = {
    "notification_feed": """
        subscription { notificationAdded { id title subject description importance type timestamp } }
    """,
    "log_tail": """
        subscription LogTail($path: String!) { logFile(path: $path) { path content totalLines startLine } }
    """,
}

ALL_LIVE_ACTIONS = set(SNAPSHOT_ACTIONS) | set(COLLECT_ACTIONS)

LIVE_ACTIONS = Literal[
    "array_state",
    "cpu",
    "cpu_telemetry",
    "log_tail",
    "memory",
    "notification_feed",
    "notifications_overview",
    "owner",
    "parity_progress",
    "server_status",
    "ups_status",
]

if set(get_args(LIVE_ACTIONS)) != ALL_LIVE_ACTIONS:
    _missing = ALL_LIVE_ACTIONS - set(get_args(LIVE_ACTIONS))
    _extra = set(get_args(LIVE_ACTIONS)) - ALL_LIVE_ACTIONS
    raise RuntimeError(
        f"LIVE_ACTIONS and ALL_LIVE_ACTIONS are out of sync. "
        f"Missing: {_missing or 'none'}. Extra: {_extra or 'none'}"
    )


def register_live_tool(mcp: FastMCP) -> None:
    """Register the unraid_live tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_live(
        action: LIVE_ACTIONS,
        path: str | None = None,
        collect_for: float = 5.0,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """Get real-time data from Unraid via WebSocket subscriptions.

        Each action opens a transient WebSocket, receives data, then closes.

        Snapshot actions (return current state):
          cpu              - Real-time CPU utilization (all cores)
          memory           - Real-time memory and swap utilization
          cpu_telemetry    - CPU power draw and temperature per package
          array_state      - Live array state and parity status
          parity_progress  - Live parity check progress
          ups_status       - Real-time UPS battery and power state
          notifications_overview - Live notification counts by severity
          owner            - Live owner info
          server_status    - Live server connection state

        Collection actions (collect events for `collect_for` seconds):
          notification_feed - Collect new notification events (default: 5s window)
          log_tail         - Tail a log file (requires path; default: 5s window)

        Parameters:
          path        - Log file path for log_tail action (required)
          collect_for - Seconds to collect events for collect actions (default: 5.0)
          timeout     - WebSocket connection/handshake timeout in seconds (default: 10.0)
        """
        if action not in ALL_LIVE_ACTIONS:
            raise ToolError(
                f"Invalid action '{action}'. Must be one of: {sorted(ALL_LIVE_ACTIONS)}"
            )

        # Validate log_tail path before entering the error handler context.
        if action == "log_tail":
            if not path:
                raise ToolError("path is required for 'log_tail' action")
            # Resolve to prevent path traversal attacks (same as storage.py).
            # Using os.path.realpath instead of anyio.Path.resolve() because the
            # async variant blocks on NFS-mounted paths under /mnt/ (Perf-AI-1).
            normalized = os.path.realpath(path)  # noqa: ASYNC240
            if not any(normalized.startswith(p) for p in _ALLOWED_LOG_PREFIXES):
                raise ToolError(
                    f"path must start with one of: {', '.join(_ALLOWED_LOG_PREFIXES)}. Got: {path!r}"
                )
            path = normalized

        with tool_error_handler("live", action, logger):
            logger.info(f"Executing unraid_live action={action} timeout={timeout}")

            if action in SNAPSHOT_ACTIONS:
                data = await subscribe_once(SNAPSHOT_ACTIONS[action], timeout=timeout)
                return {"success": True, "action": action, "data": data}

            # Collect actions
            if action == "log_tail":
                events = await subscribe_collect(
                    COLLECT_ACTIONS["log_tail"],
                    variables={"path": path},
                    collect_for=collect_for,
                    timeout=timeout,
                )
                return {
                    "success": True,
                    "action": action,
                    "path": path,
                    "collect_for": collect_for,
                    "event_count": len(events),
                    "events": events,
                }

            if action == "notification_feed":
                events = await subscribe_collect(
                    COLLECT_ACTIONS["notification_feed"],
                    collect_for=collect_for,
                    timeout=timeout,
                )
                return {
                    "success": True,
                    "action": action,
                    "collect_for": collect_for,
                    "event_count": len(events),
                    "events": events,
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Live tool registered successfully")
