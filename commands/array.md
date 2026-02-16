---
description: Manage Unraid array parity checks
argument-hint: [action] [correct=true/false]
---

Execute the `unraid_array` MCP tool with action: `$1`

## Available Actions (5)

**Parity Check Operations:**
- `parity_start` - Start parity check/sync (optional: correct=true to fix errors)
- `parity_pause` - Pause running parity operation
- `parity_resume` - Resume paused parity operation
- `parity_cancel` - Cancel running parity operation
- `parity_status` - Get current parity check status

## Example Usage

```
/array parity_start
/array parity_start correct=true
/array parity_pause
/array parity_resume
/array parity_cancel
/array parity_status
```

**Note:** Use `correct=true` with `parity_start` to automatically fix any parity errors found during the check.

Use the tool to execute the requested parity operation and report the results.
