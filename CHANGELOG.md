# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.3] - 2026-04-05

### Changed
- **`install-deps.sh`**: Added Rust/Cargo support (`Cargo.lock` → `cargo build --release` into `${CLAUDE_PLUGIN_DATA}/target`).

## [1.3.2] - 2026-04-05

### Changed
- **SessionStart hook**: Extracted inline uv command into `.claude-plugin/install-deps.sh` — a language-agnostic script that detects the package manager from lock files (uv, npm, yarn, pnpm) and installs deps into `${CLAUDE_PLUGIN_DATA}`.

## [1.3.1] - 2026-04-05

### Changed
- **`.mcp.json`**: Added all server env vars with defaults; removed `UNRAID_CREDENTIALS_DIR` (container-only override, not user-facing).

## [1.3.0] - 2026-04-05

### Added
- **SessionStart hook**: `plugin.json` now installs Python deps via `uv sync` into `${CLAUDE_PLUGIN_DATA}/.venv` on first run and on any `uv.lock` change — fixes "server failed to start" for users installing via the plugin system.
- **Persistent venv**: MCP server command uses `UV_PROJECT_ENVIRONMENT=${CLAUDE_PLUGIN_DATA}/.venv` so the installed venv survives plugin updates without reinstalling on every session.

### Changed
- **`.mcp.json`**: Added `UV_PROJECT_ENVIRONMENT=${CLAUDE_PLUGIN_DATA}/.venv` and `--project ${CLAUDE_PLUGIN_ROOT}` so the MCP server uses the persisted venv installed by the hook.

## [1.2.5] - 2026-04-05

### Changed
- **CI gating**: `mcp-integration` now runs only when both `UNRAID_API_URL` and `UNRAID_API_KEY` secrets are present, preventing fork and unconfigured-repo runs from failing on live integration setup.
- **Plugin manifests**: Claude plugin manifest now points to `./.mcp.json` instead of embedding an inline MCP server definition; version-bearing files synchronized to `1.2.5`.

## [1.2.4] - 2026-04-04

### Added
- **Comprehensive test suite**: Added tests for core modules, configuration, validation, subscriptions, and edge cases
- **Test coverage documentation**: `tests/TEST_COVERAGE.md` with coverage map and gap analysis

### Changed
- **Documentation**: Comprehensive updates across CLAUDE.md, README, and reference docs
- **Version sync**: Fixed `pyproject.toml` version mismatch (was 1.2.2, now aligned with all manifests at 1.2.4)

## [1.2.3] - 2026-04-03

### Changed
- **hooks/hooks.json**: Removed `SessionStart` hook — `sync-env.sh` was exiting 1 on every session start when `UNRAID_MCP_BEARER_TOKEN` was not set via plugin userConfig, causing startup hook errors.

## [1.2.2] - 2026-04-03

### Changed
- **README**: Restructured to a compact reference format — removed marketing prose, replaced with minimal tables and direct headings.
- **CHANGELOG**: Adopted Keep a Changelog format.
- **Version sync**: `.codex-plugin/plugin.json` and `gemini-extension.json` brought to 1.2.2 (were stale at 1.2.0).

## [1.2.1] - 2026-04-03

### Fixed
- **OAuth discovery 401 cascade** (fixes [#17](https://github.com/jmagar/unraid-mcp/issues/17)): `BearerAuthMiddleware` was blocking `GET /.well-known/oauth-protected-resource`, causing MCP clients (e.g. Claude Code) to surface a generic "unknown error" after receiving a 401. Added `WellKnownMiddleware` (RFC 9728) placed before `BearerAuthMiddleware` that returns resource metadata with `bearer_methods_supported: ["header"]` and no `authorization_servers` — telling clients to use a pre-configured Bearer token rather than attempting an OAuth flow.

### Added
- **`docs/AUTHENTICATION.md`**: New setup guide covering token generation, server config, Claude Code client config (`"Authorization": "Bearer <token>"` header format), and troubleshooting for common 401 errors.
- **README Authentication section**: Added the missing `## 🔐 Authentication` section (was linked in TOC but not present) with quick-start examples and a link to the full guide.

## [1.2.0] - 2026-03-30

### Added
- **HTTP bearer token auth**: ASGI-level `BearerAuthMiddleware` (pure `__call__` pattern, no BaseHTTPMiddleware overhead) enforces `Authorization: Bearer <token>` on all HTTP requests. RFC 6750 compliant — missing header returns `WWW-Authenticate: Bearer realm="unraid-mcp"`, invalid token adds `error="invalid_token"`.
- **Auto token generation**: On first HTTP startup with no token configured, a `secrets.token_urlsafe(32)` token is generated, written to `~/.unraid-mcp/.env` (mode 600), announced once on STDERR without printing the secret, and removed from `os.environ` so subprocesses cannot inherit it.
- **Per-IP rate limiting**: 60 failed auth attempts per 60 seconds → 429 with `Retry-After: 60` header.
- **Gateway escape hatch**: `UNRAID_MCP_DISABLE_HTTP_AUTH=true` bypasses bearer auth for users who handle authentication at a reverse proxy / gateway layer.
- **Startup guard**: Server refuses to start in HTTP mode (`streamable-http`/`sse`) if no token is set and `UNRAID_MCP_DISABLE_HTTP_AUTH` is not explicitly enabled.
- **Tests**: 23 new tests in `tests/test_auth.py` covering pass-through scopes, 401/429 responses, RFC 6750 header differentiation, per-IP rate limiting, window expiry, token generation, and startup guard.

### Changed
- **Default transport**: `stdio` → `streamable-http`. Users running directly (not via Claude Desktop plugin) will now get an HTTP server by default. To keep stdio behaviour, set `UNRAID_MCP_TRANSPORT=stdio`. The Claude Desktop plugin (`plugin.json`) is unaffected — it hardcodes `stdio`.
- **`.env.example`**: Updated to document new auth variables (`UNRAID_MCP_BEARER_TOKEN`, `UNRAID_MCP_DISABLE_HTTP_AUTH`) and updated default transport comment.

### Breaking Changes
- **Default transport is now `streamable-http`**. Any script or service that relied on the default being `stdio` must explicitly set `UNRAID_MCP_TRANSPORT=stdio`.

## [1.1.6] - 2026-03-30

### Security

- **Path traversal**: `flash_backup` source path now validated after `posixpath.normpath` (not before) — raw-string `..` check was bypassable via encoded sequences like `foo/bar/../..`; null byte guard added
- **Key validation**: `DANGEROUS_KEY_PATTERN` now blocks space (0x20) and DEL (0x7f) in addition to existing shell metacharacters; applies to both rclone and settings key validation

### Fixed

- **Settings validation**: `configure_ups` input now validated via `_validate_settings_input` before mutation — was previously passing unvalidated dict directly to GraphQL
- **Subscription locks**: `_start_one` `last_error` write and `stop_all()` keys snapshot both now take `_task_lock` to prevent concurrent write/read races
- **Keepalive handling**: Removed `"ping"` from keepalive `elif` — ping messages require a pong response, not silent discard; only `"ka"` and `"pong"` are silently dropped
- **Middleware import**: `middleware_refs.py` `ErrorHandlingMiddleware` import changed from `TYPE_CHECKING`-only to unconditional — `isinstance()` calls at runtime were silently broken
- **Health reverse map**: `_STATUS_FROM_SEVERITY` dict hoisted to module level — was being rebuilt on every `_comprehensive_health_check` call

### Changed

- **Log content cap**: `_cap_log_content` now skipped for non-log subscriptions (only `log_tail`/`logFileSubscription` have `content` fields) — reduces unnecessary dict key lookups on every WebSocket message
- **Live assertion**: `_handle_live` now raises `RuntimeError` at import time if `COLLECT_ACTIONS` contains keys not in `_HANDLED_COLLECT_SUBACTIONS` — catches handler omissions before runtime
- **Subscription name guard**: `start_subscription` validates name matches `^[a-zA-Z0-9_]+$` before use as WebSocket message ID

### Added

- **Tests**: 27 parametrized tests for `DANGEROUS_KEY_PATTERN` covering all documented dangerous characters and safe key examples (`tests/test_validation.py`)
- **Tests**: `test_check_api_error_wrapped_tool_error` — verifies health check returns `{status: unhealthy}` when `make_graphql_request` raises `ToolError` wrapping `httpx.ConnectError`

## [1.1.5] - 2026-03-27

### Added
- **Beads issue tracking**: `bd init` — Dolt-backed issue tracker with prefix `unraid-mcp-<hash>`, hooks, and AGENTS.md integration
- **Lavra project config**: `.lavra/config/project-setup.md` — stack `python`, review agents (kieran-python-reviewer, code-simplicity-reviewer, security-sentinel, performance-oracle)
- **Codebase profile**: `.lavra/config/codebase-profile.md` — auto-generated stack/architecture/conventions reference for planning and review commands

### Changed
- **`.gitignore`**: Added lavra session-state exclusion (`.lavra/memory/session-state.md`) and beads-related entries
- **`CLAUDE.md`**: Added beads workflow integration block with mandatory `bd` usage rules and session completion protocol

## [1.1.4] - 2026-03-25

### Changed
- **Plugin branding**: `displayName` set to `unRAID` in `plugin.json` and `marketplace.json`
- **Plugin description**: Expanded to list all 3 tools and all 15 action domains with full subaction inventory (107 subactions, destructive actions marked with `*`)

## [1.1.3] - 2026-03-24

### Fixed
- **Docs accuracy**: `disk/logs` docs corrected to use `log_path`/`tail_lines` parameters (were `path`/`lines`)
- **Docs accuracy**: `rclone/create_remote` docs corrected to `provider_type`/`config_data` (were `type`/`fields`)
- **Docs accuracy**: `setting/update` docs corrected to `settings_input` parameter (was `settings`)
- **Docs accuracy**: `key/create` now documents `roles` as optional; `add_role`/`remove_role` corrected to `roles` (plural)
- **Docs accuracy**: `oidc/validate_session` now documents required `token` parameter
- **Docs accuracy**: `parity_start` quick-reference example now includes required `correct=False`
- **Docs accuracy**: `log_tail` README example now includes required `path="/var/log/syslog"`
- **Docs accuracy**: `live/parity_progress` added to event-driven subscriptions list in troubleshooting guide
- **Docs accuracy**: `live/array_state` wording softened — "may show connecting indefinitely" vs "will always show"
- **Markdown**: `endpoints.md` top-level heading moved before blockquote disclaimer (MD041)
- **Tests**: `test_resources.py` now uses `_get_resource()` helper instead of raw `mcp.providers[0]._components[...]` access; isolates FastMCP internals to one location

---

## [1.1.2] - 2026-03-23

### Security
- **Path traversal**: Removed `/mnt/` from `_ALLOWED_LOG_PREFIXES` — was exposing all Unraid user shares to path-based reads
- **Path traversal**: Added early `..` detection for `disk/logs` and `live/log_tail` before any filesystem access; added `/boot/` prefix restriction for `flash_backup` source paths
- **Timing-safe auth**: `verify_token` now uses `hmac.compare_digest` instead of `==` to prevent timing oracle attacks on API key comparison
- **Traceback leak**: `include_traceback` in `ErrorHandlingMiddleware` is now gated on `DEBUG` log level; production deployments no longer expose stack traces

### Fixed
- **Health check**: `_comprehensive_health_check` now re-raises `CredentialsNotConfiguredError` instead of swallowing it into a generic unhealthy status
- **UPS device query**: Removed non-existent `nominalPower` and `currentPower` fields from `ups_device` query — every call was failing against the live API
- **Stale credential bindings**: Subscription modules (`manager.py`, `snapshot.py`, `utils.py`, `diagnostics.py`) previously captured `UNRAID_API_KEY`/`UNRAID_API_URL` at import time; replaced with `_settings.ATTR` call-time access so `apply_runtime_config()` updates propagate correctly after credential elicitation

### Added
- **CI pipeline**: `.github/workflows/ci.yml` with 5 jobs — lint (`ruff`), typecheck (`ty`), test (`pytest -m "not integration"`), version-sync check, and `uv audit` dependency scan
- **Coverage threshold**: `fail_under = 80` added to `[tool.coverage.report]`
- **Version sync check**: `scripts/validate-marketplace.sh` now verifies `pyproject.toml` and `plugin.json` versions match

### Changed
- **Docs**: Updated `CLAUDE.md`, `README.md` to reflect 3 tools (1 primary + 2 diagnostic); corrected system domain count (19→18); fixed scripts comment
- **Docs**: `docs/AUTHENTICATION.md` H1 retitled to "Authentication Setup Guide"
- **Docs**: Added `UNRAID_CREDENTIALS_DIR` commented entry to `.env.example`
- Removed `from __future__ import annotations` from `snapshot.py` (caused TC002 false positives with FastMCP)
- Added `# noqa: ASYNC109` to `timeout` parameters in `_handle_live` and `unraid()` (valid suppressions)
- Fixed `start_array*` → `start_array` in tool docstring table (`start_array` is not in `_ARRAY_DESTRUCTIVE`)

### Refactored
- **Path validation**: Extracted `_validate_path()` in `unraid.py` — consolidates traversal check, `normpath`, and prefix validation used by both `disk/logs` and `live/log_tail` into one place; eliminates duplication
- **WebSocket auth payload**: Extracted `build_connection_init()` in `subscriptions/utils.py` — removes 4 duplicate `connection_init` blocks from `snapshot.py` (×2), `manager.py`, and `diagnostics.py`; also fixes a bug in `diagnostics.py` where `x-api-key: None` was sent when no API key was configured
- Removed `_LIVE_ALLOWED_LOG_PREFIXES` alias — direct reference to `_ALLOWED_LOG_PREFIXES`
- Moved `import hmac` to module level in `server.py` (was inside `verify_token` hot path)

---

## [1.1.1] - 2026-03-16

### Added
- **API key auth**: `Authorization: Bearer <UNRAID_MCP_API_KEY>` bearer token authentication via `ApiKeyVerifier` — machine-to-machine access without OAuth browser flow
- **MultiAuth**: When both Google OAuth and API key are configured, `MultiAuth` accepts either method
- **Google OAuth**: Full `GoogleProvider` integration — browser-based OAuth 2.0 flow with JWT session tokens; `UNRAID_MCP_JWT_SIGNING_KEY` for stable tokens across restarts
- **`fastmcp.json`**: Dev tooling configs for FastMCP

### Fixed
- Auth test isolation: use `os.environ[k] = ""` instead of `delenv` to prevent dotenv re-injection between test reloads

---

## [1.1.0] - 2026-03-16

### Breaking Changes
- **Tool consolidation**: 15 individual domain tools (`unraid_docker`, `unraid_vm`, etc.) merged into single `unraid` tool with `action` + `subaction` routing
  - Old: `unraid_docker(action="list")`
  - New: `unraid(action="docker", subaction="list")`

### Added
- **`live` tool** (11 subactions): Real-time WebSocket subscription snapshots — `cpu`, `memory`, `cpu_telemetry`, `array_state`, `parity_progress`, `ups_status`, `notifications_overview`, `notification_feed`, `log_tail`, `owner`, `server_status`
- **`customization` tool** (5 subactions): `theme`, `public_theme`, `is_initial_setup`, `sso_enabled`, `set_theme`
- **`plugin` tool** (3 subactions): `list`, `add`, `remove`
- **`oidc` tool** (5 subactions): `providers`, `provider`, `configuration`, `public_providers`, `validate_session`
- **Persistent `SubscriptionManager`**: `unraid://live/*` MCP resources backed by long-lived WebSocket connections with auto-start and reconnection
- **`diagnose_subscriptions`** and **`test_subscription_query`** diagnostic tools
- `array`: Added `parity_history`, `start_array`, `stop_array`, `add_disk`, `remove_disk`, `mount_disk`, `unmount_disk`, `clear_disk_stats`
- `keys`: Added `add_role`, `remove_role`
- `settings`: Added `update_ssh` (confirm required)
- `stop_array` added to `_ARRAY_DESTRUCTIVE`
- `gate_destructive_action` helper in `core/guards.py` — centralized elicitation + confirm guard
- Full safety test suite: `TestNoGraphQLCallsWhenUnconfirmed` (zero-I/O guarantee for all 13 destructive actions)

### Fixed
- Removed 29 actions confirmed absent from live API v4.29.2 via GraphQL introspection (Docker organizer mutations, `unassignedDevices`, `warningsAndAlerts`, etc.)
- `log_tail` path validated against allowlist before subscription start
- WebSocket auth uses `x-api-key` connectionParams format

---

## [1.0.0] - 2026-03-14 through 2026-03-15

### Breaking Changes
- Credential storage moved to `~/.unraid-mcp/.env` (dir 700, file 600); all runtimes load from this path
- `unraid_health(action="setup")` is the only tool that triggers credential elicitation; all others propagate `CredentialsNotConfiguredError`

### Added
- `CredentialsNotConfiguredError` sentinel — propagates cleanly through `tool_error_handler` with exact credential path in the error message
- `is_configured()` and `apply_runtime_config()` in `settings.py` for runtime credential injection
- `elicit_and_configure()` with `.env` persistence and confirmation before overwrite
- 28 GraphQL mutations across storage, docker, notifications, and new settings tool
- Comprehensive test suite expansion: schema validation (99 tests), HTTP layer (respx), property tests, safety audit, contract tests

### Fixed
- Numerous PR review fixes across 50+ commits (CodeRabbit, ChatGPT-Codex review rounds)
- Shell scripts hardened against injection and null guards
- Notification enum validation, subscription lock split, safe_get semantics

---

## [0.6.0] - 2026-03-15

### Added
- Subscription byte/line cap to prevent unbounded memory growth
- `asyncio.timeout` bounds on `subscribe_once` / `subscribe_collect`
- Partial auto-start for subscriptions (best-effort on startup)

### Fixed
- WebSocket URL scheme handling (`ws://`/`wss://`)
- `flash_backup` path validation and smoke test assertions

---

## [0.5.0] - 2026-03-15

*Tool expansion and live subscription foundation.*

---

## [0.4.x] - 2026-03-13 through 2026-03-14

*Credential elicitation system, per-tool refactors, and mutation additions.*

---

## [0.2.x] - 2026-02-15 through 2026-03-13

*Initial public release hardening: PR review cycles, test suite expansion, security fixes, plugin manifest.*

---

## [0.1.0] - 2026-02-08

### Added
- Consolidated 26 tools into 10 tools with 90 actions
- FastMCP architecture migration with `uv` toolchain
- Docker Compose support with health checks
- WebSocket subscription infrastructure

---

*Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). Versioning: [Semantic Versioning](https://semver.org/).*
