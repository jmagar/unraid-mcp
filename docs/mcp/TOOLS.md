# MCP Tools Reference

## Design Philosophy

unraid-mcp exposes four MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `unraid` | Primary tool -- action+subaction dispatch for 15 domains | `action`, `subaction`, plus domain-specific params |
| `unraid_help` | Returns markdown reference for all actions | _(none)_ |
| `diagnose_subscriptions` | Inspect WebSocket subscription states | _(none)_ |
| `test_subscription_query` | Test a GraphQL subscription query | `query` (allowlisted fields only) |

The consolidated action pattern keeps the MCP surface small (4 tools) while supporting 107 subactions across 15 domains. Clients call `unraid_help` first to discover available operations, then call `unraid` with the appropriate action and subaction.

## Primary Tool: `unraid`

### Input Schema

```python
unraid(
    action: str,       # Domain (required)
    subaction: str,    # Operation (required)
    confirm: bool,     # True to bypass elicitation for destructive ops
    # ... domain-specific parameters
)
```

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `Literal[15 values]` | yes | Domain to operate on |
| `subaction` | `str` | yes | Operation within the domain |
| `confirm` | `bool` | no | Set `True` for destructive subactions (default: `False`) |
| `container_id` | `str` | no | Docker container ID or name (fuzzy match supported) |
| `vm_id` | `str` | no | VM identifier |
| `disk_id` | `str` | no | Disk identifier |
| `notification_id` | `str` | no | Single notification ID |
| `notification_ids` | `list[str]` | no | Multiple notification IDs |
| `key_id` | `str` | no | API key identifier |
| `name` | `str` | no | Name for create/update operations |
| `path` | `str` | no | Log file path (for `live/log_tail`) |
| `collect_for` | `float` | no | WebSocket collection duration in seconds (default: 5.0) |
| `limit` | `int` | no | Max items to return (default: 20) |
| `offset` | `int` | no | Pagination offset (default: 0) |

### Actions and Subactions

#### `system` (18 subactions)

Server information, metrics, network, and UPS management.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `overview` | Complete system summary (recommended starting point) | -- |
| `server` | Hostname, version, uptime | -- |
| `servers` | All known Unraid servers | -- |
| `array` | Array status and disk list | -- |
| `network` | Network interfaces and config | -- |
| `registration` | License and registration status | -- |
| `variables` | Environment variables | -- |
| `metrics` | Real-time CPU, memory, I/O usage | -- |
| `services` | Running services status | -- |
| `display` | Display settings | -- |
| `config` | System configuration | -- |
| `online` | Quick online status check | -- |
| `owner` | Server owner information | -- |
| `settings` | User settings and preferences | -- |
| `flash` | USB flash drive details | -- |
| `ups_devices` | List all UPS devices | -- |
| `ups_device` | Single UPS device details | `device_id` |
| `ups_config` | UPS configuration | -- |

#### `health` (4 subactions)

Health checks, connection testing, diagnostics, and credential setup.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `check` | Comprehensive health check (connectivity, array, disks, containers, VMs, resources) | -- |
| `test_connection` | Test API connectivity and authentication, returns latency | -- |
| `diagnose` | Detailed diagnostic report with subscription status and middleware error stats | -- |
| `setup` | Configure credentials interactively via elicitation (stores to `~/.unraid-mcp/.env`) | -- |

#### `array` (13 subactions)

Parity checks, array lifecycle, and disk operations.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `parity_status` | Current parity check progress and status | -- | -- |
| `parity_history` | Historical parity check results | -- | -- |
| `parity_start` | Start a parity check | `correct` (bool) | -- |
| `parity_pause` | Pause a running parity check | -- | -- |
| `parity_resume` | Resume a paused parity check | -- | -- |
| `parity_cancel` | Cancel a running parity check | -- | -- |
| `start_array` | Start the array | -- | -- |
| `stop_array` | Stop the array | -- | Yes |
| `add_disk` | Add a disk to the array | `slot`, `disk_id` | -- |
| `remove_disk` | Remove a disk from the array | `slot` | Yes |
| `mount_disk` | Mount a disk | `disk_id` | -- |
| `unmount_disk` | Unmount a disk | `disk_id` | -- |
| `clear_disk_stats` | Clear disk statistics permanently | -- | Yes |

#### `disk` (6 subactions)

Shares, physical disks, log files.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `shares` | List network shares | -- | -- |
| `disks` | All physical disks with health and temperatures | -- | -- |
| `disk_details` | Detailed info for a specific disk | `disk_id` | -- |
| `log_files` | List available log files | -- | -- |
| `logs` | Read log content | `log_path`, `tail_lines` | -- |
| `flash_backup` | Trigger a flash backup | `remote_name`, `source_path`, `destination_path`, `backup_options` | Yes |

#### `docker` (7 subactions)

Container lifecycle and network inspection.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `list` | All containers with status, image, state | -- |
| `details` | Single container details | `container_id` |
| `start` | Start a container | `container_id` |
| `stop` | Stop a container | `container_id` |
| `restart` | Restart a container | `container_id` |
| `networks` | List Docker networks | -- |
| `network_details` | Details for a specific network | `network_id` |

Container identification supports name, ID, or partial name (fuzzy match).

#### `vm` (9 subactions)

Virtual machine lifecycle.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `list` | All VMs with state | -- | -- |
| `details` | Single VM details | `vm_id` | -- |
| `start` | Start a VM | `vm_id` | -- |
| `stop` | Gracefully stop a VM | `vm_id` | -- |
| `pause` | Pause a VM | `vm_id` | -- |
| `resume` | Resume a paused VM | `vm_id` | -- |
| `reboot` | Reboot a VM | `vm_id` | -- |
| `force_stop` | Force stop a VM (no graceful shutdown) | `vm_id` | Yes |
| `reset` | Hard reset a VM | `vm_id` | Yes |

#### `notification` (12 subactions)

System notification management.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `overview` | Notification counts (unread, archived by type) | -- | -- |
| `list` | List notifications | `list_type`, `limit`, `offset` | -- |
| `create` | Create a notification | `title`, `subject`, `description`, `importance` | -- |
| `archive` | Archive a notification | `notification_id` | -- |
| `mark_unread` | Mark a notification as unread | `notification_id` | -- |
| `recalculate` | Recalculate notification counts | -- | -- |
| `archive_all` | Archive all unread notifications | -- | -- |
| `archive_many` | Archive multiple notifications | `notification_ids` | -- |
| `unarchive_many` | Unarchive multiple notifications | `notification_ids` | -- |
| `unarchive_all` | Unarchive all archived notifications | -- | -- |
| `delete` | Delete a notification permanently | `notification_id`, `notification_type` | Yes |
| `delete_archived` | Delete all archived notifications | -- | Yes |

#### `key` (7 subactions)

API key management.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `list` | All API keys | -- | -- |
| `get` | Single key details | `key_id` | -- |
| `create` | Create a new key | `name`, `roles`, `permissions` | -- |
| `update` | Update a key | `key_id`, `name`, `roles`, `permissions` | -- |
| `delete` | Delete a key permanently | `key_id` | Yes |
| `add_role` | Add a role to a key | `key_id`, `roles` | -- |
| `remove_role` | Remove a role from a key | `key_id`, `roles` | -- |

#### `plugin` (3 subactions)

Plugin management.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `list` | All installed plugins | `bundled` | -- |
| `add` | Install plugins | `names` (list) | -- |
| `remove` | Uninstall plugins | `names` (list), `restart` | Yes |

#### `rclone` (4 subactions)

Cloud storage remote management.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `list_remotes` | List configured rclone remotes | -- | -- |
| `config_form` | Get configuration form for a remote type | `provider_type` | -- |
| `create_remote` | Create a new remote | `name`, `provider_type`, `config_data` | -- |
| `delete_remote` | Delete a remote | `name` | Yes |

#### `setting` (2 subactions)

System settings and UPS configuration.

| Subaction | Description | Extra params | Destructive |
|-----------|-------------|-------------|-------------|
| `update` | Update system settings | `settings_input` | -- |
| `configure_ups` | Configure UPS settings | `ups_config` | Yes |

#### `customization` (5 subactions)

Theme and UI customization.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `theme` | Current theme settings | -- |
| `public_theme` | Public-facing theme | -- |
| `is_initial_setup` | Check if initial setup is complete | -- |
| `sso_enabled` | Check SSO status | -- |
| `set_theme` | Update theme | `theme_name` |

#### `oidc` (5 subactions)

OIDC/SSO provider management.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `providers` | List configured OIDC providers | -- |
| `provider` | Single provider details | `provider_id` |
| `configuration` | OIDC configuration | -- |
| `public_providers` | Public-facing provider list | -- |
| `validate_session` | Validate current SSO session | `token` |

#### `user` (1 subaction)

| Subaction | Description |
|-----------|-------------|
| `me` | Current authenticated user info |

#### `live` (11 subactions)

Real-time WebSocket subscription snapshots. Returns a "connecting" placeholder on first call -- retry momentarily for live data.

| Subaction | Description | Extra params |
|-----------|-------------|-------------|
| `cpu` | Live CPU utilization | `collect_for` |
| `memory` | Live memory usage | `collect_for` |
| `cpu_telemetry` | Detailed CPU telemetry (power, temp) | `collect_for` |
| `array_state` | Live array state changes | `collect_for` |
| `parity_progress` | Live parity check progress | `collect_for` |
| `ups_status` | Live UPS status | `collect_for` |
| `notifications_overview` | Live notification counts | `collect_for` |
| `owner` | Live owner info | `collect_for` |
| `server_status` | Live server status | `collect_for` |
| `log_tail` | Live log tail stream | `path` (required), `collect_for` |
| `notification_feed` | Live notification feed | `collect_for` |

## Destructive Operations

All destructive operations require `confirm=True`. Without it, interactive clients are prompted via MCP elicitation; non-interactive clients receive a `ToolError` instructing them to re-call with `confirm=True`.

### Destructive subactions summary

| Domain | Subaction | Risk |
|--------|-----------|------|
| `array` | `stop_array` | Stops array while containers/VMs may use shares |
| `array` | `remove_disk` | Removes disk from array |
| `array` | `clear_disk_stats` | Clears disk statistics permanently |
| `vm` | `force_stop` | Hard kills VM without graceful shutdown |
| `vm` | `reset` | Hard resets VM |
| `notification` | `delete` | Permanently deletes a notification |
| `notification` | `delete_archived` | Permanently deletes all archived notifications |
| `rclone` | `delete_remote` | Removes a cloud storage remote |
| `key` | `delete` | Permanently deletes an API key |
| `disk` | `flash_backup` | Triggers flash backup operation |
| `setting` | `configure_ups` | Modifies UPS configuration |
| `plugin` | `remove` | Uninstalls a plugin |

## Error Responses

Errors use FastMCP's `ToolError` for user-facing messages:

- **ToolError** -- invalid action, subaction, or missing required parameter
- **CredentialsNotConfiguredError** -- triggers elicitation or setup instructions
- **TimeoutError** -- upstream Unraid API did not respond in time
- **GraphQL errors** -- converted to ToolError with descriptive messages

## Example Tool Calls

```python
# System overview
unraid(action="system", subaction="overview")

# Health check
unraid(action="health", subaction="check")

# List Docker containers
unraid(action="docker", subaction="list")

# Restart a specific container
unraid(action="docker", subaction="restart", container_id="plex")

# Live CPU monitoring for 3 seconds
unraid(action="live", subaction="cpu", collect_for=3.0)

# Tail a log file
unraid(action="live", subaction="log_tail", path="/var/log/syslog", collect_for=5.0)

# Stop array (destructive)
unraid(action="array", subaction="stop_array", confirm=True)

# List notifications (paginated)
unraid(action="notification", subaction="list", limit=10, list_type="UNREAD")
```

## See Also

- [SCHEMA.md](SCHEMA.md) -- Schema definitions behind these tools
- [AUTH.md](AUTH.md) -- Authentication required before tool calls
- [ENV.md](ENV.md) -- Environment variable configuration
- [ELICITATION.md](ELICITATION.md) -- Interactive credential and confirmation flows
