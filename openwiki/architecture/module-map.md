---
type: "Reference"
title: "Module Map"
openwiki_generated: true
---

# Module Map

Source file organization and what each major component does.

## Core application

### Entry point

**`src/main.rs`**
- Parses command-line arguments
- Loads `~/.unraid/.env` (or `/data/.env` in container)
- Initializes logging
- Dispatches to one of three modes:
  - HTTP MCP server (no args or `serve mcp`)
  - stdio MCP (`mcp`)
  - CLI (any other args)
- Contains `is_loopback_host()` helper for auth bypass detection
- Safety guard: refuses non-loopback bind with no auth unless `UNRAID_NOAUTH=true`

### Public library

**`src/lib.rs`**
- Re-exports public API surface
- Module declarations (`app`, `config`, `graphql`, `mcp`, `logging`, `observability`, `token_limit`)
- `testing` module (doc-hidden) with helpers:
  - `loopback_state()` - Pre-configured `AppState` with `LoopbackDev` policy
  - `bearer_state(token)` - AppState with static bearer token
  - `oauth_state(data_dir)` - AppState with OAuth mounted
  - `stub_service()` - Service pointing at dummy URL

## Business logic

### Service layer

**`src/app.rs`** (15KB)
- `UnraidService` - thin pass-through layer with no business logic
- One async method per action (30+ methods)
- Each method delegates to corresponding `UnraidClient` method
- Example:
  ```rust
  pub async fn server(&self) -> Result<Value> {
      self.client.server().await
  }
  ```

**Why this layer exists:** Separation of concerns. The service could add caching, validation, or orchestration without affecting the MCP/CLI layers or the GraphQL client.

### GraphQL client

**`src/graphql.rs`** (44KB)
- `UnraidClient` - HTTP client for the Unraid GraphQL API
- One async method per action (matches `UnraidService` methods)
- Each method builds and runs a GraphQL query via `run_typed()` or `query()`
- `run_typed<T>()` - Generic helper for cynic operations
- `send_graphql()` - Low-level HTTP POST to `UNRAID_API_URL`
  - Sets `x-api-key: UNRAID_API_KEY` header
  - Passes query as variables (not interpolated, prevents injection)
  - Respects `UNRAID_API_SKIP_TLS_VERIFY`
- `UnraidClient::new()` - Builder that validates config and creates reqwest client

**`src/gql_typed.rs`** (98KB)
- Typed GraphQL operations using cynic derives
- `QueryFragment`, `MutationFragment`, `InputObject` structs for all operations
- Checked against vendored SDL at compile time via `build.rs`
- Examples:
  ```rust
  #[derive(cynic::QueryFragment, Serialize)]
  #[cynic(graphql_type = "Query")]
  pub struct ServerQuery {
      pub server: ServerData,
  }
  ```
- Handles type quirks (ID!, BigInt, field name collisions, enum case mismatches)
- `#[serde(rename_all = "camelCase")]` on structs for round-trip through `Value`

**`build.rs`**
- Registers `schema/unraid-schema.graphql` with cynic as the default schema
- Runs `cargo:rerun-if-changed` on the schema file

## MCP layer

### MCP orchestration

**`src/mcp.rs`**
- `AppState` - Shared state for HTTP server (config, service, counters, auth policy)
- `AuthPolicy` enum:
  - `LoopbackDev` - No auth (loopback or no-auth flag)
  - `Mounted { auth_state }` - Bearer token or OAuth
- `build_auth_layer()` - Constructs Axum middleware for the selected policy

### RMCP server

**`src/mcp/rmcp_server.rs`** (14KB)
- `UnraidMcpServer` - Implements RMCP `ServerHandler` trait
- Tool handler: dispatches to `tools::dispatch_action()`
- Resource handler: exposes `unraid://schema/mcp-tool` JSON Schema
- Prompt handler: exposes `server_summary` prompt
- Scope enforcement via `required_scope_for(action)`
- Authorization context extraction from request extensions

### Action dispatch

**`src/mcp/tools.rs`** (38KB)
- `dispatch_action()` - Matches action string to service method call
- HELP_TEXT - Markdown reference for all actions
- Implements pagination envelope (items, total, has_more, next_offset)
- Response truncation (~40KB cap via `token_limit.rs`)

**`src/mcp/schemas.rs`** (18KB)
- **Single source of truth for valid actions**
- `ACTIONS: &[ActionSpec]` - Slice defining all actions with:
  - `name` - Action identifier
  - `scope` - `None` (help), `Read`, or `Write`
- `UNRAID_ACTIONS` enum - Derived from ACTIONS (for JSON Schema)
- `VALID_ACTIONS` - Derived comma-separated list for error messages
- `required_scope_for(action)` - Scope lookup helper
- `Scope` enum: `None`, `Read`, `Write`

**Where to add a new action:**
1. Add cynic operation in `gql_typed.rs`
2. Add client method in `graphql.rs`
3. Add service method in `app.rs`
4. Add entry to `ACTIONS` in `schemas.rs`
5. Add match arm in `tools.rs`
6. Add CLI command/parse/dispatch/format in `src/cli/` submodules

### HTTP routing

**`src/mcp/routes.rs`** (5KB)
- Axum router setup:
  - `POST /mcp` - RMCP handler
  - `GET /health` - Observability probe
  - `GET /.well-known/*` - OAuth discovery (when OAuth mounted)
  - `GET /status` - Server info (auth required)
- CORS middleware
- Host header validation middleware
- Request size limits

### Other MCP components

**`src/mcp/prompts.rs`** (1KB)
- Defines `server_summary` prompt template

**`src/mcp/host_filter.rs`** (4KB)
- Validates `Host` header against configured whitelist

## CLI layer

**`src/cli.rs`** (136 bytes)
- Module facade only (re-exports submodules)

**`src/cli/parse.rs`** (10KB)
- Parses CLI args into `CliCommand` enum
- Handles flags like `--json`, `--help`, `--version`

**`src/cli/commands.rs`** (3KB)
- `CliCommand` enum - One variant per CLI command

**`src/cli/dispatch.rs`** (13KB)
- Matches `CliCommand` to service method call
- Returns formatted result for terminal output

**`src/cli/format.rs`** (27KB)
- Human-readable formatters for each action
- `fmt_*` functions return styled terminal output

**`src/cli/setup.rs`** (12KB)
- `setup install` - Installs the server
- `setup plugin-hook` - Called from Unraid plugin hooks
- `doctor` - Installation validator

**`src/cli/doctor.rs`** (16KB)
- Health checks: config, connectivity, runtime environment

## Configuration

**`src/config.rs`** (11KB)
- `Config` struct - Top-level config (mcp + unraid)
- `McpConfig` - HTTP server config (host, port, auth, etc.)
- `UnraidConfig` - GraphQL API config (URL, key, TLS verify)
- `AuthConfig` - OAuth sub-config
- `default_data_dir()` - Returns `~/.unraid/` or `/data/` (container)
- `load_dotenv()` - Loads `.env` file with symlink guard
- `Config::load()` - Loads from env vars + optional `config.toml`

## Observability

**`src/observability.rs`** (4KB)
- `Counters` struct - Request tracking (total, errors, by action)
- `health_check()` - Probes upstream Unraid API reachability
- `/health` endpoint returns 503 if upstream is down

**`src/token_limit.rs`** (2KB)
- `truncate_utf8()` - Truncates JSON at UTF-8 boundary (~40KB)

## Logging

**`src/logging.rs`** (2KB)
- `init_logging()` - Sets up dual output (console + JSON file)
- `should_colorize()` - Detects TTY for colored output

**`src/logging/formatters.rs`**
- Aurora-colored console formatter for stderr

## Testing support

**`src/mock.rs`** (13KB, `test-support` feature)
- Scenario-driven offline mock of the Unraid GraphQL API
- `classify_query()` - Routes query by root field to scenario fixture
- Used by tests and by `examples/mock_unraid.rs`

**`examples/mock_unraid.rs`**
- Standalone mock server for development
- Runs `mock_unraid` binary with `--features test-support`

## Plugin integration

**`plugins/unraid/`**
- Claude Code plugin integration
- `.mcp.json` - MCP client configuration
- `hooks/` - Plugin lifecycle hooks
- `skills/unraid/SKILL.md` - Skill documentation

## Schema and tests

**`schema/unraid-schema.graphql`**
- Vendored Unraid SDL with provenance header
- Used by cynic for compile-time type checking
- Used by schema-contract test (`tests/schema_contract.rs`)

**`tests/`**
- Integration tests covering auth, dispatch, pagination, OAuth, stdio, etc.
- See [operations/testing.md](../operations/testing.md) for details

## Build and tooling

**`Justfile`**
- Development commands: `just test`, `just fmt`, `just clippy`, `just build`
- Container commands: `just docker-run`, `just docker-shell`

**`.github/workflows/`**
- `ci.yml` - Format, clippy, test, audit checks
- `schema-drift.yml` - Daily schema drift detection
- `docker-publish.yml` - OCI image publishing
- `release.yml` - Release automation

**`Cargo.toml`**
- Workspace with `xtask` crate
- MSRV: 1.90
- Key dependencies: tokio, axum, rmcp, reqwest, cynic, lab-auth

**`install.sh`**
- One-line installer for local development
