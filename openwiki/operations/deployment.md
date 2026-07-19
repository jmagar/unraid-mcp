# Deployment

How to install and run unrust in different environments.

## Quickstart (local development)

### Prerequisites

- Rust 1.90+ (`rustup show` or `curl https://sh.rustup.rs | sh`)
- Unraid API URL and API key (Settings → API Management in Unraid web UI)

### Install via one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/jmagar/runraid/main/install.sh | bash
```

**What it does:**
1. Runs pre-flight checks (OS/arch, tools, disk space, PATH)
2. Downloads latest release binary to `~/.local/bin/runraid` OR builds from source
3. Creates `~/.unraid/` data directory
4. Writes starter `~/.unraid/.env`
5. Runs `runraid doctor`
6. Prints next steps

**Installed binary:** `~/.local/bin/runraid`

**Data directory:** `~/.unraid/`

### Build from source

```bash
git clone https://github.com/jmagar/runraid
cd unrust
cargo build --release

# Binary at target/release/runraid
```

### Configure

**Create `~/.unraid/.env`:**
```bash
export UNRAID_API_URL="https://10-1-0-2.<hash>.myunraid.net:31337/graphql"
export UNRAID_API_KEY="your-api-key-here"
export UNRAID_RMCP_PORT="40010"
export UNRAID_RMCP_DISABLE_HTTP_AUTH="true"

# If using self-signed cert
export UNRAID_API_SKIP_TLS_VERIFY="true"
```

Or copy the example:
```bash
cp .env.example ~/.unraid/.env
# Edit ~/.unraid/.env with your credentials
```

### Run

```bash
# Start HTTP MCP server
runraid serve mcp
# or just
runraid

# Verify
curl -sf http://localhost:40010/health | jq .
# → {"status":"ok"}

# First MCP call
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
  }' | jq .
```

## Docker deployment

### Build image

```bash
docker build -f config/Dockerfile -t unrust:latest .
```

### Run with docker-compose

```yaml
# docker-compose.yml
services:
  unraid-rmcp:
    image: unrust:latest
    ports:
      - "40010:40010"
    environment:
      UNRAID_API_URL: "https://tower.local/graphql"
      UNRAID_API_KEY: "your-api-key"
      UNRAID_RMCP_DISABLE_HTTP_AUTH: "true"
      UNRAID_API_SKIP_TLS_VERIFY: "true"  # if self-signed
    volumes:
      - unraid-data:/data

volumes:
  unraid-data:
```

**Run:**
```bash
docker-compose up -d
```

### Run with Docker CLI

```bash
docker run -d \
  --name runraid \
  -p 40010:40010 \
  -e UNRAID_API_URL="https://tower.local/graphql" \
  -e UNRAID_API_KEY="your-api-key" \
  -e UNRAID_RMCP_DISABLE_HTTP_AUTH="true" \
  -e UNRAID_API_SKIP_TLS_VERIFY="true" \
  -v unraid-data:/data \
  unrust:latest
```

**Data directory in containers:** `/data/`

**Log files:** Written to `/data/unraid-rmcp.log.*`

## Production deployment

### Systemd service

**Create `/etc/systemd/system/unraid-rmcp.service`:**
```ini
[Unit]
Description=Unraid MCP Server
After=network.target

[Service]
Type=simple
User=unraid
Group=unraid
WorkingDirectory=/opt/unraid-rmcp
Environment="UNRAID_API_URL=https://tower.local/graphql"
Environment="UNRAID_API_KEY=your-api-key"
Environment="UNRAID_RMCP_PORT=40010"
Environment="UNRAID_RMCP_TOKEN=your-bearer-token"
EnvironmentFile=/opt/unraid-rmcp/.env
ExecStart=/opt/unraid-rmcp/runraid serve mcp
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable unraid-rmcp
sudo systemctl start unraid-rmcp
sudo systemctl status unraid-rmcp
```

### Reverse proxy (Nginx)

**Config:**
```nginx
upstream unraid_rmcp {
    server 127.0.0.1:40010;
}

server {
    listen 443 ssl;
    server_name unraid.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /mcp {
        proxy_pass http://unraid_rmcp;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_set_header Connection "";
        proxy_buffering off;
        chunked_transfer_encoding off;
    }

    location /health {
        proxy_pass http://unraid_rmcp;
        access_log off;
    }
}
```

### OAuth production setup

**Environment:**
```bash
UNRAID_RMCP_AUTH_MODE=oauth
UNRAID_RMCP_PUBLIC_URL=https://unraid.example.com
UNRAID_RMCP_GOOGLE_CLIENT_ID=your-client-id
UNRAID_RMCP_GOOGLE_CLIENT_SECRET=your-client-secret
UNRAID_RMCP_AUTH_ADMIN_EMAIL=admin@example.com
```

**Google OAuth app setup:**
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Authorized redirect URI: `https://unraid.example.com/callback`
3. Authorized JavaScript origin: `https://unraid.example.com`
4. Copy Client ID and Secret to env vars

**JWT key:** Auto-generated on first run at `/data/jwt.pem` (or `~/.unraid/jwt.pem`)

**Token store:** SQLite at `/data/auth.db` (or `~/.unraid/auth.db`)

### Health monitoring

**Health endpoint:** `GET /health`

**Response:**
```json
{"status":"ok"}
```

**Failure (upstream down):**
```json
{"status":"error","message":"Unraid API unreachable"}
```

**Monitoring example:**
```bash
# Check every minute
watch -n 60 'curl -sf http://localhost:40010/health | jq .'

# Prometheus scrape config
scrape_configs:
  - job_name: 'unraid-rmcp'
    static_configs:
      - targets: ['localhost:40010']
    metrics_path: '/health'
```

### Log aggregation

**Log files:** `~/.unraid/unraid-rmcp.log.*` (JSON format, rotated)

**Example log entry:**
```json
{
  "timestamp": "2026-06-15T12:34:56.789Z",
  "level": "INFO",
  "message": "tools/call succeeded",
  "target": "unraid_rmcp::mcp::tools",
  "action": "server",
  "duration_ms": 234
}
```

**Log aggregation options:**
- Forward to Loki via promtail
- Parse with Fluent Bit
- Ship to Elasticsearch via Filebeat

## Claude Code integration

### Install as MCP server

**Add to `~/.claude/mcp_servers.json` or project `.mcp.json`:**
```json
{
  "mcpServers": {
    "unraid": {
      "command": "/path/to/runraid",
      "args": ["mcp"],
      "env": {
        "UNRAID_API_URL": "https://tower.local/graphql",
        "UNRAID_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Install as Claude Code plugin

**Plugin directory:** `plugins/unraid/`

**Plugin manifest:** `plugins/unraid/.claude-plugin/plugin.json`

**Install via Claude Code:**
1. Open Claude Code settings
2. Browse plugins
3. Install "unraid-rmcp"

**Plugin environment variables** set via Claude Code UI map to standard env vars at runtime.

## Transport modes

### HTTP MCP (default)

**Start:** `runraid serve mcp`

**Bind:** `0.0.0.0:40010` (configurable)

**Use case:** Claude Desktop, remote clients, reverse proxy

### stdio MCP

**Start:** `runraid mcp`

**Use case:** Claude Code, MCP clients that spawn the server as a child process

### CLI

**Start:** `runraid <command>`

**Use case:** Human interaction, scripts

## Upgrades

### Upgrade via one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/jmagar/runraid/main/install.sh | bash
```

### Upgrade via cargo

```bash
cargo install --force --path .
```

### Upgrade via Docker

```bash
docker pull ghcr.io/jmagar/runraid:latest
docker stop unraid-rmcp
docker rm unraid-rmcp
# Run with new image
```

### Zero-downtime upgrade (systemd)

```bash
# Pull new binary
sudo systemctl stop unraid-rmcp
curl -fsSL https://github.com/jmagar/runraid/releases/latest/download/runraid-amd64 -o /opt/unraid-rmcp/runraid
chmod +x /opt/unraid-rmcp/runraid
sudo systemctl start unraid-rmcp
```

## Source references

- Install script: `install.sh`
- Dockerfile: `config/Dockerfile`
- Docker compose: `docker-compose.yml`, `docker-compose.prod.yml`
- Systemd service template: (create in `/etc/systemd/system/`)
- Config examples: `config.example.toml`, `.env.example`
