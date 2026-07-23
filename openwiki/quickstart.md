---
type: "Reference"
title: "OpenWiki: unrust (unraid-rmcp)"
openwiki_generated: true
---

# OpenWiki: unrust (unraid-rmcp)

**unrust** is a Rust-based MCP (Model Context Protocol) server that bridges Claude and other MCP clients to the Unraid server GraphQL API. It provides read-only access to Unraid server data including array health, Docker containers, VMs, shares, logs, metrics, UPS status, and more.

## What this project is

`unraid-rmcp` is a Rust binary (`runraid`) that acts as a bridge between MCP clients (like Claude) and Unraid servers. It:

- Exposes a single `unraid` MCP tool with 30+ actions covering the full Unraid GraphQL API surface
- Supports both read queries and write mutations (with scope-based authorization)
- Runs as an HTTP MCP server (RMCP Streamable HTTP) or stdio MCP server
- Provides a CLI for direct human interaction
- Uses typed GraphQL operations (via cynic) validated against the vendored Unraid schema at compile time

## Quickstart

### Prerequisites
- Rust 1.90+ (`rustup show`)
- Unraid API URL and API key (from Settings → API Management in Unraid web UI)

### Run locally

```bash
# Clone and build
git clone https://github.com/jmagar/runraid
cd unrust
cargo build --release

# Configure environment
export UNRAID_API_URL="https://10-1-0-2.<hash>.myunraid.net:31337/graphql"
export UNRAID_API_KEY="your-api-key-here"
export UNRAID_RMCP_PORT=40010
export UNRAID_RMCP_DISABLE_HTTP_AUTH=true

# Or copy and edit .env
cp .env .env.local

# Start the MCP HTTP server
cargo run -- serve mcp

# Verify health
curl -sf http://localhost:40010/health | jq .
# → {"status":"ok"}
```

### First MCP call

```bash
curl -s -X POST http://localhost:40010/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "unraid",
      "arguments": {"action": "server"}
    }
  }' | jq -r '.result.content[0].text' | jq .
```

### One-line installer

```bash
curl -fsSL https://raw.githubusercontent.com/jmagar/runraid/main/install.sh | bash
```

## Documentation sections

### [Architecture](architecture/README.md)
How the project is structured and how requests flow through the system.

- **[Runtime architecture](architecture/runtime.md)** - Request flow, transport modes, auth modes, and key components
- **[Module map](architecture/module-map.md)** - Source file organization and where to make changes

### [Domain](domain/README.md)
The core concepts and data models this project deals with.

- **[MCP tools](domain/mcp-tools.md)** - The `unraid` tool, available actions, and scope model
- **[GraphQL API integration](domain/graphql-api.md)** - Unraid GraphQL client, typed operations, and schema management

### [Operations](operations/README.md)
How to deploy, configure, test, and develop the project.

- **[Configuration](operations/configuration.md)** - Environment variables, config files, and data directories
- **[Deployment](operations/deployment.md)** - Local, Docker, and production deployment options
- **[Testing](operations/testing.md)** - Test suite organization and running tests
- **[Development workflow](operations/development.md)** - Adding actions, code style, and release process

## Key concepts

**Thin shim architecture.** The CLI and MCP layers contain no business logic—they parse their input format and delegate to `UnraidService`, which delegates to `UnraidClient`. All data retrieval happens in the GraphQL client.

**Action-based dispatch.** The single MCP tool uses an `action` string parameter to select operations. `src/mcp/schemas.rs` contains the `ACTIONS` registry—the single source of truth for valid actions.

**GraphQL as the data layer.** The server POSTs queries to `UNRAID_API_URL` with `x-api-key: UNRAID_API_KEY`. Responses flow back as `serde_json::Value` through the dispatch/CLI/MCP layers.

**Typed at the wire, Value downstream.** Most operations are defined as typed cynic structs in `gql_typed.rs`, checked against the vendored SDL at compile time. Operations run over the existing reqwest client and serialize back to `Value` for compatibility with dispatch/formatters/MCP.

**Scope model.** Actions require either no scope (`help`), `unraid:read` (all queries plus `status`), or `unraid:admin` (mutations). A read-scoped token cannot reach a mutation. Scopes are enforced in `rmcp_server.rs`.

**Auth modes.** Three auth policies:
- `LoopbackDev` - No auth when bound to 127.x
- Bearer token - Static `UNRAID_RMCP_TOKEN`
- OAuth (Google) - JWT-based via `lab-auth`

**Schema as contract.** The vendored Unraid SDL (`schema/unraid-schema.graphql`) is the source of truth. A CI job runs daily to detect drift. Operations are type-checked at compile time via cynic.

## Transports

| Mode | Command | Description |
|------|---------|-------------|
| HTTP MCP | `runraid serve mcp` or `runraid` | RMCP Streamable HTTP on `POST /mcp` |
| stdio MCP | `runraid mcp` | Child-process transport for MCP clients |
| CLI | `runraid <command>` | Human-readable or `--json` output |

## When working in this repository

1. **Read the architecture section first** - Understand the request flow and where code lives
2. **Check the domain section** - Learn about MCP actions and GraphQL operations
3. **Follow the development workflow** - Use the Justfile, respect formatting rules, add tests
4. **Run tests before committing** - `cargo test` or `just test`
5. **Check CI requirements** - The pipeline enforces formatting, clippy, tests, and security audits

## External resources

- [GitHub repository](https://github.com/jmagar/runraid)
- [Unraid API documentation](https://docs.unraid.net/api/)
- [MCP specification](https://modelcontextprotocol.io/)
