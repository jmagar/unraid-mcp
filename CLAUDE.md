# unraid-mcp — Claude Code instructions

## What this project is

`unraid-mcp` is a Rust binary (`runraid`) that bridges Claude to the Unraid server GraphQL API via the Model Context Protocol. It is read-only: all data actions fetch data; none modify state.

## Module map

| File | Role |
|------|------|
| `src/graphql.rs` | `UnraidClient` — raw HTTP client, one method per GraphQL query |
| `src/app.rs` | `UnraidService` — thin pass-through to `UnraidClient` (no business logic) |
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
UNRAID_API_URL                Unraid GraphQL endpoint (required)
UNRAID_API_KEY                API key for x-api-key header (required)
UNRAID_API_SKIP_TLS_VERIFY    Skip TLS cert check (default false)
UNRAID_MCP_HOST               Bind host (default 0.0.0.0)
UNRAID_MCP_PORT               Bind port (default 40010)
UNRAID_MCP_TOKEN              Static bearer token for /mcp
UNRAID_MCP_DISABLE_HTTP_AUTH  Disable MCP auth entirely (1/true/yes)
UNRAID_MCP_NO_AUTH            Alias that disables MCP auth entirely (1/true/yes)
UNRAID_MCP_ALLOWED_HOSTS      Extra comma-separated Host header values
UNRAID_MCP_ALLOWED_ORIGINS    Extra comma-separated CORS origins
UNRAID_MCP_PUBLIC_URL         Public URL for OAuth metadata
UNRAID_MCP_AUTH_MODE          Auth mode: `bearer` (default) or `oauth`
UNRAID_MCP_AUTH_ADMIN_EMAIL   Admin email for OAuth policy
UNRAID_MCP_GOOGLE_CLIENT_ID       Google OAuth client ID
UNRAID_MCP_GOOGLE_CLIENT_SECRET   Google OAuth client secret
UNRAID_NOAUTH                 Permits a NON-loopback bind without auth being mounted.
                              This is NOT the same as the two flags above — it does
                              NOT disable auth; it only lifts main.rs's safety check
                              that otherwise refuses a non-127.x bind in no-auth mode.
RUST_LOG                      Log filter
```

The binary also loads `~/.unraid/.env` (or `/data/.env` in a container) at startup
via `dotenvy` before `Config::load` — see `load_dotenv()` in `config.rs`. A symlinked
`.env` is refused (symlink-attack guard); already-set env vars are not overridden.

## How to add a new action

The set of valid actions lives in ONE place: the `ACTIONS: &[ActionSpec]` slice in
`src/mcp/schemas.rs`. The schema enum (`UNRAID_ACTIONS`), the error-message action
list (`VALID_ACTIONS` in `tools.rs`), and the MCP scope gating (`required_scope_for`
in `rmcp_server.rs`) are all *derived* from it — do not hand-maintain those lists.

1. **`src/graphql.rs`** — add `pub async fn your_action(&self) -> Result<Value>` that calls `self.query(...)`.

2. **`src/app.rs`** — add a delegating method: `pub async fn your_action(&self) -> Result<Value> { self.client.your_action().await }`.

3. **`src/mcp/schemas.rs`** — add **one** entry to the `ACTIONS` slice:
   `ActionSpec { name: "your_action", read_only: true }`. This single entry feeds
   the schema enum, the valid-actions error text, and the scope check. Set
   `read_only: true` for any data action (it then requires the `unraid:read`
   scope); `read_only: false` means the action needs **no** scope and is reserved
   for `help`-style meta actions. Anything not in this slice falls through to the
   `DENY_SCOPE` sentinel and is unreachable, so the entry is mandatory.

4. **`src/mcp/tools.rs`** — add the dispatch match arm in `dispatch_action`:
   `"your_action" => state.service.your_action().await,`. Also add the description
   to `HELP_TEXT`.

5. **`src/cli.rs`** — add the `CliCommand` variant, parse arm in `CliCommand::parse`, dispatch arm in `run`, and a human-readable formatter `fmt_your_action`.

That's it — no separate scope list or schema-enum edit is needed; both are derived
from the `ACTIONS` entry in step 3, and a unit test in each of `schemas.rs` and
`rmcp_server.rs` asserts the derived lists stay consistent.

For actions with parameters (like `docker_logs` with `id` and `tail`), follow the `docker_logs` pattern in `tools.rs` for extracting args with `string_arg` and `i64_arg`.

## Common gotchas

- **BigInt fields** from the Unraid GraphQL API arrive as JSON strings, not numbers. See `bigint_f64()` in `cli.rs`. Memory sizes in the `metrics` query use this pattern.
- **Temperature unit** is a GraphQL enum (`CELSIUS`, `FAHRENHEIT`, `KELVIN`). See `temp_unit_symbol()` in `cli.rs`.
- **`flash.guid`** is declared non-nullable in the Unraid schema but can be null at runtime. The query omits it.
- **Default port**: the built-in default in `config.rs` (`default_mcp_port()`) is **40010**, matching `config.toml`. The project runs on 40010.
- **Scopes**: `unraid:read` is required for every data action (including `status`). `unraid:admin` satisfies `unraid:read`. `help` has no scope requirement.
- **Pagination + truncation (MCP surface only)**: list actions accept optional `limit`/`offset` (and `state`/`name` filters where relevant) and return a `{items, total, limit, offset, has_more, next_offset}` envelope. MCP responses are truncated at ~40 KB. Neither pagination nor the truncation cap is exposed through the CLI.
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

Most data actions exist on both surfaces, but the two are **not** a perfect mirror —
there are known, intentional gaps:

- **`status`** is **MCP-only** — it is an observability action with no CLI command.
- **`doctor`** and **`setup`** (incl. `setup install` / `setup plugin-hook`) are
  **CLI-only** — they are not exposed as MCP actions.
- **Pagination/filtering** (`limit`/`offset`/`state`/`name`) and the **~40 KB
  response truncation** are part of the **MCP surface only**; the CLI does not take
  these params.

The `help` MCP action maps to `runraid --help`.

| Service Method | MCP Action | CLI Command |
|---|---|---|
| `service.array()` | `unraid(action="array")` | `runraid array` |
| `service.disks()` | `unraid(action="disks")` | `runraid disks` |
| `service.docker()` | `unraid(action="docker")` | `runraid docker` |
| `service.docker_logs(id, tail)` | `unraid(action="docker_logs", id=…, tail=…)` | `runraid docker logs <id> [--tail N]` |
| `service.vms()` | `unraid(action="vms")` | `runraid vms` |
| `service.server()` | `unraid(action="server")` | `runraid server` |
| `service.info()` | `unraid(action="info")` | `runraid info` |
| `service.shares()` | `unraid(action="shares")` | `runraid shares` |
| `service.notifications()` | `unraid(action="notifications")` | `runraid notifications` |
| `service.log_files()` | `unraid(action="log_files")` | `runraid log-files` |
| `service.log_file(path, lines, start_line)` | `unraid(action="log_file", path=…, lines=…, start_line=…)` | `runraid log <path> [--lines N] [--start-line N]` |
| `service.services()` | `unraid(action="services")` | `runraid services` |
| `service.network()` | `unraid(action="network")` | `runraid network` |
| `service.ups()` | `unraid(action="ups")` | `runraid ups` |
| `service.ups_config()` | `unraid(action="ups_config")` | `runraid ups-config` |
| `service.metrics()` | `unraid(action="metrics")` | `runraid metrics` |
| `service.plugins()` | `unraid(action="plugins")` | `runraid plugins` |
| `service.parity_history()` | `unraid(action="parity_history")` | `runraid parity-history` |
| `service.vars()` | `unraid(action="vars")` | `runraid vars` |
| `service.registration()` | `unraid(action="registration")` | `runraid registration` |
| `service.flash()` | `unraid(action="flash")` | `runraid flash` |
| `service.rclone()` | `unraid(action="rclone")` | `runraid rclone` |
| `service.remote_access()` | `unraid(action="remote_access")` | `runraid remote-access` |
| `service.connect()` | `unraid(action="connect")` | `runraid connect` |
| `service.status()` | `unraid(action="status")` | _(MCP-only — no CLI command)_ |
| _(meta)_ | `unraid(action="help")` | `runraid --help` |
| _(CLI-only)_ | _(no MCP action)_ | `runraid doctor` |
| _(CLI-only)_ | _(no MCP action)_ | `runraid setup [install\|plugin-hook]` |

## Build commands

```bash
cargo build --release     # produces target/release/runraid
just dev                  # cargo run -- serve mcp
just test                 # cargo test
just lint                 # cargo clippy -- -D warnings
just fmt                  # cargo fmt
just gen-token            # openssl rand -hex 32
```


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
