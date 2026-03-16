"""Tests for ApiKeyVerifier and _build_auth() in server.py."""

import importlib
from unittest.mock import MagicMock, patch

import pytest

from unraid_mcp.server import ApiKeyVerifier, _build_auth


# ---------------------------------------------------------------------------
# ApiKeyVerifier unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_api_key_verifier_accepts_correct_key():
    """Returns AccessToken when the presented token matches the configured key."""
    verifier = ApiKeyVerifier("secret-key-abc123")
    result = await verifier.verify_token("secret-key-abc123")

    assert result is not None
    assert result.client_id == "api-key-client"
    assert result.token == "secret-key-abc123"


@pytest.mark.asyncio
async def test_api_key_verifier_rejects_wrong_key():
    """Returns None when the token does not match."""
    verifier = ApiKeyVerifier("secret-key-abc123")
    result = await verifier.verify_token("wrong-key")

    assert result is None


@pytest.mark.asyncio
async def test_api_key_verifier_rejects_empty_token():
    """Returns None for an empty string token."""
    verifier = ApiKeyVerifier("secret-key-abc123")
    result = await verifier.verify_token("")

    assert result is None


@pytest.mark.asyncio
async def test_api_key_verifier_empty_key_rejects_empty_token():
    """When initialised with empty key, even an empty token is rejected.

    An empty UNRAID_MCP_API_KEY means auth is disabled — ApiKeyVerifier
    should not be instantiated in that case.  But if it is, it must not
    grant access via an empty bearer token.
    """
    verifier = ApiKeyVerifier("")
    result = await verifier.verify_token("")

    assert result is None


# ---------------------------------------------------------------------------
# _build_auth() integration tests
# ---------------------------------------------------------------------------


def test_build_auth_returns_none_when_nothing_configured(monkeypatch):
    """Returns None when neither Google OAuth nor API key is set."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "")
    monkeypatch.setenv("UNRAID_MCP_API_KEY", "")

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    result = _build_auth()
    assert result is None


def test_build_auth_returns_api_key_verifier_when_only_api_key_set(monkeypatch):
    """Returns ApiKeyVerifier when UNRAID_MCP_API_KEY is set but Google OAuth is not."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "")
    monkeypatch.setenv("UNRAID_MCP_API_KEY", "my-secret-api-key")

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    result = _build_auth()
    assert isinstance(result, ApiKeyVerifier)


def test_build_auth_returns_google_provider_when_only_oauth_set(monkeypatch):
    """Returns GoogleProvider when Google OAuth vars are set but no API key."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.setenv("UNRAID_MCP_API_KEY", "")
    monkeypatch.setenv("UNRAID_MCP_JWT_SIGNING_KEY", "x" * 32)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    mock_provider = MagicMock()
    with patch("unraid_mcp.server.GoogleProvider", return_value=mock_provider):
        result = _build_auth()

    assert result is mock_provider


def test_build_auth_returns_multi_auth_when_both_configured(monkeypatch):
    """Returns MultiAuth when both Google OAuth and UNRAID_MCP_API_KEY are set."""
    from fastmcp.server.auth import MultiAuth

    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.setenv("UNRAID_MCP_API_KEY", "my-secret-api-key")
    monkeypatch.setenv("UNRAID_MCP_JWT_SIGNING_KEY", "x" * 32)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    mock_provider = MagicMock()
    with patch("unraid_mcp.server.GoogleProvider", return_value=mock_provider):
        result = _build_auth()

    assert isinstance(result, MultiAuth)
    # Server is the Google provider
    assert result.server is mock_provider
    # One additional verifier — the ApiKeyVerifier
    assert len(result.verifiers) == 1
    assert isinstance(result.verifiers[0], ApiKeyVerifier)


def test_build_auth_multi_auth_api_key_verifier_uses_correct_key(monkeypatch):
    """The ApiKeyVerifier inside MultiAuth is seeded with the configured key."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.setenv("UNRAID_MCP_API_KEY", "super-secret-token")
    monkeypatch.setenv("UNRAID_MCP_JWT_SIGNING_KEY", "x" * 32)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    with patch("unraid_mcp.server.GoogleProvider", return_value=MagicMock()):
        result = _build_auth()

    verifier = result.verifiers[0]
    assert verifier._api_key == "super-secret-token"
