# Configuration

Environment variables, config files, and data directories for unrust.

## Environment variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `UNRAID_API_URL` | Unraid GraphQL endpoint URL | `https://10-1-0-2.<hash>.myunraid.net:31337/graphql` |
| `UNRAID_API_KEY` | API key for `x-api-key` header | `your-api-key-here` |

**Get your API credentials:**
1. Open Unraid web UI
2. Go to **Settings → API Management**
3. Create or copy your API key

### Optional - MCP server

| Variable | Description | Default |
|----------|-------------|---------|
| `UNRAID_RMCP_HOST` | Bind address | `0.0.0.0` |
| `UNRAID_RMCP_PORT` | Bind port | `40010` |
| `UNRAID_RMCP_TOKEN` | Static bearer token for `/mcp` | (none) |
| `UNRAID_RMCP_DISABLE_HTTP_AUTH` | Disable MCP auth entirely | `false` |
| `UNRAID_RMCP_NO_AUTH` | Alias for `DISABLE_HTTP_AUTH` | `false` |
| `UNRAID_RMCP_AUTH_MODE` | Auth mode: `bearer` or `oauth` | `bearer` |
| `UNRAID_RMCP_PUBLIC_URL` | Public URL for OAuth metadata | (none) |
| `UNRAID_RMCP_GOOGLE_CLIENT_ID` | Google OAuth client ID | (none) |
| `UNRAID_RMCP_GOOGLE_CLIENT_SECRET` | Google OAuth client secret | (none) |
| `UNRAID_RMCP_AUTH_ADMIN_EMAIL` | Admin email for OAuth | (none) |
| `UNRAID_RMCP_ALLOWED_HOSTS` | Extra comma-separated Host headers | (none) |
| `UNRAID_RMCP_ALLOWED_ORIGINS` | Extra comma-separated CORS origins | (none) |

### Optional - Unraid API

| Variable | Description | Default |
|----------|-------------|---------|
| `UNRAID_API_SKIP_TLS_VERIFY` | Skip TLS cert verification | `false` |

Set to `true` if your Unraid API uses a self-signed certificate.

### Optional - Security

| Variable | Description | Default |
|----------|-------------|---------|
| `UNRAID_NOAUTH` | Permit non-loopback bind without auth | `false` |

**WARNING:** This is NOT the same as disabling auth. It only lifts the safety check that refuses a non-127.x bind in no-auth mode. The server still runs without auth.

### Optional - Logging

| Variable | Description | Default |
|----------|-------------|---------|
| `RUST_LOG` | Log filter (tracing-subscriber format) | `info` (server mode), `warn` (CLI/stdio) |

Examples:
- `RUST_LOG=debug` - verbose debugging
- `RUST_LOG=unraid_rmcp=debug` - debug only for this crate
- `RUST_LOG=warn` - warnings only

## Config files

### `~/.unraid/.env` (local) or `/data/.env` (container)

Loaded at startup via `dotenvy` before `Config::load`.

**Purpose:** Allow the binary to find credentials without a process manager injecting env vars.

**Behavior:**
- Symlink-guarded: a symlinked `.env` is refused (security)
- Non-overriding: already-set env vars are not overridden
- Path detection:
  - Containers: `/data/.env`
  - Local: `~/.unraid/.env`

**Example `.env`:**
```bash
UNRAID_API_URL="https://10-1-0-2.abcd.myunraid.net:31337/graphql"
UNRAID_API_KEY="your-api-key-here"
UNRAID_RMCP_PORT="40010"
UNRAID_RMCP_DISABLE_HTTP_AUTH="true"
```

### `config.toml` (optional)

Loaded from current directory or `~/.unraid/`. Less common than env vars—mostly used for complex OAuth setups.

**Structure:**
```toml
[mcp]
host = "0.0.0.0"
port = 40010
server_name = "unraid-rmcp"
no_auth = false
# api_token = "..." # or UNRAID_RMCP_TOKEN

[mcp.auth]
mode = "bearer"  # or "oauth"
public_url = "https://unraid.example.com"
google_client_id = "..."
google_client_secret = "..."
admin_email = "admin@example.com"
sqlite_path = "/data/auth.db"
key_path = "/data/jwt.pem"

[unraid]
api_url = "https://tower.local/graphql"
api_key = "your-api-key"
skip_tls_verify = false
```

**See:** `config.example.toml` for a full template.

### `server.json` (MCP registry)

MCP server descriptor for the Model Context Protocol registry.

**Purpose:** Published to MCP server registry, allows Claude Desktop to discover the server.

**Fields:**
- Server metadata (name, description, version, repository)
- OCI image reference
- Required environment variables with descriptions
- Remote endpoint (if hosting a public server)

## Data directory

**Location:**
- Containers: `/data/`
- Local: `~/.unraid/`

**Contents:**
- `.env` - Environment variables (optional)
- `auth.db` - OAuth token store (when `UNRAID_RMCP_AUTH_MODE=oauth`)
- `jwt.pem` - JWT signing key (auto-generated for OAuth)
- `unraid-rmcp.log.*` - JSON log files (when running in server mode)

**Detection logic (`config.rs::default_data_dir()`):**
```rust
if /.dockerenv exists || RUNNING_IN_CONTAINER=true {
    return "/data";
} else {
    return "$HOME/.unraid";
}
```

## Auth modes

### No auth (LoopbackDev)

**Active when:**
- Bound to loopback address (127.x, ::1, localhost), OR
- `UNRAID_RMCP_DISABLE_HTTP_AUTH=true`

**No credentials required.** Suitable for local development.

### Bearer token

**Active when:**
- `UNRAID_RMCP_TOKEN` is set AND not in loopback mode

**Usage:**
```bash
curl -X POST http://localhost:40010/mcp \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### OAuth (Google)

**Active when:**
- `UNRAID_RMCP_AUTH_MODE=oauth`
- OAuth credentials configured

**Required config:**
```bash
UNRAID_RMCP_AUTH_MODE=oauth
UNRAID_RMCP_PUBLIC_URL=https://unraid.example.com
UNRAID_RMCP_GOOGLE_CLIENT_ID=your-client-id
UNRAID_RMCP_GOOGLE_CLIENT_SECRET=your-client-secret
UNRAID_RMCP_AUTH_ADMIN_EMAIL=admin@example.com
```

**Behavior:**
- Uses `lab-auth` crate for JWT validation
- Scopes: `unraid:read` and `unraid:admin`
- JWKS endpoint at `/.well-known/jwks.json`
- Discovery metadata at `/.well-known/oauth-authorization-server`

## Plugin integration (Claude Code)

When running as a Claude Code plugin, environment variables are mapped from plugin options:

**`plugins/unraid/.claude-plugin/plugin.json`:**
```json
{
  "options": {
    "UNRAID_API_URL": {
      "type": "string",
      "displayName": "Unraid API URL"
    },
    "UNRAID_API_KEY": {
      "type": "string",
      "displayName": "API key",
      "secret": true
    }
  }
}
```

**At runtime:**
- Plugin hook passes `CLAUDE_PLUGIN_OPTION_UNRAID_API_URL`
- `src/cli/setup.rs::apply_plugin_options()` maps to `UNRAID_API_URL`

## Configuration loading order

1. **Load `~/.unraid/.env`** (or `/data/.env` in container) via `load_dotenv()`
2. **Parse `config.toml`** if present (via `Config::from_path()`)
3. **Read environment variables** (overrides config file)
4. **Apply defaults** for missing values

**Code reference:** `src/config.rs::Config::load()`

## Validation

**`runraid doctor`** checks:
- Config file syntax
- API URL format
- Data directory writable
- Port not already in use
- (Optional) Upstream connectivity

**Run:**
```bash
runraid doctor
```

## Source references

- Config structs: `src/config.rs`
- Env loading: `src/config.rs::load_dotenv()`, `Config::load()`
- Doctor command: `src/cli/doctor.rs`
- Example config: `config.example.toml`
- Example env: `.env.example`
