"""Live (subscriptions) domain handler for the Unraid MCP tool.

Covers: cpu, memory, cpu_telemetry, array_state, parity_progress, ups_status,
notifications_overview, notification_feed, log_tail, owner, server_status (11 subactions).
"""

from typing import Any

from ..config.logging import logger
from ..core.exceptions import ToolError, tool_error_handler
from ._disk import _ALLOWED_LOG_PREFIXES, _validate_path


# ===========================================================================
# LIVE (subscriptions)
# ===========================================================================


async def _handle_live(
    subaction: str,
    path: str | None,
    collect_for: float,
    timeout: float,  # noqa: ASYNC109
) -> dict[str, Any]:
    from ..subscriptions.queries import COLLECT_ACTIONS, EVENT_DRIVEN_ACTIONS, SNAPSHOT_ACTIONS
    from ..subscriptions.snapshot import subscribe_collect, subscribe_once

    all_live = set(SNAPSHOT_ACTIONS) | set(COLLECT_ACTIONS)
    if subaction not in all_live:
        raise ToolError(
            f"Invalid subaction '{subaction}' for live. Must be one of: {sorted(all_live)}"
        )

    if subaction == "log_tail":
        if not path:
            raise ToolError("path is required for live/log_tail")
        path = _validate_path(path, _ALLOWED_LOG_PREFIXES, "path")

    with tool_error_handler("live", subaction, logger):
        logger.info(f"Executing unraid action=live subaction={subaction} timeout={timeout}")

        if subaction in SNAPSHOT_ACTIONS:
            if subaction in EVENT_DRIVEN_ACTIONS:
                try:
                    data = await subscribe_once(SNAPSHOT_ACTIONS[subaction], timeout=timeout)
                except ToolError as e:
                    if "timed out" in str(e):
                        return {
                            "success": True,
                            "subaction": subaction,
                            "status": "no_recent_events",
                            "message": f"No events received in {timeout:.0f}s — this subscription only emits on state changes",
                        }
                    raise
            else:
                data = await subscribe_once(SNAPSHOT_ACTIONS[subaction], timeout=timeout)
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "log_tail":
            events = await subscribe_collect(
                COLLECT_ACTIONS["log_tail"],
                variables={"path": path},
                collect_for=collect_for,
                timeout=timeout,
            )
            return {
                "success": True,
                "subaction": subaction,
                "path": path,
                "collect_for": collect_for,
                "event_count": len(events),
                "events": events,
            }

        if subaction == "notification_feed":
            events = await subscribe_collect(
                COLLECT_ACTIONS["notification_feed"], collect_for=collect_for, timeout=timeout
            )
            return {
                "success": True,
                "subaction": subaction,
                "collect_for": collect_for,
                "event_count": len(events),
                "events": events,
            }

        raise ToolError(f"Unhandled live subaction '{subaction}' — this is a bug")
