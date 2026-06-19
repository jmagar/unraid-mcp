import json
import os
import stat
import sys
from unittest.mock import patch

import pytest


def test_apply_plugin_options_maps_present_vars():
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(
        os.environ,
        {
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "https://tower.local/graphql/",
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "  secret123  ",
        },
        clear=False,
    ):
        resolved = apply_plugin_options()

    assert resolved["UNRAID_API_URL"] == "https://tower.local/graphql"  # trailing slash stripped
    assert resolved["UNRAID_API_KEY"] == "secret123"  # whitespace trimmed


def test_apply_plugin_options_skips_missing_and_empty():
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(os.environ, {"CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": ""}, clear=False):
        os.environ.pop("CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY", None)
        resolved = apply_plugin_options()

    assert "UNRAID_API_URL" not in resolved
    assert "UNRAID_API_KEY" not in resolved


def test_apply_plugin_options_rejects_newline_injection():
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(
        os.environ,
        {
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "https://x\nUNRAID_API_KEY=evil",
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "ok",
        },
        clear=False,
    ):
        resolved = apply_plugin_options()

    assert "UNRAID_API_URL" not in resolved  # rejected for newline
    assert resolved["UNRAID_API_KEY"] == "ok"


def test_run_plugin_hook_writes_env_when_both_present(tmp_path, capsys):
    from unraid_mcp.core import setup as setup_mod

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch.dict(
            os.environ,
            {
                "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "https://tower.local/graphql",
                "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "secret123",
            },
            clear=False,
        ),
        patch.object(setup_mod, "CREDENTIALS_DIR", creds_dir),
        patch.object(setup_mod, "CREDENTIALS_ENV_PATH", creds_file),
        patch.object(setup_mod, "PROJECT_ROOT", tmp_path),
    ):
        rc = setup_mod.run_plugin_hook()

    assert rc == 0
    assert creds_file.exists()
    content = creds_file.read_text()
    assert "UNRAID_API_URL=https://tower.local/graphql" in content
    assert "UNRAID_API_KEY=secret123" in content
    assert stat.S_IMODE(creds_file.stat().st_mode) == 0o600
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is True


def test_run_plugin_hook_advisory_when_missing(tmp_path, capsys):
    from unraid_mcp.core import setup as setup_mod

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch.object(setup_mod, "CREDENTIALS_DIR", creds_dir),
        patch.object(setup_mod, "CREDENTIALS_ENV_PATH", creds_file),
        patch.object(setup_mod, "PROJECT_ROOT", tmp_path),
    ):
        os.environ.pop("CLAUDE_PLUGIN_OPTION_UNRAID_API_URL", None)
        os.environ.pop("CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY", None)
        rc = setup_mod.run_plugin_hook()

    assert rc == 0
    assert not creds_file.exists()
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is False
    assert len(report["advisory_failures"]) == 2


def test_main_setup_dispatch_invokes_plugin_hook():
    import unraid_mcp.main as main_mod

    with (
        patch.object(sys, "argv", ["unraid-mcp", "setup", "plugin-hook"]),
        patch("unraid_mcp.core.setup.run_plugin_hook", return_value=0) as mock_hook,
        pytest.raises(SystemExit) as exc,
    ):
        main_mod.main()

    assert exc.value.code == 0
    mock_hook.assert_called_once()
