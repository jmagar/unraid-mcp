# Runtime Architecture

How requests flow through unrust, from MCP client to Unraid server and back.

## Request flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Client (Claude)                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ HTTP (RMCP) or stdio
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Axum HTTP Server                         │
│  ├─ POST /mcp        → RMCP handler                                 │
│  ├─ GET  /health     → observability probe                          │
│  └─ OAuth discovery routes (when AuthPolicy::Mounted + OAuth)       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Auth check (if not LoopbackDev)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/mcp/rmcp_server.rs - RMCP ServerHandler                        │
│  ├─ tools/list()     → enumerates the `unraid` tool                  │
│  ├─ tools/call()     → dispatches by action string                  │
│  └─ scope check      → enforces unraid:read / unraid:admin          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Action dispatch
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/mcp/tools.rs - Action dispatcher                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ "server"  → state.service.server().await                      │  │
│  │ "array"   → state.service.array().await                       │  │
│  │ "docker"  → state.service.docker(args).await                  │  │
│  │ ... (30+ actions matched from ACTIONS slice)                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Service layer (thin pass-through)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/app.rs - UnraidService                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ pub async fn server(&self) -> Result<Value>                  │  │
│  │     self.client.server().await                                │  │
│  │                                                               │  │
│  │ pub async fn array(&self) -> Result<Value>                   │  │
│  │     self.client.array().await                                 │  │
│  │                                                               │  │
│  │ ... (one delegating method per action)                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ GraphQL client
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/graphql.rs - UnraidClient                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ pub async fn server(&self) -> Result<Value>                   │  │
│  │     self.run_typed(ServerQuery).await                          │  │
│  │                                                               │  │
│  │ pub async fn array(&self) -> Result<Value>                    │  │
│  │     self.run_typed(ArrayQuery).await                           │  │
│  │                                                               │  │
│  │ fn run_typed<T>(&self, op: T) -> Result<Value>                │  │
│  │     where T: cynic::Operation + Serialize                      │  │
│  │     let response = self.send_graphql(                          │  │
│  │         op.build_query().serialize(),                          │  │
│  │         op.get_variable_definitions()                          │  │
│  │     ).await?                                                   │  │
│  │     op.parse_response(response)                                │  │
│  │         .map(|data| serde_json::to_value(data).unwrap())       │  │
│  │         .map_err(|e| e.into())                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  fn send_graphql(...) → POSTs to UNRAID_API_URL with:               │
│    - Header: x-api-key: UNRAID_API_KEY                              │
│    - Body: GraphQL query + variables (not interpolated)             │
│    - TLS verify controlled by UNRAID_API_SKIP_TLS_VERIFY            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ HTTP request
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Unraid GraphQL API (myunraid.net)                 │
│                    Returns JSON response                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Response (JSON) flows back up
                               ▼
                        MCP client receives result
```

## Transport modes

### HTTP MCP (RMCP Streamable HTTP)

Default mode. Server binds to `0.0.0.0:40010` (configurable) and accepts POST requests to `/mcp`.

**Starting:**
```bash
runraid serve mcp   # explicit
runraid             # default (no args)
```

**Key characteristics:**
- RMCP protocol framing over HTTP
- Accepts `application/json` or `text/event-stream` (SSE)
- Stateless or stateful session support
- Auth required unless `LoopbackDev` mode (bound to 127.x)
- CORS enabled for configured origins

### stdio MCP

Child-process transport. Used by MCP clients that launch the server as a subprocess.

**Starting:**
```bash
runraid mcp
```

**Key characteristics:**
- RMCP over stdio (stdin/stdout)
- No HTTP server
- No auth (implicit trust via process spawn)
- Used by Claude Code's MCP client integration

### CLI

Direct human interaction. Not an MCP transport.

**Starting:**
```bash
runraid server              # human-readable output
runraid array --json        # JSON output
runraid docker id mycontainer
```

**Key characteristics:**
- Parses CLI args into action + parameters
- Formats output for terminal or JSON
- Shares all underlying logic with MCP (same service/client)

## Auth modes

The server uses an `AuthPolicy` enum to determine authentication behavior.

### LoopbackDev (no auth)

**Active when:**
- `UNRAID_RMCP_DISABLE_HTTP_AUTH=true` OR
- `UNRAID_RMCP_NO_AUTH=true` (deprecated alias) OR
- Bound to loopback address (127.x, ::1, localhost)

**Behavior:**
- No auth check on `/mcp`
- Useful for local development
- Safety: server refuses to bind to non-loopback with no auth unless `UNRAID_NOAUTH=true`

### Bearer token

**Active when:**
- `UNRAID_RMCP_TOKEN` is set AND not in loopback mode

**Behavior:**
- Expects `Authorization: Bearer <token>` header
- Valid token proceeds to tool handler
- Invalid/missing token returns 401

### OAuth (Google)

**Active when:**
- `UNRAID_RMCP_AUTH_MODE=oauth`
- OAuth credentials configured (client ID, secret, etc.)

**Behavior:**
- Uses `lab-auth` crate for JWT validation
- Supports Google OAuth flow
- Scopes: `unraid:read` (queries) and `unraid:admin` (mutations)
- JWKS endpoint exposed at `/.well-known/jwks.json`
- Discovery metadata at `/.well-known/oauth-authorization-server`

## Key components

| Component | File | Responsibility |
|-----------|------|-----------------|
| **Mode dispatch** | `src/main.rs` | Decides whether to run HTTP server, stdio MCP, or CLI |
| **HTTP server** | `src/mcp/routes.rs` | Axum router, middleware, route handlers |
| **RMCP handler** | `src/mcp/rmcp_server.rs` | Implements MCP protocol, tool/prompt/resource handlers |
| **Action dispatch** | `src/mcp/tools.rs` | Matches action string to service method call |
| **Service layer** | `src/app.rs` | Thin pass-through to GraphQL client (no business logic) |
| **GraphQL client** | `src/graphql.rs` | HTTP client, typed operations, variable interpolation |
| **Typed ops** | `src/gql_typed.rs` | cynic-derived QueryFragment/InputObject structs |
| **Config** | `src/config.rs` | Environment loading, TOML parsing, defaults |
| **Observability** | `src/observability.rs` | Health check, request counters |
| **Auth policy** | `src/mcp.rs` | `AuthPolicy` enum, auth layer builder |
| **Schema registry** | `src/mcp/schemas.rs` | `ACTIONS` slice (single source of truth) |
| **CLI parse/dispatch** | `src/cli/parse.rs`, `src/cli/dispatch.rs` | CLI arg parsing and routing |

## Typed GraphQL operations (cynic)

The project uses **cynic** for compile-time query type checking:

1. **build.rs** registers `schema/unraid-schema.graphql` as the default cynic schema
2. Operations in `gql_typed.rs` derive `cynic::QueryFragment` or `cynic::MutationFragment`
3. At compile time, cynic validates each operation against the vendored SDL
4. Invalid queries (wrong fields, wrong args, wrong types) fail to compile
5. At runtime, `run_typed()` executes the operation via the existing reqwest client and serializes the typed response back to `Value`

**Key files:**
- `schema/unraid-schema.graphql` - Vendored Unraid SDL (contract)
- `build.rs` - Schema registration
- `src/gql_typed.rs` - Typed operations (98KB generated/derived code)
- `src/graphql.rs` - `run_typed()` execution helper

**Why typed at the wire but Value downstream?**
- Compile-time safety against schema drift
- Single transport layer (reqwest)
- Compatibility with existing dispatch/formatters/MCP layers that expect `Value`

## Error handling

Errors flow back up the stack as `anyhow::Result<T>` or `thiserror`-derived types:

1. **GraphQL client** - HTTP errors, JSON parse errors, GraphQL errors (wrapped in `anyhow`)
2. **Service layer** - Pass-through (no new errors)
3. **MCP dispatch** - Invalid action returns error text to MCP client
4. **Auth layer** - 401 Unauthorized on missing/invalid credentials
5. **Observability** - Health endpoint returns 503 if upstream probe fails

## Testing the runtime flow

The test suite (`tests/`) covers the full runtime flow without a real Unraid server:

- `tests/upstream.rs` - Mock Unraid responses at the HTTP layer
- `tests/scenarios.rs` - Pre-canned response fixtures for all actions
- `tests/auth_modes.rs` - All three auth policies
- `tests/oauth_flow.rs` - JWT validation with real RS256 keys
- `tests/dispatch.rs` - Action routing through the MCP layer
- `tests/stdio_mcp.rs` - stdio transport end-to-end

Tests use stub `UnraidService` instances pointing at `http://localhost:1/graphql`, so no real GraphQL calls are made.
