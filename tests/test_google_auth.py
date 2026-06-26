"""Tests for the optional Google OAuth authentication path.

Covers:
  - google_oauth_enabled() gating on client id + secret
  - build_google_provider() returns None when disabled (default deployment)
  - scope parsing (default + custom comma/space separated)
  - fail-closed config errors: missing base_url, partial persistence config,
    invalid Fernet key
  - in-memory vs encrypted-on-disk (FileTreeStore) provider construction
  - run_server() omits the bearer/well-known ASGI middleware when OAuth is active
"""

from __future__ import annotations

import contextlib
from unittest.mock import patch

import pytest

import unraid_mcp.config.settings as s
from unraid_mcp.core.google_auth import (
    GoogleOAuthConfigError,
    _parse_scopes,
    build_google_provider,
    google_oauth_enabled,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOOGLE_ATTRS = (
    "UNRAID_MCP_GOOGLE_CLIENT_ID",
    "UNRAID_MCP_GOOGLE_CLIENT_SECRET",
    "UNRAID_MCP_GOOGLE_BASE_URL",
    "UNRAID_MCP_GOOGLE_REQUIRED_SCOPES",
    "UNRAID_MCP_GOOGLE_REDIRECT_PATH",
    "UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY",
    "UNRAID_MCP_GOOGLE_ENCRYPTION_KEY",
    "UNRAID_MCP_GOOGLE_STORAGE_DIR",
)


@contextlib.contextmanager
def _google_settings(**overrides):
    """Temporarily set UNRAID_MCP_GOOGLE_* settings globals, restoring after."""
    originals = {name: getattr(s, name) for name in _GOOGLE_ATTRS}
    try:
        # Clear all first so each test starts from a known (disabled) baseline.
        for name in _GOOGLE_ATTRS:
            setattr(s, name, None)
        for name, value in overrides.items():
            setattr(s, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(s, name, value)


def _fernet_key() -> str:
    from cryptography.fernet import Fernet

    return Fernet.generate_key().decode()


# ---------------------------------------------------------------------------
# Enable gate
# ---------------------------------------------------------------------------


class TestEnableGate:
    def test_disabled_by_default(self):
        with _google_settings():
            assert google_oauth_enabled() is False
            assert build_google_provider() is None

    def test_disabled_with_only_client_id(self):
        with _google_settings(UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com"):
            assert google_oauth_enabled() is False

    def test_disabled_with_only_secret(self):
        with _google_settings(UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret"):
            assert google_oauth_enabled() is False

    def test_empty_strings_do_not_enable(self):
        with _google_settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="   ",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="",
        ):
            assert google_oauth_enabled() is False

    def test_enabled_with_both(self):
        with _google_settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
        ):
            assert google_oauth_enabled() is True


# ---------------------------------------------------------------------------
# Scope parsing
# ---------------------------------------------------------------------------


class TestScopeParsing:
    def test_default_scopes_when_unset(self):
        assert _parse_scopes(None) == [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ]

    def test_default_scopes_when_blank(self):
        assert _parse_scopes("   ") == [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ]

    def test_comma_separated(self):
        assert _parse_scopes("openid, email, profile") == ["openid", "email", "profile"]

    def test_space_separated(self):
        assert _parse_scopes("openid email profile") == ["openid", "email", "profile"]

    def test_mixed_separators_and_extra_whitespace(self):
        assert _parse_scopes(" openid ,email  profile ") == ["openid", "email", "profile"]


# ---------------------------------------------------------------------------
# Config errors (fail closed)
# ---------------------------------------------------------------------------


class TestConfigErrors:
    def test_missing_base_url_raises(self):
        with (
            _google_settings(
                UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
                UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
            ),
            pytest.raises(GoogleOAuthConfigError, match="UNRAID_MCP_GOOGLE_BASE_URL"),
        ):
            build_google_provider()

    def test_only_jwt_key_raises(self):
        with (
            _google_settings(
                UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
                UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
                UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
                UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY="jwt-key",
            ),
            pytest.raises(GoogleOAuthConfigError, match="requires BOTH"),
        ):
            build_google_provider()

    def test_only_encryption_key_raises(self):
        with (
            _google_settings(
                UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
                UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
                UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
                UNRAID_MCP_GOOGLE_ENCRYPTION_KEY=_fernet_key(),
            ),
            pytest.raises(GoogleOAuthConfigError, match="requires BOTH"),
        ):
            build_google_provider()

    def test_invalid_fernet_key_raises(self, tmp_path):
        with (
            _google_settings(
                UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
                UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
                UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
                UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY="jwt-key",
                UNRAID_MCP_GOOGLE_ENCRYPTION_KEY="not-a-valid-fernet-key",
                UNRAID_MCP_GOOGLE_STORAGE_DIR=str(tmp_path / "tokens"),
            ),
            pytest.raises(GoogleOAuthConfigError, match="not a valid Fernet key"),
        ):
            build_google_provider()


# ---------------------------------------------------------------------------
# Provider construction
# ---------------------------------------------------------------------------


class TestProviderConstruction:
    def test_in_memory_provider(self):
        with _google_settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
            UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
        ):
            provider = build_google_provider()
        assert provider is not None
        assert type(provider).__name__ == "GoogleProvider"

    def test_custom_scopes_and_redirect_path(self):
        with _google_settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
            UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
            UNRAID_MCP_GOOGLE_REQUIRED_SCOPES="openid profile",
            UNRAID_MCP_GOOGLE_REDIRECT_PATH="/auth/google/callback",
        ):
            provider = build_google_provider()
        assert provider is not None

    def test_encrypted_persistence_creates_storage_dir(self, tmp_path):
        storage = tmp_path / "oauth-tokens"
        with _google_settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="x.apps.googleusercontent.com",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="GOCSPX-secret",
            UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
            UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY="jwt-signing-key",
            UNRAID_MCP_GOOGLE_ENCRYPTION_KEY=_fernet_key(),
            UNRAID_MCP_GOOGLE_STORAGE_DIR=str(storage),
        ):
            provider = build_google_provider()
        assert provider is not None
        assert storage.is_dir()


# ---------------------------------------------------------------------------
# run_server() middleware selection
# ---------------------------------------------------------------------------


class TestRunServerMiddlewareSelection:
    def _capture_middleware(self, google_provider):
        """Run run_server() in HTTP mode and return the middleware list passed to mcp.run."""
        import unraid_mcp.server as server

        captured: dict = {}

        def fake_run(*args, **kwargs):
            captured["middleware"] = kwargs.get("middleware")

        orig_transport = s.UNRAID_MCP_TRANSPORT
        try:
            s.UNRAID_MCP_TRANSPORT = "streamable-http"
            with (
                patch.object(server, "_google_auth_provider", google_provider),
                patch.object(server.mcp, "run", side_effect=fake_run),
                patch.object(server, "ensure_token_exists"),
                patch.object(server, "log_configuration_status"),
                patch.object(s, "UNRAID_MCP_BEARER_TOKEN", "tok"),
            ):
                server.run_server()
        finally:
            s.UNRAID_MCP_TRANSPORT = orig_transport
        return captured.get("middleware")

    def test_bearer_path_installs_three_middleware(self):
        middleware = self._capture_middleware(google_provider=None)
        assert middleware is not None
        # Health + WellKnown + Bearer
        assert len(middleware) == 3

    def test_oauth_path_installs_only_health(self):
        sentinel = object()  # stand-in for a built GoogleProvider
        middleware = self._capture_middleware(google_provider=sentinel)
        assert middleware is not None
        # Only HealthMiddleware — bearer + well-known are omitted under OAuth.
        assert len(middleware) == 1
