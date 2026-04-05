# Unraid MCP

<!-- mcp-name: tv.tootie/unraid-mcp -->

[![PyPI](https://img.shields.io/pypi/v/unraid-mcp)](https://pypi.org/project/unraid-mcp/) [![ghcr.io](https://img.shields.io/badge/ghcr.io-jmagar%2Funraid--mcp-blue?logo=docker)](https://github.com/jmagar/unraid-mcp/pkgs/container/unraid-mcp)

MCP server for Unraid NAS management. Exposes a unified `unraid` action router with 15 action domains and 107 subactions, plus `unraid_help` and two diagnostic tools, all backed by Unraid's GraphQL API and real-time WebSocket subscriptions.

## Overview

Four MCP tools are exposed:

| Tool | Purpose |
| --- | --- |
| `unraid` | Unified action router for all Unraid operations (15 domains, 107 subactions) |
| `unraid_help` | Returns markdown documentation for all actions and parameters |
| `diagnose_subscriptions` | Inspect WebSocket subscription connection states and errors |
| `test_subscription_query` | Test a specific GraphQL subscription query against allowlisted fields |

The server supports streamable-http (default), SSE (deprecated), and stdio transports. HTTP transports require RFC 6750 bearer authentication via `UNRAID_MCP_BEARER_TOKEN`.

## What this repository ships

- `unraid_mcp/server.py`: FastMCP server with 4-layer middleware chain and ASGI bearer auth
- `unraid_mcp/tools/`: 16 domain modules (array, customization, disk, docker, health, key, live, notification, oidc, plugin, rclone, setting, system, user, vm) plus the consolidated `unraid.py` router
- `unraid_mcp/subscriptions/`: WebSocket subscription manager, resource registration, diagnostics, and snapshot queries
- `unraid_mcp/core/`: GraphQL client, elicitation-based setup, destructive action guards, auth middleware
- `unraid_mcp/config/`: Settings management and structured logging
- `skills/unraid/SKILL.md`: Client-facing skill documentation
- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`: Client manifests
- `docker-compose.yaml`, `Dockerfile`, `entrypoint.sh`: Container deployment
- `scripts/`: Security checks, dependency audits, and plugin validation
- `hooks/`: Post-tool hooks for env permissions and gitignore enforcement

## Tools

### `unraid`

Single entry point for all Unraid operations. Select the operation with `action` + `subaction`.

| Action | Subactions | Description |
| --- | --- | --- |
| `system` (18) | `overview`, `array`, `network`, `registration`, `variables`, `metrics`, `services`, `display`, `config`, `online`, `owner`, `settings`, `server`, `servers`, `flash`, `ups_devices`, `ups_device`, `ups_config` | Server info, metrics, network, UPS |
| `health` (4) | `check`, `test_connection`, `diagnose`, `setup` | Health checks, connection test, credential setup |
| `array` (13) | `parity_status`, `parity_history`, `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`, `start_array`, `stop_array`\*, `add_disk`, `remove_disk`\*, `mount_disk`, `unmount_disk`, `clear_disk_stats`\* | Parity checks, array lifecycle, disk operations |
| `disk` (6) | `shares`, `disks`, `disk_details`, `log_files`, `logs`, `flash_backup`\* | Shares, physical disks, log files |
| `docker` (7) | `list`, `details`, `start`, `stop`, `restart`, `networks`, `network_details` | Container lifecycle and network inspection |
| `vm` (9) | `list`, `details`, `start`, `stop`, `pause`, `resume`, `force_stop`\*, `reboot`, `reset`\* | Virtual machine lifecycle |
| `notification` (12) | `overview`, `list`, `create`, `archive`, `mark_unread`, `recalculate`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`\*, `delete_archived`\* | Notification CRUD |
| `key` (7) | `list`, `get`, `create`, `update`, `delete`\*, `add_role`, `remove_role` | API key management |
| `plugin` (3) | `list`, `add`, `remove`\* | Plugin management |
| `rclone` (4) | `list_remotes`, `config_form`, `create_remote`, `delete_remote`\* | Cloud storage remotes |
| `setting` (2) | `update`, `configure_ups`\* | System settings and UPS config |
| `customization` (5) | `theme`, `public_theme`, `is_initial_setup`, `sso_enabled`, `set_theme` | Theme and UI customization |
| `oidc` (5) | `providers`, `provider`, `configuration`, `public_providers`, `validate_session` | OIDC/SSO provider management |
| `user` (1) | `me` | Current authenticated user |
| `live` (11) | `cpu`, `memory`, `cpu_telemetry`, `array_state`, `parity_progress`, `ups_status`, `notifications_overview`, `notification_feed`, `log_tail`, `owner`, `server_status` | Real-time WebSocket subscription snapshots |

\* Destructive -- requires `confirm=True`

### `unraid_help`

Returns the full action reference as Markdown. Call this to discover available actions.

```python
unraid_help()
```

## Installation

### Marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install unraid-mcp @jmagar-claude-homelab
```

### Local development

```bash
uv sync --dev
uv run unraid-mcp-server
```

### Docker

```bash
just up
```

Or manually:

```bash
docker compose up -d
```

## Authentication

The MCP server uses bearer token authentication for HTTP transports (streamable-http, SSE).

A token is auto-generated on first HTTP startup if none is configured. It is written to `~/.unraid-mcp/.env`.

To generate manually:

```bash
openssl rand -hex 32
```

Set it in `~/.unraid-mcp/.env`:

```bash
UNRAID_MCP_BEARER_TOKEN=<generated-token>
```

Configure your MCP client to send the token as a Bearer header. See [AUTH](mcp/AUTH.md) for detailed setup.

To disable auth (only behind a trusted reverse proxy):

```bash
UNRAID_MCP_DISABLE_HTTP_AUTH=true
```

## Configuration

Copy `.env.example` to `~/.unraid-mcp/.env` and fill in the required values:

```bash
mkdir -p ~/.unraid-mcp
cp .env.example ~/.unraid-mcp/.env
chmod 600 ~/.unraid-mcp/.env
```

Or use the interactive setup wizard:

```python
unraid(action="health", subaction="setup")
```

### Environment variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `UNRAID_API_URL` | yes | -- | Unraid GraphQL endpoint (e.g. `https://tower.local/graphql`) |
| `UNRAID_API_KEY` | yes | -- | Unraid API key (Settings > Management Access > API Keys) |
| `UNRAID_MCP_BEARER_TOKEN` | yes\* | auto-generated | Bearer token for MCP HTTP auth |
| `UNRAID_MCP_PORT` | no | `6970` | Port for the MCP HTTP server |

\*Required when `UNRAID_MCP_TRANSPORT != stdio` and `UNRAID_MCP_DISABLE_HTTP_AUTH != true`.

See [CONFIG](CONFIG.md) for all variables including logging, SSL, subscriptions, and Docker settings.

## Quick start

```python
# First-time setup
unraid(action="health", subaction="setup")

# System overview
unraid(action="system", subaction="overview")

# Health check
unraid(action="health", subaction="check")

# List Docker containers
unraid(action="docker", subaction="list")

# Restart a container
unraid(action="docker", subaction="restart", container_id="plex")

# Parity status
unraid(action="array", subaction="parity_status")

# Live CPU monitoring
unraid(action="live", subaction="cpu")

# Stop array (destructive)
unraid(action="array", subaction="stop_array", confirm=True)
```

## Docker usage

```bash
# Build and start
just up

# View logs
just logs

# Health check
just health
# or: curl http://localhost:6970/health

# Stop
just down
```

The `/health` endpoint is unauthenticated for liveness probes.

## Related plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [homelab-core](https://github.com/jmagar/claude-homelab) | core | Core agents, commands, skills, and setup/health workflows for homelab management. |
| [overseerr-mcp](https://github.com/jmagar/overseerr-mcp) | media | Search movies and TV shows, submit requests, and monitor failed requests via Overseerr. |
| [unifi-mcp](https://github.com/jmagar/unifi-mcp) | infrastructure | Monitor and manage UniFi devices and network health. |
| [swag-mcp](https://github.com/jmagar/swag-mcp) | infrastructure | Manage SWAG nginx reverse proxy configurations. |
| [synapse-mcp](https://github.com/jmagar/synapse-mcp) | infrastructure | Docker management and SSH remote operations across homelab hosts. |
| [arcane-mcp](https://github.com/jmagar/arcane-mcp) | infrastructure | Manage Docker environments, containers, images, volumes, and networks. |
| [syslog-mcp](https://github.com/jmagar/syslog-mcp) | infrastructure | Receive, index, and search syslog streams via SQLite FTS5. |
| [gotify-mcp](https://github.com/jmagar/gotify-mcp) | utilities | Send push notifications and manage Gotify messages and applications. |
| [plugin-lab](https://github.com/jmagar/plugin-lab) | dev-tools | Scaffold, review, align, and deploy homelab MCP plugins. |
| [axon](https://github.com/jmagar/axon) | research | Self-hosted web crawl, ingest, embed, and RAG pipeline with MCP tooling. |

## License

MIT
