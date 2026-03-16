"""Tests for Google OAuth settings loading."""

import importlib
from typing import Any


def _reload_settings(monkeypatch, overrides: dict) -> Any:
    """Reload settings module with given env vars set."""
    for k, v in overrides.items():
        monkeypatch.setenv(k, v)
    import unraid_mcp.config.settings as mod

    importlib.reload(mod)
    return mod


def test_google_auth_defaults_to_empty(monkeypatch):
    """Google auth vars default to empty string when not set."""
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("UNRAID_MCP_BASE_URL", raising=False)
    monkeypatch.delenv("UNRAID_MCP_JWT_SIGNING_KEY", raising=False)
    mod = _reload_settings(monkeypatch, {})
    assert mod.GOOGLE_CLIENT_ID == ""
    assert mod.GOOGLE_CLIENT_SECRET == ""
    assert mod.UNRAID_MCP_BASE_URL == ""
    assert mod.UNRAID_MCP_JWT_SIGNING_KEY == ""


def test_google_auth_reads_env_vars(monkeypatch):
    """Google auth vars are read from environment."""
    mod = _reload_settings(
        monkeypatch,
        {
            "GOOGLE_CLIENT_ID": "test-client-id.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "GOCSPX-test-secret",
            "UNRAID_MCP_BASE_URL": "http://10.1.0.2:6970",
            "UNRAID_MCP_JWT_SIGNING_KEY": "a" * 32,
        },
    )
    assert mod.GOOGLE_CLIENT_ID == "test-client-id.apps.googleusercontent.com"
    assert mod.GOOGLE_CLIENT_SECRET == "GOCSPX-test-secret"
    assert mod.UNRAID_MCP_BASE_URL == "http://10.1.0.2:6970"
    assert mod.UNRAID_MCP_JWT_SIGNING_KEY == "a" * 32


def test_google_auth_enabled_requires_both_vars(monkeypatch):
    """is_google_auth_configured() requires both client_id and client_secret."""
    # Only client_id — not configured
    mod = _reload_settings(
        monkeypatch,
        {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "",
            "UNRAID_MCP_BASE_URL": "http://10.1.0.2:6970",
        },
    )
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    importlib.reload(mod)
    assert not mod.is_google_auth_configured()

    # Both set — configured
    mod2 = _reload_settings(
        monkeypatch,
        {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "test-secret",
            "UNRAID_MCP_BASE_URL": "http://10.1.0.2:6970",
        },
    )
    assert mod2.is_google_auth_configured()


def test_google_auth_requires_base_url(monkeypatch):
    """is_google_auth_configured() is False when base_url is missing."""
    mod = _reload_settings(
        monkeypatch,
        {
            "GOOGLE_CLIENT_ID": "test-id",
            "GOOGLE_CLIENT_SECRET": "test-secret",
        },
    )
    monkeypatch.delenv("UNRAID_MCP_BASE_URL", raising=False)
    importlib.reload(mod)
    assert not mod.is_google_auth_configured()
