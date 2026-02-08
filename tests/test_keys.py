"""Tests for unraid_keys tool."""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> AsyncMock:
    with patch("unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")


class TestKeysValidation:
    async def test_delete_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete", key_id="k:1")

    async def test_get_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="get")

    async def test_create_requires_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="name"):
            await tool_fn(action="create")

    async def test_update_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="update")

    async def test_delete_requires_key_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="key_id"):
            await tool_fn(action="delete", confirm=True)


class TestKeysActions:
    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "apiKeys": [{"id": "k:1", "name": "mcp-key", "roles": ["admin"]}]
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="list")
        assert len(result["keys"]) == 1

    async def test_get(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"apiKey": {"id": "k:1", "name": "mcp-key", "roles": ["admin"]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="get", key_id="k:1")
        assert result["name"] == "mcp-key"

    async def test_create(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "createApiKey": {"id": "k:new", "name": "new-key", "key": "secret123", "roles": []}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="create", name="new-key")
        assert result["success"] is True
        assert result["key"]["name"] == "new-key"

    async def test_create_with_roles(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "createApiKey": {"id": "k:new", "name": "admin-key", "key": "secret", "roles": ["admin"]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="create", name="admin-key", roles=["admin"])
        assert result["success"] is True

    async def test_update(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateApiKey": {"id": "k:1", "name": "renamed", "roles": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="update", key_id="k:1", name="renamed")
        assert result["success"] is True

    async def test_delete(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"deleteApiKeys": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="delete", key_id="k:1", confirm=True)
        assert result["success"] is True
