# Development Workflow

How to contribute to unrust, including adding actions, code style, and the release process.

## Development setup

### Prerequisites

- Rust 1.90+ (MSRV defined in `Cargo.toml`)
- Just (command runner): `cargo install just`
- Docker (optional, for container testing)

### Clone and build

```bash
git clone https://github.com/jmagar/runraid
cd unrust
cargo build
```

### Run in development

```bash
# HTTP MCP server (auto-reload)
cargo run -- serve mcp

# CLI
cargo run -- server

# stdio MCP
cargo run -- mcp
```

### Development tools

**Just commands:**
```bash
just test      # Run tests
just fmt       # Format code
just clippy    # Run linter
just build     # Build release
just docker-build  # Build Docker image
just docker-run    # Run container
just shell     # Shell into container
```

## Code style

### Formatting

**Formatter:** `rustfmt` (standard Rust formatter)

**Check:** `cargo fmt -- --check` (fails if not formatted)

**Apply:** `cargo fmt`

**CI gate:** Fails CI if code is not formatted

### Linting

**Linter:** `clippy` (Rust linting tool)

**Check:** `cargo clippy --all-targets --features test-support -- -D warnings`

**Warnings as errors:** CI treats any clippy warning as an error

**Common patterns:**
- Avoid `unwrap()` in production code (use `?` or `expect()` with context)
- Prefer `map()`, `and_then()`, `filter()` over manual `match`
- Use ` anyhow::Context` for error chain with context

### Naming conventions

- **Modules:** `snake_case` (`src/graphql_client.rs`, `src/mcp/mod.rs`)
- **Types:** `PascalCase` (`UnraidService`, `McpConfig`)
- **Functions:** `snake_case` (`dispatch_action`, `build_auth_layer`)
- **Constants:** `SCREAMING_SNAKE_CASE` (`ACTIONS`, `VALID_ACTIONS`)
- **Enums:** `PascalCase` variants (`AuthMode::Bearer`, `Scope::Read`)

### Error handling

**Use `anyhow::Result` for application errors:**
```rust
use anyhow::Result;

pub async fn server(&self) -> Result<Value> {
    let response = self.send_graphql(...).await?;
    Ok(response)
}
```

**Use `thiserror` for library errors:**
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Missing required env var: {0}")]
    MissingVar(String),
}
```

**Context on errors:**
```rust
let response = self.client.post(&self.api_url)
    .await
    .context("Failed to POST to Unraid API")?;
```

## Adding a new action

Follow this sequence to add a new action across all layers.

### 1. Add cynic operation (`src/gql_typed.rs`)

Define the GraphQL operation as a typed cynic struct:

```rust
#[derive(cynic::QueryFragment, Serialize)]
#[cynic(graphql_type = "Query")]
pub struct YourActionQuery {
    pub your_action: YourActionData,
}

#[derive(cynic::QueryFragment, Serialize)]
pub struct YourActionData {
    pub field1: String,
    pub field2: i32,
    // ... more fields
}
```

**Check compile errors:** cynic validates against the vendored SDL. If the field doesn't exist or has the wrong type, compilation fails.

### 2. Add client method (`src/graphql.rs`)

Add a method to `UnraidClient` that runs the typed operation:

```rust
impl UnraidClient {
    pub async fn your_action(&self) -> Result<Value> {
        self.run_typed(YourActionQuery).await
    }
}
```

### 3. Add service method (`src/app.rs`)

Add a pass-through method to `UnraidService`:

```rust
impl UnraidService {
    pub async fn your_action(&self) -> Result<Value> {
        self.client.your_action().await
    }
}
```

### 4. Register action (`src/mcp/schemas.rs`)

Add **one entry** to the `ACTIONS` slice:

```rust
pub static ACTIONS: &[ActionSpec] = &[
    // ... existing actions
    ActionSpec {
        name: "your_action",
        scope: Scope::Read,  // or Scope::Write for mutations
        description: "Your action description",
    },
];
```

**This single entry:**
- Adds to the MCP schema enum (`UNRAID_ACTIONS`)
- Adds to the error-message action list (`VALID_ACTIONS`)
- Defines scope requirements (`required_scope_for`)

### 5. Add dispatch arm (`src/mcp/tools.rs`)

Add the match arm in `dispatch_action()`:

```rust
pub async fn dispatch_action(state: &AppState, args: Value) -> Result<Value> {
    let action = args.get("action").and_then(|v| v.as_str()).unwrap_or("");

    match action {
        // ... existing actions
        "your_action" => state.service.your_action().await,
        _ => Err(...),
    }
}
```

**Add to HELP_TEXT:**
```rust
const HELP_TEXT: &str = r#"
...
### Your Action

Description here.
"#;
```

### 6. Add CLI support (`src/cli/`)

**`src/cli/commands.rs`:**
```rust
pub enum CliCommand {
    // ... existing commands
    YourAction,
}
```

**`src/cli/parse.rs`:**
```rust
pub fn parse_args(args: &[String]) -> Result<CliCommand> {
    match args.first().map(|s| s.as_str()) {
        // ... existing commands
        Some("your-action") => Ok(CliCommand::YourAction),
        // ...
    }
}
```

**`src/cli/dispatch.rs`:**
```rust
pub async fn dispatch(cmd: CliCommand, service: &UnraidService) -> Result<String> {
    match cmd {
        // ... existing commands
        CliCommand::YourAction => {
            let data = service.your_action().await?;
            Ok(fmt_your_action(data))
        }
    }
}
```

**`src/cli/format.rs`:**
```rust
pub fn fmt_your_action(value: Value) -> String {
    // Format value for terminal output
    todo!()
}
```

### 7. Add fixture (`tests/fixtures/scenarios/healthy.json`)

Add the response fixture for the mock server:

```json
{
  "data": {
    "yourAction": {
      "field1": "value1",
      "field2": 123
    }
  }
}
```

### 8. Update tests (automatic)

**Mock router:** `classify_query()` in `src/mock.rs` automatically routes the new query if it follows naming conventions.

**Test lists:** `upstream_action_calls()` and `mutation_action_calls()` in `tests/schema_contract.rs` are derived from `ACTIONS`, so they automatically include the new action.

**Schema contract test:** Validates the new query against the vendored SDL. If the query is malformed, `cargo test schema_contract` fails.

## Adding pagination to an action

For list actions, add pagination support in the MCP layer:

### 1. Update cynic operation

Add arguments to the query:

```rust
#[derive(cynic::QueryFragment, Serialize)]
pub struct YourListQuery {
    #[arguments(limit: $limit, offset: $offset)]
    pub your_list: Vec<YourItem>,
}
```

### 2. Update client method

Accept parameters:

```rust
pub async fn your_list(&self, limit: u32, offset: u32) -> Result<Value> {
    let query = YourListQuery::build(vars! { limit, offset });
    self.run_typed(query).await
}
```

### 3. Add pagination in tools.rs

Wrap in envelope:

```rust
"your_list" => {
    let limit = args.get("limit").and_then(|v| v.as_u64()).unwrap_or(50) as u32;
    let offset = args.get("offset").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
    let items = state.service.your_list(limit, offset).await?;
    let total = items.as_array().unwrap().len() as u64;
    let has_more = (offset + limit as u32) < total as u32;
    let next_offset = if has_more { Some(offset + limit as u32) } else { None };
    
    json!({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
        "next_offset": next_offset
    })
}
```

## Vendoring schema updates

When Unraid's GraphQL API changes:

1. **Fetch new schema:**
   ```bash
   git clone https://github.com/unraid/api.git /tmp/unraid-api
   cp /tmp/unraid-api/api/generated-schema.graphql schema/unraid-schema.graphql
   ```

2. **Add provenance header:**
   ```graphql
   # ─────────────────────────────────────────────────────────────────────────────
   # Vendored Unraid GraphQL schema (SDL) — used ONLY by tests/dev tooling.
   #
   # Source : github.com/unraid/api  → api/generated-schema.graphql
   # Commit : <new-commit-hash>
   # Method : copied from a local clone of unraid/api
   # >>> VENDOR-HEADER-END <<<
   # ─────────────────────────────────────────────────────────────────────────────
   ```

3. **Run schema-contract test:**
   ```bash
   cargo test schema_contract
   ```

4. **Fix broken queries:**
   - Update cynic structs in `gql_typed.rs`
   - Update client methods in `graphql.rs`
   - Update fixtures in `tests/fixtures/scenarios/`

5. **Run tests:**
   ```bash
   cargo test
   ```

## Release process

### 1. Update version

**`Cargo.toml`:**
```toml
[package]
version = "0.2.0"  # Bump version
```

**`server.json`:**
```json
{
  "version": "0.2.0",
  "packages": [{
    "identifier": "ghcr.io/jmagar/runraid:0.2.0"
  }]
}
```

### 2. Update CHANGELOG

**`CHANGELOG.md`:**
```markdown
## [0.2.0] - 2026-XX-XX

### Added
- New action `your_action` for ...
- Pagination support on `your_list`

### Changed
- ...
```

### 3. Commit and tag

```bash
git add -A
git commit -m "Release 0.2.0"
git tag v0.2.0
git push && git push --tags
```

### 4. CI automation

**`.github/workflows/release.yml`:**
- Builds release binaries (linux/amd64 only — arm64 is not supported)
- Publishes to GitHub Releases
- Publishes OCI image to GHCR

**Manual steps:**
- Run `./scripts/bump-version.sh` (automates version bumps)
- Run `./scripts/refresh-docs.sh` (syncs docs from source)

### 5. Publish

Release is automatic via CI after tag push.

**Artifacts:**
- GitHub Release with binaries
- OCI image at `ghcr.io/jmagar/runraid:<version>`

## CI/CD

### Workflow triggers

**`.github/workflows/ci.yml`:**
- Runs on push to `main`
- Runs on pull requests

### Checks

1. **Format check** - Fails if code not formatted
2. **Clippy** - Fails on any warnings
3. **Tests** - Full test suite via nextest
4. **TOML format** - Fails if TOML not formatted
5. **Security audit** - Fails on new advisories
6. **Secret leak detection** - Fails if secrets committed

### Drift detection

**`.github/workflows/schema-drift.yml`:**
- Runs daily at 06:00 UTC
- Compares vendored SDL to upstream
- Opens issue if drift detected

## Debugging

### Enable debug logging

```bash
RUST_LOG=debug cargo run -- serve mcp
```

### Enable tracing

```bash
RUST_LOG=unraid_rmcp=debug,tower_http=trace cargo run -- serve mcp
```

### Debug queries

Dump GraphQL queries before sending:

```rust
eprintln!("Query: {}", query);
let response = self.send_graphql(query, variables).await?;
```

### Use mock server

```bash
cargo run --example mock_unraid --features test-support &
export UNRAID_API_URL="http://localhost:4000"
cargo run -- serve mcp
```

## Code review checklist

Before submitting PR:

- [ ] Code formatted (`cargo fmt`)
- [ ] No clippy warnings (`cargo clippy`)
- [ ] Tests pass (`cargo test`)
- [ ] New actions added to `ACTIONS` slice
- [ ] Help text updated in `tools.rs`
- [ ] CLI commands added (if applicable)
- [ ] Fixtures added (if applicable)
- [ ] CHANGELOG updated
- [ ] Documentation updated (if user-facing)

## Source references

- Development commands: `Justfile`
- CI config: `.github/workflows/`
- Schema vendoring: `schema/unraid-schema.graphql`
- Schema contract test: `tests/schema_contract.rs`
- Release script: `scripts/bump-version.sh`
- Docs refresh: `scripts/refresh-docs.sh`
