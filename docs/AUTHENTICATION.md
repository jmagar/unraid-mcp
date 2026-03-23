# Authentication Setup Guide

This document covers both Google OAuth 2.0 and API key bearer token authentication for the Unraid MCP HTTP server. It explains how to protect the server using FastMCP's built-in `GoogleProvider` for OAuth, or a static bearer token for headless/machine access.

---

## Overview

By default the MCP server is **open** — any client on the network can call tools. Setting three environment variables enables Google OAuth 2.1 authentication: clients must complete a Google login flow before the server will execute any tool.

OAuth state (issued tokens, refresh tokens) is persisted to an encrypted file store at `~/.local/share/fastmcp/oauth-proxy/`, so sessions survive server restarts when `UNRAID_MCP_JWT_SIGNING_KEY` is set.

> **Transport requirement**: OAuth only works with HTTP transports (`streamable-http` or `sse`). It has no effect on `stdio` — the server logs a warning if you configure both.

---

## Prerequisites

- Google account with access to [Google Cloud Console](https://console.cloud.google.com/)
- MCP server reachable at a known URL from your browser (LAN IP, Tailscale IP, or public domain)
- `UNRAID_MCP_TRANSPORT=streamable-http` (the default)

---

## Step 1: Create a Google OAuth Client

1. Open [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: anything (e.g. `Unraid MCP`)
5. **Authorized redirect URIs** — add exactly:
   ```
   http://<your-server-ip>:6970/auth/callback
   ```
   Replace `<your-server-ip>` with the IP/hostname your browser uses to reach the MCP server (e.g. `10.1.0.2`, `100.x.x.x` for Tailscale, or a domain name).
6. Click **Create** — copy the **Client ID** and **Client Secret**

---

## Step 2: Configure Environment Variables

Add these to `~/.unraid-mcp/.env` (the canonical credential file for all runtimes):

```bash
# Google OAuth (optional — enables authentication)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret

# Public base URL of this MCP server (must match the redirect URI above)
UNRAID_MCP_BASE_URL=http://10.1.0.2:6970

# Stable JWT signing key — prevents token invalidation on server restart
# Generate one: python3 -c "import secrets; print(secrets.token_hex(32))"
UNRAID_MCP_JWT_SIGNING_KEY=your-64-char-hex-string
```

**All four variables at once** (copy-paste template):

```bash
cat >> ~/.unraid-mcp/.env <<'EOF'

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
UNRAID_MCP_BASE_URL=http://10.1.0.2:6970
UNRAID_MCP_JWT_SIGNING_KEY=
EOF
```

Then fill in the blanks.

---

## Step 3: Generate a Stable JWT Signing Key

Without `UNRAID_MCP_JWT_SIGNING_KEY`, FastMCP derives a key on startup. Any server restart invalidates all existing tokens and forces every client to re-authenticate.

Generate a stable key once:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output into `UNRAID_MCP_JWT_SIGNING_KEY`. This value never needs to change unless you intentionally want to invalidate all sessions.

---

## Step 4: Restart the Server

```bash
# Docker Compose
docker compose restart unraid-mcp

# Direct / uv
uv run unraid-mcp-server
```

On startup you should see:

```
INFO  [SERVER] Google OAuth enabled — base_url=http://10.1.0.2:6970, redirect_uri=http://10.1.0.2:6970/auth/callback
```

---

## How Authentication Works

1. An MCP client connects to `http://<server>:6970/mcp`
2. The server responds with a `401 Unauthorized` and an OAuth authorization URL
3. The client opens the URL in a browser; the user logs in with Google
4. Google redirects to `<UNRAID_MCP_BASE_URL>/auth/callback` with an authorization code
5. FastMCP exchanges the code for tokens, issues a signed JWT, and returns it to the client
6. The client includes the JWT in subsequent requests — the server validates it without hitting Google again
7. Tokens persist to `~/.local/share/fastmcp/oauth-proxy/` — sessions survive server restarts

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | For OAuth | `""` | OAuth 2.0 Client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | For OAuth | `""` | OAuth 2.0 Client Secret from Google Cloud Console |
| `UNRAID_MCP_BASE_URL` | For OAuth | `""` | Public base URL of this server — must match the authorized redirect URI |
| `UNRAID_MCP_JWT_SIGNING_KEY` | Recommended | auto-derived | Stable 32+ char secret for JWT signing — prevents token invalidation on restart |

OAuth is activated only when **all three** of `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `UNRAID_MCP_BASE_URL` are non-empty. Omit any one to run without authentication.

---

## Disabling OAuth

Remove (or empty) `GOOGLE_CLIENT_ID` from `~/.unraid-mcp/.env` and restart. The server reverts to unauthenticated mode and logs:

```
WARNING  [SERVER] No authentication configured — MCP server is open to all clients on the network.
```

---

## Troubleshooting

**`redirect_uri_mismatch` from Google**
The redirect URI in Google Cloud Console must exactly match `<UNRAID_MCP_BASE_URL>/auth/callback` — same scheme, host, port, and path. Trailing slashes matter.

**Tokens invalidated after restart**
Set `UNRAID_MCP_JWT_SIGNING_KEY` to a stable secret (see Step 3). Without it, FastMCP generates a new key on every start.

**`stdio` transport warning**
OAuth requires an HTTP transport. Set `UNRAID_MCP_TRANSPORT=streamable-http` (the default) or `sse`.

**Client cannot reach the callback URL**
`UNRAID_MCP_BASE_URL` must be the address your browser uses to reach the server — not `localhost` or `0.0.0.0`. Use the LAN IP, Tailscale IP, or a domain name.

**OAuth configured but server not starting**
Check `logs/unraid-mcp.log` or `docker compose logs unraid-mcp` for startup errors.

---

## API Key Authentication (Alternative / Combined)

For machine-to-machine access (scripts, CI, other agents) without a browser-based OAuth flow, set `UNRAID_MCP_API_KEY`:

```bash
# In ~/.unraid-mcp/.env
UNRAID_MCP_API_KEY=your-secret-token
```

Clients present it as a standard bearer token:

```
Authorization: Bearer your-secret-token
```

**Combining with Google OAuth**: set both `GOOGLE_CLIENT_ID` and `UNRAID_MCP_API_KEY`. The server activates `MultiAuth` and accepts either method — Google OAuth for interactive clients, API key for headless clients.

**Reusing the Unraid API key**: you can set `UNRAID_MCP_API_KEY` to the same value as `UNRAID_API_KEY` for simplicity. The two vars are kept separate so each concern has its own name.

**Standalone API key** (no Google OAuth): set only `UNRAID_MCP_API_KEY`. The server validates bearer tokens directly with no OAuth redirect flow.

---

## Security Notes

- OAuth protects the MCP HTTP interface — the Unraid GraphQL API itself still uses `UNRAID_API_KEY`
- OAuth state files at `~/.local/share/fastmcp/oauth-proxy/` should be on a private filesystem; do not expose them
- Restrict Google OAuth to specific accounts via the Google Cloud Console **OAuth consent screen** → **Test users** if you don't want to publish the app
- `UNRAID_MCP_JWT_SIGNING_KEY` is a credential — store it in `~/.unraid-mcp/.env` (mode 600), never in source control
