# unraid-mcp — Claude Code instructions

## What this project is

`unraid-mcp` is a Rust binary (`unraid`) that bridges Claude to the Unraid server GraphQL API via the Model Context Protocol. It is read-only: all 24 actions fetch data; none modify state.

## Module map

| File | Role |
|------|------|
| `src/graphql.rs` | `UnraidClient` — raw HTTP client, one method per GraphQL query |
| `src/app.rs` | `UnraidService` — business layer, thin wrapper over the client |
| `src/mcp/tools.rs` | Dispatches JSON args to service methods, returns `Value` |
| `src/mcp/schemas.rs` | MCP tool JSON Schema and action enum |
| `src/mcp/rmcp_server.rs` | RMCP `ServerHandler`: tools, resources, prompts, scope checks |
| `src/mcp/routes.rs` | Axum router: `/mcp`, `/health`, OAuth discovery routes |
| `src/mcp/prompts.rs` | MCP prompts (`server_summary`) |
| `src/mcp.rs` | `AppState`, `AuthPolicy`, `build_auth_layer` |
| `src/config.rs` | Config structs, env loading, TOML parsing |
| `src/cli.rs` | CLI arg parsing, human-readable formatters |
| `src/main.rs` | Mode dispatch: HTTP server / stdio / CLI |
| `src/lib.rs` | Public API surface + `testing` helpers |

## Key patterns

**Thin shims.** Neither the CLI nor the MCP tool contains logic. They parse their input format and delegate to `UnraidService`. The service delegates to `UnraidClient`. All data retrieval is in the client's GraphQL queries.

**Action-based dispatch.** The single MCP tool `unraid` uses an `action` string parameter. `mcp/tools.rs` matches on `action` and calls the corresponding service method.

**GraphQL as the data layer.** `graphql.rs` POSTs to `UNRAID_API_URL` with `x-api-key: UNRAID_API_KEY`. Responses are `serde_json::Value` throughout — no typed schema on the Rust side.

**Auth policy enum.** `AuthPolicy::LoopbackDev` skips all auth. `AuthPolicy::Mounted` uses `lab-auth` (bearer token or OAuth). Auth is automatically set to `LoopbackDev` when `config.mcp.host` starts with `127.` or `no_auth` is set.

## Environment variables

```
UNRAID_API_URL              Unraid GraphQL endpoint (required)
UNRAID_API_KEY              API key for x-api-key header (required)
UNRAID_API_SKIP_TLS_VERIFY  Skip TLS cert check (default false)
UNRAID_MCP_HOST             Bind host (default 0.0.0.0)
UNRAID_MCP_PORT             Bind port (config.toml default: 6970)
UNRAID_MCP_TOKEN            Static bearer token for /mcp
UNRAID_MCP_DISABLE_HTTP_AUTH  Disable MCP auth (1/true/yes)
UNRAID_MCP_NO_AUTH            Alias for disabling auth
UNRAID_MCP_ALLOWED_HOSTS    Extra comma-separated Host header values
UNRAID_MCP_ALLOWED_ORIGINS  Extra comma-separated CORS origins
UNRAID_MCP_PUBLIC_URL       Public URL for OAuth metadata
RUST_LOG                    Log filter
```

## How to add a new action

1. **`src/graphql.rs`** — add `pub async fn your_action(&self) -> Result<Value>` that calls `self.query(...)`.

2. **`src/app.rs`** — add a delegating method: `pub async fn your_action(&self) -> Result<Value> { self.client.your_action().await }`.

3. **`src/mcp/tools.rs`** — add the match arm: `"your_action" => state.service.your_action().await,`. Also add the description to `HELP_TEXT`.

4. **`src/mcp/schemas.rs`** — add `"your_action"` to the `UNRAID_ACTIONS` slice.

5. **`src/cli.rs`** — add the `CliCommand` variant, parse arm in `CliCommand::parse`, dispatch arm in `run`, and a human-readable formatter `fmt_your_action`.

For actions with parameters (like `docker_logs` with `id` and `tail`), follow the `docker_logs` pattern in `tools.rs` for extracting args with `string_arg` and `i64_arg`.

## Common gotchas

- **BigInt fields** from the Unraid GraphQL API arrive as JSON strings, not numbers. See `bigint_f64()` in `cli.rs`. Memory sizes in the `metrics` query use this pattern.
- **Temperature unit** is a GraphQL enum (`CELSIUS`, `FAHRENHEIT`, `KELVIN`). See `temp_unit_symbol()` in `cli.rs`.
- **`flash.guid`** is declared non-nullable in the Unraid schema but can be null at runtime. The query omits it.
- **Default port**: `config.rs` built-in default is 3100, but `config.toml` sets 6970. The project runs on 6970.
- **Scopes**: `unraid:read` is required for all 24 data actions. `unraid:admin` satisfies `unraid:read`. `help` has no scope requirement.
- **Tests** in `tests/` use stub clients pointing at `http://localhost:1/graphql`. They do not need a real Unraid server.
- **`tests/test_live.sh` and `tests/TEST_COVERAGE.md`** are stale syslog-mcp artifacts; ignore them.

## Test files

| File | What it tests |
|------|---------------|
| `tests/auth_modes.rs` | Auth middleware: LoopbackDev, bearer, OAuth; `/health`, `/mcp`, well-known routes |
| `tests/cli_help.rs` | `--help` and `--version` flags |
| `tests/oauth_flow.rs` | RS256 JWT acceptance/rejection, scope checks, expired/wrong-issuer tokens |
| `tests/rmcp_compat.rs` | RMCP stateless JSON-response mode, SSE negotiation |
| `tests/stdio_mcp.rs` | stdio child-process transport: `tools/list` then `tools/call` |
| `tests/spike_rmcp_extensions.rs` | Axum extension propagation into tool handlers |

## CLI ↔ MCP action parity

Every MCP action has a corresponding CLI command (§37 pattern). The `help` MCP action
maps to `unraid --help`. Full parity verified — no gaps.

| Service Method | MCP Action | CLI Command |
|---|---|---|
| `service.array()` | `unraid(action="array")` | `unraid array` |
| `service.disks()` | `unraid(action="disks")` | `unraid disks` |
| `service.docker()` | `unraid(action="docker")` | `unraid docker` |
| `service.docker_logs(id, tail)` | `unraid(action="docker_logs", id=…, tail=…)` | `unraid docker logs <id> [--tail N]` |
| `service.vms()` | `unraid(action="vms")` | `unraid vms` |
| `service.server()` | `unraid(action="server")` | `unraid server` |
| `service.info()` | `unraid(action="info")` | `unraid info` |
| `service.shares()` | `unraid(action="shares")` | `unraid shares` |
| `service.notifications()` | `unraid(action="notifications")` | `unraid notifications` |
| `service.log_files()` | `unraid(action="log_files")` | `unraid log-files` |
| `service.log_file(path, lines, start_line)` | `unraid(action="log_file", path=…, lines=…, start_line=…)` | `unraid log <path> [--lines N] [--start-line N]` |
| `service.services()` | `unraid(action="services")` | `unraid services` |
| `service.network()` | `unraid(action="network")` | `unraid network` |
| `service.ups()` | `unraid(action="ups")` | `unraid ups` |
| `service.ups_config()` | `unraid(action="ups_config")` | `unraid ups-config` |
| `service.metrics()` | `unraid(action="metrics")` | `unraid metrics` |
| `service.plugins()` | `unraid(action="plugins")` | `unraid plugins` |
| `service.parity_history()` | `unraid(action="parity_history")` | `unraid parity-history` |
| `service.vars()` | `unraid(action="vars")` | `unraid vars` |
| `service.registration()` | `unraid(action="registration")` | `unraid registration` |
| `service.flash()` | `unraid(action="flash")` | `unraid flash` |
| `service.rclone()` | `unraid(action="rclone")` | `unraid rclone` |
| `service.remote_access()` | `unraid(action="remote_access")` | `unraid remote-access` |
| `service.connect()` | `unraid(action="connect")` | `unraid connect` |
| _(meta)_ | `unraid(action="help")` | `unraid --help` |

## Build commands

```bash
cargo build --release     # produces target/release/unraid
just dev                  # cargo run -- serve mcp
just test                 # cargo test
just lint                 # cargo clippy -- -D warnings
just fmt                  # cargo fmt
just gen-token            # openssl rand -hex 32
```
