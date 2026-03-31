---
name: unraid
description: "This skill should be used when the user mentions Unraid, asks to check server health, monitor array or disk status, list or restart Docker containers, start or stop VMs, read system logs, check parity status, view notifications, manage API keys, configure rclone remotes, check UPS or power status, get live CPU or memory data, force stop a VM, check disk temperatures, or perform any operation on an Unraid NAS server. Also use when the user needs to set up or configure Unraid MCP credentials."
---

# Unraid MCP Skill

## Mode Detection

**MCP mode** (preferred): Use when `mcp__unraid-mcp__unraid` tool is available.

**HTTP fallback**: Use when MCP tools are unavailable. Credentials are in Bash subprocesses
as `$CLAUDE_PLUGIN_OPTION_UNRAID_API_URL` and `$CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY`.
Do NOT attempt `${user_config.unraid_api_key}` in curl — sensitive values only work
as `$CLAUDE_PLUGIN_OPTION_*` in Bash subprocesses.

**MCP URL**: `${user_config.unraid_mcp_url}`

---

Use the single `unraid` MCP tool with `action` (domain) + `subaction` (operation) for all Unraid operations.

## Setup

First time? Run setup to configure credentials:

```
unraid(action="health", subaction="setup")
```

Credentials are stored at `~/.unraid-mcp/.env`. Re-run `setup` any time to update or verify.

## Calling Convention

```
unraid(action="<domain>", subaction="<operation>", [additional params])
```

**Examples:**
```
unraid(action="system",  subaction="overview")
unraid(action="docker",  subaction="list")
unraid(action="health",  subaction="check")
unraid(action="array",   subaction="parity_status")
unraid(action="disk",    subaction="disks")
unraid(action="vm",      subaction="list")
unraid(action="notification", subaction="overview")
unraid(action="live",    subaction="cpu")
```

---

## All Domains and Subactions

### `system` — Server Information
| Subaction | Description |
|-----------|-------------|
| `overview` | Complete system summary (recommended starting point) |
| `server` | Hostname, version, uptime |
| `servers` | All known Unraid servers |
| `array` | Array status and disk list |
| `network` | Network interfaces and config |
| `registration` | License and registration status |
| `variables` | Environment variables |
| `metrics` | Real-time CPU, memory, I/O usage |
| `services` | Running services status |
| `display` | Display settings |
| `config` | System configuration |
| `online` | Quick online status check |
| `owner` | Server owner information |
| `settings` | User settings and preferences |
| `flash` | USB flash drive details |
| `ups_devices` | List all UPS devices |
| `ups_device` | Single UPS device (requires `device_id`) |
| `ups_config` | UPS configuration |

### `health` — Diagnostics
| Subaction | Description |
|-----------|-------------|
| `check` | Comprehensive health check — connectivity, array, disks, containers, VMs, resources |
| `test_connection` | Test API connectivity and authentication |
| `diagnose` | Detailed diagnostic report with troubleshooting recommendations |
| `setup` | Configure credentials interactively (stores to `~/.unraid-mcp/.env`) |

### `array` — Array & Parity
| Subaction | Description |
|-----------|-------------|
| `parity_status` | Current parity check progress and status |
| `parity_history` | Historical parity check results |
| `parity_start` | Start a parity check |
| `parity_pause` | Pause a running parity check |
| `parity_resume` | Resume a paused parity check |
| `parity_cancel` | Cancel a running parity check |
| `start_array` | Start the array |
| `stop_array` | ⚠️ Stop the array (requires `confirm=True`) |
| `add_disk` | Add a disk to the array (requires `slot`, `id`) |
| `remove_disk` | ⚠️ Remove a disk (requires `slot`, `confirm=True`) |
| `mount_disk` | Mount a disk |
| `unmount_disk` | Unmount a disk |
| `clear_disk_stats` | ⚠️ Clear disk statistics (requires `confirm=True`) |

### `disk` — Storage & Logs
| Subaction | Description |
|-----------|-------------|
| `shares` | List network shares |
| `disks` | All physical disks with health and temperatures |
| `disk_details` | Detailed info for a specific disk (requires `disk_id`) |
| `log_files` | List available log files |
| `logs` | Read log content (requires `log_path`; optional `tail_lines`) |
| `flash_backup` | ⚠️ Trigger a flash backup (requires `confirm=True`) |

### `docker` — Containers
| Subaction | Description |
|-----------|-------------|
| `list` | All containers with status, image, state |
| `details` | Single container details (requires container identifier) |
| `start` | Start a container (requires container identifier) |
| `stop` | Stop a container (requires container identifier) |
| `restart` | Restart a container (requires container identifier) |
| `networks` | List Docker networks |
| `network_details` | Details for a specific network (requires `network_id`) |

**Container Identification:** Name, ID, or partial name (fuzzy match supported).

### `vm` — Virtual Machines
| Subaction | Description |
|-----------|-------------|
| `list` | All VMs with state |
| `details` | Single VM details (requires `vm_id`) |
| `start` | Start a VM (requires `vm_id`) |
| `stop` | Gracefully stop a VM (requires `vm_id`) |
| `pause` | Pause a VM (requires `vm_id`) |
| `resume` | Resume a paused VM (requires `vm_id`) |
| `reboot` | Reboot a VM (requires `vm_id`) |
| `force_stop` | ⚠️ Force stop a VM (requires `vm_id`, `confirm=True`) |
| `reset` | ⚠️ Hard reset a VM (requires `vm_id`, `confirm=True`) |

### `notification` — Notifications
| Subaction | Description |
|-----------|-------------|
| `overview` | Notification counts (unread, archived by type) |
| `list` | List notifications (optional `filter`, `limit`, `offset`) |
| `mark_unread` | Mark a notification as unread (requires `notification_id`) |
| `create` | Create a notification (requires `title`, `subject`, `description`, `importance`) |
| `archive` | Archive a notification (requires `notification_id`) |
| `delete` | ⚠️ Delete a notification (requires `notification_id`, `notification_type`, `confirm=True`) |
| `delete_archived` | ⚠️ Delete all archived (requires `confirm=True`) |
| `archive_all` | Archive all unread notifications |
| `archive_many` | Archive multiple (requires `ids` list) |
| `unarchive_many` | Unarchive multiple (requires `ids` list) |
| `unarchive_all` | Unarchive all archived notifications |
| `recalculate` | Recalculate notification counts |

### `key` — API Keys
| Subaction | Description |
|-----------|-------------|
| `list` | All API keys |
| `get` | Single key details (requires `key_id`) |
| `create` | Create a new key (requires `name`; optional `roles`, `permissions`) |
| `update` | Update a key (requires `key_id`) |
| `delete` | ⚠️ Delete a key (requires `key_id`, `confirm=True`) |
| `add_role` | Add a role to a key (requires `key_id`, `roles`) |
| `remove_role` | Remove a role from a key (requires `key_id`, `roles`) |

### `plugin` — Plugins
| Subaction | Description |
|-----------|-------------|
| `list` | All installed plugins |
| `add` | Install plugins (requires `names` — list of plugin names) |
| `remove` | ⚠️ Uninstall plugins (requires `names` — list of plugin names, `confirm=True`) |

### `rclone` — Cloud Storage
| Subaction | Description |
|-----------|-------------|
| `list_remotes` | List configured rclone remotes |
| `config_form` | Get configuration form for a remote type |
| `create_remote` | Create a new remote (requires `name`, `provider_type`, `config_data`) |
| `delete_remote` | ⚠️ Delete a remote (requires `name`, `confirm=True`) |

### `setting` — System Settings
| Subaction | Description |
|-----------|-------------|
| `update` | Update system settings (requires `settings_input` object) |
| `configure_ups` | ⚠️ Configure UPS settings (requires `confirm=True`) |

### `customization` — Theme & Appearance
| Subaction | Description |
|-----------|-------------|
| `theme` | Current theme settings |
| `public_theme` | Public-facing theme |
| `is_initial_setup` | Check if initial setup is complete |
| `sso_enabled` | Check SSO status |
| `set_theme` | Update theme (requires theme parameters) |

### `oidc` — SSO / OpenID Connect
| Subaction | Description |
|-----------|-------------|
| `providers` | List configured OIDC providers |
| `provider` | Single provider details (requires `provider_id`) |
| `configuration` | OIDC configuration |
| `public_providers` | Public-facing provider list |
| `validate_session` | Validate current SSO session (requires `token`) |

### `user` — Current User
| Subaction | Description |
|-----------|-------------|
| `me` | Current authenticated user info |

### `live` — Real-Time Subscriptions
These use persistent WebSocket connections. Returns a "connecting" placeholder on the first call — retry momentarily for live data.

| Subaction | Description |
|-----------|-------------|
| `cpu` | Live CPU utilization |
| `memory` | Live memory usage |
| `cpu_telemetry` | Detailed CPU telemetry |
| `array_state` | Live array state changes |
| `parity_progress` | Live parity check progress |
| `ups_status` | Live UPS status |
| `notifications_overview` | Live notification counts |
| `owner` | Live owner info |
| `server_status` | Live server status |
| `log_tail` | Live log tail stream |
| `notification_feed` | Live notification feed |

---

## Destructive Actions

All require `confirm=True` as an explicit parameter. Without it, the action is blocked and elicitation is triggered.

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

---

## Common Workflows

### First-time setup
```
unraid(action="health", subaction="setup")
unraid(action="health", subaction="check")
```

### System health overview
```
unraid(action="system", subaction="overview")
unraid(action="health", subaction="check")
```

### Container management
```
unraid(action="docker", subaction="list")
unraid(action="docker", subaction="details", container_id="plex")
unraid(action="docker", subaction="restart", container_id="sonarr")
```

### Array and disk status
```
unraid(action="array",  subaction="parity_status")
unraid(action="disk",   subaction="disks")
unraid(action="system", subaction="array")
```

### Read logs
```
unraid(action="disk", subaction="log_files")
unraid(action="disk", subaction="logs", log_path="/var/log/syslog", tail_lines=50)
```

### Live monitoring
```
unraid(action="live", subaction="cpu")
unraid(action="live", subaction="memory")
unraid(action="live", subaction="array_state")
```

### VM operations
```
unraid(action="vm", subaction="list")
unraid(action="vm", subaction="start",      vm_id="<id>")
unraid(action="vm", subaction="force_stop", vm_id="<id>", confirm=True)
```

---

## Notes

- **Rate limit:** 100 requests / 10 seconds
- **Log path validation:** Only `/var/log/`, `/boot/logs/`, `/mnt/` prefixes accepted
- **Container logs:** Docker container stdout/stderr are NOT accessible via API — use SSH + `docker logs`
- **`arraySubscription`:** Known Unraid API bug — `live/array_state` may show "connecting" indefinitely
- **Event-driven subs** (`notifications_overview`, `owner`, `server_status`, `ups_status`): Only populate cache on first real server event

---

## HTTP Fallback Mode

When MCP tools are unavailable, use direct GraphQL queries via curl. Credentials are
available as `$CLAUDE_PLUGIN_OPTION_*` environment variables in Bash subprocesses.

```bash
# System overview
curl -s "$CLAUDE_PLUGIN_OPTION_UNRAID_API_URL" \
  -H "x-api-key: $CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ info { os { hostname uptime } } }"}'

# List Docker containers
curl -s "$CLAUDE_PLUGIN_OPTION_UNRAID_API_URL" \
  -H "x-api-key: $CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ docker { containers { names state status } } }"}'

# Array status
curl -s "$CLAUDE_PLUGIN_OPTION_UNRAID_API_URL" \
  -H "x-api-key: $CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ array { state capacity { kilobytes { free used total } } disks { name status temp } } }"}'
```
