---
description: Query Unraid server information and configuration
argument-hint: [action] [additional-args]
---

Execute the `unraid_info` MCP tool with action: `$1`

## Available Actions (19)

**System Overview:**
- `overview` - Complete system summary with all key metrics
- `server` - Server details (hostname, version, uptime)
- `servers` - List all known Unraid servers

**Array & Storage:**
- `array` - Array status, disks, and health

**Network & Registration:**
- `network` - Network configuration and interfaces
- `registration` - Registration status and license info
- `connect` - Connect service configuration
- `online` - Online status check

**Configuration:**
- `config` - System configuration settings
- `settings` - User settings and preferences
- `variables` - Environment variables
- `display` - Display settings

**Services & Monitoring:**
- `services` - Running services status
- `metrics` - System metrics (CPU, RAM, disk I/O)
- `ups_devices` - List all UPS devices
- `ups_device` - Get specific UPS device details (requires device_id)
- `ups_config` - UPS configuration

**Ownership:**
- `owner` - Server owner information
- `flash` - USB flash drive details

## Example Usage

```
/unraid-info overview
/unraid-info array
/unraid-info metrics
/unraid-info ups_device [device-id]
```

Use the tool to retrieve the requested information and present it in a clear, formatted manner.
