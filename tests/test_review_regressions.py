"""Regression coverage for packaging, manifests, and hook scripts."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifest_restores_stdio_server_definition() -> None:
    plugin = json.loads((PROJECT_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert plugin["userConfig"]["unraid_mcp_token"]["sensitive"] is True
    assert "mcpServers" in plugin
    assert plugin["mcpServers"] == "./.mcp.json"


def test_ci_gates_live_integration_job_on_unraid_secrets() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    # Secrets are mapped to env vars at job level; step if-condition checks env vars
    # (GitHub Actions forbids secrets.* in if conditions — security policy)
    assert "secrets.UNRAID_API_URL" in workflow
    assert "secrets.UNRAID_API_KEY" in workflow
    assert "env.UNRAID_API_URL != ''" in workflow
    assert "env.UNRAID_API_KEY != ''" in workflow


def test_container_configs_use_runtime_port_variable() -> None:
    compose = (PROJECT_ROOT / "docker-compose.yaml").read_text()
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()
    assert "${UNRAID_MCP_PORT:-6970}:${UNRAID_MCP_PORT:-6970}" in compose
    assert "${UNRAID_MCP_PORT:-6970}" in compose
    assert "${UNRAID_MCP_PORT:-6970}" in dockerfile


def test_test_live_script_uses_safe_counters_and_resource_failures() -> None:
    script = (PROJECT_ROOT / "tests" / "test_live.sh").read_text()
    assert "(( PASS++ ))" in script
    assert "(( FAIL++ ))" in script
    assert "(( SKIP++ ))" in script


def test_sync_env_rejects_multiline_values(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(tmp_path)
    env["CLAUDE_PLUGIN_OPTION_UNRAID_API_URL"] = "https://tower.local\nINJECT=1"

    result = subprocess.run(  # noqa: S603
        ["/usr/bin/bash", str(PROJECT_ROOT / "hooks" / "scripts" / "sync-env.sh")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "control characters" in result.stderr


def test_sync_env_rejects_empty_bearer_token(tmp_path: Path) -> None:
    """sync-env must fail when no bearer token is provided — auto-generation was removed."""
    env_file = tmp_path / ".env"
    env_file.write_text("UNRAID_MCP_BEARER_TOKEN=\n")

    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(tmp_path)

    result = subprocess.run(  # noqa: S603
        ["/usr/bin/bash", str(PROJECT_ROOT / "hooks" / "scripts" / "sync-env.sh")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "UNRAID_MCP_BEARER_TOKEN is not set" in result.stderr


def test_ensure_gitignore_preserves_ignore_before_negation(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("!backups/.gitkeep\n")

    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(tmp_path)

    result = subprocess.run(  # noqa: S603
        ["/usr/bin/bash", str(PROJECT_ROOT / "hooks" / "scripts" / "ensure-gitignore.sh")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    lines = gitignore.read_text().splitlines()
    assert lines.index("backups/*") < lines.index("!backups/.gitkeep")
