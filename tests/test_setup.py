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
    import os

    from unraid_mcp.config import settings

    original_url = settings.UNRAID_API_URL
    original_key = settings.UNRAID_API_KEY
    original_env_url = os.environ.get("UNRAID_API_URL")
    original_env_key = os.environ.get("UNRAID_API_KEY")
    try:
        settings.apply_runtime_config("https://newurl.com/graphql", "newkey")
        assert settings.UNRAID_API_URL == "https://newurl.com/graphql"
        assert settings.UNRAID_API_KEY == "newkey"
        assert os.environ["UNRAID_API_URL"] == "https://newurl.com/graphql"
        assert os.environ["UNRAID_API_KEY"] == "newkey"
    finally:
        # Reset module globals
        settings.UNRAID_API_URL = original_url
        settings.UNRAID_API_KEY = original_key
        # Reset os.environ
        if original_env_url is None:
            os.environ.pop("UNRAID_API_URL", None)
        else:
            os.environ["UNRAID_API_URL"] = original_env_url
        if original_env_key is None:
            os.environ.pop("UNRAID_API_KEY", None)
        else:
            os.environ["UNRAID_API_KEY"] = original_env_key


def test_run_server_does_not_exit_when_creds_missing(monkeypatch):
    """Server should not sys.exit(1) when credentials are absent."""
    import unraid_mcp.config.settings as settings_mod

    monkeypatch.setattr(settings_mod, "UNRAID_API_URL", None)
    monkeypatch.setattr(settings_mod, "UNRAID_API_KEY", None)

    from unraid_mcp import server as server_mod

    with (
        patch.object(server_mod, "mcp") as mock_mcp,
        patch("unraid_mcp.server.logger") as mock_logger,
    ):
        mock_mcp.run.side_effect = SystemExit(0)
        try:
            server_mod.run_server()
        except SystemExit as e:
            assert e.code == 0, f"Unexpected sys.exit({e.code}) — server crashed on missing creds"
        mock_logger.warning.assert_called()
        warning_msgs = [call[0][0] for call in mock_logger.warning.call_args_list]
        assert any("elicitation" in msg for msg in warning_msgs), (
            f"Expected a warning containing 'elicitation', got: {warning_msgs}"
        )


@pytest.mark.asyncio
async def test_elicit_and_configure_writes_env_file(tmp_path):
    """elicit_and_configure writes a .env file and calls apply_runtime_config."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from unraid_mcp.core.setup import elicit_and_configure

    mock_ctx = MagicMock()
    mock_result = MagicMock()
    mock_result.action = "accept"
    mock_result.data = MagicMock()
    mock_result.data.api_url = "https://myunraid.example.com/graphql"
    mock_result.data.api_key = "abc123secret"
    mock_ctx.elicit = AsyncMock(return_value=mock_result)

    with (
        patch("unraid_mcp.core.setup.PROJECT_ROOT", tmp_path),
        patch("unraid_mcp.core.setup.apply_runtime_config") as mock_apply,
    ):
        result = await elicit_and_configure(mock_ctx)

    assert result is True
    env_file = tmp_path / ".env"
    assert env_file.exists()
    content = env_file.read_text()
    assert "UNRAID_API_URL=https://myunraid.example.com/graphql" in content
    assert "UNRAID_API_KEY=abc123secret" in content
    mock_apply.assert_called_once_with("https://myunraid.example.com/graphql", "abc123secret")


@pytest.mark.asyncio
async def test_elicit_and_configure_returns_false_on_decline():
    from unittest.mock import AsyncMock, MagicMock

    from unraid_mcp.core.setup import elicit_and_configure

    mock_ctx = MagicMock()
    mock_result = MagicMock()
    mock_result.action = "decline"
    mock_ctx.elicit = AsyncMock(return_value=mock_result)

    result = await elicit_and_configure(mock_ctx)
    assert result is False


@pytest.mark.asyncio
async def test_elicit_and_configure_returns_false_on_cancel():
    from unittest.mock import AsyncMock, MagicMock

    from unraid_mcp.core.setup import elicit_and_configure

    mock_ctx = MagicMock()
    mock_result = MagicMock()
    mock_result.action = "cancel"
    mock_ctx.elicit = AsyncMock(return_value=mock_result)

    result = await elicit_and_configure(mock_ctx)
    assert result is False


@pytest.mark.asyncio
async def test_make_graphql_request_raises_sentinel_when_unconfigured():
    """make_graphql_request raises CredentialsNotConfiguredError (not ToolError) when
    credentials are absent, so callers can trigger elicitation."""
    from unraid_mcp.config import settings as settings_mod
    from unraid_mcp.core.client import make_graphql_request
    from unraid_mcp.core.exceptions import CredentialsNotConfiguredError

    original_url = settings_mod.UNRAID_API_URL
    original_key = settings_mod.UNRAID_API_KEY
    try:
        settings_mod.UNRAID_API_URL = None
        settings_mod.UNRAID_API_KEY = None
        with pytest.raises(CredentialsNotConfiguredError):
            await make_graphql_request("{ __typename }")
    finally:
        settings_mod.UNRAID_API_URL = original_url
        settings_mod.UNRAID_API_KEY = original_key
