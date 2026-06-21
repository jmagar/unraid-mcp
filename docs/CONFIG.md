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
| `UNRAID_MCP_MAX_RESPONSE_BYTES` | `40000` | Max serialized tool-response size (~10K tokens). Over-cap responses are replaced with a parseable JSON truncation marker (`{"error":"response_truncated","truncated":true,...}`). |

## Authentication variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_MCP_BEARER_TOKEN` | auto-generated | Bearer token for HTTP auth. Auto-generated on first HTTP startup if absent. Generate manually with `openssl rand -hex 32`. |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | `false` | Set `true` to disable bearer auth. Only valid behind a trusted fronting gateway — requires `UNRAID_MCP_TRUST_PROXY=true` to bind a public interface (see below). |
| `UNRAID_MCP_TRUST_PROXY` | `false` | Required second opt-in when auth is disabled (`UNRAID_MCP_DISABLE_HTTP_AUTH=true`) and the server binds a non-loopback interface. Asserts a fronting gateway terminates auth; without it, a public bind with auth disabled is refused. |

## SSL variables

| Variable | Default | Description |
| --- | --- | --- |
| `UNRAID_VERIFY_SSL` | `true` | SSL verification for the upstream Unraid API. **Recommended for self-signed certs: point this at a CA-bundle path** (`/path/to/ca.pem`) to trust the cert without disabling verification. `false` disables verification entirely (dangerous — see `UNRAID_ALLOW_INSECURE_TLS`). |
| `UNRAID_ALLOW_INSECURE_TLS` | `false` | Required second opt-in when `UNRAID_VERIFY_SSL=false`. Disabling verification sends the `UNRAID_API_KEY` to an unverified peer over **both** the httpx GraphQL client and the WebSocket subscription connection, exposing it to MITM interception. The server refuses to start with verification off unless this is `true`. Prefer the CA-bundle path instead. |

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

## Rate limiting

Two independent limiters:

- **Upstream token bucket (authoritative):** `core/client.py` `_RateLimiter` — 90 tokens,
  9.0 tokens/sec refill (~9 rps), modeling Unraid's hard **100 req / 10 s** limit with
  ~10% headroom. Every outbound GraphQL call acquires a token first; 429s are retried with
  backoff. This is what keeps the server inside Unraid's burst window.
- **Inbound abuse/DoS guard:** `SlidingWindowRateLimitingMiddleware` — 540 requests per
  60-second sliding window on the MCP surface. It does **not** bound Unraid's 10-second
  burst (a per-minute window can't), so it is not the upstream limiter.

## Middleware configuration

Configured in code:

| Middleware | Setting | Value |
| --- | --- | --- |
| Rate limiting (inbound) | Max requests | 540 per 60-second sliding window (abuse/DoS guard, not the upstream limiter) |
| Response limiting | Max size | 40 KB default (`UNRAID_MCP_MAX_RESPONSE_BYTES=40000`); over-cap responses are replaced with a parseable JSON truncation marker, not byte-cut |
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
