# tests/test_live.py
"""Tests for live subactions of the consolidated unraid tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from conftest import make_tool_fn


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


@pytest.fixture
def _mock_subscribe_once():
    with patch("unraid_mcp.subscriptions.snapshot.subscribe_once") as m:
        yield m


@pytest.fixture
def _mock_subscribe_collect():
    with patch("unraid_mcp.subscriptions.snapshot.subscribe_collect") as m:
        yield m


@pytest.mark.asyncio
async def test_cpu_returns_snapshot(_mock_subscribe_once):
    _mock_subscribe_once.return_value = {"systemMetricsCpu": {"percentTotal": 23.5, "cpus": []}}
    result = await _make_tool()(action="live", subaction="cpu")
    assert result["success"] is True
    assert result["data"]["systemMetricsCpu"]["percentTotal"] == 23.5


@pytest.mark.asyncio
async def test_memory_returns_snapshot(_mock_subscribe_once):
    _mock_subscribe_once.return_value = {
        "systemMetricsMemory": {"total": 32000000000, "used": 10000000000, "percentTotal": 31.2}
    }
    result = await _make_tool()(action="live", subaction="memory")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_log_tail_requires_path(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = []
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="path"):
        await _make_tool()(action="live", subaction="log_tail")


@pytest.mark.asyncio
async def test_log_tail_with_path(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"logFile": {"path": "/var/log/syslog", "content": "line1\nline2", "totalLines": 2}}
    ]
    result = await _make_tool()(
        action="live", subaction="log_tail", path="/var/log/syslog", collect_for=1.0
    )
    assert result["success"] is True
    assert result["event_count"] == 1


@pytest.mark.asyncio
async def test_notification_feed_collects_events(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"notificationAdded": {"id": "1", "title": "Alert"}},
        {"notificationAdded": {"id": "2", "title": "Info"}},
    ]
    result = await _make_tool()(action="live", subaction="notification_feed", collect_for=2.0)
    assert result["event_count"] == 2


@pytest.mark.asyncio
async def test_log_tail_caps_events_default(_mock_subscribe_collect):
    # Tool param default is 20 — a noisy log window must not flood context.
    _mock_subscribe_collect.return_value = [
        {"logFile": {"path": "/var/log/syslog", "content": f"line{i}"}} for i in range(60)
    ]
    result = await _make_tool()(
        action="live", subaction="log_tail", path="/var/log/syslog", collect_for=1.0
    )
    assert result["event_count"] == 20
    assert len(result["events"]) == 20
    assert result["page"]["truncated"] is True
    assert result["page"]["total"] == 60


@pytest.mark.asyncio
async def test_log_tail_limit_zero_returns_all(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"logFile": {"path": "/var/log/syslog", "content": f"line{i}"}} for i in range(60)
    ]
    result = await _make_tool()(
        action="live", subaction="log_tail", path="/var/log/syslog", collect_for=1.0, limit=0
    )
    assert result["event_count"] == 60
    assert result["page"]["truncated"] is False


@pytest.mark.asyncio
async def test_notification_feed_caps_events_default(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"notificationAdded": {"id": str(i)}} for i in range(60)
    ]
    result = await _make_tool()(action="live", subaction="notification_feed", collect_for=2.0)
    assert result["event_count"] == 20
    assert len(result["events"]) == 20
    assert result["page"]["truncated"] is True


@pytest.mark.asyncio
async def test_notification_feed_limit_narrows(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"notificationAdded": {"id": str(i)}} for i in range(60)
    ]
    result = await _make_tool()(
        action="live", subaction="notification_feed", collect_for=2.0, limit=5
    )
    assert result["event_count"] == 5


@pytest.mark.asyncio
async def test_notification_feed_limit_zero_returns_all(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"notificationAdded": {"id": str(i)}} for i in range(60)
    ]
    result = await _make_tool()(
        action="live", subaction="notification_feed", collect_for=2.0, limit=0
    )
    assert result["event_count"] == 60
    assert result["page"]["truncated"] is False


@pytest.mark.asyncio
async def test_invalid_subaction_raises():
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="Invalid subaction"):
        await _make_tool()(action="live", subaction="nonexistent")


@pytest.mark.asyncio
async def test_snapshot_propagates_tool_error(_mock_subscribe_once):
    """Non-event-driven (streaming) actions still propagate timeout as ToolError."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = ToolError("Subscription timed out after 10s")
    with pytest.raises(ToolError, match="timed out"):
        await _make_tool()(action="live", subaction="cpu")


@pytest.mark.asyncio
async def test_event_driven_timeout_returns_no_recent_events(_mock_subscribe_once):
    """Event-driven subscriptions return a graceful no_recent_events response on timeout."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = ToolError("Subscription timed out after 10s")
    result = await _make_tool()(action="live", subaction="notifications_overview")
    assert result["success"] is True
    assert result["status"] == "no_recent_events"
    assert "No events received" in result["message"]


@pytest.mark.asyncio
async def test_event_driven_non_timeout_error_propagates(_mock_subscribe_once):
    """Non-timeout ToolErrors from event-driven subscriptions still propagate."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = ToolError("Subscription auth failed")
    with pytest.raises(ToolError, match="auth failed"):
        await _make_tool()(action="live", subaction="owner")


@pytest.mark.asyncio
async def test_log_tail_rejects_invalid_path(_mock_subscribe_collect):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="must start with"):
        await _make_tool()(action="live", subaction="log_tail", path="/etc/shadow")


@pytest.mark.asyncio
async def test_snapshot_wraps_bare_exception(_mock_subscribe_once):
    """Bare exceptions from subscribe_once are wrapped in ToolError by tool_error_handler."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = RuntimeError("WebSocket connection refused")
    with pytest.raises(ToolError):
        await _make_tool()(action="live", subaction="cpu")


def test_collect_actions_all_handled():
    """Every COLLECT_ACTIONS key must have an explicit handler in _handle_live.

    If this test fails, a new key was added to COLLECT_ACTIONS in
    subscriptions/queries.py without adding a corresponding if-branch in
    tools/_live.py — which would cause a ToolError('this is a bug') at runtime.
    Fix: add an if-branch in _handle_live for the new key.
    """
    import inspect

    from unraid_mcp.subscriptions.queries import COLLECT_ACTIONS
    from unraid_mcp.tools._live import _handle_live

    source = inspect.getsource(_handle_live)
    unhandled = {key for key in COLLECT_ACTIONS if f'"{key}"' not in source}
    assert not unhandled, (
        f"COLLECT_ACTIONS keys without handlers in _handle_live: {unhandled}. "
        "Add an if-branch in unraid_mcp/tools/_live.py."
    )


@pytest.mark.asyncio
async def test_log_tail_level_filters_events(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {
            "logFile": {
                "path": "/var/log/syslog",
                "content": "a info\nb [ERROR] boom\nc info\nd info",
                "totalLines": 4,
            }
        }
    ]
    result = await _make_tool()(
        action="live",
        subaction="log_tail",
        path="/var/log/syslog",
        collect_for=1.0,
        level="error",
        context=1,
    )
    assert result["filter"] == {"level": "error", "context": 1}
    log_file = result["events"][0]["logFile"]
    # match at idx1, context 1 → idx 0..2
    assert log_file["content"] == "a info\nb [ERROR] boom\nc info"
    # only the single [ERROR] line actually matched the severity filter (#48)
    assert log_file["matchedLines"] == 1
    # 3 real lines returned (match + 2 context), no "---" separator
    assert log_file["returnedLines"] == 3
    assert log_file["matchedLines"] < log_file["returnedLines"]
    # original fields preserved
    assert log_file["path"] == "/var/log/syslog"


@pytest.mark.asyncio
async def test_log_tail_no_level_unchanged(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"logFile": {"path": "/var/log/syslog", "content": "a info\nb [ERROR] boom"}}
    ]
    result = await _make_tool()(
        action="live", subaction="log_tail", path="/var/log/syslog", collect_for=1.0
    )
    assert result["filter"] is None
    assert result["events"][0]["logFile"]["content"] == "a info\nb [ERROR] boom"


# ---------------------------------------------------------------------------
# New subscriptions: display, notifications_warnings, plugin_install_updates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_display_returns_snapshot(_mock_subscribe_once):
    _mock_subscribe_once.return_value = {
        "displaySubscription": {"theme": "white", "locale": "en_US"}
    }
    result = await _make_tool()(action="live", subaction="display")
    assert result["success"] is True
    assert result["data"]["displaySubscription"]["theme"] == "white"


@pytest.mark.asyncio
async def test_notifications_warnings_returns_snapshot(_mock_subscribe_once):
    _mock_subscribe_once.return_value = {
        "notificationsWarningsAndAlerts": [{"id": "n1", "importance": "ALERT"}]
    }
    result = await _make_tool()(action="live", subaction="notifications_warnings")
    assert result["success"] is True
    assert result["data"]["notificationsWarningsAndAlerts"][0]["importance"] == "ALERT"


@pytest.mark.asyncio
async def test_plugin_install_updates_requires_operation_id(_mock_subscribe_collect):
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_collect.return_value = []
    with pytest.raises(ToolError, match="operation_id is required"):
        await _make_tool()(action="live", subaction="plugin_install_updates")


@pytest.mark.asyncio
async def test_plugin_install_updates_passes_operation_id(_mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"pluginInstallUpdates": {"operationId": "op1", "status": "RUNNING"}}
    ]
    result = await _make_tool()(
        action="live",
        subaction="plugin_install_updates",
        operation_id="op1",
        collect_for=1.0,
    )
    assert result["success"] is True
    assert result["events"][0]["pluginInstallUpdates"]["operationId"] == "op1"
    # operationId must be forwarded as a subscription variable
    assert _mock_subscribe_collect.call_args.kwargs["variables"] == {"operationId": "op1"}


@pytest.mark.asyncio
async def test_snapshot_actions_all_handled():
    """Every SNAPSHOT_ACTIONS key must route through _handle_live without error.

    Guards against adding a subscription key but forgetting the handler branch.
    """
    from unittest.mock import patch

    from unraid_mcp.subscriptions.queries import SNAPSHOT_ACTIONS

    with patch("unraid_mcp.subscriptions.snapshot.subscribe_once") as once:
        once.return_value = {"ok": True}
        for action in SNAPSHOT_ACTIONS:
            result = await _make_tool()(action="live", subaction=action, timeout=1.0)
            assert result["subaction"] == action
