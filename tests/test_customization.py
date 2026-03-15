# tests/test_customization.py
"""Tests for unraid_customization tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.tools.customization.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


def _make_tool():
    return make_tool_fn(
        "unraid_mcp.tools.customization",
        "register_customization_tool",
        "unraid_customization",
    )


@pytest.mark.asyncio
async def test_theme_returns_customization(_mock_graphql):
    _mock_graphql.return_value = {
        "customization": {"theme": {"name": "azure"}, "partnerInfo": None, "activationCode": None}
    }
    result = await _make_tool()(action="theme")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_public_theme(_mock_graphql):
    _mock_graphql.return_value = {"publicTheme": {"name": "black"}}
    result = await _make_tool()(action="public_theme")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_is_initial_setup(_mock_graphql):
    _mock_graphql.return_value = {"isInitialSetup": False}
    result = await _make_tool()(action="is_initial_setup")
    assert result["success"] is True
    assert result["data"]["isInitialSetup"] is False


@pytest.mark.asyncio
async def test_set_theme_requires_theme(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="theme_name"):
        await _make_tool()(action="set_theme")


@pytest.mark.asyncio
async def test_set_theme_success(_mock_graphql):
    _mock_graphql.return_value = {
        "customization": {"setTheme": {"name": "azure", "showBannerImage": True}}
    }
    result = await _make_tool()(action="set_theme", theme_name="azure")
    assert result["success"] is True
