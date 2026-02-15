"""Tests for unraid_users tool."""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> AsyncMock:
    with patch("unraid_mcp.tools.users.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.users", "register_users_tool", "unraid_users")


class TestUsersValidation:
    async def test_delete_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete", user_id="u:1")

    async def test_get_requires_user_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="user_id"):
            await tool_fn(action="get")

    async def test_add_requires_name_and_password(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="requires name and password"):
            await tool_fn(action="add")

    async def test_delete_requires_user_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="user_id"):
            await tool_fn(action="delete", confirm=True)


class TestUsersActions:
    async def test_me(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"me": {"id": "u:1", "name": "root", "description": "", "roles": ["ADMIN"]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="me")
        assert result["name"] == "root"

    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "users": [{"id": "u:1", "name": "root"}, {"id": "u:2", "name": "guest"}]
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="list")
        assert len(result["users"]) == 2

    async def test_get(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"user": {"id": "u:1", "name": "root", "description": "", "roles": ["ADMIN"]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="get", user_id="u:1")
        assert result["name"] == "root"

    async def test_add(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"addUser": {"id": "u:3", "name": "newuser", "description": "", "roles": ["USER"]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="add", name="newuser", password="pass123")
        assert result["success"] is True

    async def test_add_with_role(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"addUser": {"id": "u:3", "name": "admin2", "description": "", "roles": ["ADMIN"]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="add", name="admin2", password="pass123", role="admin")
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["role"] == "ADMIN"

    async def test_delete(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"deleteUser": {"id": "u:2", "name": "guest"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="delete", user_id="u:2", confirm=True)
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["id"] == "u:2"

    async def test_cloud(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"cloud": {"status": "connected", "apiKey": "***"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="cloud")
        assert result["status"] == "connected"

    async def test_remote_access(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"remoteAccess": {"enabled": True, "url": "https://example.com"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="remote_access")
        assert result["enabled"] is True

    async def test_origins(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"allowedOrigins": ["http://localhost", "https://example.com"]}
        tool_fn = _make_tool()
        result = await tool_fn(action="origins")
        assert len(result["origins"]) == 2


class TestUsersNoneHandling:
    """Verify actions return empty dict (not TypeError) when API returns None."""

    async def test_me_returns_none(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"me": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="me")
        assert result == {}

    async def test_get_returns_none(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"user": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="get", user_id="u:1")
        assert result == {}

    async def test_cloud_returns_none(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"cloud": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="cloud")
        assert result == {}

    async def test_remote_access_returns_none(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"remoteAccess": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="remote_access")
        assert result == {}
