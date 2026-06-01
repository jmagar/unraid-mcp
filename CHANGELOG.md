# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-06-01

### Changed

- Plugin `SessionStart`/`ConfigChange` hooks now call `${CLAUDE_PLUGIN_ROOT}/bin/runraid setup plugin-hook` directly instead of going through the `plugin-setup.sh` shell wrapper. The env-var mapping the script performed (`CLAUDE_PLUGIN_OPTION_*` → `UNRAID_*`) now lives in `apply_plugin_options()` in `src/cli/setup.rs`, hoisted in `run_cli` before `Config::load()` (unraid is template-style: the setup check validates the pre-loaded config). The `CLAUDE_PLUGIN_DATA` → `UNRAID_HOME` re-export was dropped (redundant: `setup_data_dir()` reads `CLAUDE_PLUGIN_DATA` natively).

### Removed

- `plugins/unraid/hooks/plugin-setup.sh` — the wrapper was a pure env-mapping middleman now handled by the binary's `setup plugin-hook` command.

## [0.1.0] - 2026-05-13

### Added

- Initial release of unraid-mcp
- 24 read-only MCP actions via the Unraid GraphQL API
- RMCP Streamable HTTP transport on port 6970
- stdio MCP transport (`unraid mcp`)
- CLI with human-readable and `--json` output for all 24 actions
- Static bearer token auth and OAuth (Google) auth via lab-auth
- `LoopbackDev` auth bypass when bound to 127.x or `UNRAID_MCP_DISABLE_HTTP_AUTH=true`
- `unraid://schema/mcp-tool` MCP resource exposing the tool JSON Schema
- `server_summary` MCP prompt
- Integration tests: auth modes, CLI help, OAuth flow, RMCP compat, stdio transport
