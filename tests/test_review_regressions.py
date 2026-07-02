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


def test_plugin_manifests_do_not_hardcode_env_configurable_defaults() -> None:
    """Regression coverage for GitHub issue #137.

    ``.mcp.json`` (Claude Code) and ``.codex-plugin/plugin.json`` (Codex) used to
    hardcode ``UNRAID_VERIFY_SSL=true`` in their ``env`` block. Because
    ``_load_env_files()`` uses ``load_dotenv(override=False)``, a value already
    present in the process env from these manifests permanently shadows the same
    var configured in ``~/.unraid-mcp/.env`` — so a user pointing
    ``UNRAID_VERIFY_SSL`` at a CA-bundle path for a self-signed cert had that
    silently ignored. The same shadowing risk applies to any other var these
    manifests hardcode to a value that merely duplicates the package default
    (``UNRAID_MCP_LOG_LEVEL``, ``UNRAID_MCP_LOG_FILE``,
    ``UNRAID_AUTO_START_SUBSCRIPTIONS``, ``UNRAID_MAX_RECONNECT_ATTEMPTS``) —
    none of them serve a purpose beyond matching ``Settings()``'s own default,
    so none of them belong in the manifest. ``UNRAID_MCP_TRANSPORT=stdio`` is
    the one legitimate exception: it differs from the package default
    (``streamable-http``) and is mandatory for a plugin-launched subprocess,
    which talks to its host over stdio.
    """
    shadowing_prone_vars = {
        "UNRAID_VERIFY_SSL",
        "UNRAID_MCP_LOG_LEVEL",
        "UNRAID_MCP_LOG_FILE",
        "UNRAID_AUTO_START_SUBSCRIPTIONS",
        "UNRAID_MAX_RECONNECT_ATTEMPTS",
    }

    mcp_json = json.loads((PROJECT_ROOT / "plugins" / "unraid" / ".mcp.json").read_text())
    mcp_env = mcp_json["mcpServers"]["unraid-mcp"]["env"]

    codex_manifest = json.loads(
        (PROJECT_ROOT / "plugins" / "unraid" / ".codex-plugin" / "plugin.json").read_text()
    )
    codex_env = codex_manifest["mcpServers"]["unraid-mcp"]["env"]

    for env_block, label in ((mcp_env, ".mcp.json"), (codex_env, ".codex-plugin/plugin.json")):
        leaked = shadowing_prone_vars & env_block.keys()
        assert not leaked, (
            f"{label} hardcodes {leaked}, which duplicates a Settings() default and would "
            "silently shadow the same var configured in ~/.unraid-mcp/.env "
            "(load_dotenv(override=False)) — see issue #137"
        )
        # The mandatory transport override must still be present.
        assert env_block.get("UNRAID_MCP_TRANSPORT") == "stdio"


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


def test_docker_runtime_python_matches_builder_minor_version() -> None:
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()
    assert "uv:python3.12-bookworm-slim" in dockerfile
    assert "FROM python:3.12-slim-bookworm AS runtime" in dockerfile
    assert "FROM python@sha256:" not in dockerfile


def test_test_live_script_uses_safe_counters_and_resource_failures() -> None:
    script = (PROJECT_ROOT / "tests" / "test_live.sh").read_text()
    assert "(( PASS++ ))" in script
    assert "(( FAIL++ ))" in script
    assert "(( SKIP++ ))" in script
