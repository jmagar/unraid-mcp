# tests/test_plugins.py
"""Tests for unraid_plugins tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mcp():
    return FastMCP("test")


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.tools.plugins.make_graphql_request") as m:
        yield m


def _make_tool(mcp):
    from unraid_mcp.tools.plugins import register_plugins_tool

    register_plugins_tool(mcp)
    # FastMCP 3.x: access tool fn via internal provider components (same as conftest.make_tool_fn)
    local_provider = mcp.providers[0]
    tool = local_provider._components["tool:unraid_plugins@"]
    return tool.fn


@pytest.mark.asyncio
async def test_list_returns_plugins(mcp, _mock_graphql):
    _mock_graphql.return_value = {
        "plugins": [
            {"name": "my-plugin", "version": "1.0.0", "hasApiModule": True, "hasCliModule": False}
        ]
    }
    result = await _make_tool(mcp)(action="list")
    assert result["success"] is True
    assert len(result["data"]["plugins"]) == 1


@pytest.mark.asyncio
async def test_add_requires_names(mcp, _mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="names"):
        await _make_tool(mcp)(action="add")


@pytest.mark.asyncio
async def test_add_success(mcp, _mock_graphql):
    _mock_graphql.return_value = {"addPlugin": False}  # False = auto-restart triggered
    result = await _make_tool(mcp)(action="add", names=["my-plugin"])
    assert result["success"] is True


@pytest.mark.asyncio
async def test_remove_requires_confirm(mcp, _mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool(mcp)(action="remove", names=["my-plugin"], confirm=False)


@pytest.mark.asyncio
async def test_remove_with_confirm(mcp, _mock_graphql):
    _mock_graphql.return_value = {"removePlugin": True}
    result = await _make_tool(mcp)(action="remove", names=["my-plugin"], confirm=True)
    assert result["success"] is True
