"""Tests for key subactions of the consolidated unraid tool."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.core.client.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool() -> Callable[..., Any]:
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


class TestKeysValidation:
    async def test_delete_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action="key", subaction="delete", key_id="k:1")

    async def test_get_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="key", subaction="get")

    async def test_create_requires_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="name"):
            await tool_fn(action="key", subaction="create")

    async def test_update_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="key", subaction="update")

    async def test_delete_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="key", subaction="delete", confirm=True)


class TestKeysActions:
    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKeys": [{"id": "k:1", "name": "mcp-key", "roles": ["admin"]}]
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="list")
        assert len(result["keys"]) == 1

    async def test_get(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKey": {"id": "k:1", "name": "mcp-key", "roles": ["admin"]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="get", key_id="k:1")
        assert result["name"] == "mcp-key"

    async def test_create(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKey": {
                "create": {"id": "k:new", "name": "new-key", "key": "secret123", "roles": []}
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="create", name="new-key")
        assert result["success"] is True
        assert result["key"]["name"] == "new-key"

    async def test_create_with_roles(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKey": {
                "create": {
                    "id": "k:new",
                    "name": "admin-key",
                    "key": "secret",
                    "roles": ["admin"],
                }
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="create", name="admin-key", roles=["admin"])
        assert result["success"] is True

    async def test_update(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKey": {"update": {"id": "k:1", "name": "renamed", "roles": []}}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="update", key_id="k:1", name="renamed")
        assert result["success"] is True

    async def test_delete(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"apiKey": {"delete": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="key", subaction="delete", key_id="k:1", confirm=True)
        assert result["success"] is True

    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("connection lost")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Failed to execute key/list"):
            await tool_fn(action="key", subaction="list")

    async def test_add_role_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="key", subaction="add_role", roles=["VIEWER"])

    async def test_add_role_requires_role(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="role"):
            await tool_fn(action="key", subaction="add_role", key_id="abc:local")

    async def test_add_role_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"apiKey": {"addRole": True}}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="key", subaction="add_role", key_id="abc:local", roles=["VIEWER"]
        )
        assert result["success"] is True

    async def test_remove_role_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"apiKey": {"removeRole": True}}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="key", subaction="remove_role", key_id="abc:local", roles=["VIEWER"]
        )
        assert result["success"] is True
