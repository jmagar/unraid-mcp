# Destructive Actions

**Last Updated:** 2026-03-16
**Total destructive actions:** 12 across 8 domains (single `unraid` tool)

All destructive actions require `confirm=True` at the call site. There is no additional environment variable gate — `confirm` is the sole guard.

> **mcporter commands below** use `$MCP_URL` (default: `http://localhost:6970/mcp`). Run `test-actions.sh` for automated non-destructive coverage; destructive actions are always skipped there and tested manually per the strategies below.
>
> **Calling convention (v1.0.0+):** All operations use the single `unraid` tool with `action` (domain) + `subaction` (operation). For example:
> `mcporter call --http-url "$MCP_URL" --tool unraid --args '{"action":"docker","subaction":"list"}'`

---

## `array`

### `stop_array` — Stop the Unraid array

**Strategy: mock/safety audit only.**
Stopping the array unmounts all shares and can interrupt running containers and VMs accessing array data. Test via `tests/safety/` confirming the `confirm=False` guard raises `ToolError`. Do not run live unless all containers and VMs are shut down first.

---

### `remove_disk` — Remove a disk from the array

```bash
# Prerequisite: array must already be stopped; use a disk you intend to remove

mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"array","subaction":"remove_disk","disk_id":"<DISK_ID>","confirm":true}' --output json
```

---

### `clear_disk_stats` — Clear I/O statistics for a disk (irreversible)

```bash
# Discover disk IDs
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"disk","subaction":"disks"}' --output json

# Clear stats for a specific disk
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"array","subaction":"clear_disk_stats","disk_id":"<DISK_ID>","confirm":true}' --output json
```

---

## `vm`

### `force_stop` — Hard power-off a VM (potential data corruption)

```bash
# Prerequisite: create a minimal Alpine test VM in Unraid VM manager
# (Alpine ISO, 512MB RAM, no persistent disk, name contains "mcp-test")

VID=$(mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"vm","subaction":"list"}' --output json \
  | python3 -c "import json,sys; vms=json.load(sys.stdin).get('vms',[]); print(next(v.get('uuid',v.get('id','')) for v in vms if 'mcp-test' in v.get('name','')))")

mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"vm\",\"subaction\":\"force_stop\",\"vm_id\":\"$VID\",\"confirm\":true}" --output json

# Verify: VM state should return to stopped
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"vm\",\"subaction\":\"details\",\"vm_id\":\"$VID\"}" --output json
```

---

### `reset` — Hard reset a VM (power cycle without graceful shutdown)

```bash
# Same minimal Alpine test VM as above
VID=$(mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"vm","subaction":"list"}' --output json \
  | python3 -c "import json,sys; vms=json.load(sys.stdin).get('vms',[]); print(next(v.get('uuid',v.get('id','')) for v in vms if 'mcp-test' in v.get('name','')))")

mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"vm\",\"subaction\":\"reset\",\"vm_id\":\"$VID\",\"confirm\":true}" --output json
```

---

## `notification`

### `delete` — Permanently delete a notification

```bash
# 1. Create a test notification, then list to get the real stored ID (create response
#    ID is ULID-based; stored filename uses a unix timestamp, so IDs differ)
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"create","title":"mcp-test-delete","subject":"safe to delete","description":"MCP destructive action test","importance":"INFO"}' --output json
NID=$(mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"list","notification_type":"UNREAD"}' --output json \
  | python3 -c "
import json,sys
notifs=json.load(sys.stdin).get('notifications',[])
matches=[n['id'] for n in reversed(notifs) if n.get('title')=='mcp-test-delete']
print(matches[0] if matches else '')")

# 2. Delete it (notification_type required)
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"notification\",\"subaction\":\"delete\",\"notification_id\":\"$NID\",\"notification_type\":\"UNREAD\",\"confirm\":true}" --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"list"}' --output json | python3 -c \
  "import json,sys; ns=[n for n in json.load(sys.stdin).get('notifications',[]) if 'mcp-test' in n.get('title','')]; print('clean' if not ns else ns)"
```

---

### `delete_archived` — Wipe all archived notifications (bulk, irreversible)

```bash
# 1. Create and archive a test notification
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"create","title":"mcp-test-archive-wipe","subject":"archive me","description":"safe to delete","importance":"INFO"}' --output json
AID=$(mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"list","notification_type":"UNREAD"}' --output json \
  | python3 -c "
import json,sys
notifs=json.load(sys.stdin).get('notifications',[])
matches=[n['id'] for n in reversed(notifs) if n.get('title')=='mcp-test-archive-wipe']
print(matches[0] if matches else '')")
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"notification\",\"subaction\":\"archive\",\"notification_id\":\"$AID\"}" --output json

# 2. Wipe all archived
# NOTE: this deletes ALL archived notifications, not just the test one
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"notification","subaction":"delete_archived","confirm":true}' --output json
```

> Run on `shart` if archival history on `tootie` matters.

---

## `rclone`

### `delete_remote` — Remove an rclone remote configuration

```bash
# 1. Create a throwaway local remote (points to /tmp — no real data)
#    Parameters: name (str), provider_type (str), config_data (dict)
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"rclone","subaction":"create_remote","name":"mcp-test-remote","provider_type":"local","config_data":{"root":"/tmp"}}' --output json

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"rclone","subaction":"delete_remote","name":"mcp-test-remote","confirm":true}' --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"rclone","subaction":"list_remotes"}' --output json | python3 -c \
  "import json,sys; remotes=json.load(sys.stdin).get('remotes',[]); print('clean' if 'mcp-test-remote' not in remotes else 'FOUND — cleanup failed')"
```

> Note: `delete_remote` removes the config only — it does NOT delete data in the remote storage.

---

## `key`

### `delete` — Delete an API key (immediately revokes access)

```bash
# 1. Create a test key (names cannot contain hyphens; ID is at key.id)
KID=$(mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"key","subaction":"create","name":"mcp test key","roles":["VIEWER"]}' --output json \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('key',{}).get('id',''))")

# 2. Delete it
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args "{\"action\":\"key\",\"subaction\":\"delete\",\"key_id\":\"$KID\",\"confirm\":true}" --output json

# 3. Verify
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"key","subaction":"list"}' --output json | python3 -c \
  "import json,sys; ks=json.load(sys.stdin).get('keys',[]); print('clean' if not any('mcp test key' in k.get('name','') for k in ks) else 'FOUND — cleanup failed')"
```

---

## `disk`

### `flash_backup` — Rclone backup of flash drive (overwrites destination)

```bash
# Prerequisite: create a dedicated test remote pointing away from real backup destination
# (use rclone create_remote first, or configure mcp-test-remote manually)

mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"disk","subaction":"flash_backup","remote_name":"mcp-test-remote","source_path":"/boot","destination_path":"/flash-backup-test","confirm":true}' --output json
```

> Never point at the same destination as your real flash backup. Create a dedicated `mcp-test-remote` (see `rclone: delete_remote` above for provisioning pattern).

---

## `setting`

### `configure_ups` — Overwrite UPS monitoring configuration

**Strategy: mock/safety audit only.**
Wrong config can break UPS integration. If live testing is required: read current config via `unraid(action="system", subaction="ups_config")`, save values, re-apply identical values (no-op), verify response matches. Test via `tests/safety/` for guard behavior.

---

## `plugin`

### `remove` — Uninstall a plugin (irreversible without re-install)

**Strategy: mock/safety audit only.**
Removing a plugin cannot be undone without a full re-install. Test via `tests/safety/` confirming the `confirm=False` guard raises `ToolError`. Do not run live unless the plugin is intentionally being uninstalled.

```bash
# If live testing is necessary (intentional removal only):
mcporter call --http-url "$MCP_URL" --tool unraid \
  --args '{"action":"plugin","subaction":"remove","names":["<plugin-name>"],"confirm":true}' --output json
```

---

## Safety Audit (Automated)

The `tests/safety/` directory contains pytest tests that verify:
- Every destructive action raises `ToolError` when called with `confirm=False`
- Every destructive action raises `ToolError` when called without the `confirm` parameter
- The `_*_DESTRUCTIVE` sets in `unraid_mcp/tools/unraid.py` stay in sync with the actions listed above
- No GraphQL request reaches the network layer when confirmation is missing (`TestNoGraphQLCallsWhenUnconfirmed`)
- Non-destructive actions never require `confirm` (`TestNonDestructiveActionsNeverRequireConfirm`)

These run as part of the standard test suite:

```bash
uv run pytest tests/safety/ -v
```

---

## Summary Table

| Domain (`action=`) | Subaction | Strategy | Target Server |
|--------------------|-----------|----------|---------------|
| `array` | `stop_array` | Mock/safety audit only | — |
| `array` | `remove_disk` | Array must be stopped; use intended disk | either |
| `array` | `clear_disk_stats` | Discover disk ID → clear | either |
| `vm` | `force_stop` | Minimal Alpine test VM | either |
| `vm` | `reset` | Minimal Alpine test VM | either |
| `notification` | `delete` | Create notification → destroy | either |
| `notification` | `delete_archived` | Create → archive → wipe | shart preferred |
| `rclone` | `delete_remote` | Create local:/tmp remote → destroy | either |
| `key` | `delete` | Create test key → destroy | either |
| `disk` | `flash_backup` | Dedicated test remote, isolated path | either |
| `setting` | `configure_ups` | Mock/safety audit only | — |
| `plugin` | `remove` | Mock/safety audit only | — |
