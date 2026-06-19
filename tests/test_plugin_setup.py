import json
import os
import stat
import sys
from unittest.mock import patch

import pytest


# Both plugin-option env vars, so tests can clear them in one place. patch.dict
# snapshots os.environ on entry and restores it on exit, so popping these inside a
# `patch.dict(os.environ, ..., clear=False)` block never leaks to other tests.
_OPTION_VARS = (
    "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL",
    "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY",
)


def _clear_option_vars() -> None:
    for var in _OPTION_VARS:
        os.environ.pop(var, None)


def test_apply_plugin_options_maps_present_vars():
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(
        os.environ,
        {
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "https://tower.local/graphql/",
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "  secret123/  ",
        },
        clear=False,
    ):
        resolved = apply_plugin_options()

    assert resolved["UNRAID_API_URL"] == "https://tower.local/graphql"  # trailing slash stripped
    assert resolved["UNRAID_API_KEY"] == "secret123/"  # trimmed, slash NOT stripped on key


def test_apply_plugin_options_skips_missing_and_empty():
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(os.environ, {"CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": ""}, clear=False):
        os.environ.pop("CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY", None)
        resolved = apply_plugin_options()

    assert "UNRAID_API_URL" not in resolved
    assert "UNRAID_API_KEY" not in resolved


# NUL (\0) cannot be placed in os.environ (the OS rejects it), so it can't reach
# apply_plugin_options via a plugin option — it's covered by the direct _safe_env_value
# unit test below. Newline/CR are the reachable injection vectors.
@pytest.mark.parametrize("bad_char", ["\n", "\r"])
def test_apply_plugin_options_rejects_control_char_injection(bad_char):
    from unraid_mcp.core.setup import apply_plugin_options

    with patch.dict(
        os.environ,
        {
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": f"https://x{bad_char}UNRAID_API_KEY=evil",
            "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "ok",
        },
        clear=False,
    ):
        resolved = apply_plugin_options()

    assert "UNRAID_API_URL" not in resolved  # rejected for control char
    assert resolved["UNRAID_API_KEY"] == "ok"


@pytest.mark.parametrize("value", ["", "x\ny", "x\ry", "x\0y"])
def test_safe_env_value_rejects_empty_and_control_chars(value):
    from unraid_mcp.core.setup import _safe_env_value

    assert _safe_env_value(value) is None


def test_safe_env_value_accepts_normal():
    from unraid_mcp.core.setup import _safe_env_value

    assert _safe_env_value("https://tower.local/graphql") == "https://tower.local/graphql"


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


def test_run_plugin_hook_idempotent_rewrite(tmp_path, capsys):
    """Running the hook twice with identical input yields one entry per key, byte-identical."""
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
        setup_mod.run_plugin_hook()
        first = creds_file.read_text()
        capsys.readouterr()  # drain
        setup_mod.run_plugin_hook()
        second = creds_file.read_text()

    assert first == second  # idempotent
    assert second.count("UNRAID_API_URL=") == 1
    assert second.count("UNRAID_API_KEY=") == 1
    assert stat.S_IMODE(creds_file.stat().st_mode) == 0o600


@pytest.mark.parametrize(
    ("present_var", "present_canonical", "missing_canonical"),
    [
        ("CLAUDE_PLUGIN_OPTION_UNRAID_API_URL", "UNRAID_API_URL", "UNRAID_API_KEY"),
        ("CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY", "UNRAID_API_KEY", "UNRAID_API_URL"),
    ],
)
def test_run_plugin_hook_advisory_when_only_one_present(
    tmp_path, capsys, present_var, present_canonical, missing_canonical
):
    """One credential present must NOT write a partial .env; advisory names the missing one."""
    from unraid_mcp.core import setup as setup_mod

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch.dict(os.environ, {present_var: "value"}, clear=False),
        patch.object(setup_mod, "CREDENTIALS_DIR", creds_dir),
        patch.object(setup_mod, "CREDENTIALS_ENV_PATH", creds_file),
        patch.object(setup_mod, "PROJECT_ROOT", tmp_path),
    ):
        _clear_option_vars()
        os.environ[present_var] = "value"
        rc = setup_mod.run_plugin_hook()

    assert rc == 0
    assert not creds_file.exists()
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is False
    assert len(report["advisory_failures"]) == 1
    assert missing_canonical in report["advisory_failures"][0]


def test_run_plugin_hook_advisory_when_missing(tmp_path, capsys):
    from unraid_mcp.core import setup as setup_mod

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch.dict(os.environ, {}, clear=False),
        patch.object(setup_mod, "CREDENTIALS_DIR", creds_dir),
        patch.object(setup_mod, "CREDENTIALS_ENV_PATH", creds_file),
        patch.object(setup_mod, "PROJECT_ROOT", tmp_path),
    ):
        _clear_option_vars()
        rc = setup_mod.run_plugin_hook()

    assert rc == 0
    assert not creds_file.exists()
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is False
    assert len(report["advisory_failures"]) == 2
    # Advisory text is the operator's only guidance — it must name the vars + path.
    joined = " ".join(report["advisory_failures"])
    assert "UNRAID_API_URL" in joined
    assert "UNRAID_API_KEY" in joined
    assert str(creds_file) in joined


def test_run_plugin_hook_reports_rejected_value_distinctly(tmp_path, capsys):
    """A present-but-unsafe value is surfaced as 'rejected', not silently dropped."""
    from unraid_mcp.core import setup as setup_mod

    creds_dir = tmp_path / "creds"
    creds_file = creds_dir / ".env"

    with (
        patch.dict(
            os.environ,
            {
                "CLAUDE_PLUGIN_OPTION_UNRAID_API_URL": "https://ok.local",
                "CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY": "bad\nkey",
            },
            clear=False,
        ),
        patch.object(setup_mod, "CREDENTIALS_DIR", creds_dir),
        patch.object(setup_mod, "CREDENTIALS_ENV_PATH", creds_file),
        patch.object(setup_mod, "PROJECT_ROOT", tmp_path),
    ):
        rc = setup_mod.run_plugin_hook()

    assert rc == 0
    assert not creds_file.exists()
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is False
    assert len(report["advisory_failures"]) == 1
    advisory = report["advisory_failures"][0]
    assert "UNRAID_API_KEY" in advisory
    assert "rejected" in advisory.lower()


def test_run_plugin_hook_returns_zero_on_write_failure(tmp_path, capsys):
    """A .env write error must be surfaced in advisory_failures, not escape (always exit 0)."""
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
        patch.object(setup_mod, "_write_env", side_effect=PermissionError("denied")),
    ):
        rc = setup_mod.run_plugin_hook()

    assert rc == 0  # never blocks the session
    report = json.loads(capsys.readouterr().out)
    assert report["ran_repair"] is False
    assert len(report["advisory_failures"]) == 1
    assert "Failed to write" in report["advisory_failures"][0]
    assert "PermissionError" in report["advisory_failures"][0]


@pytest.mark.parametrize("argv", [["unraid-mcp", "setup", "plugin-hook"], ["unraid-mcp", "setup"]])
def test_main_setup_dispatch_invokes_plugin_hook(argv):
    import unraid_mcp.main as main_mod

    with (
        patch.object(sys, "argv", argv),
        patch("unraid_mcp.core.setup.run_plugin_hook", return_value=0) as mock_hook,
        pytest.raises(SystemExit) as exc,
    ):
        main_mod.main()

    assert exc.value.code == 0
    mock_hook.assert_called_once()


def test_main_setup_rejects_unknown_subcommand():
    import unraid_mcp.main as main_mod

    with (
        patch.object(sys, "argv", ["unraid-mcp", "setup", "bogus"]),
        patch("unraid_mcp.core.setup.run_plugin_hook") as mock_hook,
        pytest.raises(SystemExit) as exc,
    ):
        main_mod.main()

    assert exc.value.code == 2
    mock_hook.assert_not_called()


def test_main_without_setup_does_not_dispatch_hook():
    """Normal startup must not be hijacked by the setup guard."""
    import unraid_mcp.main as main_mod

    with (
        patch.object(sys, "argv", ["unraid-mcp"]),
        patch("unraid_mcp.core.setup.run_plugin_hook") as mock_hook,
        patch("unraid_mcp.server.run_server") as mock_run_server,
    ):
        main_mod.main()

    mock_hook.assert_not_called()
    mock_run_server.assert_called_once()
