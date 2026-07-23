# Tests — unraid-rmcp

## Overview

The test suite is Rust integration tests under `tests/`. It does not require a
real Unraid server. Most protocol and middleware tests use a stub service;
scenario and schema-contract tests mount the repository's scenario-driven
GraphQL mock and drive the real Rust dispatch and typed serialization paths.

The mock action suite is intentionally the full GraphQL surface:

- every registered read action runs against every mock scenario;
- every registered mutation runs against every mock scenario;
- mutations affect only canned mock responses and never contact production;
- every generated query/mutation and fixture is validated against the vendored
  Unraid SDL.

Run all tests:
```bash
cargo test
# or
just test
```

## Test files

### `tests/auth_modes.rs`

Tests the auth middleware in all three `AuthPolicy` modes.

**Coverage:**
- `well_known_returns_200_when_oauth_mounted` — OAuth discovery endpoint is reachable only in OAuth mode
- `well_known_returns_404_when_bearer_only` — discovery is absent in bearer-only mode
- `well_known_returns_404_when_loopback_dev` — discovery is absent in loopback dev mode
- `jwks_returns_200_when_oauth_mounted` — JWKS endpoint available in OAuth mode
- `health_returns_200_in_all_modes` — `/health` is always unauthenticated
- `mcp_without_credentials_returns_401_when_mounted` — `/mcp` requires auth when `AuthPolicy::Mounted`
- `mcp_without_credentials_succeeds_when_loopback_dev` — `/mcp` is open in loopback dev mode
- `tools_list_succeeds_with_auth_context` — valid auth context reaches tool listing
- `protected_resource_returns_200_when_oauth_mounted` — protected resource metadata available in OAuth mode
- `well_known_response_body_has_required_fields` — OAuth metadata body shape validation
- `jwks_response_body_has_keys_array` — JWKS response contains `keys` array

---

### `tests/cli_help.rs`

Tests `--help` and `--version` flags.

**Coverage:**
- `--help` / `-h` / `help` — prints usage text without error
- `--version` / `-V` / `version` — prints version string containing `unraid-rmcp`

---

### `tests/oauth_flow.rs`

Tests JWT-level OAuth authentication using real RS256 keys generated in a temp directory. No Google credentials needed.

**Coverage:**
- `valid_jwt_with_read_scope_allows_stats` — `unraid:read` scope accepts `tools/call`
- `valid_jwt_with_admin_scope_satisfies_read` — `unraid:admin` satisfies `unraid:read` requirement
- `expired_jwt_returns_401` — expired JWT (`exp` in the past) is rejected
- `jwt_with_wrong_issuer_returns_401` — JWT with wrong `iss` claim is rejected
- `jwt_with_empty_scope_is_denied_at_scope_check` — JWT is valid but action is denied at scope check
- Additional tests for invalid signature, missing claims

---

### `tests/rmcp_compat.rs`

Tests RMCP transport negotiation.

**Coverage:**
- `rmcp_stateless_json_response_returns_application_json` — `Accept: application/json` returns `Content-Type: application/json`
- `rmcp_stateless_sse_mode_is_distinct_from_json_response_target` — SSE accept header handled
- `rmcp_stateful_mode_keeps_sse_even_when_json_response_is_enabled` — stateful mode SSE behaviour

---

### `tests/stdio_mcp.rs`

Tests the stdio child-process transport end-to-end.

**Coverage:**
- `stdio_child_process_lists_tools_and_calls_queries` — spawns `unraid mcp` as a child process, sends `tools/list`, verifies the `unraid` tool is present, sends `tools/call` with `action=help`, verifies response

---

### `tests/spike_rmcp_extensions.rs`

Tests that Axum HTTP extensions (used for auth context propagation) are correctly available inside tool handlers in both stateless and stateful RMCP modes.

**Coverage:**
- `axum_extension_propagates_into_tool_handler_stateless` — custom extension injected by middleware is readable from tool handler in stateless mode
- `axum_extension_propagates_into_tool_handler_stateful` — same in stateful mode

---

### `tests/scenarios.rs`

Mounts each scenario (`healthy`, `degraded`, `parity-running`, and
`disk-failing`) as an HTTP GraphQL mock, then runs every canonical read and
write action through the real MCP dispatch. The test is named
`every_read_and_write_action_dispatches_in_every_mock_scenario` so the coverage
boundary is explicit.

### `tests/schema_contract.rs`

Captures every generated query and mutation, validates each operation against
`schema/unraid-schema.graphql`, and checks every scenario fixture's selected
response fields and scalar/enum values against that operation.

### `tests/live_schema_contract.rs`

Compares the vendored SDL structurally with
`schema/live-introspection.json`, a normalized snapshot captured from the
production Unraid API. Refresh or check the live snapshot with
`just schema-live-capture` and `just schema-live-diff`; both commands require
`UNRAID_API_URL` and `UNRAID_API_KEY`. The daily schema-drift workflow also
runs this check against the upstream configured in the production `runraid`
container.

---

### `tests/test_live.sh`

Shell integration test. **This file is stale** — it references syslog-mcp actions (`syslog search`, `syslog tail`, etc.) and is not applicable to unraid-rmcp.

### `tests/TEST_COVERAGE.md`

**Stale** — documents the syslog-mcp test suite. Does not apply to unraid-rmcp.

### `tests/mcporter/test-tools.sh`

**Stale** — syslog-mcp tool test script.

## Test helpers

`src/lib.rs` exposes a `testing` module (gated on `feature = "test-support"`) with:

- `testing::loopback_state()` — `AppState` with `AuthPolicy::LoopbackDev` and a stub service
- `testing::bearer_state(token)` — `AppState` with static bearer token
- `testing::oauth_state(data_dir)` — `AppState` with full OAuth stack (real RS256 key, temp SQLite)
- `testing::build_auth_state(data_dir)` — lower-level `AuthState` builder for custom test setups

Stub-only tests point at `http://localhost:1/graphql` with a dummy API key.
Scenario and schema-contract tests instead use an ephemeral wiremock HTTP server
backed by `tests/fixtures/scenarios/*.json`.
