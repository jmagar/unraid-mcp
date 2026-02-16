"""Tests for unraid_rclone tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.rclone.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.rclone", "register_rclone_tool", "unraid_rclone")


@pytest.mark.usefixtures("_mock_graphql")
class TestRcloneValidation:
    async def test_delete_requires_confirm(self) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete_remote", name="gdrive")

    async def test_create_requires_fields(self) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="requires name"):
            await tool_fn(action="create_remote")

    async def test_delete_requires_name(self) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="name is required"):
            await tool_fn(action="delete_remote", confirm=True)


class TestRcloneActions:
    async def test_list_remotes(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"rclone": {"remotes": [{"name": "gdrive", "type": "drive"}]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="list_remotes")
        assert len(result["remotes"]) == 1

    async def test_config_form(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "rclone": {"configForm": {"id": "form:1", "dataSchema": {}, "uiSchema": {}}}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="config_form")
        assert result["id"] == "form:1"

    async def test_config_form_with_provider(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "rclone": {"configForm": {"id": "form:s3", "dataSchema": {}, "uiSchema": {}}}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="config_form", provider_type="s3")
        assert result["id"] == "form:s3"
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"formOptions": {"providerType": "s3"}}

    async def test_create_remote(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "rclone": {"createRCloneRemote": {"name": "newremote", "type": "s3"}}
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="create_remote",
            name="newremote",
            provider_type="s3",
            config_data={"bucket": "mybucket"},
        )
        assert result["success"] is True

    async def test_create_remote_with_empty_config(self, _mock_graphql: AsyncMock) -> None:
        """Empty config_data dict should be accepted (not rejected by truthiness)."""
        _mock_graphql.return_value = {
            "rclone": {"createRCloneRemote": {"name": "ftp-remote", "type": "ftp"}}
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="create_remote",
            name="ftp-remote",
            provider_type="ftp",
            config_data={},
        )
        assert result["success"] is True

    async def test_delete_remote(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"rclone": {"deleteRCloneRemote": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="delete_remote", name="gdrive", confirm=True)
        assert result["success"] is True

    async def test_delete_remote_failure(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"rclone": {"deleteRCloneRemote": False}}
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Failed to delete"):
            await tool_fn(action="delete_remote", name="gdrive", confirm=True)
