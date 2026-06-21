# Deployment Guide

Deployment patterns for unraid-mcp. Choose the method that fits your environment.

## Local Development

```bash
# Install dependencies
uv sync --dev

# Start server (streamable-http on port 6970)
uv run unraid-mcp-server

# Or via Justfile
just dev
```

The server reads credentials from `~/.unraid-mcp/.env`. Create this file from `.env.example`, or (as a Claude Code plugin) set the credential fields in the plugin config form so the setup hook writes them for you.

## Docker Compose (recommended for production)

### Quick start

```bash
just up
```

### Manual

```bash
docker compose up -d
```

### Configuration

The `docker-compose.yaml` provides:

- **Multi-stage build**: Builder (uv + dependencies) and runtime (Python 3.12 slim)
- **Non-root user**: Runs as `mcp:1000`
- **Resource limits**: 1024 MB memory, 1.0 CPU
- **Named volume**: `unraid-mcp-credentials` for `~/.unraid-mcp/`
- **Health check**: HTTP `GET /health` every 30s (auto-skips for stdio transport)
- **External network**: Optional `DOCKER_NETWORK` for service mesh integration

### Environment

The container reads from `~/.claude-homelab/.env` via `env_file`. Required variables:

```bash
UNRAID_API_URL=https://your-unraid-server
UNRAID_API_KEY=your_api_key
UNRAID_MCP_BEARER_TOKEN=your_bearer_token
```

### Volumes

| Volume | Container path | Purpose |
|--------|---------------|---------|
| `./logs` | `/app/logs` | Application logs |
| `./backups` | `/app/backups` | Flash backup storage |
| `unraid-mcp-credentials` | `/home/mcp/.unraid-mcp` | Credential persistence |

## Docker standalone

```bash
# Build
docker build -t unraid-mcp .

# Run
docker run -d \
  --name unraid-mcp \
  -p 6970:6970 \
  -e UNRAID_API_URL=https://your-unraid-server \
  -e UNRAID_API_KEY=your_api_key \
  -e UNRAID_MCP_BEARER_TOKEN=your_bearer_token \
  -v unraid-mcp-credentials:/home/mcp/.unraid-mcp \
  unraid-mcp
```

## PyPI package

```bash
# Install globally
pip install unraid-mcp

# Run
unraid-mcp-server

# Or via uvx (no install needed)
uvx unraid-mcp
```

## GitHub Container Registry

```bash
docker pull ghcr.io/jmagar/unraid-mcp:latest
```

Available tags: `latest`, `main`, `v1.2.3`, `v1.2`, `v1`, `sha-<commit>`.

Multi-arch: `linux/amd64` and `linux/arm64`.

## Entrypoint validation

The `entrypoint.sh` validates required environment variables before starting the server:

- `UNRAID_API_URL` -- always required
- `UNRAID_API_KEY` -- always required
- `UNRAID_MCP_BEARER_TOKEN` -- required for HTTP transport with auth enabled

If any are missing, the container exits with a descriptive error listing the missing variables.

## Behind a reverse proxy

For SWAG, nginx, or Traefik:

1. Set `UNRAID_MCP_DISABLE_HTTP_AUTH=true` (the proxy handles auth)
2. Proxy to `http://unraid-mcp:6970/mcp`
3. Ensure WebSocket upgrade headers are forwarded for subscription support

See `docs/unraid.subdomain.conf` for a SWAG nginx example.

### `DISABLE_HTTP_AUTH=true` trust boundary

Disabling bearer auth removes the server's only inbound authentication. It is **only** safe
when a fronting gateway terminates auth in front of it. Enforce the boundary at deploy time:

- **A fronting gateway is required.** Never expose the server with auth disabled directly to
  an untrusted network.
- **Do not publish the container port to the host's public interface.** In
  `docker-compose.yaml`, either omit the `ports:` mapping entirely (reach the server only
  over the internal `DOCKER_NETWORK` the gateway shares) or scope it to loopback, e.g.
  `ports: ["127.0.0.1:6970:6970"]`. A published `0.0.0.0` port + disabled auth is an open
  endpoint.
- **`UNRAID_MCP_TRUST_PROXY=true` is required to bind a public (non-loopback) interface**
  while auth is disabled — it is the explicit acknowledgement that a trusted proxy sits in
  front. Without it, the server refuses to bind publicly with auth off.

## See Also

- [TRANSPORT.md](TRANSPORT.md) -- Transport-specific configuration
- [AUTH.md](AUTH.md) -- Bearer token setup
- [CONNECT.md](CONNECT.md) -- Client connection guides
- [../CONFIG.md](../CONFIG.md) -- Full environment variable reference
