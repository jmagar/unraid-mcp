# tests/test_live.py
"""Tests for unraid_live subscription snapshot tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mcp():
    return FastMCP("test")


def _make_live_tool(mcp):
    from unraid_mcp.tools.live import register_live_tool

    register_live_tool(mcp)
    local_provider = mcp.providers[0]
    tool = local_provider._components["tool:unraid_live@"]
    return tool.fn


@pytest.fixture
def _mock_subscribe_once():
    with patch("unraid_mcp.tools.live.subscribe_once") as m:
        yield m


@pytest.fixture
def _mock_subscribe_collect():
    with patch("unraid_mcp.tools.live.subscribe_collect") as m:
        yield m


@pytest.mark.asyncio
async def test_cpu_returns_snapshot(mcp, _mock_subscribe_once):
    _mock_subscribe_once.return_value = {"systemMetricsCpu": {"percentTotal": 23.5, "cpus": []}}
    tool_fn = _make_live_tool(mcp)
    result = await tool_fn(action="cpu")
    assert result["success"] is True
    assert result["data"]["systemMetricsCpu"]["percentTotal"] == 23.5


@pytest.mark.asyncio
async def test_memory_returns_snapshot(mcp, _mock_subscribe_once):
    _mock_subscribe_once.return_value = {
        "systemMetricsMemory": {"total": 32000000000, "used": 10000000000, "percentTotal": 31.2}
    }
    tool_fn = _make_live_tool(mcp)
    result = await tool_fn(action="memory")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_log_tail_requires_path(mcp, _mock_subscribe_collect):
    _mock_subscribe_collect.return_value = []
    tool_fn = _make_live_tool(mcp)
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="path"):
        await tool_fn(action="log_tail")


@pytest.mark.asyncio
async def test_log_tail_with_path(mcp, _mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"logFile": {"path": "/var/log/syslog", "content": "line1\nline2", "totalLines": 2}}
    ]
    tool_fn = _make_live_tool(mcp)
    result = await tool_fn(action="log_tail", path="/var/log/syslog", collect_for=1.0)
    assert result["success"] is True
    assert result["event_count"] == 1


@pytest.mark.asyncio
async def test_notification_feed_collects_events(mcp, _mock_subscribe_collect):
    _mock_subscribe_collect.return_value = [
        {"notificationAdded": {"id": "1", "title": "Alert"}},
        {"notificationAdded": {"id": "2", "title": "Info"}},
    ]
    tool_fn = _make_live_tool(mcp)
    result = await tool_fn(action="notification_feed", collect_for=2.0)
    assert result["event_count"] == 2


@pytest.mark.asyncio
async def test_invalid_action_raises(mcp):
    from unraid_mcp.core.exceptions import ToolError

    tool_fn = _make_live_tool(mcp)
    with pytest.raises(ToolError, match="Invalid action"):
        await tool_fn(action="nonexistent")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_snapshot_propagates_tool_error(mcp, _mock_subscribe_once):
    from unraid_mcp.core.exceptions import ToolError

    _mock_subscribe_once.side_effect = ToolError("Subscription timed out after 10s")
    tool_fn = _make_live_tool(mcp)
    with pytest.raises(ToolError, match="timed out"):
        await tool_fn(action="cpu")


@pytest.mark.asyncio
async def test_log_tail_rejects_invalid_path(mcp, _mock_subscribe_collect):
    from unraid_mcp.core.exceptions import ToolError

    tool_fn = _make_live_tool(mcp)
    with pytest.raises(ToolError, match="must start with"):
        await tool_fn(action="log_tail", path="/etc/shadow")
