# Authentication Setup Guide

The unraid-mcp server uses **static Bearer token authentication** for HTTP
transports (`streamable-http`, `sse`).  There is no OAuth flow — you generate
a token once and put it in both the server config and the MCP client config.

`stdio` transport (the Claude Code plugin default) runs as a local subprocess
and does **not** require a token.

---

## Quick start

### 1. Generate a token

```bash
openssl rand -hex 32
# example output: a3f8c2d1e4b7...
```

### 2. Set the token on the server

Add it to `~/.unraid-mcp/.env` (preferred) or the project `.env`:

```env
UNRAID_MCP_BEARER_TOKEN=a3f8c2d1e4b7...
```

Or run the interactive setup tool:

```
unraid(action="health", subaction="setup")
```

### 3. Configure your MCP client

#### Claude Code (`~/.claude/claude.json` or `claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "unraid": {
      "type": "http",
      "url": "http://your-server:6970/mcp",
      "headers": {
        "Authorization": "Bearer a3f8c2d1e4b7..."
      }
    }
  }
}
```

> **Important:** The value must be `Bearer <token>` (with the `Bearer ` prefix
> and a space).  Omitting the prefix causes an immediate 401.

#### Docker Compose (server side)

```yaml
environment:
  UNRAID_MCP_BEARER_TOKEN: "a3f8c2d1e4b7..."
  UNRAID_MCP_TRANSPORT: streamable-http
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `UNRAID_MCP_BEARER_TOKEN` | *(none)* | Required for HTTP transport. Generate with `openssl rand -hex 32`. |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | `false` | Set `true` to disable auth entirely (testing/trusted-network only). |

---

## How it works

1. The server starts an HTTP listener on port 6970.
2. Every request must include `Authorization: Bearer <token>` or it gets a
   `401 Unauthorized` response.
3. `/health` (Docker healthcheck) is always allowed without a token.
4. `/.well-known/oauth-protected-resource` is served without a token so MCP
   clients can discover the auth scheme automatically (RFC 9728).  It returns
   `{"bearer_methods_supported":["header"]}` with no `authorization_servers`,
   telling clients to use a pre-configured Bearer token.

---

## Troubleshooting

### `401 Unauthorized` — "missing authorization header"

The `Authorization` header is absent.  Check:

- Your MCP client config has `"headers": {"Authorization": "Bearer <token>"}`.
- The token in the client exactly matches `UNRAID_MCP_BEARER_TOKEN` on the server.
- No proxy between client and server is stripping the `Authorization` header.

### `401 Unauthorized` — "invalid token"

The header is present but the token value is wrong.  Regenerate and update
both sides, then restart the server.

### Claude Code shows "An unknown error occurred connecting to the MCP server"

This was a bug fixed in v1.2.1: the `/.well-known/oauth-protected-resource`
endpoint was not exempt from auth, so Claude Code's auth-discovery flow
received a 401 and surfaced a generic error.  Upgrade to v1.2.1 or later.

### Temporarily disable auth for testing

```env
UNRAID_MCP_DISABLE_HTTP_AUTH=true
```

Remove this before exposing the server outside a trusted network.
