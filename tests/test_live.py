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
async def test_invalid_subaction_raises():
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="Invalid subaction"):
        await _make_tool()(action="live", subaction="nonexistent")


@pytest.mark.asyncio
async def test_snapshot_propagates_tool_error(_mock_subscribe_once):
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = ToolError("Subscription timed out after 10s")
    with pytest.raises(ToolError, match="timed out"):
        await _make_tool()(action="live", subaction="cpu")


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
