"""Tests for unraid_users tool.

NOTE: Unraid GraphQL API only supports the me() query.
User management operations (list, add, delete, cloud, remote_access, origins) are NOT available in the API.
"""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.users.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.users", "register_users_tool", "unraid_users")


class TestUsersValidation:
    """Test validation for invalid actions."""

    async def test_invalid_action_rejected(self, _mock_graphql: AsyncMock) -> None:
        """Test that non-existent actions are rejected with clear error."""
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="list")

        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="add")

        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="delete")

        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="cloud")


class TestUsersActions:
    """Test the single supported action: me."""

    async def test_me(self, _mock_graphql: AsyncMock) -> None:
        """Test querying current authenticated user."""
        _mock_graphql.return_value = {
            "me": {"id": "u:1", "name": "root", "description": "", "roles": ["ADMIN"]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="me")
        assert result["name"] == "root"
        assert result["roles"] == ["ADMIN"]
        _mock_graphql.assert_called_once()

    async def test_me_default_action(self, _mock_graphql: AsyncMock) -> None:
        """Test that 'me' is the default action."""
        _mock_graphql.return_value = {
            "me": {"id": "u:1", "name": "root", "description": "", "roles": ["ADMIN"]}
        }
        tool_fn = _make_tool()
        result = await tool_fn()
        assert result["name"] == "root"


class TestUsersNoneHandling:
    """Verify actions return empty dict (not TypeError) when API returns None."""

    async def test_me_returns_none(self, _mock_graphql: AsyncMock) -> None:
        """Test that me returns empty dict when API returns None."""
        _mock_graphql.return_value = {"me": None}
        tool_fn = _make_tool()
        result = await tool_fn(action="me")
        assert result == {}
