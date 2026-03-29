# tests/test_oidc.py
"""Tests for oidc subactions of the consolidated unraid tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.core.client.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


@pytest.mark.asyncio
async def test_providers_returns_list(_mock_graphql):
    _mock_graphql.return_value = {
        "oidcProviders": [
            {"id": "1:local", "name": "Google", "clientId": "abc", "scopes": ["openid"]}
        ]
    }
    result = await _make_tool()(action="oidc", subaction="providers")
    assert "providers" in result
    assert len(result["providers"]) == 1


@pytest.mark.asyncio
async def test_public_providers(_mock_graphql):
    _mock_graphql.return_value = {"publicOidcProviders": []}
    result = await _make_tool()(action="oidc", subaction="public_providers")
    assert result["providers"] == []


@pytest.mark.asyncio
async def test_provider_requires_provider_id(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="provider_id"):
        await _make_tool()(action="oidc", subaction="provider")


@pytest.mark.asyncio
async def test_validate_session_requires_token(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="token"):
        await _make_tool()(action="oidc", subaction="validate_session")


@pytest.mark.asyncio
async def test_configuration(_mock_graphql):
    _mock_graphql.return_value = {
        "oidcConfiguration": {"providers": [], "defaultAllowedOrigins": []}
    }
    result = await _make_tool()(action="oidc", subaction="configuration")
    assert result["providers"] == []
    assert result["defaultAllowedOrigins"] == []


@pytest.mark.asyncio
async def test_provider_null_raises_tool_error(_mock_graphql):
    """oidcProvider null response should raise ToolError, not return {}."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_graphql.return_value = {"oidcProvider": None}
    with pytest.raises(ToolError, match="not found"):
        await _make_tool()(action="oidc", subaction="provider", provider_id="p:missing")


@pytest.mark.asyncio
async def test_validate_session_null_raises_tool_error(_mock_graphql):
    """validateOidcSession null response should raise ToolError, not return {}."""
    from unraid_mcp.core.exceptions import ToolError

    _mock_graphql.return_value = {"validateOidcSession": None}
    with pytest.raises(ToolError, match="Session validation returned no data"):
        await _make_tool()(action="oidc", subaction="validate_session", token="bad-token")


@pytest.mark.asyncio
async def test_validate_session_valid(_mock_graphql):
    """Successful validate_session should return the validation result dict."""
    _mock_graphql.return_value = {"validateOidcSession": {"valid": True, "username": "alice"}}
    result = await _make_tool()(action="oidc", subaction="validate_session", token="good-token")
    assert result["valid"] is True
    assert result["username"] == "alice"
