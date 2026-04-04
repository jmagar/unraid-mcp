# mcporter Integration Tests

Live integration smoke-tests for the unraid-mcp server.

---

## `test-http.sh` — HTTP live test, requires a running server

Full end-to-end smoke-test over the HTTP transport. No mcporter required — uses `curl` and `jq`.

```bash
# Local server, auth disabled (gateway handles auth)
./tests/mcporter/test-http.sh --skip-auth

# Local server with bearer token
./tests/mcporter/test-http.sh --token <your-token>

# Remote server via gateway
./tests/mcporter/test-http.sh --url https://unraid.tootie.tv/mcp --skip-auth

# With explicit token
./tests/mcporter/test-http.sh --url http://localhost:6970/mcp --token <tok>

# Verbose (print raw response bodies)
./tests/mcporter/test-http.sh --skip-auth --verbose
```

Token is auto-read from `~/.unraid-mcp/.env` if not supplied via `--token`.

### What it tests

| Phase | Tests |
|---|---|
| **1 · Middleware** | `/health`, `/.well-known/oauth-protected-resource`, `/.well-known/oauth-protected-resource/mcp` (all without auth) |
| **2 · Auth** | No-token → 401, bad-token → 401 `invalid_token`, good-token → passes (skipped with `--skip-auth`) |
| **3 · MCP protocol** | `initialize`, `tools/list` (tool count + named tools), `ping` |
| **4 · Tool smoke-tests** | 14 non-destructive subactions across all domains |
| **4b · Guard bypass** | `confirm=True` bypasses destructive guard on `notification/delete` and `vm/force_stop` |

Prerequisites: `curl`, `jq`.

---

## `test-tools.sh` — stdio, no running server needed

```bash
./tests/mcporter/test-tools.sh                        # sequential, 25s timeout
./tests/mcporter/test-tools.sh --parallel             # parallel suites
./tests/mcporter/test-tools.sh --timeout-ms 10000     # tighter timeout
./tests/mcporter/test-tools.sh --verbose              # print raw responses
```

Launches `uv run unraid-mcp-server` in stdio mode for each tool call. Requires `mcporter`, `uv`, and `python3` in `PATH`. Good for CI pipelines — no persistent server process needed.

---

## What `test-tools.sh` Tests

### Phase 1 — Param-free reads

All actions requiring no arguments beyond `action` itself.

| Tool | Actions tested |
|------|----------------|
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
| `unraid_settings` | *(all 9 actions skipped — mutations only)* |

### Phase 2 — ID-discovered reads

IDs are extracted from Phase 1 responses and used for actions requiring a specific resource. Each is skipped if Phase 1 returned no matching resources.

| Action | Source of ID |
|--------|--------------|
| `docker: details` | first container from `docker: list` |
| `docker: logs` | first container from `docker: list` |
| `docker: network_details` | first network from `docker: networks` |
| `storage: disk_details` | first disk from `storage: disks` |
| `storage: logs` | first path from `storage: log_files` |
| `vm: details` | first VM from `vm: list` |
| `keys: get` | first key from `keys: list` |

### Skipped actions (and why)

| Label | Meaning |
|-------|---------|
| `destructive (confirm=True required)` | Permanently modifies or deletes data |
| `mutation — state-changing` | Modifies live system state (container/VM lifecycle, settings) |
| `mutation — creates …` | Creates a new resource |

**Full skip list:**
- `unraid_info`: `update_server`, `update_ssh`
- `unraid_array`: `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`
- `unraid_storage`: `flash_backup`
- `unraid_docker`: `start`, `stop`, `restart`, `pause`, `unpause`, `update`, `remove`, `update_all`, `create_folder`, `set_folder_children`, `delete_entries`, `move_to_folder`, `move_to_position`, `rename_folder`, `create_folder_with_items`, `update_view_prefs`, `reset_template_mappings`
- `unraid_vm`: `start`, `stop`, `pause`, `resume`, `reboot`, `force_stop`, `reset`
- `unraid_notifications`: `create`, `create_unique`, `archive`, `unread`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`, `delete_archived`
- `unraid_rclone`: `create_remote`, `delete_remote`
- `unraid_keys`: `create`, `update`, `delete`
- `unraid_settings`: all 9 actions

### Output format

```
  <action label>                                              PASS
  <action label>                                              FAIL
      <first 3 lines of error detail>
  <action label>                                              SKIP (reason)

Results: 42 passed  0 failed  37 skipped  (79 total)
```

Exit code `0` when all executed tests pass, `1` if any fail.

---

## Destructive Actions

Neither script executes destructive actions. They are explicitly `skip_test`-ed with reason `"destructive (confirm=True required)"`.

All destructive actions require `confirm=True` at the call site. There is no environment variable gate — `confirm` is the sole guard.

### Safe Testing Strategy

| Strategy | When to use |
|----------|-------------|
| **Create → destroy** | Action has a create counterpart (keys, notifications, rclone remotes, docker folders) |
| **No-op apply** | Action mutates config but can be re-applied with current values unchanged (`update_ssh`) |
| **Dedicated test remote** | Action requires a remote target (`flash_backup`) |
| **Test VM** | Action requires a live VM (`force_stop`, `reset`) |
| **Mock/safety audit only** | Global blast radius, no safe isolation (`update_all`, `reset_template_mappings`, `setup_remote_access`, `configure_ups`) |
| **Secondary server only** | Run on `shart` (10.1.0.3), never `tootie` (10.1.0.2) |

For exact per-action mcporter commands, see [`docs/DESTRUCTIVE_ACTIONS.md`](../../docs/DESTRUCTIVE_ACTIONS.md).

---

## Prerequisites

```bash
# mcporter CLI
npm install -g mcporter

# uv (for test-tools.sh stdio mode)
curl -LsSf https://astral.sh/uv/install.sh | sh

# python3 — used for inline JSON extraction
python3 --version  # 3.12+
```

---

## Cleanup

`test-tools.sh` spawns stdio server subprocesses per call — they exit when mcporter finishes each invocation — and may write a timestamped log file under `${TMPDIR:-/tmp}`. It does not leave background processes.
