# tests/test_oidc.py
"""Tests for unraid_oidc tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.tools.oidc.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


def _make_tool():
    return make_tool_fn(
        "unraid_mcp.tools.oidc",
        "register_oidc_tool",
        "unraid_oidc",
    )


@pytest.mark.asyncio
async def test_providers_returns_list(_mock_graphql):
    _mock_graphql.return_value = {
        "oidcProviders": [
            {"id": "1:local", "name": "Google", "clientId": "abc", "scopes": ["openid"]}
        ]
    }
    result = await _make_tool()(action="providers")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_public_providers(_mock_graphql):
    _mock_graphql.return_value = {"publicOidcProviders": []}
    result = await _make_tool()(action="public_providers")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_provider_requires_provider_id(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="provider_id"):
        await _make_tool()(action="provider")


@pytest.mark.asyncio
async def test_validate_session_requires_token(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="token"):
        await _make_tool()(action="validate_session")


@pytest.mark.asyncio
async def test_configuration(_mock_graphql):
    _mock_graphql.return_value = {
        "oidcConfiguration": {"providers": [], "defaultAllowedOrigins": []}
    }
    result = await _make_tool()(action="configuration")
    assert result["success"] is True
