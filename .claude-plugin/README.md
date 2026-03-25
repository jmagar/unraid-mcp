# Unraid MCP Plugin

Query, monitor, and manage Unraid servers via GraphQL API using a single consolidated `unraid` tool with action+subaction routing.

**Version:** 1.1.3 | **Category:** Infrastructure | **Tags:** unraid, homelab, graphql, docker, virtualization

---

## Installation

```bash
/plugin marketplace add jmagar/unraid-mcp
/plugin install unraid @unraid-mcp
```

After install, configure credentials:

```python
unraid(action="health", subaction="setup")
```

Credentials are stored at `~/.unraid-mcp/.env`. Get an API key from **Unraid WebUI → Settings → Management Access → API Keys**.

---

## Tools

### `unraid` — Primary Tool (107 subactions, 15 domains)

Call as `unraid(action="<domain>", subaction="<operation>", [params])`.

#### `system` — Server Information (18 subactions)
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

#### `health` — Diagnostics (4 subactions)
| Subaction | Description |
|-----------|-------------|
| `check` | Comprehensive health check — connectivity, array, disks, containers, VMs, resources |
| `test_connection` | Test API connectivity and authentication |
| `diagnose` | Detailed diagnostic report with troubleshooting recommendations |
| `setup` | Configure credentials interactively (stores to `~/.unraid-mcp/.env`) |

#### `array` — Array & Parity (13 subactions)
| Subaction | Description |
|-----------|-------------|
| `parity_status` | Current parity check progress and status |
| `parity_history` | Historical parity check results |
| `parity_start` | Start a parity check (requires `correct`) |
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

#### `disk` — Storage & Logs (6 subactions)
| Subaction | Description |
|-----------|-------------|
| `shares` | List network shares |
| `disks` | All physical disks with health and temperatures |
| `disk_details` | Detailed info for a specific disk (requires `disk_id`) |
| `log_files` | List available log files |
| `logs` | Read log content (requires `log_path`; optional `tail_lines`) |
| `flash_backup` | ⚠️ Trigger a flash backup (requires `confirm=True`) |

#### `docker` — Containers (7 subactions)
| Subaction | Description |
|-----------|-------------|
| `list` | All containers with status, image, state |
| `details` | Single container details (requires container identifier) |
| `start` | Start a container (requires container identifier) |
| `stop` | Stop a container (requires container identifier) |
| `restart` | Restart a container (requires container identifier) |
| `networks` | List Docker networks |
| `network_details` | Details for a specific network (requires `network_id`) |

Container identification: name, ID, or partial name (fuzzy match).

#### `vm` — Virtual Machines (9 subactions)
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

#### `notification` — Notifications (12 subactions)
| Subaction | Description |
|-----------|-------------|
| `overview` | Notification counts (unread, archived by type) |
| `list` | List notifications (optional `filter`, `limit`, `offset`) |
| `create` | Create a notification (requires `title`, `subject`, `description`, `importance`) |
| `archive` | Archive a notification (requires `notification_id`) |
| `mark_unread` | Mark a notification as unread (requires `notification_id`) |
| `recalculate` | Recalculate notification counts |
| `archive_all` | Archive all unread notifications |
| `archive_many` | Archive multiple (requires `ids` list) |
| `unarchive_many` | Unarchive multiple (requires `ids` list) |
| `unarchive_all` | Unarchive all archived notifications |
| `delete` | ⚠️ Delete a notification (requires `notification_id`, `notification_type`, `confirm=True`) |
| `delete_archived` | ⚠️ Delete all archived (requires `confirm=True`) |

#### `key` — API Keys (7 subactions)
| Subaction | Description |
|-----------|-------------|
| `list` | All API keys |
| `get` | Single key details (requires `key_id`) |
| `create` | Create a new key (requires `name`; optional `roles`, `permissions`) |
| `update` | Update a key (requires `key_id`) |
| `delete` | ⚠️ Delete a key (requires `key_id`, `confirm=True`) |
| `add_role` | Add roles to a key (requires `key_id`, `roles`) |
| `remove_role` | Remove roles from a key (requires `key_id`, `roles`) |

#### `plugin` — Plugins (3 subactions)
| Subaction | Description |
|-----------|-------------|
| `list` | All installed plugins |
| `add` | Install plugins (requires `names` list) |
| `remove` | ⚠️ Uninstall plugins (requires `names` list, `confirm=True`) |

#### `rclone` — Cloud Storage (4 subactions)
| Subaction | Description |
|-----------|-------------|
| `list_remotes` | List configured rclone remotes |
| `config_form` | Get configuration form for a remote type |
| `create_remote` | Create a new remote (requires `name`, `provider_type`, `config_data`) |
| `delete_remote` | ⚠️ Delete a remote (requires `name`, `confirm=True`) |

#### `setting` — System Settings (2 subactions)
| Subaction | Description |
|-----------|-------------|
| `update` | Update system settings (requires `settings_input` object) |
| `configure_ups` | ⚠️ Configure UPS settings (requires `confirm=True`) |

#### `customization` — Theme & Appearance (5 subactions)
| Subaction | Description |
|-----------|-------------|
| `theme` | Current theme settings |
| `public_theme` | Public-facing theme |
| `is_initial_setup` | Check if initial setup is complete |
| `sso_enabled` | Check SSO status |
| `set_theme` | Update theme (requires theme parameters) |

#### `oidc` — SSO / OpenID Connect (5 subactions)
| Subaction | Description |
|-----------|-------------|
| `providers` | List configured OIDC providers |
| `provider` | Single provider details (requires `provider_id`) |
| `configuration` | OIDC configuration |
| `public_providers` | Public-facing provider list |
| `validate_session` | Validate current SSO session (requires `token`) |

#### `user` — Current User (1 subaction)
| Subaction | Description |
|-----------|-------------|
| `me` | Current authenticated user info |

#### `live` — Real-Time Subscriptions (11 subactions)
Persistent WebSocket connections. Returns `{"status": "connecting"}` on first call — retry momentarily.

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
| `log_tail` | Live log tail stream (requires `path`) |
| `notification_feed` | Live notification feed |

---

### `diagnose_subscriptions` — Subscription Diagnostics

Inspect WebSocket subscription connection states, errors, and URLs. No parameters required.

---

### `test_subscription_query` — Subscription Query Tester

Test a specific GraphQL subscription query against the live Unraid API. Uses an allowlisted set of safe fields only.

---

## Destructive Actions

All require `confirm=True`. Without it, the action is blocked.

| Domain | Subaction |
|--------|-----------|
| `array` | `stop_array`, `remove_disk`, `clear_disk_stats` |
| `vm` | `force_stop`, `reset` |
| `notification` | `delete`, `delete_archived` |
| `rclone` | `delete_remote` |
| `key` | `delete` |
| `disk` | `flash_backup` |
| `setting` | `configure_ups` |
| `plugin` | `remove` |

---

## Support

- **Issues:** https://github.com/jmagar/unraid-mcp/issues
- **Repository:** https://github.com/jmagar/unraid-mcp
- **Skill docs:** `skills/unraid/SKILL.md`
- **API reference:** `skills/unraid/references/`
