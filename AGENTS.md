# AGENTS.md — unraid-mcp

Agent instructions for this repository.

## What this project is

`unraid-mcp` is a Rust MCP server that provides read-only access to an Unraid server via its GraphQL API. The binary is named `unraid`. It exposes 24 actions through a single `unraid` MCP tool and an equivalent CLI. There is no local database, no background tasks, no syslog ingestion — just a GraphQL client wrapped in MCP and CLI interfaces.

## Build and verify

```bash
cargo build              # debug build
cargo build --release    # produces target/release/unraid
cargo check              # type-check without building
cargo clippy -- -D warnings  # lint (must be clean before committing)
cargo fmt                # format (enforced by CI)
cargo test               # run all tests
```

Justfile shortcuts:
```bash
just dev      # cargo run -- serve mcp
just test     # cargo test
just lint     # cargo clippy -- -D warnings
just fmt      # cargo fmt
just build    # cargo build
just release  # cargo build --release
just gen-token  # openssl rand -hex 32
```

## Required environment variables

Two env vars are required; without them the binary exits on startup:

```
UNRAID_API_URL   — Unraid GraphQL endpoint (e.g. https://10-1-0-2.<hash>.myunraid.net:31337/graphql)
UNRAID_API_KEY   — API key for the x-api-key header
```

Set `UNRAID_API_SKIP_TLS_VERIFY=true` if the Unraid API uses a self-signed certificate.

For development without a real Unraid server, tests stub the client — see `src/lib.rs` `testing` module.

## Module map

```
src/
  main.rs           — Mode dispatch: serve_mcp | serve_stdio_mcp | run_cli
  config.rs         — Config structs + env loading (TOML + env vars)
  graphql.rs        — UnraidClient: HTTP POST to GraphQL API, one method per query
  app.rs            — UnraidService: delegates to UnraidClient, one method per action
  lib.rs            — Public exports; testing:: helpers
  cli.rs            — CLI arg parsing + human-readable formatters
  mcp.rs            — AppState, AuthPolicy, build_auth_layer
  mcp/
    tools.rs        — execute_tool: match action → service call
    schemas.rs      — UNRAID_ACTIONS list + JSON Schema for the unraid tool
    rmcp_server.rs  — ServerHandler impl: list_tools, call_tool, resources, prompts
    routes.rs       — Axum router: /mcp, /health, OAuth discovery
    prompts.rs      — server_summary prompt
```

## How to add a new action

1. `src/graphql.rs` — add `pub async fn your_action(&self) -> Result<Value>` that calls `self.query(r#"query { ... }"#).await`

2. `src/app.rs` — add `pub async fn your_action(&self) -> Result<Value> { self.client.your_action().await }`

3. `src/mcp/schemas.rs` — add `"your_action"` to the `UNRAID_ACTIONS` const slice

4. `src/mcp/tools.rs` — add `"your_action" => state.service.your_action().await,` to the match. Update `HELP_TEXT`.

5. `src/cli.rs` — add `YourAction` to `CliCommand`, parse arm in `CliCommand::parse`, dispatch arm in `run`, formatter `fmt_your_action`

If the action requires parameters, follow the `docker_logs` pattern: add fields to the `CliCommand` variant, extract with `string_arg`/`i64_arg` in `tools.rs`, and add flag parsing with `flag_i64` in `cli.rs`.

## Auth model

`AuthPolicy` is an enum:
- `LoopbackDev` — no auth; selected when `no_auth=true` or host starts with `127.`
- `Mounted { auth_state: None }` — static bearer token via `UNRAID_MCP_TOKEN`
- `Mounted { auth_state: Some(_) }` — OAuth (Google) via lab-auth

Scopes required for tool execution:
- `unraid:read` — all 24 data actions
- `unraid:admin` — satisfies `unraid:read`
- No scope — `help` action

`/health` is always unauthenticated.

## Key gotchas

- **BigInt fields** from the GraphQL API arrive as JSON strings. `bigint_f64()` in `cli.rs` handles this. Memory size fields in `metrics` use this pattern.
- **`flash.guid`** is non-nullable in the Unraid schema but null at runtime. The GraphQL query omits it.
- **Default port**: `config.rs` built-in is 3100; `config.toml` overrides to 6970. Document 6970 as the project port.
- **Logging goes to stderr**, not stdout — stdout is reserved for the stdio MCP transport.
- **No write operations** exist. Do not add any — this is a read-only monitoring tool.
- **Tests do not need a real Unraid server.** The `testing::loopback_state()` helper provides a stub service.

## Test files (summary)

| File | What it covers |
|------|----------------|
| `tests/auth_modes.rs` | Auth middleware across all three `AuthPolicy` variants |
| `tests/cli_help.rs` | `--help` and `--version` flags |
| `tests/oauth_flow.rs` | RS256 JWT validation, scope checks, expired/wrong-issuer tokens |
| `tests/rmcp_compat.rs` | RMCP transport negotiation (JSON vs SSE) |
| `tests/stdio_mcp.rs` | stdio child-process MCP: `tools/list` + `tools/call` |
| `tests/spike_rmcp_extensions.rs` | Axum extension propagation into tool handlers |

`tests/test_live.sh`, `tests/TEST_COVERAGE.md`, and `tests/mcporter/test-tools.sh` are stale syslog-mcp artifacts — ignore them.

## Stale files (do not use as reference)

The following files were not fully updated during the unraid-mcp conversion and still contain incorrect content:

- `docker-compose.yml` — still uses syslog-mcp image, container name, and syslog ports
- `config/Dockerfile` — may reference syslog binary name and ports
- `config/mcporter.json` — points to syslog-mcp on port 3100
- `deploy/` — syslog-specific rsyslog configs and AppArmor profile
- `Justfile` — some targets reference syslog binary name (`syslog-mcp`)
- `tests/test_live.sh` — syslog-mcp shell integration test
- `tests/TEST_COVERAGE.md` — syslog-mcp test documentation
- `tests/mcporter/test-tools.sh` — syslog-mcp tool test script

When working on this codebase, treat `src/` as the source of truth.

## HTTP endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/mcp` | POST | yes (when configured) | RMCP Streamable HTTP |
| `/health` | GET | no | Returns `{"status":"ok"}` |
| `/*` | any | — | 404 with `{"error":"not_found"}` |

## Version bumping

When bumping the version, update `Cargo.toml` version field and add a `CHANGELOG.md` entry. Run `cargo check` after to confirm `Cargo.lock` is updated.

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

## Plugin setup hooks

Plugin setup is owned by the binary. Keep `plugins/unraid/hooks/plugin-setup.sh` as a thin adapter that maps `CLAUDE_PLUGIN_OPTION_*` values to environment variables, prepares appdata, ensures `unraid` is on `PATH`, and then calls `unraid setup plugin-hook "$@"`.

`unraid setup check` is read-only, `unraid setup repair` is idempotent, and `unraid setup plugin-hook --no-repair` is audit mode. Do not add Docker Compose, systemd, or service bootstrap logic back into the hook script.
