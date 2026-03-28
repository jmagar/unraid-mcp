# tests/test_plugins.py
"""Tests for plugin subactions of the consolidated unraid tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from conftest import make_tool_fn


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.core.client.make_graphql_request") as m:
        yield m


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


@pytest.mark.asyncio
async def test_list_returns_plugins(_mock_graphql):
    _mock_graphql.return_value = {
        "plugins": [
            {"name": "my-plugin", "version": "1.0.0", "hasApiModule": True, "hasCliModule": False}
        ]
    }
    result = await _make_tool()(action="plugin", subaction="list")
    assert result["success"] is True
    assert len(result["data"]["plugins"]) == 1


@pytest.mark.asyncio
async def test_add_requires_names(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="names"):
        await _make_tool()(action="plugin", subaction="add")


@pytest.mark.asyncio
async def test_add_success(_mock_graphql):
    _mock_graphql.return_value = {"addPlugin": False}  # False = auto-restart triggered
    result = await _make_tool()(action="plugin", subaction="add", names=["my-plugin"])
    assert result["success"] is True


@pytest.mark.asyncio
async def test_remove_requires_confirm(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool()(action="plugin", subaction="remove", names=["my-plugin"], confirm=False)


@pytest.mark.asyncio
async def test_remove_with_confirm(_mock_graphql):
    _mock_graphql.return_value = {"removePlugin": True}
    result = await _make_tool()(
        action="plugin", subaction="remove", names=["my-plugin"], confirm=True
    )
    assert result["success"] is True
