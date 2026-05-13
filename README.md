# unraid-mcp

Rust MCP server that bridges Claude (and any MCP client) to the Unraid server GraphQL API. Exposes 24 read-only actions covering array health, Docker, VMs, shares, logs, metrics, UPS, and more.

## Architecture

```
                      ┌────────────────────────────────────┐
  Claude / MCP ◀────▶ │  POST /mcp  (RMCP Streamable HTTP) │
  stdio client ◀────▶ │  unraid mcp  (stdio transport)      │
                      │                                    │
                      │  mcp/tools.rs  ─▶  app.rs          │
                      │                       │            │
                      │                  graphql.rs        │
                      │                       │            │
                      │             POST <UNRAID_API_URL>   │
                      │             x-api-key: <key>       │
                      └───────────────────────┼────────────┘
                                              │
                              Unraid GraphQL API (myunraid.net)
```

- `graphql.rs` — HTTP client: POSTs GraphQL queries to the Unraid API with the `x-api-key` header
- `app.rs` — `UnraidService`: business layer, one method per action, no logic
- `mcp/tools.rs` — thin shim: parse JSON args, call service, return `Value`
- `cli.rs` — thin shim: parse CLI args, call service, format and print
- `main.rs` — mode dispatch: HTTP MCP server, stdio MCP, or CLI

## Quickstart

### Prerequisites

- Rust 1.86+ (`rustup show`)
- Unraid API URL and API key (Settings → API Management in Unraid)

### Run

```bash
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp

# Set required environment variables
export UNRAID_API_URL="https://10-1-0-2.<hash>.myunraid.net:31337/graphql"
export UNRAID_API_KEY="your-api-key-here"
export UNRAID_MCP_PORT=6970
export UNRAID_MCP_DISABLE_HTTP_AUTH=true

# Or copy .env and edit it
cp .env .env.local

# Start the MCP HTTP server
cargo run -- serve mcp

# Verify it is up
curl -sf http://localhost:6970/health | jq .
# → {"status":"ok"}
```

### First MCP call

```bash
curl -s -X POST http://localhost:6970/mcp \
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
  }' | jq .result.content[0].text | jq -r . | jq .
```

## Transports

| Mode | Command | Description |
|------|---------|-------------|
| HTTP MCP | `unraid serve mcp` or `unraid` (no args) | RMCP Streamable HTTP on `POST /mcp` |
| stdio MCP | `unraid mcp` | For MCP clients that launch the server as a child process |
| CLI | `unraid <command>` | Human-readable or `--json` output |

## MCP Tool Reference

One tool is exposed: `unraid`. Set the required `action` argument to select the operation.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "unraid",
    "arguments": {"action": "array"}
  }
}
```

### Core actions

| Action | Description |
|--------|-------------|
| `array` | Array state, disk health, parity check status, capacity |
| `disks` | Physical disks with SMART status, temperature, interface type |
| `docker` | All Docker containers: state, status, ports, update availability |
| `docker_logs` | Container logs — requires `id`, optional `tail` (default 100) |
| `vms` | Virtual machines and their state |
| `server` | Server identity, LAN/WAN IP, local and remote URLs |
| `info` | OS, CPU, memory layout, Unraid and kernel versions |
| `shares` | User shares with size, cache settings, LUKS status |
| `notifications` | Active warnings and alerts with overview counts |

### System actions

| Action | Description |
|--------|-------------|
| `services` | Running system services with uptime |
| `network` | Network access URLs (type, name, IPv4, IPv6) |
| `metrics` | Live CPU percent per core, memory usage, temperature sensors |
| `vars` | System configuration variables (hostname, sharing, SSL, SSH) |
| `registration` | License type, state, expiry |
| `flash` | USB flash drive vendor and product info |

### Log actions

| Action | Description | Extra args |
|--------|-------------|-----------|
| `log_files` | List available log files with sizes and modification times | — |
| `log_file` | Read a log file | `path` (required), `lines`, `start_line` |

### Storage actions

| Action | Description |
|--------|-------------|
| `parity_history` | All past parity check results (date, duration, speed, errors) |
| `rclone` | Backup remote configurations and drive names |

### UPS actions

| Action | Description |
|--------|-------------|
| `ups` | UPS devices: battery charge, estimated runtime, power load |
| `ups_config` | UPS monitoring configuration (service, type, shutdown thresholds) |

### Remote access actions

| Action | Description |
|--------|-------------|
| `remote_access` | WAN access type and port forwarding configuration |
| `connect` | Unraid Connect dynamic remote access status and settings |

### Plugin actions

| Action | Description |
|--------|-------------|
| `plugins` | Installed community plugins with versions |

### Meta

| Action | Description |
|--------|-------------|
| `help` | Markdown reference for all actions (no auth required) |

### Action parameters

| Parameter | Type | Used by | Description |
|-----------|------|---------|-------------|
| `action` | string | all | Operation to perform (required) |
| `id` | string | `docker_logs` | Container ID |
| `path` | string | `log_file` | Log file path |
| `lines` | integer | `log_file` | Number of lines to read |
| `start_line` | integer | `log_file` | Starting line number (1-indexed) |
| `tail` | integer | `docker_logs` | Lines to return (default 100) |

## CLI Reference

All CLI commands accept `--json` for machine-readable output.

```
unraid [serve]                        Start MCP HTTP server (default)
unraid mcp                            Start MCP stdio transport

Core:
  unraid array [--json]
  unraid disks [--json]
  unraid docker [--json]
  unraid docker logs <id> [--tail N] [--json]
  unraid vms [--json]
  unraid server [--json]
  unraid info [--json]
  unraid shares [--json]
  unraid notifications [--json]

System:
  unraid services [--json]
  unraid network [--json]
  unraid metrics [--json]
  unraid vars [--json]
  unraid registration [--json]
  unraid flash [--json]

Logs:
  unraid log-files [--json]
  unraid log <path> [--lines N] [--start-line N] [--json]

Storage:
  unraid parity-history [--json]
  unraid rclone [--json]

UPS:
  unraid ups [--json]
  unraid ups-config [--json]

Remote access:
  unraid remote-access [--json]
  unraid connect [--json]

Plugins:
  unraid plugins [--json]
```

## HTTP Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/mcp` | POST | yes (when configured) | RMCP Streamable HTTP |
| `/health` | GET | no | Always returns `{"status":"ok"}` |
| `/mcp/.well-known/oauth-authorization-server` | GET | no | OAuth metadata (OAuth mode only) |

## Configuration

Configuration loads from three sources, highest priority first:

1. Environment variables
2. `config.toml` (if present in the working directory)
3. Built-in defaults

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UNRAID_API_URL` | **yes** | — | Unraid GraphQL endpoint |
| `UNRAID_API_KEY` | **yes** | — | API key sent as `x-api-key` header |
| `UNRAID_API_SKIP_TLS_VERIFY` | no | `false` | Skip TLS certificate check |
| `UNRAID_MCP_HOST` | no | `0.0.0.0` | Bind host |
| `UNRAID_MCP_PORT` | no | `3100` | Bind port (project default: `6970` via config.toml) |
| `UNRAID_MCP_TOKEN` | no | — | Static bearer token for `/mcp` |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | no | `false` | Disable MCP auth (safe on loopback or trusted networks) |
| `UNRAID_MCP_NO_AUTH` | no | `false` | Alias for disabling auth |
| `UNRAID_MCP_ALLOWED_HOSTS` | no | — | Extra comma-separated Host header values |
| `UNRAID_MCP_ALLOWED_ORIGINS` | no | — | Extra comma-separated CORS origins |
| `UNRAID_MCP_PUBLIC_URL` | no | — | Public URL for OAuth metadata |
| `RUST_LOG` | no | `info` | Log filter (e.g. `debug`, `warn`) |

### config.toml

```toml
[unraid]
api_url = "https://10-1-0-2.<hash>.myunraid.net:31337/graphql"
api_key  = "your-api-key"
# skip_tls_verify = false

[mcp]
host = "0.0.0.0"
port = 6970
server_name = "unraid-mcp"
# allowed_hosts = ["unraid.example.com"]
# allowed_origins = ["https://unraid.example.com"]
```

## Authentication

Three auth modes are supported:

**No auth (loopback or trusted network):** Set `UNRAID_MCP_DISABLE_HTTP_AUTH=true`. Auth is also automatically disabled when the bind host starts with `127.`.

**Static bearer token:** Set `UNRAID_MCP_TOKEN=<token>`. All `/mcp` requests must include `Authorization: Bearer <token>`. `/health` remains unauthenticated.

**OAuth (Google):** Set `UNRAID_MCP_PUBLIC_URL`, `UNRAID_MCP_GOOGLE_CLIENT_ID`, `UNRAID_MCP_GOOGLE_CLIENT_SECRET`, and `UNRAID_MCP_AUTH_ADMIN_EMAIL`. The server issues RS256 JWTs after Google login. Scopes: `unraid:read`, `unraid:admin`.

## Development

```bash
just dev       # cargo run -- serve mcp
just check     # cargo check
just lint      # cargo clippy -- -D warnings
just fmt       # cargo fmt
just test      # cargo test
just build     # cargo build
just release   # cargo build --release
just gen-token # openssl rand -hex 32
```

## Claude Code / stdio config

```json
{
  "mcpServers": {
    "unraid-mcp": {
      "command": "/path/to/unraid",
      "args": ["mcp"],
      "env": {
        "UNRAID_API_URL": "https://...",
        "UNRAID_API_KEY": "your-key",
        "RUST_LOG": "warn"
      }
    }
  }
}
```

## License

MIT
