---
description: Manage Unraid system settings and configuration
argument-hint: [action] [additional-args]
---

Execute the `unraid_settings` MCP tool with action: `$1`

## Available Actions (9)

All settings actions are mutations that modify server configuration.

**General Settings:**
- `update` - Update general system settings (timezone, locale, etc.)
- `update_temperature` - Update temperature unit preference (Celsius/Fahrenheit)
- `update_time` - Update NTP and time configuration

**UPS Configuration:**
- `configure_ups` - Configure UPS settings (requires `confirm=True` — DESTRUCTIVE)

**API & Connectivity:**
- `update_api` - Update Unraid Connect API settings

**Unraid Connect (My Servers):**
- `connect_sign_in` - Sign in to Unraid Connect cloud service
- `connect_sign_out` - Sign out of Unraid Connect cloud service

**Remote Access:**
- `setup_remote_access` - Configure remote access settings (requires `confirm=True` — DESTRUCTIVE)
- `enable_dynamic_remote_access` - Enable/configure dynamic remote access (requires `confirm=True` — DESTRUCTIVE)

## Example Usage

```
/unraid-settings update
/unraid-settings update_temperature
/unraid-settings update_time
/unraid-settings update_api
/unraid-settings connect_sign_in
/unraid-settings connect_sign_out
```

**⚠️ Destructive Operations (require `confirm=True`):**
- `configure_ups` - Modifies UPS hardware configuration
- `setup_remote_access` - Changes network access policies
- `enable_dynamic_remote_access` - Changes network access policies

**IMPORTANT:** Settings changes take effect immediately and may affect server accessibility.

Use the tool to execute the requested settings operation and report the results.
