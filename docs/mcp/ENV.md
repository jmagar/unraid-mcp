# Environment Variable Reference

## Deployment paths

unraid-mcp supports two deployment models:

| Path | Transport | Credentials | Auth |
|------|-----------|-------------|------|
| **Plugin (stdio)** | stdio | `${userConfig.*}` in `.mcp.json` | None (stdio) |
| **Docker (HTTP)** | streamable-http | `.env` file | Bearer token |

For plugin deployment, see [Plugin CONFIG](../plugin/CONFIG.md).

## Upstream Service

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_API_URL` | yes | -- | yes (in plugin.json) | Unraid GraphQL endpoint. No trailing slash. |
| `UNRAID_API_KEY` | yes | -- | yes | Unraid API key from Settings > Management Access > API Keys |

## MCP Server

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_MCP_HOST` | no | `0.0.0.0` | no | Bind address for HTTP transport |
| `UNRAID_MCP_PORT` | no | `6970` | no | HTTP server port (1-65535) |
| `UNRAID_MCP_TRANSPORT` | no | `streamable-http` | no | Transport: `streamable-http`, `stdio`, or `sse` |

## Authentication

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_MCP_BEARER_TOKEN` | conditional | auto-generated | yes | Bearer token for HTTP auth. Required when transport is HTTP and auth is not disabled. |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | no | `false` | no | Disable bearer auth (only behind a trusted gateway) |

## SSL/TLS

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_VERIFY_SSL` | no | `true` | no | SSL verification for upstream API. `false` for self-signed certs, or a CA bundle path. |

## Logging

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_MCP_LOG_LEVEL` | no | `INFO` | no | Log verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `UNRAID_MCP_LOG_FILE` | no | `unraid-mcp.log` | no | Log filename in the logs/ directory |

## Subscriptions

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_AUTO_START_SUBSCRIPTIONS` | no | `true` | no | Auto-start WebSocket subscriptions on boot |
| `UNRAID_MAX_RECONNECT_ATTEMPTS` | no | `10` | no | Max WebSocket reconnection attempts |
| `UNRAID_AUTOSTART_LOG_PATH` | no | auto-detect | no | Log file path for log tail subscription |

## Credentials Directory

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `UNRAID_CREDENTIALS_DIR` | no | `~/.unraid-mcp` | no | Override credentials directory path |

## Docker / Compose

| Variable | Required | Default | Sensitive | Description |
|----------|----------|---------|-----------|-------------|
| `PUID` | no | `1000` | no | User ID for container process |
| `PGID` | no | `1000` | no | Group ID for container process |
| `DOCKER_NETWORK` | no | -- | no | External Docker network name |

## Loading priority

The server loads the first `.env` file found:

1. `~/.unraid-mcp/.env`
2. `~/.unraid-mcp/.env.local`
3. `/app/.env.local`
4. `<project-root>/.env.local`
5. `<project-root>/.env`
6. `unraid_mcp/.env`

## See Also

- [AUTH.md](AUTH.md) -- Authentication details
- [../CONFIG.md](../CONFIG.md) -- Full configuration reference with timeouts and middleware
- [ELICITATION.md](ELICITATION.md) -- Interactive credential setup
