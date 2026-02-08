"""Tests for unraid_array tool."""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> AsyncMock:
    with patch("unraid_mcp.tools.array.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.array", "register_array_tool", "unraid_array")


class TestArrayValidation:
    async def test_destructive_action_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        for action in ("start", "stop", "shutdown", "reboot"):
            with pytest.raises(ToolError, match="destructive"):
                await tool_fn(action=action)

    async def test_disk_action_requires_disk_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        for action in ("mount_disk", "unmount_disk", "clear_stats"):
            with pytest.raises(ToolError, match="disk_id"):
                await tool_fn(action=action)


class TestArrayActions:
    async def test_start_array(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setState": {"state": "STARTED"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="start", confirm=True)
        assert result["success"] is True
        assert result["action"] == "start"
        _mock_graphql.assert_called_once()

    async def test_parity_start_with_correct(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=True)
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"correct": True}

    async def test_parity_history(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"array": {"parityCheckStatus": {"progress": 50}}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_history")
        assert result["success"] is True

    async def test_mount_disk(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"mountArrayDisk": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="mount_disk", disk_id="disk:1")
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"id": "disk:1"}

    async def test_shutdown(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"shutdown": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="shutdown", confirm=True)
        assert result["success"] is True
        assert result["action"] == "shutdown"

    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("disk error")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="disk error"):
            await tool_fn(action="parity_history")
