"""Live (subscriptions) domain handler for the Unraid MCP tool.

Covers: cpu, memory, cpu_telemetry, array_state, parity_progress, ups_status,
notifications_overview, notifications_warnings, notification_feed, log_tail, owner,
server_status, docker_container_stats, temperature, display,
plugin_install_updates (16 subactions).
"""

from typing import Any

from ..config.logging import logger
from ..core.exceptions import ToolError, tool_error_handler
from ..core.pagination import cap_list
from ._disk import _ALLOWED_LOG_PREFIXES, _validate_path


# ===========================================================================
# LIVE (subscriptions)
# ===========================================================================


def _filter_log_event(event: dict[str, Any], level: str, context: int) -> dict[str, Any]:
    """Apply severity/context filtering to a single log_tail event's content.

    Each event is shaped ``{"logFile": {"content": "...", ...}}``. The ``content``
    field is a newline-joined block of log lines. Returns a shallow-copied event
    with the filtered content, a ``matchedLines`` count (lines that actually
    matched the severity filter) and a ``returnedLines`` count (real log lines
    returned including context, excluding ``"---"`` separators). Events lacking a
    string ``content`` are returned unchanged.
    """
    from ..core.utils import count_log_matches, filter_log_lines

    log_file = event.get("logFile")
    if not isinstance(log_file, dict):
        return event
    content = log_file.get("content")
    if not isinstance(content, str):
        return event

    lines = content.split("\n")
    filtered = filter_log_lines(lines, level=level, context=context)
    new_log_file = {
        **log_file,
        "content": "\n".join(filtered),
        "matchedLines": count_log_matches(lines, level=level),
        "returnedLines": sum(1 for line in filtered if line != "---"),
    }
    return {**event, "logFile": new_log_file}


async def _handle_live(
    subaction: str,
    path: str | None,
    collect_for: float,
    timeout: float,  # noqa: ASYNC109
    level: str | None = None,
    context: int = 2,
    limit: int | None = None,
    operation_id: str | None = None,
) -> dict[str, Any]:
    # IMPORTANT: Every key in COLLECT_ACTIONS must have an explicit handler in _handle_live below.
    # Adding to COLLECT_ACTIONS without updating this function causes a ToolError at runtime.
    from ..core.utils import validate_subaction
    from ..subscriptions.manager import subscription_manager
    from ..subscriptions.queries import COLLECT_ACTIONS, EVENT_DRIVEN_ACTIONS, SNAPSHOT_ACTIONS
    from ..subscriptions.snapshot import subscribe_collect, subscribe_once

    all_live = set(SNAPSHOT_ACTIONS) | set(COLLECT_ACTIONS)
    validate_subaction(subaction, all_live, "live")

    if subaction == "log_tail":
        if not path:
            raise ToolError("path is required for live/log_tail")
        path = _validate_path(path, _ALLOWED_LOG_PREFIXES, "path")

    with tool_error_handler("live", subaction, logger):
        logger.info(f"Executing unraid action=live subaction={subaction} timeout={timeout}")

        if subaction in SNAPSHOT_ACTIONS:
            # Warm-cache fast path: when the persistent SubscriptionManager is
            # auto-starting subscriptions, a long-lived WebSocket for this snapshot
            # subaction is already holding fresh data. The snapshot subaction name
            # is identical to the manager's subscription name (both come from
            # SNAPSHOT_ACTIONS keys — see manager.subscription_configs), so we can
            # serve the cached resource data directly and skip the full per-call WS
            # handshake. Falls through to the live path below when the cache is cold
            # (None) or auto-start is disabled.
            if subscription_manager.auto_start_enabled:
                cached = await subscription_manager.get_resource_data(subaction)
                if cached is not None:
                    logger.debug(
                        "live/%s served from warm subscription cache (skipped fresh WS)",
                        subaction,
                    )
                    return {
                        "success": True,
                        "subaction": subaction,
                        "source": "cache",
                        "data": cached,
                    }

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
            return {"success": True, "subaction": subaction, "source": "live", "data": data}

        if subaction == "log_tail":
            events = await subscribe_collect(
                COLLECT_ACTIONS["log_tail"],
                variables={"path": path},
                collect_for=collect_for,
                timeout=timeout,
            )
            if level is not None:
                events = [_filter_log_event(e, level, context) for e in events]
            # Hard-cap the number of collected events so a noisy log over the
            # window can't flood the agent's context.
            capped, meta = cap_list(events, limit)
            return {
                "success": True,
                "subaction": subaction,
                "path": path,
                "collect_for": collect_for,
                "filter": {"level": level, "context": context} if level is not None else None,
                "event_count": len(capped),
                "events": capped,
                "page": meta,
            }

        if subaction in ("notification_feed", "plugin_install_updates"):
            # pluginInstallUpdates(operationId: ID!) requires the operation id;
            # notification_feed takes no variables.
            variables: dict[str, Any] | None = None
            if subaction == "plugin_install_updates":
                if not operation_id:
                    raise ToolError("operation_id is required for live/plugin_install_updates")
                variables = {"operationId": operation_id}
            events = await subscribe_collect(
                COLLECT_ACTIONS[subaction],
                variables=variables,
                collect_for=collect_for,
                timeout=timeout,
            )
            # Hard-cap the number of collected events (see log_tail above).
            capped, meta = cap_list(events, limit)
            return {
                "success": True,
                "subaction": subaction,
                "collect_for": collect_for,
                "event_count": len(capped),
                "events": capped,
                "page": meta,
            }

        raise ToolError(f"Unhandled live subaction '{subaction}' — this is a bug")
