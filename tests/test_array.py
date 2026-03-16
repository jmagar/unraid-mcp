"""Tests for unraid_array tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.array.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.array", "register_array_tool", "unraid_array")


class TestArrayValidation:
    async def test_invalid_action_rejected(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="start")

    async def test_removed_actions_are_invalid(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        for action in (
            "start",
            "stop",
            "shutdown",
            "reboot",
            "clear_stats",
        ):
            with pytest.raises(ToolError, match="Invalid action"):
                await tool_fn(action=action)

    async def test_parity_start_requires_correct(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="correct is required"):
            await tool_fn(action="parity_start")
        _mock_graphql.assert_not_called()


class TestArrayActions:
    async def test_parity_start(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=False)
        assert result["success"] is True
        assert result["action"] == "parity_start"
        _mock_graphql.assert_called_once()
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"correct": False}

    async def test_parity_start_with_correct(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=True)
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"correct": True}

    async def test_parity_status(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"array": {"parityCheckStatus": {"progress": 50}}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_status")
        assert result["success"] is True

    async def test_parity_pause(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"pause": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_pause")
        assert result["success"] is True

    async def test_parity_resume(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"resume": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_resume")
        assert result["success"] is True

    async def test_parity_cancel(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"cancel": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_cancel")
        assert result["success"] is True

    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("disk error")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Failed to execute array/parity_status"):
            await tool_fn(action="parity_status")


class TestArrayMutationFailures:
    """Tests for mutation responses that indicate failure."""

    async def test_parity_start_mutation_returns_false(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": False}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=False)
        assert result["success"] is True
        assert result["data"] == {"parityCheck": {"start": False}}

    async def test_parity_start_mutation_returns_null(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": None}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=False)
        assert result["success"] is True
        assert result["data"] == {"parityCheck": {"start": None}}

    async def test_parity_start_mutation_returns_empty_object(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": {}}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start", correct=False)
        assert result["success"] is True
        assert result["data"] == {"parityCheck": {"start": {}}}

    async def test_mutation_timeout(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = TimeoutError("operation timed out")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="timed out"):
            await tool_fn(action="parity_cancel")


class TestArrayNetworkErrors:
    """Tests for network-level failures in array operations."""

    async def test_http_500_server_error(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = ToolError("HTTP error 500: Internal Server Error")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="HTTP error 500"):
            await tool_fn(action="parity_start", correct=False)

    async def test_connection_refused(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = ToolError("Network connection error: Connection refused")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Network connection error"):
            await tool_fn(action="parity_status")


# ---------------------------------------------------------------------------
# New actions: parity_history, start/stop array, disk operations
# ---------------------------------------------------------------------------


# parity_history


@pytest.mark.asyncio
async def test_parity_history_returns_history(_mock_graphql):
    _mock_graphql.return_value = {
        "parityHistory": [{"date": "2026-03-01T00:00:00Z", "status": "COMPLETED", "errors": 0}]
    }
    result = await _make_tool()(action="parity_history")
    assert result["success"] is True
    assert len(result["data"]["parityHistory"]) == 1


# Array state mutations


@pytest.mark.asyncio
async def test_start_array(_mock_graphql):
    _mock_graphql.return_value = {"array": {"setState": {"state": "STARTED"}}}
    result = await _make_tool()(action="start_array")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_stop_array_requires_confirm(_mock_graphql):
    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool()(action="stop_array", confirm=False)


@pytest.mark.asyncio
async def test_stop_array_with_confirm(_mock_graphql):
    _mock_graphql.return_value = {"array": {"setState": {"state": "STOPPED"}}}
    result = await _make_tool()(action="stop_array", confirm=True)
    assert result["success"] is True


# add_disk


@pytest.mark.asyncio
async def test_add_disk_requires_disk_id(_mock_graphql):
    with pytest.raises(ToolError, match="disk_id"):
        await _make_tool()(action="add_disk")


@pytest.mark.asyncio
async def test_add_disk_success(_mock_graphql):
    _mock_graphql.return_value = {"array": {"addDiskToArray": {"state": "STARTED"}}}
    result = await _make_tool()(action="add_disk", disk_id="abc123:local")
    assert result["success"] is True


# remove_disk — destructive


@pytest.mark.asyncio
async def test_remove_disk_requires_confirm(_mock_graphql):
    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool()(action="remove_disk", disk_id="abc123:local", confirm=False)


@pytest.mark.asyncio
async def test_remove_disk_with_confirm(_mock_graphql):
    _mock_graphql.return_value = {"array": {"removeDiskFromArray": {"state": "STOPPED"}}}
    result = await _make_tool()(action="remove_disk", disk_id="abc123:local", confirm=True)
    assert result["success"] is True


# mount_disk / unmount_disk


@pytest.mark.asyncio
async def test_mount_disk_requires_disk_id(_mock_graphql):
    with pytest.raises(ToolError, match="disk_id"):
        await _make_tool()(action="mount_disk")


@pytest.mark.asyncio
async def test_unmount_disk_success(_mock_graphql):
    _mock_graphql.return_value = {"array": {"unmountArrayDisk": {"id": "abc123:local"}}}
    result = await _make_tool()(action="unmount_disk", disk_id="abc123:local")
    assert result["success"] is True


# clear_disk_stats — destructive


@pytest.mark.asyncio
async def test_clear_disk_stats_requires_confirm(_mock_graphql):
    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool()(action="clear_disk_stats", disk_id="abc123:local", confirm=False)


@pytest.mark.asyncio
async def test_clear_disk_stats_with_confirm(_mock_graphql):
    _mock_graphql.return_value = {"array": {"clearArrayDiskStatistics": True}}
    result = await _make_tool()(action="clear_disk_stats", disk_id="abc123:local", confirm=True)
    assert result["success"] is True
