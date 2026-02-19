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
            "mount_disk",
            "unmount_disk",
            "clear_stats",
        ):
            with pytest.raises(ToolError, match="Invalid action"):
                await tool_fn(action=action)


class TestArrayActions:
    async def test_parity_start(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start")
        assert result["success"] is True
        assert result["action"] == "parity_start"
        _mock_graphql.assert_called_once()

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
        result = await tool_fn(action="parity_start")
        assert result["success"] is True
        assert result["data"] == {"parityCheck": {"start": False}}

    async def test_parity_start_mutation_returns_null(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": None}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start")
        assert result["success"] is True
        assert result["data"] == {"parityCheck": {"start": None}}

    async def test_parity_start_mutation_returns_empty_object(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"parityCheck": {"start": {}}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_start")
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
            await tool_fn(action="parity_start")

    async def test_connection_refused(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = ToolError("Network connection error: Connection refused")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Network connection error"):
            await tool_fn(action="parity_status")
