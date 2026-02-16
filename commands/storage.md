---
description: Query Unraid storage, shares, and disk information
argument-hint: [action] [additional-args]
---

Execute the `unraid_storage` MCP tool with action: `$1`

## Available Actions (6)

**Shares & Disks:**
- `shares` - List all user shares with sizes and allocation
- `disks` - List all disks in the array
- `disk_details` - Get detailed info for a specific disk (requires disk identifier)
- `unassigned` - List unassigned devices

**Logs:**
- `log_files` - List available system log files
- `logs` - Read log file contents (requires log file path)

## Example Usage

```
/unraid-storage shares
/unraid-storage disks
/unraid-storage disk_details disk1
/unraid-storage unassigned
/unraid-storage log_files
/unraid-storage logs /var/log/syslog
```

**Note:** Log file paths must start with `/var/log/`, `/boot/logs/`, or `/mnt/`

Use the tool to retrieve the requested storage information and present it clearly.
