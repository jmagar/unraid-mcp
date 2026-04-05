# Configuration Reference -- unraid-mcp

Complete environment variable reference and configuration options.

## Environment file

The canonical configuration file is `~/.unraid-mcp/.env`. The server searches for `.env` files in this priority order:

1. `~/.unraid-mcp/.env` -- primary (canonical credentials dir, all runtimes)
2. `~/.unraid-mcp/.env.local` -- local overrides (only if primary is absent)
3. `/app/.env.local` -- Docker compat mount
4. `<project-root>/.env.local` -- dev overrides
5. `<project-root>/.env` -- dev fallback
6. `unraid_mcp/.env` -- last resort

Override the credentials directory with `UNRAID_CREDENTIALS_DIR`.

## Required variables

| Variable | Description |
| --- | --- |
| `UNRAID_API_URL` | Unraid GraphQL endpoint (e.g. `https://tower.local/graphql`). No trailing slash. |
| `UNRAID_API_KEY` | Unraid API key. Found in Settings > Management Access > API Keys. |

## Server variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_MCP_HOST` | `0.0.0.0` | Bind address for HTTP transport |
| `UNRAID_MCP_PORT` | `6970` | Port for the MCP HTTP server. Must be 1-65535. |
| `UNRAID_MCP_TRANSPORT` | `streamable-http` | Transport method: `streamable-http`, `stdio`, or `sse` (deprecated) |

## Authentication variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_MCP_BEARER_TOKEN` | auto-generated | Bearer token for HTTP auth. Auto-generated on first HTTP startup if absent. Generate manually with `openssl rand -hex 32`. |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | `false` | Set `true` to disable bearer auth (only behind a trusted gateway). |

## SSL variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_VERIFY_SSL` | `true` | SSL verification for upstream Unraid API. Set `false` for self-signed certs. Can also be a path to a CA bundle. |

## Logging variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_MCP_LOG_LEVEL` | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `UNRAID_MCP_LOG_FILE` | `unraid-mcp.log` | Log filename (written to `logs/` directory or `/app/logs/` in Docker) |

Log files are capped at 10 MB and overwritten to prevent disk space issues.

## Subscription variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_AUTO_START_SUBSCRIPTIONS` | `true` | Auto-start WebSocket subscriptions on server boot |
| `UNRAID_MAX_RECONNECT_ATTEMPTS` | `10` | Maximum WebSocket reconnection attempts before giving up |
| `UNRAID_AUTOSTART_LOG_PATH` | auto-detect | Log file path for the log tail subscription. Defaults to `/var/log/syslog` if available. |

## Credentials directory

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_CREDENTIALS_DIR` | `~/.unraid-mcp` | Override the credentials directory path. Useful for containers or custom deployments. |

## Docker variables

| Variable | Default | Description |
| --- | --- | --- |
| `PUID` | `1000` | User ID for the container process |
| `PGID` | `1000` | Group ID for the container process |
| `DOCKER_NETWORK` | -- | External Docker network name. Leave unset for default bridge. |

## Timeouts

Configured in code (not via environment variables):

| Context | Timeout | Notes |
| --- | --- | --- |
| Default HTTP requests | 30s | Standard GraphQL queries |
| Disk operations | 90s | SMART data queries need longer |
| Tool execution | 120s | FastMCP tool timeout |
| WebSocket collection | 5s default | Configurable via `collect_for` parameter |

## Middleware configuration

Configured in code:

| Middleware | Setting | Value |
| --- | --- | --- |
| Rate limiting | Max requests | 540 per 60-second sliding window |
| Response limiting | Max size | 512 KB (truncated, not errored) |
| Logging | Methods logged | `tools/call`, `resources/read` |
| Error handling | Traceback included | Only when `LOG_LEVEL=DEBUG` |

## Example .env file

```bash
# Core API Configuration (Required)
UNRAID_API_KEY=your_api_key
UNRAID_API_URL=http://your-unraid-server

# MCP Server Settings
UNRAID_MCP_HOST=0.0.0.0
UNRAID_MCP_PORT=6970
UNRAID_MCP_TRANSPORT=streamable-http

# HTTP Bearer Token Authentication
UNRAID_MCP_BEARER_TOKEN=your_bearer_token

# Safety flags
UNRAID_MCP_DISABLE_HTTP_AUTH=false

# Docker user / network
DOCKER_NETWORK=
PGID=1000
PUID=1000
```
