"""Tests for _build_google_auth() in server.py."""

import importlib
from unittest.mock import MagicMock, patch

from unraid_mcp.server import _build_google_auth


def test_build_google_auth_returns_none_when_unconfigured(monkeypatch):
    """Returns None when Google OAuth env vars are absent."""
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("UNRAID_MCP_BASE_URL", raising=False)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    result = _build_google_auth()
    assert result is None


def test_build_google_auth_returns_provider_when_configured(monkeypatch):
    """Returns GoogleProvider instance when all required vars are set."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.setenv("UNRAID_MCP_JWT_SIGNING_KEY", "x" * 32)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    mock_provider = MagicMock()
    mock_provider_class = MagicMock(return_value=mock_provider)

    with patch("unraid_mcp.server.GoogleProvider", mock_provider_class):
        result = _build_google_auth()

    assert result is mock_provider
    mock_provider_class.assert_called_once_with(
        client_id="test-id.apps.googleusercontent.com",
        client_secret="GOCSPX-test-secret",
        base_url="http://10.1.0.2:6970",
        jwt_signing_key="x" * 32,
    )


def test_build_google_auth_omits_jwt_key_when_empty(monkeypatch):
    """jwt_signing_key is omitted (not passed as empty string) when not set."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.delenv("UNRAID_MCP_JWT_SIGNING_KEY", raising=False)

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    mock_provider_class = MagicMock(return_value=MagicMock())

    with patch("unraid_mcp.server.GoogleProvider", mock_provider_class):
        _build_google_auth()

    call_kwargs = mock_provider_class.call_args.kwargs
    assert "jwt_signing_key" not in call_kwargs


def test_build_google_auth_warns_on_stdio_transport(monkeypatch):
    """Logs a warning when Google auth is configured but transport is stdio."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "GOCSPX-test-secret")
    monkeypatch.setenv("UNRAID_MCP_BASE_URL", "http://10.1.0.2:6970")
    monkeypatch.setenv("UNRAID_MCP_TRANSPORT", "stdio")

    import unraid_mcp.config.settings as s

    importlib.reload(s)

    warning_messages: list[str] = []

    with (
        patch("unraid_mcp.server.GoogleProvider", MagicMock(return_value=MagicMock())),
        patch("unraid_mcp.server.logger") as mock_logger,
    ):
        mock_logger.warning.side_effect = lambda msg, *a, **kw: warning_messages.append(msg)
        _build_google_auth()

    assert any("stdio" in m.lower() for m in warning_messages)
