# test-actions.sh

Non-destructive smoke test for every readable action in the Unraid MCP server,
executed via `mcporter call`.

## Usage

```bash
# Against local server (default: http://localhost:6970/mcp)
./scripts/test-actions.sh

# Against a specific server
./scripts/test-actions.sh http://10.1.0.2:6970/mcp

# Via environment variable
UNRAID_MCP_URL=http://10.1.0.2:6970/mcp ./scripts/test-actions.sh
```

Exit code is `0` when all executed tests pass, `1` if any fail.

## Prerequisites

- `mcporter` on `$PATH`
- `python3` on `$PATH` (used for JSON result inspection and ID extraction)
- Unraid MCP server reachable at the target URL

Start the server if needed:

```bash
docker compose up -d          # production container
uv run unraid-mcp-server      # local dev
```

## What It Tests

The script runs in two sequential phases.

### Phase 1 — Param-free reads

All actions that require no arguments beyond `action` itself.

| Tool | Actions tested |
|---|---|
| `unraid_info` | `overview`, `array`, `network`, `registration`, `connect`, `variables`, `metrics`, `services`, `display`, `config`, `online`, `owner`, `settings`, `server`, `servers`, `flash`, `ups_devices`, `ups_device`, `ups_config` |
| `unraid_array` | `parity_status` |
| `unraid_storage` | `disks`, `shares`, `unassigned`, `log_files` |
| `unraid_docker` | `list`, `networks`, `port_conflicts`, `check_updates`, `sync_templates`, `refresh_digests` |
| `unraid_vm` | `list` |
| `unraid_notifications` | `overview`, `list`, `warnings`, `recalculate` |
| `unraid_rclone` | `list_remotes`, `config_form` |
| `unraid_users` | `me` |
| `unraid_keys` | `list` |
| `unraid_health` | `check`, `test_connection`, `diagnose` |

### Phase 2 — ID-discovered reads

The script extracts IDs from Phase 1 responses and uses them to test actions
that require a specific resource identifier. Each is skipped if Phase 1 returned
no matching resources.

| Action | Source of ID |
|---|---|
| `docker: details` | first container from `docker: list` |
| `docker: logs` | first container from `docker: list` |
| `docker: network_details` | first network from `docker: networks` |
| `storage: disk_details` | first disk from `storage: disks` |
| `storage: logs` | first path from `storage: log_files` |
| `vm: details` | first VM from `vm: list` |
| `keys: get` | first key from `keys: list` |

## What Is Skipped (and Why)

Actions are skipped for one of three reasons shown in the output:

| Label | Meaning |
|---|---|
| `destructive (confirm=True required)` | Action requires `confirm=True`; running it would permanently modify or delete data |
| `mutation — state-changing` | Action modifies live system state (container lifecycle, VM state, settings) |
| `mutation — creates …` | Action creates a new resource |

### Full skip list

**unraid_info**: `update_server`, `update_ssh`
**unraid_array**: `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`
**unraid_storage**: `flash_backup`
**unraid_docker**: `start`, `stop`, `restart`, `pause`, `unpause`, `update`, `remove`, `update_all`, `create_folder`, `set_folder_children`, `delete_entries`, `move_to_folder`, `move_to_position`, `rename_folder`, `create_folder_with_items`, `update_view_prefs`, `reset_template_mappings`
**unraid_vm**: `start`, `stop`, `pause`, `resume`, `reboot`, `force_stop`, `reset`
**unraid_notifications**: `create`, `create_unique`, `archive`, `unread`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`, `delete_archived`
**unraid_rclone**: `create_remote`, `delete_remote`
**unraid_keys**: `create`, `update`, `delete`
**unraid_settings**: all 9 actions

## Cleanup

The script creates **no temporary files and no background processes**. There is
nothing to clean up on exit or interrupt. Status lines and error details go to
the terminal via stderr; captured JSON responses from `run_test_capture` live
only in local shell variables and are discarded when the script exits.

`set -euo pipefail` ensures the script exits immediately on unexpected errors.
Arithmetic increments use `((var++)) || true` to safely handle the zero-to-one
transition without triggering the pipefail exit.

## Output Format

```
  <action label>                                              PASS
  <action label>                                              FAIL
      <first 3 lines of error>
  <action label>                                              SKIP (reason)
```

Summary line at the end:

```
Results: 42 passed  0 failed  37 skipped  (79 total)
```

If any tests fail, the summary lists each failed label for quick triage.
