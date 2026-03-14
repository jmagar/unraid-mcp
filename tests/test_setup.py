from unittest.mock import patch

import pytest

from unraid_mcp.core.exceptions import CredentialsNotConfiguredError, ToolError


def test_credentials_not_configured_error_exists():
    err = CredentialsNotConfiguredError()
    assert str(err) == "Unraid credentials are not configured."


def test_credentials_not_configured_error_is_exception():
    """CredentialsNotConfiguredError must be catchable as a plain Exception."""
    with pytest.raises(Exception):
        raise CredentialsNotConfiguredError()


def test_credentials_not_configured_error_is_not_tool_error():
    """CredentialsNotConfiguredError must NOT be a ToolError — it bypasses MCP protocol error handling."""
    assert not issubclass(CredentialsNotConfiguredError, ToolError)


def test_settings_is_configured_true():
    from unraid_mcp.config import settings

    with (
        patch.object(settings, "UNRAID_API_URL", "https://example.com"),
        patch.object(settings, "UNRAID_API_KEY", "key123"),
    ):
        assert settings.is_configured() is True


def test_settings_is_configured_false_when_missing():
    from unraid_mcp.config import settings

    with (
        patch.object(settings, "UNRAID_API_URL", None),
        patch.object(settings, "UNRAID_API_KEY", None),
    ):
        assert settings.is_configured() is False


def test_settings_apply_runtime_config_updates_module_globals():
    from unraid_mcp.config import settings

    original_url = settings.UNRAID_API_URL
    original_key = settings.UNRAID_API_KEY
    settings.apply_runtime_config("https://newurl.com/graphql", "newkey")
    assert settings.UNRAID_API_URL == "https://newurl.com/graphql"
    assert settings.UNRAID_API_KEY == "newkey"
    # Reset so other tests are not affected
    settings.UNRAID_API_URL = original_url
    settings.UNRAID_API_KEY = original_key
