"""Regression coverage for packaging and manifests."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifest_restores_stdio_server_definition() -> None:
    plugin = json.loads(
        (PROJECT_ROOT / "plugins" / "unraid" / ".claude-plugin" / "plugin.json").read_text()
    )
    assert plugin["userConfig"]["unraid_api_key"]["sensitive"] is True
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
