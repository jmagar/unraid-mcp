# Unraid MCP

<!-- mcp-name: tv.tootie/unraid-mcp -->

[![PyPI](https://img.shields.io/pypi/v/unraid-mcp)](https://pypi.org/project/unraid-mcp/) [![ghcr.io](https://img.shields.io/badge/ghcr.io-jmagar%2Funraid--mcp-blue?logo=docker)](https://github.com/jmagar/unraid-mcp/pkgs/container/unraid-mcp)

GraphQL-backed MCP server for Unraid. Exposes a unified `unraid` tool for system inspection, management operations, live telemetry, and destructive actions gated by explicit confirmation.

## Overview

The server translates MCP tool calls into Unraid GraphQL queries and mutations over HTTP and WebSocket. All operations share a single `unraid` tool routed by `action` + `subaction`. Live telemetry uses WebSocket subscriptions that stream real-time data from the Unraid API.

## What this repository ships

- `unraid_mcp/` — server, GraphQL client, WebSocket subscriptions, config, and tool handlers
- `skills/unraid/` — client-facing skill docs
- `docs/` — authentication, destructive-action, and publishing references
- `.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json` — client manifests
- `docker-compose.yaml`, `Dockerfile`, `entrypoint.sh` — container deployment
- `tests/` — unit, safety, schema, HTTP-layer, and live coverage

## Tools

### Tool index

| Tool | Purpose |
| --- | --- |
| `unraid` | Unified action/subaction router for all operations |
| `unraid_help` | Returns this reference as Markdown |
| `diagnose_subscriptions` | Full diagnostic dump of the WebSocket subscription system |
| `test_subscription_query` | Probe a raw GraphQL subscription for schema/debug work |

### `unraid` — action groups

All operations go through one tool. Pick an `action`, then a `subaction` within it.

#### `system` — 18 subactions

Server information, metrics, network, and UPS.

| Subaction | Description | Required params |
| --- | --- | --- |
| `overview` | OS, CPU, memory layout, versions, machine ID | — |
| `array` | Array state, capacity, disk health summary | — |
| `network` | Access URLs, HTTP/HTTPS ports, LAN/WAN IPs | — |
| `registration` | License type, key file, expiration | — |
| `variables` | Full Unraid variable set (timezone, shares, etc.) | — |
| `metrics` | Live CPU % and memory usage | — |
| `services` | Running services with name, online status, version | — |
| `display` | Current UI theme name | — |
| `config` | Config validity and error state | — |
| `online` | Boolean reachability check | — |
| `owner` | Owner username, avatar, profile URL | — |
| `settings` | Unified settings key/value map | — |
| `server` | Single-call summary: hostname, uptime, Unraid version, array state | — |
| `servers` | All registered servers with LAN/WAN IPs and URLs | — |
| `flash` | Flash drive vendor and product info | — |
| `ups_devices` | All UPS devices with battery and power metrics | — |
| `ups_device` | Single UPS device details | `device_id` |
| `ups_config` | UPS daemon configuration | — |

#### `health` — 4 subactions

Connection and system health diagnostics.

| Subaction | Description | Required params |
| --- | --- | --- |
| `check` | Comprehensive health: API latency, array state, alerts, Docker container summary | — |
| `test_connection` | Ping the Unraid API and return latency in ms | — |
| `diagnose` | Subscription system status, error counts, reconnect state | — |
| `setup` | Interactive credential setup (supports MCP elicitation) | — |

#### `array` — 13 subactions

Parity checks and array disk operations. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `parity_status` | Current parity check progress, speed, errors | — | — |
| `parity_history` | Past parity check results | — | — |
| `parity_start` | Start a parity check | `correct` (bool) | — |
| `parity_pause` | Pause a running parity check | — | — |
| `parity_resume` | Resume a paused parity check | — | — |
| `parity_cancel` | Cancel a running parity check | — | — |
| `start_array` | Start the Unraid array | — | — |
| `stop_array` | Stop the Unraid array | `confirm=True` | * |
| `add_disk` | Add a disk to the array | `disk_id`; optional `slot` | — |
| `remove_disk` | Remove a disk from the array (array must be stopped) | `disk_id`, `confirm=True` | * |
| `mount_disk` | Mount an array disk | `disk_id` | — |
| `unmount_disk` | Unmount an array disk | `disk_id` | — |
| `clear_disk_stats` | Clear I/O statistics for a disk (irreversible) | `disk_id`, `confirm=True` | * |

#### `disk` — 6 subactions

Shares, physical disks, log files, and flash backup. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `shares` | All user shares with size, allocation settings, LUKS status | — | — |
| `disks` | Physical disk list (ID, device, name) | — | — |
| `disk_details` | Single disk: serial, size, temperature | `disk_id` | — |
| `log_files` | List available log files (name, path, size, modified) | — | — |
| `logs` | Read log file content with line range | `log_path`; optional `tail_lines` (default 100, max 10000) | — |
| `flash_backup` | Initiate rclone backup of the flash drive to a remote | `remote_name`, `source_path` (must start with `/boot`), `destination_path`, `confirm=True` | * |

**`flash_backup` details:** Calls the Unraid `initiateFlashBackup` GraphQL mutation, which triggers an rclone copy from the flash drive to a configured rclone remote. The destination on the remote is overwritten if it exists. Returns `{ status, jobId }`. To restore: use rclone to copy the backup back to the flash drive, or extract individual config files. Configure the rclone remote first via `rclone/create_remote`.

#### `docker` — 7 subactions

Container lifecycle and network inspection. No destructive subactions.

| Subaction | Description | Required params |
| --- | --- | --- |
| `list` | All containers: ID, names, image, state, status, autoStart | — |
| `details` | Full container detail: ports, mounts, labels, network settings | `container_id` |
| `start` | Start a container | `container_id` |
| `stop` | Stop a container | `container_id` |
| `restart` | Stop then start a container (stop + start in sequence) | `container_id` |
| `networks` | All Docker networks: ID, name, driver, scope | — |
| `network_details` | Single network with IPv6, containers, options, labels | `network_id` |

Container identifiers accept full ID, short ID prefix, exact name, or unambiguous name prefix. Mutations (`start`, `stop`, `restart`) require an exact name or full ID.

#### `vm` — 9 subactions

Virtual machine lifecycle. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `list` | All VMs: ID, name, state, UUID | — | — |
| `details` | Single VM details | `vm_id` | — |
| `start` | Start a VM | `vm_id` | — |
| `stop` | Gracefully stop a VM | `vm_id` | — |
| `pause` | Pause a running VM | `vm_id` | — |
| `resume` | Resume a paused VM | `vm_id` | — |
| `reboot` | Reboot a VM | `vm_id` | — |
| `force_stop` | Hard power-off a VM (data loss possible) | `vm_id`, `confirm=True` | * |
| `reset` | Hard reset a VM without graceful shutdown | `vm_id`, `confirm=True` | * |

`vm_id` accepts UUID, prefixed ID, or VM name.

#### `notification` — 12 subactions

System notification CRUD. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `overview` | Unread and archive counts by importance (INFO/WARNING/ALERT) | — | — |
| `list` | Paginated notification list | `list_type` (UNREAD or ARCHIVE, default UNREAD); optional `importance`, `offset`, `limit` | — |
| `create` | Create a notification | `title` (≤200), `subject` (≤500), `description` (≤2000), `importance` (INFO/WARNING/ALERT) | — |
| `archive` | Archive a single notification | `notification_id` | — |
| `mark_unread` | Move an archived notification back to unread | `notification_id` | — |
| `recalculate` | Recalculate the overview counts | — | — |
| `archive_all` | Archive all unread notifications | optional `importance` to filter | — |
| `archive_many` | Archive specific notifications by ID | `notification_ids` (list) | — |
| `unarchive_many` | Unarchive specific notifications by ID | `notification_ids` (list) | — |
| `unarchive_all` | Move all archived notifications back to unread | optional `importance` to filter | — |
| `delete` | Permanently delete a single notification | `notification_id`, `notification_type`, `confirm=True` | * |
| `delete_archived` | Permanently delete all archived notifications | `confirm=True` | * |

#### `key` — 7 subactions

API key management. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `list` | All API keys with roles and permissions | — | — |
| `get` | Single API key details | `key_id` | — |
| `create` | Create an API key | `name`; optional `roles`, `permissions` | — |
| `update` | Update name, roles, or permissions | `key_id`; optional `name`, `roles`, `permissions` | — |
| `delete` | Delete an API key (immediately revokes access) | `key_id`, `confirm=True` | * |
| `add_role` | Add a role to an existing key | `key_id`, `roles` (first element used) | — |
| `remove_role` | Remove a role from an existing key | `key_id`, `roles` (first element used) | — |

#### `plugin` — 3 subactions

Unraid plugin management. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `list` | All installed plugins with version and module flags | — | — |
| `add` | Install plugins by name | `names` (list); optional `bundled`, `restart` | — |
| `remove` | Uninstall plugins by name (irreversible without re-install) | `names` (list), `confirm=True` | * |

#### `rclone` — 4 subactions

Cloud storage remote management. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `list_remotes` | All configured rclone remotes with type and parameters | — | — |
| `config_form` | Config form schema for a provider type | optional `provider_type` | — |
| `create_remote` | Create a new rclone remote | `name`, `provider_type`, `config_data` (dict of string/number/bool; max 50 keys) | — |
| `delete_remote` | Delete a rclone remote config (does not delete remote data) | `name`, `confirm=True` | * |

#### `setting` — 2 subactions

System settings. Destructive subactions marked with *.

| Subaction | Description | Required params | Destructive |
| --- | --- | --- | --- |
| `update` | Update system settings (JSON key/value input) | `settings_input` (dict; max 100 keys, scalar values only) | — |
| `configure_ups` | Overwrite UPS monitoring configuration | `ups_config` (dict), `confirm=True` | * |

#### `customization` — 5 subactions

UI theme and SSO state.

| Subaction | Description | Required params |
| --- | --- | --- |
| `theme` | Full theme, partner info, and activation code | — |
| `public_theme` | Public-facing theme and partner info (unauthenticated view) | — |
| `is_initial_setup` | Whether initial setup wizard has been completed | — |
| `sso_enabled` | Whether SSO is enabled | — |
| `set_theme` | Set the active UI theme | `theme_name` |

#### `oidc` — 5 subactions

OpenID Connect / SSO provider management.

| Subaction | Description | Required params |
| --- | --- | --- |
| `providers` | All OIDC providers with client ID, scopes, auth rules | — |
| `provider` | Single provider details | `provider_id` |
| `configuration` | OIDC configuration with default allowed origins | — |
| `public_providers` | Public provider list (button text, icon, style) | — |
| `validate_session` | Validate an OIDC session token | `token` |

#### `user` — 1 subaction

| Subaction | Description | Required params |
| --- | --- | --- |
| `me` | Authenticated user: ID, name, description, roles | — |

#### `live` — 11 subactions (WebSocket subscriptions)

The `live` action group reads from active WebSocket subscriptions to the Unraid GraphQL API. Instead of issuing HTTP queries, it opens a `graphql-transport-ws` connection and either waits for one snapshot or collects events over a window.

Two delivery modes:

- **Snapshot** (`SNAPSHOT_ACTIONS`): opens a subscription and returns the first message received within `timeout` seconds. For event-driven subactions (`parity_progress`, `ups_status`, `notifications_overview`, `owner`, `server_status`), a timeout means no recent state change — not an error.
- **Collect** (`COLLECT_ACTIONS`): opens a subscription and accumulates all events for `collect_for` seconds, then returns the full event list. Used for streaming data like log lines and notification feeds.

| Subaction | Mode | Description | Required params |
| --- | --- | --- | --- |
| `cpu` | Snapshot | CPU utilization: total % and per-core breakdown | — |
| `memory` | Snapshot | Memory: total, used, free, swap, percentages | — |
| `cpu_telemetry` | Snapshot | CPU power draw and temperature | — |
| `array_state` | Snapshot | Array state, capacity, parity check status | — |
| `parity_progress` | Snapshot (event-driven) | Parity check progress, speed, errors | — |
| `ups_status` | Snapshot (event-driven) | UPS battery, charge, runtime, power load | — |
| `notifications_overview` | Snapshot (event-driven) | Notification counts by importance | — |
| `owner` | Snapshot (event-driven) | Owner profile changes | — |
| `server_status` | Snapshot (event-driven) | Server registration and connectivity | — |
| `log_tail` | Collect | Stream log file lines | `path` (must start with `/var/log/` or `/boot/logs/`) |
| `notification_feed` | Collect | Stream incoming notifications | — |

Optional parameters for `live`:

- `collect_for` (float, default `5.0`) — collection window in seconds for collect-mode subactions
- `timeout` (float, default `10.0`) — WebSocket receive timeout in seconds

### `diagnose_subscriptions`

Returns a full diagnostic dump of the subscription system: auto-start status, reconnect configuration, per-subscription state (active, last error, data received), error counts, and troubleshooting recommendations. Useful when `live` subactions return no data.

### `test_subscription_query`

Accepts a raw GraphQL subscription string and sends it directly over WebSocket. Validates the query first — must be a `subscription` operation targeting one of the whitelisted fields: `logFile`, `containerStats`, `cpu`, `memory`, `array`, `network`, `docker`, `vm`. Mutation and query keywords are rejected. Returns the first message received or a note that the subscription is waiting for events.

### Destructive actions summary

All destructive actions require `confirm=True`. Omitting it or passing `confirm=False` raises a `ToolError` before any network request is made.

| Action | Subaction | Notes |
| --- | --- | --- |
| `array` | `stop_array` | Unmounts shares; stop containers and VMs first |
| `array` | `remove_disk` | Array must be stopped first |
| `array` | `clear_disk_stats` | I/O stats are permanently erased |
| `vm` | `force_stop` | Hard power-off; unsaved data may be lost |
| `vm` | `reset` | Hard reset; unsaved data may be lost |
| `notification` | `delete` | Permanent; requires `notification_type` |
| `notification` | `delete_archived` | Wipes all archived notifications |
| `rclone` | `delete_remote` | Removes config only; does not delete remote data |
| `key` | `delete` | Immediately revokes all clients using that key |
| `disk` | `flash_backup` | Overwrites destination; configure a dedicated remote |
| `setting` | `configure_ups` | Overwrites UPS daemon config |
| `plugin` | `remove` | Irreversible without re-install |

### Tool parameters reference

| Parameter | Type | Used by |
| --- | --- | --- |
| `action` | str | all |
| `subaction` | str | all |
| `confirm` | bool (default `False`) | destructive subactions |
| `device_id` | str | `system/ups_device` |
| `disk_id` | str | `array`, `disk` |
| `correct` | bool | `array/parity_start` |
| `slot` | int | `array/add_disk` |
| `log_path` | str | `disk/logs` |
| `tail_lines` | int (default 100, max 10000) | `disk/logs` |
| `remote_name` | str | `disk/flash_backup` |
| `source_path` | str | `disk/flash_backup` |
| `destination_path` | str | `disk/flash_backup` |
| `backup_options` | dict | `disk/flash_backup` |
| `container_id` | str | `docker` mutations and `details` |
| `network_id` | str | `docker/network_details` |
| `vm_id` | str | `vm` (all except `list`) |
| `notification_id` | str | `notification/archive`, `mark_unread`, `delete` |
| `notification_ids` | list[str] | `notification/archive_many`, `unarchive_many` |
| `notification_type` | str (UNREAD/ARCHIVE) | `notification/delete` |
| `importance` | str (INFO/WARNING/ALERT) | `notification` filter and create |
| `list_type` | str (UNREAD/ARCHIVE, default UNREAD) | `notification/list` |
| `title` | str (≤200) | `notification/create` |
| `subject` | str (≤500) | `notification/create` |
| `description` | str (≤2000) | `notification/create` |
| `offset` | int (default 0) | `notification/list` |
| `limit` | int (default 20) | `notification/list` |
| `key_id` | str | `key` subactions |
| `name` | str | `key/create`, `key/update`, `rclone` |
| `roles` | list[str] | `key` subactions |
| `permissions` | list[str] | `key` subactions |
| `names` | list[str] | `plugin/add`, `plugin/remove` |
| `bundled` | bool (default `False`) | `plugin/add`, `plugin/remove` |
| `restart` | bool (default `True`) | `plugin/add`, `plugin/remove` |
| `provider_type` | str | `rclone/config_form`, `rclone/create_remote` |
| `config_data` | dict | `rclone/create_remote` |
| `settings_input` | dict | `setting/update` |
| `ups_config` | dict | `setting/configure_ups` |
| `theme_name` | str | `customization/set_theme` |
| `provider_id` | str | `oidc/provider` |
| `token` | str | `oidc/validate_session` |
| `path` | str | `live/log_tail` |
| `collect_for` | float (default `5.0`) | `live` collect-mode subactions |
| `timeout` | float (default `10.0`) | `live` all subactions |

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

Equivalent entrypoints:

```bash
uv run unraid-mcp
uv run python -m unraid_mcp
```

### Docker

```bash
docker compose up -d
```

## Configuration

Create `.env` from `.env.example`:

```bash
just setup
```

### Environment variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `UNRAID_API_URL` | Yes | — | GraphQL endpoint URL, e.g. `https://tower.local/graphql` |
| `UNRAID_API_KEY` | Yes | — | Unraid API key (see below) |
| `UNRAID_MCP_TRANSPORT` | No | `streamable-http` | Transport: `streamable-http`, `stdio`, or `sse` (deprecated) |
| `UNRAID_MCP_HOST` | No | `0.0.0.0` | Bind address for HTTP transports |
| `UNRAID_MCP_PORT` | No | `6970` | Listen port for HTTP transports |
| `UNRAID_MCP_BEARER_TOKEN` | Conditional | — | Static Bearer token for HTTP transports; auto-generated on first start if unset |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | No | `false` | Set `true` to skip Bearer auth (use behind a reverse proxy that handles auth) |
| `DOCKER_NETWORK` | No | — | External Docker network to join; leave blank for default bridge |
| `PGID` | No | `1000` | Container process GID |
| `PUID` | No | `1000` | Container process UID |

### How to find UNRAID_API_KEY

1. Open the Unraid web UI.
2. Go to **Settings → Management Access → API Keys**.
3. Create a new key or copy an existing one.
4. Paste the value into `UNRAID_API_KEY`.

### UNRAID_API_KEY vs UNRAID_MCP_BEARER_TOKEN

These are two separate credentials with different purposes:

- `UNRAID_API_KEY` — authenticates the MCP server to the **Unraid GraphQL API**. Every GraphQL request carries this key as a header. Obtained from the Unraid web UI.
- `UNRAID_MCP_BEARER_TOKEN` — authenticates **MCP clients** (Claude Code, Claude Desktop, etc.) to **this MCP server**. Clients must send `Authorization: Bearer <token>` on every HTTP request. Generate with `openssl rand -hex 32` or `just gen-token`.

### UNRAID_MCP_DISABLE_HTTP_AUTH

Set this to `true` when a reverse proxy (nginx, Caddy, Traefik, SWAG) already handles authentication before requests reach the MCP server. Disabling the built-in check removes the Bearer token requirement at the MCP layer. Do not expose the server directly to untrusted networks with this flag enabled.

### Transport modes

- `streamable-http` — default; exposes an HTTP endpoint, requires Bearer token unless auth is disabled
- `stdio` — subprocess mode for Claude Code local plugin; no Bearer token needed
- `sse` — legacy Server-Sent Events; deprecated but functional

Credential files are loaded in priority order: `~/.unraid-mcp/.env` first, then project `.env` as a fallback.

## Usage examples

### System inspection

```python
unraid(action="system", subaction="overview")
unraid(action="system", subaction="array")
unraid(action="live", subaction="cpu")
unraid(action="live", subaction="memory")
unraid(action="health", subaction="check")
```

### Parity check workflow

```python
unraid(action="array", subaction="parity_status")
unraid(action="array", subaction="parity_start", correct=True)   # correcting pass
unraid(action="array", subaction="parity_start", correct=False)  # read-only pass
unraid(action="live",  subaction="parity_progress", timeout=15.0)
unraid(action="array", subaction="parity_pause")
unraid(action="array", subaction="parity_resume")
unraid(action="array", subaction="parity_cancel")
unraid(action="array", subaction="parity_history")
```

### Docker management

```python
unraid(action="docker", subaction="list")
unraid(action="docker", subaction="start",   container_id="plex")
unraid(action="docker", subaction="stop",    container_id="plex")
unraid(action="docker", subaction="restart", container_id="plex")
unraid(action="docker", subaction="details", container_id="plex")
unraid(action="docker", subaction="networks")
```

### VM operations

```python
unraid(action="vm", subaction="list")
unraid(action="vm", subaction="start",      vm_id="windows11")
unraid(action="vm", subaction="stop",       vm_id="windows11")
unraid(action="vm", subaction="pause",      vm_id="windows11")
unraid(action="vm", subaction="resume",     vm_id="windows11")
unraid(action="vm", subaction="force_stop", vm_id="windows11", confirm=True)
```

### Log tailing

```python
unraid(action="live", subaction="log_tail",  path="/var/log/syslog", collect_for=5.0)
unraid(action="disk", subaction="logs",      log_path="/var/log/syslog", tail_lines=200)
unraid(action="disk", subaction="log_files")
```

### Notifications

```python
unraid(action="notification", subaction="overview")
unraid(action="notification", subaction="list", list_type="UNREAD", limit=10)
unraid(action="notification", subaction="list", list_type="UNREAD", importance="ALERT")
unraid(
    action="notification",
    subaction="create",
    title="Test",
    subject="Test notification",
    description="Created via MCP",
    importance="INFO",
)
unraid(action="live", subaction="notification_feed", collect_for=10.0)
```

### Flash backup

```python
unraid(action="rclone", subaction="list_remotes")
unraid(
    action="disk",
    subaction="flash_backup",
    remote_name="my-backup-remote",
    source_path="/boot",
    destination_path="/flash-backups/tower",
    confirm=True,  # overwrites destination
)
```

## Development commands

| Command | Effect |
| --- | --- |
| `just dev` | Start development server via `uv run python -m unraid_mcp` |
| `just test` | Run full test suite |
| `just lint` | Run ruff linter |
| `just fmt` | Run ruff formatter |
| `just typecheck` | Run pyright or mypy |
| `just test-live` | Run live integration tests (requires a running Unraid server) |
| `just up` | Start via Docker Compose |
| `just down` | Stop Docker Compose containers |
| `just logs` | Tail Docker Compose container logs |
| `just health` | Check `/health` endpoint |
| `just gen-token` | Generate a secure random Bearer token |
| `just check-contract` | Docker security, baked-env, and ignore-file checks |
| `just setup` | Create `.env` from `.env.example` if missing |
| `just clean` | Remove build artifacts and caches |

## Verification

```bash
just lint
just typecheck
just test
```

For a stdio MCP smoke test:

```bash
uv run unraid-mcp-server
```

For an HTTP health check after `just up`:

```bash
just health
```

The automated safety tests in `tests/safety/` verify that every destructive action raises a `ToolError` without `confirm=True` and that no GraphQL request reaches the network layer in that case.

## GraphQL schema overview

The server issues queries and mutations against the Unraid GraphQL API. Key query roots:

| Root | Used by |
| --- | --- |
| `info` | `system/overview`, `system/display`, health check |
| `array` | `system/array`, `array/*` |
| `vars` | `system/network`, `system/variables` |
| `metrics` | `system/metrics` |
| `services` | `system/services` |
| `servers` | `system/servers`, `system/network` |
| `registration` | `system/registration` |
| `online` | `system/online`, `health/test_connection` |
| `owner` | `system/owner` |
| `settings` | `system/settings` |
| `flash` | `system/flash` |
| `upsDevices` / `upsDeviceById` | `system/ups_devices`, `system/ups_device` |
| `upsConfiguration` | `system/ups_config` |
| `parityHistory` | `array/parity_history` |
| `disk` / `disks` | `disk/disk_details`, `disk/disks` |
| `shares` | `disk/shares` |
| `logFiles` / `logFile` | `disk/log_files`, `disk/logs` |
| `docker.containers` / `docker.networks` | `docker/*` |
| `vms` | `vm/*` |
| `notifications` | `notification/*` |
| `apiKeys` / `apiKey` | `key/*` |
| `plugins` | `plugin/list` |
| `rclone` | `rclone/*` |
| `customization` | `customization/*` |
| `oidcProviders` / `oidcConfiguration` | `oidc/*` |
| `me` | `user/me` |

Subscriptions use `graphql-transport-ws` over WebSocket (falling back to legacy `graphql-ws`). The WebSocket URL is derived from `UNRAID_API_URL` by swapping the scheme (`http` → `ws`, `https` → `wss`).

## Related plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| [homelab-core](https://github.com/jmagar/claude-homelab) | core | Core agents, commands, skills, and setup/health workflows for homelab management. |
| [overseerr-mcp](https://github.com/jmagar/overseerr-mcp) | media | Search movies and TV shows, submit requests, and monitor failed requests via Overseerr. |
| [unifi-mcp](https://github.com/jmagar/unifi-mcp) | infrastructure | Monitor and manage UniFi devices, clients, firewall rules, and network health. |
| [gotify-mcp](https://github.com/jmagar/gotify-mcp) | utilities | Send and manage push notifications via a self-hosted Gotify server. |
| [swag-mcp](https://github.com/jmagar/swag-mcp) | infrastructure | Create, edit, and manage SWAG nginx reverse proxy configurations. |
| [synapse-mcp](https://github.com/jmagar/synapse-mcp) | infrastructure | Docker management (Flux) and SSH remote operations (Scout) across homelab hosts. |
| [arcane-mcp](https://github.com/jmagar/arcane-mcp) | infrastructure | Manage Docker environments, containers, images, volumes, networks, and GitOps via Arcane. |
| [syslog-mcp](https://github.com/jmagar/syslog-mcp) | infrastructure | Receive, index, and search syslog streams from all homelab hosts via SQLite FTS5. |
| [plugin-lab](https://github.com/jmagar/plugin-lab) | dev-tools | Scaffold, review, align, and deploy homelab MCP plugins with agents and canonical templates. |

## License

MIT
