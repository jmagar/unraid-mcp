# Security Guardrails -- unraid-mcp

Safety and security patterns enforced across the unraid-mcp server.

## Credential management

### Storage

- Credentials live in `~/.unraid-mcp/.env` (mode 600, directory mode 700)
- The elicitation setup wizard writes credentials atomically (tmp file + `os.replace`)
- Credentials are never written to `os.environ` after startup -- all internal consumers read from module globals via `from ..config import settings`
- Bearer tokens are removed from `os.environ` immediately after being applied to prevent subprocess inheritance

### Loading priority

The server loads from the first `.env` file found:
1. `~/.unraid-mcp/.env`
2. `~/.unraid-mcp/.env.local`
3. `/app/.env.local`
4. `<project-root>/.env.local`
5. `<project-root>/.env`
6. `unraid_mcp/.env`

### Sensitive value redaction

The `redact_sensitive()` function in `core/client.py` recursively replaces values for keys matching:
- Exact: `key`, `pin`
- Substring: `password`, `secret`, `token`, `apikey`, `authorization`, `credential`, `passphrase`, `jwt`, `cookie`, `session`

All debug logging passes through this function.

## Destructive action gating

### Two-tier confirmation

All destructive operations are gated by the `gate_destructive_action()` function in `core/guards.py`:

1. **Interactive clients (elicitation)**: The server sends an elicitation request with a checkbox confirmation. The user must explicitly check "confirmed" and submit.
2. **Non-interactive clients (confirm=True)**: Agents and API callers must pass `confirm=True` to bypass elicitation.

### Destructive actions registry

| Domain | Destructive subactions |
| --- | --- |
| `array` | `stop_array`, `remove_disk`, `clear_disk_stats` |
| `vm` | `force_stop`, `reset` |
| `notification` | `delete`, `delete_archived` |
| `rclone` | `delete_remote` |
| `key` | `delete` |
| `disk` | `flash_backup` |
| `setting` | `configure_ups` |
| `plugin` | `remove` |

Each domain module defines its own `_*_DESTRUCTIVE` set and per-action description dictionary.

### Elicitation fallback

When the MCP client does not support elicitation:
- `NotImplementedError` is caught
- A warning is logged
- The operation is blocked with a `ToolError` instructing the user to re-run with `confirm=True`

## HTTP authentication

### Bearer token (RFC 6750)

- Constant-time comparison via `hmac.compare_digest` prevents timing attacks
- Missing header returns 401 with `WWW-Authenticate: Bearer realm="unraid-mcp"`
- Invalid token returns 401 with `error="invalid_token"`
- Per-IP rate limiting: 60 failures per 60-second window triggers 429 with `Retry-After: 60`
- Maximum 10,000 unique IPs tracked to prevent memory exhaustion DoS
- Log throttling: at most one warning per IP per 30 seconds

### RFC 9728 well-known endpoint

`GET /.well-known/oauth-protected-resource` returns resource metadata with an empty `authorization_servers` list, telling MCP clients to use a pre-shared bearer token (no OAuth flow).

### Health endpoint bypass

`GET /health` is served by `HealthMiddleware` outside the auth layer, allowing unauthenticated Docker healthchecks.

## Input validation

### Log path validation

Log file paths are restricted to allowed prefixes (`/var/log/`, `/boot/logs/`, `/mnt/`) to prevent path traversal.

### GraphQL injection prevention

- All queries and mutations use pre-built query dicts (`_*_QUERIES`, `_*_MUTATIONS`)
- No string interpolation of user input into GraphQL query strings
- Subscription test tool only allows whitelisted field names: `containerStats`, `cpu`, `memory`, `array`, `network`, `docker`, `vm`

### Port validation

`UNRAID_MCP_PORT` is validated as an integer in range 1-65535 at startup. Invalid values cause immediate exit.

## Response safety

### Size limiting

`ResponseLimitingMiddleware` truncates responses exceeding 512 KB with a clear suffix rather than erroring. This protects client context windows from oversized responses.

### Rate limiting

`SlidingWindowRateLimitingMiddleware` enforces 540 requests per 60-second sliding window. This stays under the Unraid API's 600 req/min ceiling.

### Log content capping

Subscription data with log content is capped at 1 MB / 5,000 lines to prevent unbounded memory growth from persistent WebSocket streams.

## Hooks enforcement

PostToolUse hooks run after every Write, Edit, MultiEdit, or Bash operation:

- `fix-env-perms.sh`: Ensures `~/.unraid-mcp/.env` stays at mode 600
- `ensure-ignore-files.sh`: Keeps `.gitignore` and `.dockerignore` aligned with security requirements
