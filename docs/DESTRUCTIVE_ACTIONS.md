# Destructive Actions

**Last Updated:** 2026-03-13
**Total destructive actions:** 15 across 7 tools

All destructive actions require `confirm=True` at the call site. There is no additional environment variable gate — `confirm` is the sole guard.

> **mcporter commands below** use `$MCP_URL` (default: `http://localhost:6970/mcp`). Run `test-actions.sh` for automated non-destructive coverage; destructive actions are always skipped there and tested manually per the strategies below.

---

## `unraid_docker`

### `remove` — Delete a container permanently

```bash
# 1. Provision a throwaway canary container
docker run -d --name mcp-test-canary alpine sleep 3600

# 2. Discover its MCP-assigned ID
CID=$(mcporter call --http-url "$MCP_URL" --tool unraid_docker \
  --args '{"action":"list"}' --output json \
  | python3 -c "import json,sys; cs=json.load(sys.stdin).get('containers',[]); print(next(c['id'] for c in cs if 'mcp-test-canary' in c.get('name','')))")

# 3. Remove via MCP
mcporter call --http-url "$MCP_URL" --tool unraid_docker \
  --args "{\"action\":\"remove\",\"container_id\":\"$CID\",\"confirm\":true}" --output json

# 4. Verify
docker ps -a | grep mcp-test-canary  # should return nothing
```

---

### `update_all` — Pull latest images and restart all containers

**Strategy: mock/safety audit only.**
No safe live isolation — this hits every running container. Test via `tests/safety/` confirming the `confirm=False` guard raises `ToolError`. Do not run live unless all containers can tolerate a simultaneous restart.

---

### `delete_entries` — Delete Docker organizer folders/entries

```bash
# 1. Create a throwaway organizer folder
FOLDER=$(mcporter call --http-url "$MCP_URL" --tool unraid_docker \
  --args '{"action":"create_folder","name":"mcp-test-delete-me"}' --output json)
FID=$(echo "$FOLDER" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid_docker \
  --args "{\"action\":\"delete_entries\",\"entry_ids\":[\"$FID\"],\"confirm\":true}" --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid_docker \
  --args '{"action":"list"}' --output json | python3 -c \
  "import json,sys; folders=[x for x in json.load(sys.stdin).get('folders',[]) if 'mcp-test' in x.get('name','')]; print('clean' if not folders else folders)"
```

---

### `reset_template_mappings` — Wipe all template-to-container associations

**Strategy: mock/safety audit only.**
Global state — wipes all template mappings, requires full remapping afterward. No safe isolation. Test via `tests/safety/` confirming the `confirm=False` guard raises `ToolError`.

---

## `unraid_vm`

### `force_stop` — Hard power-off a VM (potential data corruption)

```bash
# Prerequisite: create a minimal Alpine test VM in Unraid VM manager
# (Alpine ISO, 512MB RAM, no persistent disk, name contains "mcp-test")

VID=$(mcporter call --http-url "$MCP_URL" --tool unraid_vm \
  --args '{"action":"list"}' --output json \
  | python3 -c "import json,sys; vms=json.load(sys.stdin).get('vms',[]); print(next(v.get('uuid',v.get('id','')) for v in vms if 'mcp-test' in v.get('name','')))")

mcporter call --http-url "$MCP_URL" --tool unraid_vm \
  --args "{\"action\":\"force_stop\",\"vm_id\":\"$VID\",\"confirm\":true}" --output json

# Verify: VM state should return to stopped
mcporter call --http-url "$MCP_URL" --tool unraid_vm \
  --args "{\"action\":\"details\",\"vm_id\":\"$VID\"}" --output json
```

---

### `reset` — Hard reset a VM (power cycle without graceful shutdown)

```bash
# Same minimal Alpine test VM as above
VID=$(mcporter call --http-url "$MCP_URL" --tool unraid_vm \
  --args '{"action":"list"}' --output json \
  | python3 -c "import json,sys; vms=json.load(sys.stdin).get('vms',[]); print(next(v.get('uuid',v.get('id','')) for v in vms if 'mcp-test' in v.get('name','')))")

mcporter call --http-url "$MCP_URL" --tool unraid_vm \
  --args "{\"action\":\"reset\",\"vm_id\":\"$VID\",\"confirm\":true}" --output json
```

---

## `unraid_notifications`

### `delete` — Permanently delete a notification

```bash
# 1. Create a test notification
NID=$(mcporter call --http-url "$MCP_URL" --tool unraid_notifications \
  --args '{"action":"create","title":"mcp-test-delete","subject":"safe to delete","description":"MCP destructive action test","importance":"normal"}' --output json \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid_notifications \
  --args "{\"action\":\"delete\",\"notification_id\":\"$NID\",\"confirm\":true}" --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid_notifications \
  --args '{"action":"list"}' --output json | python3 -c \
  "import json,sys; ns=[n for n in json.load(sys.stdin).get('notifications',[]) if 'mcp-test' in n.get('title','')]; print('clean' if not ns else ns)"
```

---

### `delete_archived` — Wipe all archived notifications (bulk, irreversible)

```bash
# 1. Create and archive a test notification first
mcporter call --http-url "$MCP_URL" --tool unraid_notifications \
  --args '{"action":"create","title":"mcp-test-archive-wipe","subject":"archive me","description":"safe to delete","importance":"normal"}' --output json
# (then archive it via action=archive if needed)

# 2. Wipe all archived
# NOTE: this deletes ALL archived notifications, not just the test one
mcporter call --http-url "$MCP_URL" --tool unraid_notifications \
  --args '{"action":"delete_archived","confirm":true}' --output json
```

> Run on `shart` if archival history on `tootie` matters.

---

## `unraid_rclone`

### `delete_remote` — Remove an rclone remote configuration

```bash
# 1. Create a throwaway local remote (points to /tmp — no real data)
mcporter call --http-url "$MCP_URL" --tool unraid_rclone \
  --args '{"action":"create_remote","name":"mcp-test-remote","remote_type":"local","config":{"root":"/tmp"}}' --output json

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid_rclone \
  --args '{"action":"delete_remote","remote_name":"mcp-test-remote","confirm":true}' --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid_rclone \
  --args '{"action":"list_remotes"}' --output json | python3 -c \
  "import json,sys; remotes=json.load(sys.stdin).get('remotes',[]); print('clean' if 'mcp-test-remote' not in remotes else 'FOUND — cleanup failed')"
```

> Note: `delete_remote` removes the config only — it does NOT delete data in the remote storage.

---

## `unraid_keys`

### `delete` — Delete an API key (immediately revokes access)

```bash
# 1. Create a test key
KID=$(mcporter call --http-url "$MCP_URL" --tool unraid_keys \
  --args '{"action":"create","name":"mcp-test-key","description":"Safe to delete — MCP destructive test"}' --output json \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid_keys \
  --args "{\"action\":\"delete\",\"key_id\":\"$KID\",\"confirm\":true}" --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid_keys \
  --args '{"action":"list"}' --output json | python3 -c \
  "import json,sys; ks=json.load(sys.stdin).get('keys',[]); print('clean' if not any('mcp-test-key' in k.get('name','') for k in ks) else 'FOUND — cleanup failed')"
```

---

## `unraid_storage`

### `flash_backup` — Rclone backup of flash drive (overwrites destination)

```bash
# Prerequisite: create a dedicated test remote pointing away from real backup destination
# (use rclone create_remote first, or configure mcp-test-remote manually)

mcporter call --http-url "$MCP_URL" --tool unraid_storage \
  --args '{"action":"flash_backup","remote_name":"mcp-test-remote","source_path":"/boot","destination_path":"/flash-backup-test","confirm":true}' --output json
```

> Never point at the same destination as your real flash backup. Create a dedicated `mcp-test-remote` (see `rclone: delete_remote` above for provisioning pattern).

---

## `unraid_settings`

### `configure_ups` — Overwrite UPS monitoring configuration

**Strategy: mock/safety audit only.**
Wrong config can break UPS integration. If live testing is required: read current config via `unraid_info ups_config`, save values, re-apply identical values (no-op), verify response matches. Test via `tests/safety/` for guard behavior.

---

### `setup_remote_access` — Modify remote access configuration

**Strategy: mock/safety audit only.**
Misconfiguration can break remote connectivity and lock you out. Do not run live. Test via `tests/safety/` confirming `confirm=False` raises `ToolError`.

---

### `enable_dynamic_remote_access` — Toggle dynamic remote access

```bash
# Strategy: toggle to false (disabling is reversible) on shart only, then restore
# Step 1: Read current state
CURRENT=$(mcporter call --http-url "$SHART_MCP_URL" --tool unraid_info \
  --args '{"action":"settings"}' --output json)

# Step 2: Disable (safe — can be re-enabled)
mcporter call --http-url "$SHART_MCP_URL" --tool unraid_settings \
  --args '{"action":"enable_dynamic_remote_access","access_url_type":"SUBDOMAINS","dynamic_enabled":false,"confirm":true}' --output json

# Step 3: Restore to previous state
mcporter call --http-url "$SHART_MCP_URL" --tool unraid_settings \
  --args '{"action":"enable_dynamic_remote_access","access_url_type":"SUBDOMAINS","dynamic_enabled":true,"confirm":true}' --output json
```

> Run on `shart` (10.1.0.3) only — never `tootie`.

---

## `unraid_info`

### `update_ssh` — Change SSH enabled state and port

```bash
# Strategy: read current config, re-apply same values (no-op change)

# 1. Read current SSH settings
CURRENT=$(mcporter call --http-url "$MCP_URL" --tool unraid_info \
  --args '{"action":"settings"}' --output json)
SSH_ENABLED=$(echo "$CURRENT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ssh',{}).get('enabled', True))")
SSH_PORT=$(echo "$CURRENT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ssh',{}).get('port', 22))")

# 2. Re-apply same values (no-op)
mcporter call --http-url "$MCP_URL" --tool unraid_info \
  --args "{\"action\":\"update_ssh\",\"ssh_enabled\":$SSH_ENABLED,\"ssh_port\":$SSH_PORT,\"confirm\":true}" --output json

# 3. Verify SSH connectivity still works
ssh root@"$UNRAID_HOST" -p "$SSH_PORT" exit
```

---

## Safety Audit (Automated)

The `tests/safety/` directory contains pytest tests that verify:
- Every destructive action raises `ToolError` when called with `confirm=False`
- Every destructive action raises `ToolError` when called without the `confirm` parameter
- The `DESTRUCTIVE_ACTIONS` set in each tool file stays in sync with the actions listed above

These run as part of the standard test suite:

```bash
uv run pytest tests/safety/ -v
```

---

## Summary Table

| Tool | Action | Strategy | Target Server |
|------|--------|----------|---------------|
| `unraid_docker` | `remove` | Pre-existing stopped container on Unraid server (skipped in test-destructive.sh) | either |
| `unraid_docker` | `update_all` | Mock/safety audit only | — |
| `unraid_docker` | `delete_entries` | Create folder → destroy | either |
| `unraid_docker` | `reset_template_mappings` | Mock/safety audit only | — |
| `unraid_vm` | `force_stop` | Minimal Alpine test VM | either |
| `unraid_vm` | `reset` | Minimal Alpine test VM | either |
| `unraid_notifications` | `delete` | Create notification → destroy | either |
| `unraid_notifications` | `delete_archived` | Create → archive → wipe | shart preferred |
| `unraid_rclone` | `delete_remote` | Create local:/tmp remote → destroy | either |
| `unraid_keys` | `delete` | Create test key → destroy | either |
| `unraid_storage` | `flash_backup` | Dedicated test remote, isolated path | either |
| `unraid_settings` | `configure_ups` | Mock/safety audit only | — |
| `unraid_settings` | `setup_remote_access` | Mock/safety audit only | — |
| `unraid_settings` | `enable_dynamic_remote_access` | Toggle false → restore | shart only |
| `unraid_info` | `update_ssh` | Read → re-apply same values (no-op) | either |
