---
description: Manage virtual machines on Unraid
argument-hint: [action] [vm-id]
---

Execute the `unraid_vm` MCP tool with action: `$1` and vm_id: `$2`

## Available Actions (9)

**Query Operations:**
- `list` - List all VMs with status and resource allocation
- `details` - Get detailed info for a VM (requires vm_id)

**Lifecycle Operations:**
- `start` - Start a stopped VM (requires vm_id)
- `stop` - Gracefully stop a running VM (requires vm_id)
- `pause` - Pause a running VM (requires vm_id)
- `resume` - Resume a paused VM (requires vm_id)
- `reboot` - Gracefully reboot a VM (requires vm_id)

**⚠️ Destructive Operations:**
- `force_stop` - Forcefully power off VM (like pulling power cord - requires vm_id + confirmation)
- `reset` - Hard reset VM (power cycle without graceful shutdown - requires vm_id + confirmation)

## Example Usage

```
/unraid-vm list
/unraid-vm details windows-10
/unraid-vm start ubuntu-server
/unraid-vm stop windows-10
/unraid-vm pause debian-vm
/unraid-vm resume debian-vm
/unraid-vm reboot ubuntu-server
```

**VM Identification:** Use VM ID (PrefixedID format: `hex64:suffix`)

**IMPORTANT:** `force_stop` and `reset` bypass graceful shutdown and may corrupt VM filesystem. Use `stop` instead for safe shutdowns.

Use the tool to execute the requested VM operation and report the results.
