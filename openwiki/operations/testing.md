# Testing

Test suite organization, running tests, and testing guidance for development.

## Test philosophy

**Integration tests, no live server.** Tests under `tests/` exercise routing, auth middleware, protocol framing, and CLI output without calling a real Unraid GraphQL API.

**Stub service.** Tests use `UnraidService` instances pointing at `http://localhost:1/graphql`, so GraphQL calls are never made.

**Scenario fixtures.** Pre-canned JSON responses in `tests/fixtures/scenarios/` represent various server states (healthy, degraded, disk-failing, etc.).

## Running tests

### All tests

```bash
cargo test
# or
just test
```

### Specific test file

```bash
cargo test tests::auth_modes
cargo test tests::oauth_flow
cargo test tests::dispatch
```

### With output

```bash
cargo test -- --nocapture
```

### Nextest (faster test runner)

```bash
cargo nextest run --all
# or
just test
```

## Test files

### `tests/auth_modes.rs`

Tests the auth middleware in all three `AuthPolicy` modes.

**Coverage:**
- OAuth discovery endpoint (`/.well-known/*`) reachable only in OAuth mode
- JWKS endpoint available only in OAuth mode
- `/health` always unauthenticated
- `/mcp` requires auth when `AuthPolicy::Mounted`
- `/mcp` open in `LoopbackDev` mode
- OAuth metadata body shape validation

**Key patterns:**
```rust
#[tokio::test]
async fn mcp_without_credentials_returns_401_when_mounted() {
    let state = testing::bearer_state("test-token");
    // Test fails without Authorization header
}
```

### `tests/cli_help.rs`

Tests CLI `--help` and `--version` flags.

**Coverage:**
- `--help` / `-h` / `help` prints usage
- `--version` / `-V` / `version` prints version string

### `tests/oauth_flow.rs`

Tests JWT-level OAuth authentication using real RS256 keys generated in a temp directory. No Google credentials needed.

**Coverage:**
- Valid JWT with `unraid:read` scope allows queries
- `unraid:admin` satisfies `unraid:read` requirement
- Expired JWT rejected (`exp` in past)
- JWT with wrong `iss` claim rejected
- JWT with empty scope denied at scope check
- Invalid signature rejected
- Missing claims rejected

**Key patterns:**
```rust
#[tokio::test]
async fn valid_jwt_with_read_scope_allows_stats() {
    let data_dir = tempfile::tempdir().unwrap();
    let token = generate_jwt(
        &data_dir,
        &["unraid:read"],
        chrono::Utc::now() + chrono::Duration::hours(1),
    );
    // Call with Authorization: Bearer <token>
}
```

### `tests/rmcp_compat.rs`

Tests RMCP transport negotiation.

**Coverage:**
- `Accept: application/json` returns `Content-Type: application/json`
- SSE accept header handled
- Stateful mode SSE behavior

### `tests/stdio_mcp.rs`

Tests the stdio child-process transport end-to-end.

**Coverage:**
- Spawn `runraid mcp` as child process
- Send `tools/list`, verify `unraid` tool present
- Send `tools/call` with `action=help`, verify response

### `tests/spike_rmcp_extensions.rs`

Tests Axum HTTP extensions propagation into tool handlers.

**Coverage:**
- Custom extension injected by middleware is readable in tool handler (stateless mode)
- Same in stateful mode

### `tests/dispatch.rs`

Tests action routing through the MCP layer.

**Coverage:**
- Valid action calls correct service method
- Invalid action returns error
- Pagination envelope structure

### `tests/paginate.rs`

Tests pagination on list actions.

**Coverage:**
- `limit` and `offset` parameters
- `has_more` and `next_offset` calculation
- Total count accuracy

### `tests/host_filter.rs`

Tests Host header validation middleware.

**Coverage:**
- Allowed hosts pass
- Disallowed hosts rejected
- Loopback bypass behavior

### `tests/upstream.rs`

Tests GraphQL client behavior at the HTTP layer.

**Coverage:**
- Query formatting and variable interpolation
- Error handling (HTTP errors, GraphQL errors)
- TLS verification behavior

### `tests/scenarios.rs`

Tests mock server scenarios.

**Coverage:**
- Mock returns correct fixture for each query type
- Scenario fixtures (healthy, degraded, disk-failing, parity-running)

### `tests/schema_contract.rs`

**Schema-as-contract test.** Validates:
- Every query in `src/graphql.rs` against the vendored SDL
- Every mock fixture against the vendored SDL
- Field types, argument types, and non-null constraints

**Run:** `cargo test schema_contract`

**Failure means:** Schema has drifted or queries are malformed.

### `tests/setup_contract.rs`

Tests plugin setup contract.

### `tests/real_binary.rs`

Tests the release binary for expected behavior.

## Test utilities

### `src/lib.rs::testing` module

Helper functions for building test state:

```rust
pub fn loopback_state() -> AppState
pub fn bearer_state(token: &str) -> AppState
pub fn oauth_state(data_dir: &Path) -> AppState
pub fn stub_service() -> UnraidService
```

**Usage:**
```rust
use unraid_rmcp::testing;

let state = testing::loopback_state();
// Use in Axum test request
```

### `src/mock.rs` (test-support feature)

Scenario-driven offline mock of the Unraid GraphQL API.

**`classify_query()`** - Routes query by root field to scenario fixture.

**Example:**
```rust
let fixture = classify_query(r#"{ server { name } }"#)
    .unwrap()
    .load_from_scenario("healthy");
// Returns JSON fixture for server query
```

### `examples/mock_unraid.rs`

Standalone mock server for development.

**Run:**
```bash
cargo run --example mock_unraid --features test-support
```

**Use:**
```bash
export UNRAID_API_URL="http://localhost:4000"
runraid serve mcp
# Server calls hit the mock instead of real Unraid
```

## Fixtures

### Scenario fixtures

**Location:** `tests/fixtures/scenarios/`

**Files:**
- `healthy.json` - Normal server state
- `degraded.json` - Warnings, issues present
- `disk-failing.json` - Disk failure scenario
- `parity-running.json` - Active parity check

**Usage in tests:**
```rust
let response = reqwest::get(mock_url).await.unwrap();
assert_eq!(response.json::<Value>().unwrap(),
    serde_json::from_str(include_str!("fixtures/scenarios/healthy.json")).unwrap()
);
```

## Coverage goals

**Current coverage areas:**
- Auth middleware (all modes)
- OAuth JWT validation
- MCP protocol framing
- Action dispatch
- CLI argument parsing
- Pagination logic
- Host header validation
- Schema contract validation

**Not covered (requires live server):**
- Real Unraid API integration
- Actual network behavior
- Performance benchmarks

## CI test suite

**`.github/workflows/ci.yml`:**

Jobs:
- `fmt` - Format check (`cargo fmt -- --check`)
- `clippy` - Lint check (`cargo clippy --all-targets --features test-support`)
- `test` - Full test suite (`cargo nextest run --profile ci`)
- `check-toml` - TOML format check
- `audit` - Security audit (rustsec)
- `gitleaks` - Secret leak detection

**Run CI locally:**
```bash
just fmt    # cargo fmt -- --check
just clippy # cargo clippy --all-targets --features test-support -- -D warnings
just test   # cargo nextest run --profile ci
```

## Writing tests

### Test template

```rust
use unraid_rmcp::testing;
use axum::body::Body;
use http::{Request, StatusCode};
use tower::ServiceExt;

#[tokio::test]
async fn your_test_name() {
    // Arrange: build test state
    let state = testing::loopback_state();

    // Act: make request
    let app = unraid_rmcp::mcp::routes::router(state);
    let response = app
        .oneshot(
            Request::builder()
                .uri("/mcp")
                .body(Body::empty())
                .unwrap()
        )
        .await
        .unwrap();

    // Assert: check response
    assert_eq!(response.status(), StatusCode::OK);
}
```

### Testing auth

```rust
#[tokio::test]
async fn test_requires_auth() {
    let state = testing::bearer_state("test-token");

    // Without Authorization header
    let app = unraid_rmcp::mcp::routes::router(state);
    let response = app
        .oneshot(Request::post("/mcp").body(Body::empty()).unwrap())
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}
```

### Testing action dispatch

```rust
use unraid_rmcp::mcp::tools;
use serde_json::json;

#[tokio::test]
async fn test_server_action() {
    let state = testing::loopback_state();
    let args = json!({"action": "server"});

    let result = tools::dispatch_action(&state, args).await;

    assert!(result.is_ok());
    let value = result.unwrap();
    assert!(value.get("server").is_some());
}
```

## Performance testing

**Not currently in the test suite.** For load testing, use:

```bash
# Install hey
go install github.com/rakyll/hey@latest

# Load test /health endpoint
hey -n 1000 -c 10 http://localhost:40010/health

# Load test /mcp with proper JSON body
hey -n 100 -c 5 \
  -m POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"unraid","arguments":{"action":"server"}}}' \
  http://localhost:40010/mcp
```

## Source references

- Test suite: `tests/`
- Testing helpers: `src/lib.rs::testing`
- Mock server: `src/mock.rs`, `examples/mock_unraid.rs`
- Fixtures: `tests/fixtures/scenarios/`
- Schema contract: `tests/schema_contract.rs`
- CI config: `.github/workflows/ci.yml`
