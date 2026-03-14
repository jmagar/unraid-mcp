from pathlib import Path
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

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
        patch("unraid_mcp.core.setup.PROJECT_ROOT", tmp_path),
        patch("unraid_mcp.core.setup.apply_runtime_config") as mock_apply,
    ):
        result = await elicit_and_configure(mock_ctx)

    assert result is True
    assert creds_file.exists()
    content = creds_file.read_text()
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


@pytest.mark.asyncio
async def test_auto_elicitation_triggered_on_credentials_not_configured():
    """Any tool call with missing creds auto-triggers elicitation before erroring."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from conftest import make_tool_fn
    from fastmcp import FastMCP

    from unraid_mcp.core.exceptions import CredentialsNotConfiguredError
    from unraid_mcp.tools.info import register_info_tool

    test_mcp = FastMCP("test")
    register_info_tool(test_mcp)
    tool_fn = make_tool_fn("unraid_mcp.tools.info", "register_info_tool", "unraid_info")

    mock_ctx = MagicMock()

    # First call raises CredentialsNotConfiguredError, second returns data
    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise CredentialsNotConfiguredError()
        return {"info": {"os": {"hostname": "tootie"}}}

    with (
        patch("unraid_mcp.tools.info.make_graphql_request", side_effect=side_effect),
        patch(
            "unraid_mcp.tools.info.elicit_and_configure", new=AsyncMock(return_value=True)
        ) as mock_elicit,
    ):
        result = await tool_fn(action="overview", ctx=mock_ctx)

    mock_elicit.assert_called_once_with(mock_ctx)
    assert result is not None


import os  # noqa: E402 — needed for reload-based tests below


def test_credentials_dir_defaults_to_home_unraid_mcp():
    """CREDENTIALS_DIR defaults to ~/.unraid-mcp when env var is not set."""
    import importlib

    import unraid_mcp.config.settings as s

    os.environ.pop("UNRAID_CREDENTIALS_DIR", None)
    try:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("UNRAID_CREDENTIALS_DIR", None)
            importlib.reload(s)
            assert Path.home() / ".unraid-mcp" == s.CREDENTIALS_DIR
    finally:
        importlib.reload(s)  # Restore module state


def test_credentials_dir_env_var_override():
    """UNRAID_CREDENTIALS_DIR env var overrides the default."""
    import importlib

    import unraid_mcp.config.settings as s

    custom = "/tmp/custom-creds"
    try:
        with patch.dict(os.environ, {"UNRAID_CREDENTIALS_DIR": custom}):
            importlib.reload(s)
            assert Path(custom) == s.CREDENTIALS_DIR
    finally:
        # Reload without the custom env var to restore original state
        os.environ.pop("UNRAID_CREDENTIALS_DIR", None)
        importlib.reload(s)


def test_credentials_env_path_is_dot_env_inside_credentials_dir():
    import unraid_mcp.config.settings as s

    assert s.CREDENTIALS_ENV_PATH == s.CREDENTIALS_DIR / ".env"


import stat  # noqa: E402


def test_write_env_creates_credentials_dir_with_700_permissions(tmp_path):
    """_write_env creates CREDENTIALS_DIR with mode 700 (owner-only)."""
    from unraid_mcp.core.setup import _write_env

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
    ):
        _write_env("https://example.com", "mykey")

    assert creds_dir.exists()
    dir_mode = stat.S_IMODE(creds_dir.stat().st_mode)
    assert dir_mode == 0o700, f"Expected 0o700, got {oct(dir_mode)}"


def test_write_env_sets_file_permissions_600(tmp_path):
    """_write_env sets .env file permissions to 600 (owner read/write only)."""
    from unraid_mcp.core.setup import _write_env

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
    ):
        _write_env("https://example.com", "mykey")

    file_mode = stat.S_IMODE(creds_file.stat().st_mode)
    assert file_mode == 0o600, f"Expected 0o600, got {oct(file_mode)}"


def test_write_env_seeds_from_env_example_on_first_run(tmp_path):
    """_write_env copies .env.example structure and replaces credentials in-place."""
    from unraid_mcp.core.setup import _write_env

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"
    # Create a fake .env.example
    example = tmp_path / ".env.example"
    example.write_text(
        "# Example config\nFOO=bar\nUNRAID_API_URL=placeholder\nUNRAID_API_KEY=placeholder\n"
    )

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
        patch("unraid_mcp.core.setup.PROJECT_ROOT", tmp_path),
    ):
        _write_env("https://real.url", "realkey")

    content = creds_file.read_text()
    assert "UNRAID_API_URL=https://real.url" in content
    assert "UNRAID_API_KEY=realkey" in content
    assert "# Example config" in content  # comment preserved
    assert "FOO=bar" in content  # other vars preserved
    assert "placeholder" not in content  # old credential values replaced
    # Credentials should be at their original position (after comments), not prepended before them
    lines = content.splitlines()
    url_idx = next(i for i, line in enumerate(lines) if line.startswith("UNRAID_API_URL="))
    comment_idx = next(i for i, line in enumerate(lines) if line.startswith("# Example config"))
    assert comment_idx < url_idx  # Comment comes before credentials


def test_write_env_first_run_no_example_file(tmp_path):
    """_write_env works on first run when .env.example does not exist."""
    from unraid_mcp.core.setup import _write_env

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"
    # tmp_path has no .env.example

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
        patch("unraid_mcp.core.setup.PROJECT_ROOT", tmp_path),
    ):
        _write_env("https://myserver.com", "mykey123")

    assert creds_file.exists()
    content = creds_file.read_text()
    assert "UNRAID_API_URL=https://myserver.com" in content
    assert "UNRAID_API_KEY=mykey123" in content


def test_write_env_updates_existing_credentials_in_place(tmp_path):
    """_write_env updates credentials without destroying other vars."""
    from unraid_mcp.core.setup import _write_env

    creds_dir = tmp_path / "creds"
    creds_dir.mkdir(mode=0o700)
    creds_file = creds_dir / ".env"
    creds_file.write_text(
        "UNRAID_API_URL=https://old.url\nUNRAID_API_KEY=oldkey\nUNRAID_VERIFY_SSL=false\n"
    )

    with (
        patch("unraid_mcp.core.setup.CREDENTIALS_DIR", creds_dir),
        patch("unraid_mcp.core.setup.CREDENTIALS_ENV_PATH", creds_file),
        patch("unraid_mcp.core.setup.PROJECT_ROOT", tmp_path),
    ):
        _write_env("https://new.url", "newkey")

    content = creds_file.read_text()
    assert "UNRAID_API_URL=https://new.url" in content
    assert "UNRAID_API_KEY=newkey" in content
    assert "UNRAID_VERIFY_SSL=false" in content  # preserved
    assert "old" not in content


@pytest.mark.asyncio
async def test_elicit_and_configure_returns_false_when_client_not_supported():
    """elicit_and_configure returns False when client raises NotImplementedError."""
    from unittest.mock import AsyncMock, MagicMock

    from unraid_mcp.core.setup import elicit_and_configure

    mock_ctx = MagicMock()
    mock_ctx.elicit = AsyncMock(side_effect=NotImplementedError("elicitation not supported"))

    result = await elicit_and_configure(mock_ctx)
    assert result is False
