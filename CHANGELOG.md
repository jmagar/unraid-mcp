# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed the binary `unraid` → `runraid` (package remains `unraid-mcp`; env vars and
  the `~/.unraid` data dir are unchanged — only the executable name moved).
- Default MCP port is now **40010** (`config.rs` `default_mcp_port()` and `config.toml`
  agree). Earlier docs referencing 3100/6970 were incorrect.
- The binary loads `~/.unraid/.env` (or `/data/.env` in a container) at startup via
  `dotenvy` before `Config::load`, so it can find its credentials without a process
  manager. The loader is symlink-guarded (a symlinked `.env` is refused) and never
  overrides already-set env vars.

### Added

- `status` MCP action — a server reachability/health observability action
  (requires `unraid:read`). MCP-only; no CLI command.
- `setup install` and `doctor` CLI commands (CLI-only; not exposed as MCP actions).
- Pagination/filtering on list actions (`limit`/`offset`, plus `state`/`name` filters
  where relevant), returning a `{items, total, limit, offset, has_more, next_offset}`
  envelope (MCP surface).
- ~40 KB truncation cap on MCP tool responses.
- `docker_restart` action (`unraid:admin`), added after re-vendoring
  `schema/unraid-schema.graphql` from `unraid/api@2679fda1` picked up a new
  `DockerMutations.restart` mutation.
- `array_set_state` accepts optional `decryption_password`/`decryption_keyfile`
  (MCP-only — not exposed via the CLI, to avoid putting secrets in shell
  history/process listings), so an encrypted array can be started without the
  web UI unlock step. Also picked up from the same schema re-vendor.

### Fixed

- GraphQL injection: queries now pass arguments as GraphQL variables instead of
  interpolating them into the query string.
- UTF-8 truncation panic: response truncation no longer splits a multi-byte character.
- `/status` info leak: the endpoint no longer returns server details to unauthenticated
  callers.

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
