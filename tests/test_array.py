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

    async def test_parity_status(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"array": {"parityCheckStatus": {"progress": 50}}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_status")
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

    async def test_stop_array(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setState": {"state": "STOPPED"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="stop", confirm=True)
        assert result["success"] is True
        assert result["action"] == "stop"

    async def test_reboot(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"reboot": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="reboot", confirm=True)
        assert result["success"] is True
        assert result["action"] == "reboot"

    async def test_parity_pause(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"parityCheck": {"pause": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="parity_pause")
        assert result["success"] is True

    async def test_unmount_disk(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"unmountArrayDisk": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="unmount_disk", disk_id="disk:1")
        assert result["success"] is True

    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("disk error")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="disk error"):
            await tool_fn(action="parity_status")


class TestArrayMutationFailures:
    """Tests for mutation responses that indicate failure."""

    async def test_start_mutation_returns_false(self, _mock_graphql: AsyncMock) -> None:
        """Mutation returning False in the response field should still succeed (the tool
        wraps the raw response; it doesn't inspect the inner boolean)."""
        _mock_graphql.return_value = {"setState": False}
        tool_fn = _make_tool()
        result = await tool_fn(action="start", confirm=True)
        assert result["success"] is True
        assert result["data"] == {"setState": False}

    async def test_start_mutation_returns_null(self, _mock_graphql: AsyncMock) -> None:
        """Mutation returning null for the response field."""
        _mock_graphql.return_value = {"setState": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="start", confirm=True)
        assert result["success"] is True
        assert result["data"] == {"setState": None}

    async def test_start_mutation_returns_empty_object(self, _mock_graphql: AsyncMock) -> None:
        """Mutation returning an empty object for the response field."""
        _mock_graphql.return_value = {"setState": {}}
        tool_fn = _make_tool()
        result = await tool_fn(action="start", confirm=True)
        assert result["success"] is True
        assert result["data"] == {"setState": {}}

    async def test_mount_disk_mutation_returns_false(self, _mock_graphql: AsyncMock) -> None:
        """mountArrayDisk returning False indicates mount failed."""
        _mock_graphql.return_value = {"mountArrayDisk": False}
        tool_fn = _make_tool()
        result = await tool_fn(action="mount_disk", disk_id="disk:1")
        assert result["success"] is True
        assert result["data"]["mountArrayDisk"] is False

    async def test_mutation_timeout(self, _mock_graphql: AsyncMock) -> None:
        """Mid-operation timeout should be wrapped in ToolError."""

        _mock_graphql.side_effect = TimeoutError("operation timed out")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="timed out"):
            await tool_fn(action="shutdown", confirm=True)


class TestArrayNetworkErrors:
    """Tests for network-level failures in array operations."""

    async def test_http_500_server_error(self, _mock_graphql: AsyncMock) -> None:
        """HTTP 500 from the API should be wrapped in ToolError."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        _mock_graphql.side_effect = ToolError("HTTP error 500: Internal Server Error")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="HTTP error 500"):
            await tool_fn(action="start", confirm=True)

    async def test_connection_refused(self, _mock_graphql: AsyncMock) -> None:
        """Connection refused should be wrapped in ToolError."""
        _mock_graphql.side_effect = ToolError("Network connection error: Connection refused")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Network connection error"):
            await tool_fn(action="parity_status")
