---
type: "Reference"
title: "GraphQL API Integration"
openwiki_generated: true
---

# GraphQL API Integration

How unrust connects to the Unraid GraphQL API, including typed operations, schema management, and drift detection.

## GraphQL client

The `UnraidClient` in `src/graphql.rs` is the HTTP client for the Unraid GraphQL API.

### Connection details

**Endpoint:** `UNRAID_API_URL` environment variable
- Example: `https://10-1-0-2.<hash>.myunraid.net:31337/graphql`

**Authentication:** `x-api-key` header
- Value from `UNRAID_API_KEY` environment variable

**TLS verification:** Controlled by `UNRAID_API_SKIP_TLS_VERIFY`
- Default: `false` (verify certificates)
- Set to `true` for self-signed certificates

### Request flow

```rust
// Example: server() action
pub async fn server(&self) -> Result<Value> {
    self.run_typed(ServerQuery).await
}

// Generic typed operation runner
fn run_typed<T>(&self, op: T) -> Result<Value>
    where T: cynic::Operation + Serialize
{
    let response = self.send_graphql(
        op.build_query().serialize(),
        op.get_variable_definitions()
    ).await?;
    op.parse_response(response)
        .map(|data| serde_json::to_value(data).unwrap())
        .map_err(|e| e.into())
}
```

**Key points:**
- Query arguments are passed as **variables**, not interpolated (prevents GraphQL injection)
- Response is deserialized via cynic's typed parser
- Typed response is serialized back to `Value` for compatibility with MCP/CLI layers

### HTTP client configuration

- Uses `reqwest` 0.12 with `rustls-tls`
- Timeout: configured at client construction
- User agent: set via `reqwest::Client::builder()`

## Typed operations (cynic)

The project uses **cynic** for compile-time query type checking.

### How it works

1. **Schema registration** (`build.rs`)
   ```rust
   cynic_codegen::register_schema("unraid")
       .from_sdl_file("schema/unraid-schema.graphql")
       .expect("vendored Unraid SDL should parse")
       .as_default()
       .expect("registering default cynic schema should succeed");
   ```

2. **Operation definitions** (`src/gql_typed.rs`)
   ```rust
   #[derive(cynic::QueryFragment, Serialize)]
   #[cynic(graphql_type = "Query")]
   pub struct ServerQuery {
       pub server: ServerData,
   }

   #[derive(cynic::QueryFragment, Serialize)]
   pub struct ServerData {
       pub name: String,
       pub status: String,
       pub lanip: String,
       // ... more fields
   }
   ```

3. **Compile-time validation**
   - cynic checks each `QueryFragment` against the vendored SDL
   - Invalid queries (wrong fields, wrong args, wrong types) fail to compile
   - Example error: `field 'nonExistentField' does not exist on type 'Server'`

4. **Runtime execution**
   - `run_typed()` builds the query, sends it, and parses the response
   - cynic's derives generate `Deserialize` impls for response parsing
   - We add `Serialize` to structs for the round-trip back to `Value`

### Type quirks and gotchas

The Unraid SDL has some patterns that require special handling:

| Issue | Pattern | Solution |
|-------|---------|----------|
| `ID!` type | Non-null ID | Use `cynic::Id` (not `String`) |
| `BigInt` | Large integers | String scalar |
| Field name collision | `type`, `virtual` keywords | Use `r#type` + `#[cynic(rename = "...")]` |
| Argument name collision | `type:` argument | Cannot express — omit operation |
| Enum case mismatch | `UPSServiceState` vs naming | `#[cynic(graphql_type = "UPSServiceState")]` |
| Lowercase enum values | `ThemeName` enum values | `#[cynic(rename_all = "UPPERCASE")]` |
| Double-underscored values | `CONNECT__REMOTE_ACCESS` | `#[cynic(rename = "CONNECT__REMOTE_ACCESS")]` |
| Namespaced mutations | `mutation { vm { start } }` | Pair `Mutation`-root + `VmMutations`-namespace structs |

See `src/gql_typed.rs` for examples of each pattern.

### Why typed at the wire but Value downstream?

**Compile-time safety** without changing the rest of the stack:
- cynic validates queries against the schema at compile time
- The transport layer (`send_graphql`) stays on reqwest 0.12
- Dispatch, formatters, and MCP layers continue to work with `Value`
- No need to rewrite the entire stack with new types

## Schema management

### Vendored SDL

The Unraid GraphQL schema is vendored at `schema/unraid-schema.graphql`.

**Provenance header:**
```graphql
# ─────────────────────────────────────────────────────────────────────────────
# Vendored Unraid GraphQL schema (SDL) — used ONLY by tests/dev tooling.
#
# Source : github.com/unraid/api  → api/generated-schema.graphql
# Commit : 8194972b (2026-06-15)
# Method : copied from a local clone of unraid/api
# ...
```

**Purpose:**
- Compile-time type checking via cynic
- Schema-as-contract validation in tests (`tests/schema_contract.rs`)
- Drift detection via CI

### Schema drift detection

A CI job (`.github/workflows/schema-drift.yml`) runs daily to detect drift:

1. Fetch upstream SDL from `unraid/api@main`
2. Compare with vendored copy (stripping provenance header)
3. If different:
   - Open/update GitHub issue with diff
   - Label with `schema-drift`

**Response to drift:**
1. Re-vendor the schema (copy from fresh `unraid/api` clone)
2. Re-add provenance header
3. Run schema-contract test to identify broken queries/fixtures
4. Update queries and fixtures as needed

### Schema-as-contract test

`tests/schema_contract.rs` validates:
- Every query in `src/graphql.rs` against the vendored SDL
- Every mock fixture against the vendored SDL
- Field types, argument types, and non-null constraints

**Run:** `cargo test schema_contract`

This test ensures the vendored schema accurately represents what the code expects.

## Offline mock server

For development and testing, `src/mock.rs` provides a scenario-driven mock:

**`examples/mock_unraid.rs`** (requires `--features test-support`)
- Runs a local HTTP server on `localhost:4000`
- Responds to GraphQL queries based on the query's root field
- Routes to scenario fixtures in `tests/fixtures/scenarios/`

**Scenarios available:**
- `healthy.json` - Normal server state
- `degraded.json` - Degraded state (warnings, issues)
- `disk-failing.json` - Disk failure scenario
- `parity-running.json` - Active parity check

**Usage:**
```bash
cargo run --example mock_unraid --features test-support
export UNRAID_API_URL="http://localhost:4000"
runraid serve mcp
```

## GraphQL injection prevention

**Historically:** Queries interpolated arguments into the query string.

**Fix (commit 5b1a447):** All queries now use GraphQL variables.

```rust
// Before (vulnerable)
let query = format!(
    "{{ dockerLogs(id: \"{}\", tail: {}) {{ ... }} }}",
    id, tail
);

// After (safe)
let query = r#"
    query DockerLogs($id: ID!, $tail: Int) {
        dockerLogs(id: $id, tail: $tail) { ... }
    }
"#;
let variables = json!({ "id": id, "tail": tail });
self.send_graphql(query, variables).await
```

## Source references

- GraphQL client: `src/graphql.rs`
- Typed operations: `src/gql_typed.rs`
- Schema registration: `build.rs`
- Vendored SDL: `schema/unraid-schema.graphql`
- Mock server: `src/mock.rs`
- Schema contract test: `tests/schema_contract.rs`
- Drift detection: `.github/workflows/schema-drift.yml`
