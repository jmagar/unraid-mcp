# GraphQL Mutations Expansion Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all 28 missing GraphQL mutations across 11 files, bringing the server from 76 to 104 actions.

**Architecture:** Follows the existing consolidated action pattern — QUERIES/MUTATIONS dicts, ALL_ACTIONS set, Literal type with sync-guard, and handler branches inside the registered tool function. Five existing tool files gain new mutations; one new tool file (`tools/settings.py`) is created for the 9 settings/connect mutations; `server.py` gets one new import and registration.

**Tech Stack:** Python 3.12+, FastMCP, httpx, pytest, uv

---

## File Structure

| File | Change | New actions |
|---|---|---|
| `unraid_mcp/tools/notifications.py` | Modify | +5 mutations |
| `unraid_mcp/tools/storage.py` | Modify | +1 mutation |
| `unraid_mcp/tools/info.py` | Modify | +2 mutations |
| `unraid_mcp/tools/docker.py` | Modify | +11 mutations |
| `unraid_mcp/tools/settings.py` | **Create** | 9 mutations |
| `unraid_mcp/server.py` | Modify | register settings tool |
| `tests/test_notifications.py` | Modify | tests for 5 new actions |
| `tests/test_storage.py` | Modify | tests for flash_backup |
| `tests/test_info.py` | Modify | tests for update_server, update_ssh |
| `tests/test_docker.py` | Modify | tests for 11 organizer actions |
| `tests/test_settings.py` | **Create** | tests for all 9 settings actions |

---

## Chunk 1: Notifications — 5 new mutations

### Task 1: Test the 5 new notification mutations (RED)

**Files:**
- Modify: `tests/test_notifications.py`

- [ ] **Step 1: Append the new test class to `tests/test_notifications.py`**

```python
class TestNewNotificationMutations:
    async def test_archive_many_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "archiveNotifications": {
                "unread": {"info": 0, "warning": 0, "alert": 0, "total": 0},
                "archive": {"info": 2, "warning": 0, "alert": 0, "total": 2},
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="archive_many", notification_ids=["n:1", "n:2"])
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"ids": ["n:1", "n:2"]}

    async def test_archive_many_requires_ids(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="notification_ids"):
            await tool_fn(action="archive_many")

    async def test_create_unique_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifyIfUnique": {"id": "n:1", "title": "Test", "importance": "INFO"}
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="create_unique",
            title="Test",
            subject="Subj",
            description="Desc",
            importance="info",
        )
        assert result["success"] is True

    async def test_create_unique_returns_none_when_duplicate(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"notifyIfUnique": None}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="create_unique",
            title="T",
            subject="S",
            description="D",
            importance="info",
        )
        assert result["success"] is True
        assert result["duplicate"] is True

    async def test_create_unique_requires_fields(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="requires title"):
            await tool_fn(action="create_unique")

    async def test_unarchive_many_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "unarchiveNotifications": {
                "unread": {"info": 2, "warning": 0, "alert": 0, "total": 2},
                "archive": {"info": 0, "warning": 0, "alert": 0, "total": 0},
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="unarchive_many", notification_ids=["n:1", "n:2"])
        assert result["success"] is True

    async def test_unarchive_many_requires_ids(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="notification_ids"):
            await tool_fn(action="unarchive_many")

    async def test_unarchive_all_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "unarchiveAll": {
                "unread": {"info": 5, "warning": 1, "alert": 0, "total": 6},
                "archive": {"info": 0, "warning": 0, "alert": 0, "total": 0},
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="unarchive_all")
        assert result["success"] is True

    async def test_unarchive_all_with_importance(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"unarchiveAll": {"unread": {"total": 1}, "archive": {"total": 0}}}
        tool_fn = _make_tool()
        await tool_fn(action="unarchive_all", importance="WARNING")
        call_args = _mock_graphql.call_args
        assert call_args[0][1] == {"importance": "WARNING"}

    async def test_recalculate_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "recalculateOverview": {
                "unread": {"info": 3, "warning": 1, "alert": 0, "total": 4},
                "archive": {"info": 10, "warning": 0, "alert": 0, "total": 10},
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="recalculate")
        assert result["success"] is True
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/jmagar/workspace/unraid-mcp
uv run pytest tests/test_notifications.py::TestNewNotificationMutations -v 2>&1 | tail -20
```

Expected: All 10 tests FAIL with `ToolError: Invalid action` or collection errors.

---

### Task 2: Implement the 5 new notification mutations (GREEN)

**Files:**
- Modify: `unraid_mcp/tools/notifications.py`

- [ ] **Step 3: Add 5 entries to the MUTATIONS dict** (insert after the existing `"archive_all"` entry, before the closing `}`)

```python
    "archive_many": """
        mutation ArchiveNotifications($ids: [PrefixedID!]!) {
          archiveNotifications(ids: $ids) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "create_unique": """
        mutation NotifyIfUnique($input: NotificationData!) {
          notifyIfUnique(input: $input) { id title importance }
        }
    """,
    "unarchive_many": """
        mutation UnarchiveNotifications($ids: [PrefixedID!]!) {
          unarchiveNotifications(ids: $ids) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "unarchive_all": """
        mutation UnarchiveAll($importance: NotificationImportance) {
          unarchiveAll(importance: $importance) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "recalculate": """
        mutation RecalculateOverview {
          recalculateOverview {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
```

- [ ] **Step 4: Update the NOTIFICATION_ACTIONS Literal and add `notification_ids` param**

Replace the `NOTIFICATION_ACTIONS` Literal:

```python
NOTIFICATION_ACTIONS = Literal[
    "overview",
    "list",
    "warnings",
    "create",
    "archive",
    "unread",
    "delete",
    "delete_archived",
    "archive_all",
    "archive_many",
    "create_unique",
    "unarchive_many",
    "unarchive_all",
    "recalculate",
]
```

Add `notification_ids` to the tool function signature (after `description`):

```python
        notification_ids: list[str] | None = None,
```

Update the docstring to document the 5 new actions:

```
          archive_many - Archive multiple notifications by ID (requires notification_ids)
          create_unique - Create notification only if no equivalent unread exists (requires title, subject, description, importance)
          unarchive_many - Move notifications back to unread (requires notification_ids)
          unarchive_all - Move all archived notifications to unread (optional importance filter)
          recalculate - Recompute overview counts from disk
```

- [ ] **Step 5: Add handler branches** (insert before the final `raise ToolError(...)` line)

```python
            if action == "archive_many":
                if not notification_ids:
                    raise ToolError("notification_ids is required for 'archive_many' action")
                data = await make_graphql_request(MUTATIONS["archive_many"], {"ids": notification_ids})
                return {"success": True, "action": "archive_many", "data": data}

            if action == "create_unique":
                if title is None or subject is None or description is None or importance is None:
                    raise ToolError("create_unique requires title, subject, description, and importance")
                if importance.upper() not in _VALID_IMPORTANCE:
                    raise ToolError(
                        f"importance must be one of: {', '.join(sorted(_VALID_IMPORTANCE))}. "
                        f"Got: '{importance}'"
                    )
                input_data = {
                    "title": title,
                    "subject": subject,
                    "description": description,
                    "importance": importance.upper(),
                }
                data = await make_graphql_request(MUTATIONS["create_unique"], {"input": input_data})
                notification = data.get("notifyIfUnique")
                if notification is None:
                    return {"success": True, "duplicate": True, "data": None}
                return {"success": True, "duplicate": False, "data": notification}

            if action == "unarchive_many":
                if not notification_ids:
                    raise ToolError("notification_ids is required for 'unarchive_many' action")
                data = await make_graphql_request(MUTATIONS["unarchive_many"], {"ids": notification_ids})
                return {"success": True, "action": "unarchive_many", "data": data}

            if action == "unarchive_all":
                vars_: dict[str, Any] | None = None
                if importance:
                    vars_ = {"importance": importance.upper()}
                data = await make_graphql_request(MUTATIONS["unarchive_all"], vars_)
                return {"success": True, "action": "unarchive_all", "data": data}

            if action == "recalculate":
                data = await make_graphql_request(MUTATIONS["recalculate"])
                return {"success": True, "action": "recalculate", "data": data}
```

- [ ] **Step 6: Run tests — all must pass**

```bash
uv run pytest tests/test_notifications.py -v 2>&1 | tail -30
```

Expected: All tests PASS (original 24 + 10 new = 34 total).

- [ ] **Step 7: Lint**

```bash
uv run ruff check unraid_mcp/tools/notifications.py && uv run ruff format --check unraid_mcp/tools/notifications.py
```

Expected: No errors.

- [ ] **Step 8: Commit**

```bash
git add unraid_mcp/tools/notifications.py tests/test_notifications.py
git commit -m "feat: add 5 missing notification mutations (archive_many, create_unique, unarchive_many, unarchive_all, recalculate)"
```

---

## Chunk 2: Storage — flash_backup + Info — update_server/update_ssh

### Task 3: Test flash_backup mutation (RED)

**Files:**
- Modify: `tests/test_storage.py`

- [ ] **Step 1: Append new test class to `tests/test_storage.py`**

```python
class TestStorageFlashBackup:
    async def test_flash_backup_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(
                action="flash_backup",
                remote_name="myremote",
                source_path="/boot",
                destination_path="/backups/flash",
            )

    async def test_flash_backup_requires_remote_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="remote_name"):
            await tool_fn(action="flash_backup", confirm=True)

    async def test_flash_backup_requires_source_path(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="source_path"):
            await tool_fn(action="flash_backup", confirm=True, remote_name="r")

    async def test_flash_backup_requires_destination_path(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destination_path"):
            await tool_fn(action="flash_backup", confirm=True, remote_name="r", source_path="/boot")

    async def test_flash_backup_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "initiateFlashBackup": {"status": "started", "jobId": "job-123"}
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="flash_backup",
            confirm=True,
            remote_name="myremote",
            source_path="/boot",
            destination_path="/backups/flash",
        )
        assert result["success"] is True
        assert result["data"]["status"] == "started"

    async def test_flash_backup_passes_options(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"initiateFlashBackup": {"status": "started", "jobId": None}}
        tool_fn = _make_tool()
        await tool_fn(
            action="flash_backup",
            confirm=True,
            remote_name="r",
            source_path="/boot",
            destination_path="/bak",
            backup_options={"dry-run": True},
        )
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["options"] == {"dry-run": True}
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/test_storage.py::TestStorageFlashBackup -v 2>&1 | tail -15
```

Expected: All FAIL with `ToolError: Invalid action` or collection errors.

---

### Task 4: Implement flash_backup in storage.py (GREEN)

**Files:**
- Modify: `unraid_mcp/tools/storage.py`

- [ ] **Step 3: Add MUTATIONS dict and DESTRUCTIVE_ACTIONS** (insert after the QUERIES dict closing `}`)

```python
MUTATIONS: dict[str, str] = {
    "flash_backup": """
        mutation InitiateFlashBackup($input: InitiateFlashBackupInput!) {
          initiateFlashBackup(input: $input) { status jobId }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"flash_backup"}
```

- [ ] **Step 4: Update ALL_ACTIONS, STORAGE_ACTIONS Literal, and sync guard**

Replace:
```python
ALL_ACTIONS = set(QUERIES)
```
With:
```python
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)
```

Replace the STORAGE_ACTIONS Literal:
```python
STORAGE_ACTIONS = Literal[
    "shares",
    "disks",
    "disk_details",
    "unassigned",
    "log_files",
    "logs",
    "flash_backup",
]
```

- [ ] **Step 5: Add params and `confirm` to the tool function signature**

Add after `tail_lines`:
```python
        confirm: bool = False,
        remote_name: str | None = None,
        source_path: str | None = None,
        destination_path: str | None = None,
        backup_options: dict[str, Any] | None = None,
```

- [ ] **Step 6: Add validation and handler branch** (insert before the final `raise ToolError(...)`)

Add destructive guard after the action validation:
```python
        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")
```

Add handler:
```python
            if action == "flash_backup":
                if not remote_name:
                    raise ToolError("remote_name is required for 'flash_backup' action")
                if not source_path:
                    raise ToolError("source_path is required for 'flash_backup' action")
                if not destination_path:
                    raise ToolError("destination_path is required for 'flash_backup' action")
                input_data: dict[str, Any] = {
                    "remoteName": remote_name,
                    "sourcePath": source_path,
                    "destinationPath": destination_path,
                }
                if backup_options is not None:
                    input_data["options"] = backup_options
                data = await make_graphql_request(MUTATIONS["flash_backup"], {"input": input_data})
                return {"success": True, "action": "flash_backup", "data": data.get("initiateFlashBackup")}
```

Update the docstring to include:
```
          flash_backup - Initiate flash drive backup via rclone (requires remote_name, source_path, destination_path, confirm=True)
```

- [ ] **Step 7: Run all storage tests**

```bash
uv run pytest tests/test_storage.py -v 2>&1 | tail -20
```

Expected: All PASS.

- [ ] **Step 8: Lint**

```bash
uv run ruff check unraid_mcp/tools/storage.py && uv run ruff format --check unraid_mcp/tools/storage.py
```

- [ ] **Step 9: Commit**

```bash
git add unraid_mcp/tools/storage.py tests/test_storage.py
git commit -m "feat: add flash_backup mutation to storage tool"
```

---

### Task 5: Test info mutations — update_server, update_ssh (RED)

**Files:**
- Modify: `tests/test_info.py`

- [ ] **Step 10: Append new test class to `tests/test_info.py`**

```python
class TestInfoMutations:
    async def test_update_server_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateServerIdentity": {"id": "srv:1", "name": "tootie", "comment": "main server", "status": "ONLINE"}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_server", server_name="tootie", server_comment="main server")
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["name"] == "tootie"
        assert call_args[0][1]["comment"] == "main server"

    async def test_update_server_requires_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="server_name"):
            await tool_fn(action="update_server")

    async def test_update_server_with_sys_model(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateServerIdentity": {"id": "srv:1", "name": "tootie", "comment": None, "status": "ONLINE"}}
        tool_fn = _make_tool()
        await tool_fn(action="update_server", server_name="tootie", sys_model="Custom Server")
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["sysModel"] == "Custom Server"

    async def test_update_ssh_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSshSettings": {"id": "vars:1", "useSsh": True, "portssh": 22}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_ssh", ssh_enabled=True, ssh_port=22)
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["enabled"] is True
        assert call_args[0][1]["input"]["port"] == 22

    async def test_update_ssh_requires_enabled(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ssh_enabled"):
            await tool_fn(action="update_ssh", ssh_port=22)

    async def test_update_ssh_requires_port(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ssh_port"):
            await tool_fn(action="update_ssh", ssh_enabled=True)
```

- [ ] **Step 11: Run tests to confirm they fail**

```bash
uv run pytest tests/test_info.py::TestInfoMutations -v 2>&1 | tail -15
```

Expected: All FAIL.

---

### Task 6: Implement update_server and update_ssh in info.py (GREEN)

**Files:**
- Modify: `unraid_mcp/tools/info.py`

- [ ] **Step 12: Add MUTATIONS dict** (insert after the QUERIES dict closing `}`)

```python
MUTATIONS: dict[str, str] = {
    "update_server": """
        mutation UpdateServerIdentity($name: String!, $comment: String, $sysModel: String) {
          updateServerIdentity(name: $name, comment: $comment, sysModel: $sysModel) {
            id name comment status
          }
        }
    """,
    "update_ssh": """
        mutation UpdateSshSettings($input: UpdateSshInput!) {
          updateSshSettings(input: $input) { id useSsh portssh }
        }
    """,
}
```

- [ ] **Step 13: Update ALL_ACTIONS, INFO_ACTIONS Literal, and sync guard**

Replace:
```python
ALL_ACTIONS = set(QUERIES)
```
With:
```python
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)
```

Add `"update_server"` and `"update_ssh"` to the `INFO_ACTIONS` Literal (append before the closing bracket):
```python
    "update_server",
    "update_ssh",
```

Update the sync guard error message:
```python
if set(get_args(INFO_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(INFO_ACTIONS))
    _extra = set(get_args(INFO_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"INFO_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )
```

- [ ] **Step 14: Add params to the tool function signature**

Add after `device_id`:
```python
        server_name: str | None = None,
        server_comment: str | None = None,
        sys_model: str | None = None,
        ssh_enabled: bool | None = None,
        ssh_port: int | None = None,
```

- [ ] **Step 15: Add handler branches** (insert before the final `raise ToolError(...)`)

```python
            if action == "update_server":
                if server_name is None:
                    raise ToolError("server_name is required for 'update_server' action")
                variables = {"name": server_name}
                if server_comment is not None:
                    variables["comment"] = server_comment
                if sys_model is not None:
                    variables["sysModel"] = sys_model
                data = await make_graphql_request(MUTATIONS["update_server"], variables)
                return {"success": True, "action": "update_server", "data": data.get("updateServerIdentity")}

            if action == "update_ssh":
                if ssh_enabled is None:
                    raise ToolError("ssh_enabled is required for 'update_ssh' action")
                if ssh_port is None:
                    raise ToolError("ssh_port is required for 'update_ssh' action")
                data = await make_graphql_request(
                    MUTATIONS["update_ssh"],
                    {"input": {"enabled": ssh_enabled, "port": ssh_port}},
                )
                return {"success": True, "action": "update_ssh", "data": data.get("updateSshSettings")}
```

Update docstring to add:
```
          update_server - Update server name, comment, and model (requires server_name)
          update_ssh - Enable/disable SSH and set port (requires ssh_enabled, ssh_port)
```

- [ ] **Step 16: Run all info tests**

```bash
uv run pytest tests/test_info.py -v 2>&1 | tail -20
```

Expected: All PASS.

- [ ] **Step 17: Lint**

```bash
uv run ruff check unraid_mcp/tools/info.py && uv run ruff format --check unraid_mcp/tools/info.py
```

- [ ] **Step 18: Commit**

```bash
git add unraid_mcp/tools/info.py tests/test_info.py
git commit -m "feat: add update_server and update_ssh mutations to info tool"
```

---

## Chunk 3: Docker — 11 organizer mutations

### Task 7: Test the 11 Docker organizer mutations (RED)

**Files:**
- Modify: `tests/test_docker.py`

- [ ] **Step 1: Append organizer test class to `tests/test_docker.py`**

```python
# Helper fixture for organizer response
_ORGANIZER_RESPONSE = {
    "version": 1.0,
    "views": [{"id": "default", "name": "Default", "rootId": "root", "flatEntries": []}],
}


class TestDockerOrganizerMutations:
    async def test_create_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"createDockerFolder": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="create_folder", folder_name="Media Apps")
        assert result["success"] is True

    async def test_create_folder_requires_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="folder_name"):
            await tool_fn(action="create_folder")

    async def test_create_folder_passes_children(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"createDockerFolder": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        await tool_fn(action="create_folder", folder_name="Media", children_ids=["c1", "c2"])
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["childrenIds"] == ["c1", "c2"]

    async def test_set_folder_children_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setDockerFolderChildren": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="set_folder_children", children_ids=["c1"])
        assert result["success"] is True

    async def test_set_folder_children_requires_children(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="children_ids"):
            await tool_fn(action="set_folder_children")

    async def test_delete_entries_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete_entries", entry_ids=["e1"])

    async def test_delete_entries_requires_ids(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="entry_ids"):
            await tool_fn(action="delete_entries", confirm=True)

    async def test_delete_entries_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"deleteDockerEntries": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="delete_entries", entry_ids=["e1", "e2"], confirm=True)
        assert result["success"] is True

    async def test_move_to_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"moveDockerEntriesToFolder": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="move_to_folder",
            source_entry_ids=["e1"],
            destination_folder_id="folder-1",
        )
        assert result["success"] is True

    async def test_move_to_folder_requires_source_ids(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="source_entry_ids"):
            await tool_fn(action="move_to_folder", destination_folder_id="f1")

    async def test_move_to_folder_requires_destination(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destination_folder_id"):
            await tool_fn(action="move_to_folder", source_entry_ids=["e1"])

    async def test_move_to_position_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"moveDockerItemsToPosition": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="move_to_position",
            source_entry_ids=["e1"],
            destination_folder_id="folder-1",
            position=2.0,
        )
        assert result["success"] is True

    async def test_move_to_position_requires_position(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="position"):
            await tool_fn(
                action="move_to_position",
                source_entry_ids=["e1"],
                destination_folder_id="f1",
            )

    async def test_rename_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"renameDockerFolder": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="rename_folder", folder_id="f1", new_folder_name="New Name")
        assert result["success"] is True

    async def test_rename_folder_requires_folder_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="folder_id"):
            await tool_fn(action="rename_folder", new_folder_name="New")

    async def test_rename_folder_requires_new_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="new_folder_name"):
            await tool_fn(action="rename_folder", folder_id="f1")

    async def test_create_folder_with_items_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"createDockerFolderWithItems": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="create_folder_with_items", folder_name="New Folder")
        assert result["success"] is True

    async def test_create_folder_with_items_requires_name(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="folder_name"):
            await tool_fn(action="create_folder_with_items")

    async def test_update_view_prefs_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateDockerViewPreferences": _ORGANIZER_RESPONSE}
        tool_fn = _make_tool()
        result = await tool_fn(action="update_view_prefs", view_prefs={"sort": "name"})
        assert result["success"] is True

    async def test_update_view_prefs_requires_prefs(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="view_prefs"):
            await tool_fn(action="update_view_prefs")

    async def test_sync_templates_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "syncDockerTemplatePaths": {"scanned": 10, "matched": 8, "skipped": 2, "errors": []}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="sync_templates")
        assert result["success"] is True

    async def test_reset_template_mappings_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="reset_template_mappings")

    async def test_reset_template_mappings_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"resetDockerTemplateMappings": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="reset_template_mappings", confirm=True)
        assert result["success"] is True

    async def test_refresh_digests_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"refreshDockerDigests": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="refresh_digests")
        assert result["success"] is True
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/test_docker.py::TestDockerOrganizerMutations -v 2>&1 | tail -20
```

Expected: All FAIL.

---

### Task 8: Implement 11 organizer mutations in docker.py (GREEN)

**Files:**
- Modify: `unraid_mcp/tools/docker.py`

- [ ] **Step 3: Add 11 entries to the MUTATIONS dict** (append inside the existing MUTATIONS dict before its closing `}`)

```python
    "create_folder": """
        mutation CreateDockerFolder($name: String!, $parentId: String, $childrenIds: [String!]) {
          createDockerFolder(name: $name, parentId: $parentId, childrenIds: $childrenIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "set_folder_children": """
        mutation SetDockerFolderChildren($folderId: String, $childrenIds: [String!]!) {
          setDockerFolderChildren(folderId: $folderId, childrenIds: $childrenIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "delete_entries": """
        mutation DeleteDockerEntries($entryIds: [String!]!) {
          deleteDockerEntries(entryIds: $entryIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "move_to_folder": """
        mutation MoveDockerEntriesToFolder($sourceEntryIds: [String!]!, $destinationFolderId: String!) {
          moveDockerEntriesToFolder(sourceEntryIds: $sourceEntryIds, destinationFolderId: $destinationFolderId) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "move_to_position": """
        mutation MoveDockerItemsToPosition($sourceEntryIds: [String!]!, $destinationFolderId: String!, $position: Float!) {
          moveDockerItemsToPosition(sourceEntryIds: $sourceEntryIds, destinationFolderId: $destinationFolderId, position: $position) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "rename_folder": """
        mutation RenameDockerFolder($folderId: String!, $newName: String!) {
          renameDockerFolder(folderId: $folderId, newName: $newName) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "create_folder_with_items": """
        mutation CreateDockerFolderWithItems($name: String!, $parentId: String, $sourceEntryIds: [String!], $position: Float) {
          createDockerFolderWithItems(name: $name, parentId: $parentId, sourceEntryIds: $sourceEntryIds, position: $position) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "update_view_prefs": """
        mutation UpdateDockerViewPreferences($viewId: String, $prefs: JSON!) {
          updateDockerViewPreferences(viewId: $viewId, prefs: $prefs) {
            version views { id name rootId }
          }
        }
    """,
    "sync_templates": """
        mutation SyncDockerTemplatePaths {
          syncDockerTemplatePaths { scanned matched skipped errors }
        }
    """,
    "reset_template_mappings": """
        mutation ResetDockerTemplateMappings {
          resetDockerTemplateMappings
        }
    """,
    "refresh_digests": """
        mutation RefreshDockerDigests {
          refreshDockerDigests
        }
    """,
```

- [ ] **Step 4: Update DESTRUCTIVE_ACTIONS**

Replace:
```python
DESTRUCTIVE_ACTIONS = {"remove", "update_all"}
```
With:
```python
DESTRUCTIVE_ACTIONS = {"remove", "update_all", "delete_entries", "reset_template_mappings"}
```

- [ ] **Step 5: Update DOCKER_ACTIONS Literal**

Append 11 new strings to the Literal (before the closing `]`):
```python
    "create_folder",
    "set_folder_children",
    "delete_entries",
    "move_to_folder",
    "move_to_position",
    "rename_folder",
    "create_folder_with_items",
    "update_view_prefs",
    "sync_templates",
    "reset_template_mappings",
    "refresh_digests",
```

- [ ] **Step 6: Add new params to the tool function signature**

Add after `tail_lines`:
```python
        folder_name: str | None = None,
        folder_id: str | None = None,
        parent_id: str | None = None,
        children_ids: list[str] | None = None,
        entry_ids: list[str] | None = None,
        source_entry_ids: list[str] | None = None,
        destination_folder_id: str | None = None,
        position: float | None = None,
        new_folder_name: str | None = None,
        view_id: str = "default",
        view_prefs: dict[str, Any] | None = None,
```

- [ ] **Step 7: Add handler branches** (insert before the final `raise ToolError(...)`)

```python
            # --- Docker organizer mutations ---
            if action == "create_folder":
                if not folder_name:
                    raise ToolError("folder_name is required for 'create_folder' action")
                vars_: dict[str, Any] = {"name": folder_name}
                if parent_id is not None:
                    vars_["parentId"] = parent_id
                if children_ids is not None:
                    vars_["childrenIds"] = children_ids
                data = await make_graphql_request(MUTATIONS["create_folder"], vars_)
                return {"success": True, "action": "create_folder", "organizer": data.get("createDockerFolder")}

            if action == "set_folder_children":
                if not children_ids:
                    raise ToolError("children_ids is required for 'set_folder_children' action")
                vars_ = {"childrenIds": children_ids}
                if folder_id is not None:
                    vars_["folderId"] = folder_id
                data = await make_graphql_request(MUTATIONS["set_folder_children"], vars_)
                return {"success": True, "action": "set_folder_children", "organizer": data.get("setDockerFolderChildren")}

            if action == "delete_entries":
                if not entry_ids:
                    raise ToolError("entry_ids is required for 'delete_entries' action")
                data = await make_graphql_request(MUTATIONS["delete_entries"], {"entryIds": entry_ids})
                return {"success": True, "action": "delete_entries", "organizer": data.get("deleteDockerEntries")}

            if action == "move_to_folder":
                if not source_entry_ids:
                    raise ToolError("source_entry_ids is required for 'move_to_folder' action")
                if not destination_folder_id:
                    raise ToolError("destination_folder_id is required for 'move_to_folder' action")
                data = await make_graphql_request(
                    MUTATIONS["move_to_folder"],
                    {"sourceEntryIds": source_entry_ids, "destinationFolderId": destination_folder_id},
                )
                return {"success": True, "action": "move_to_folder", "organizer": data.get("moveDockerEntriesToFolder")}

            if action == "move_to_position":
                if not source_entry_ids:
                    raise ToolError("source_entry_ids is required for 'move_to_position' action")
                if not destination_folder_id:
                    raise ToolError("destination_folder_id is required for 'move_to_position' action")
                if position is None:
                    raise ToolError("position is required for 'move_to_position' action")
                data = await make_graphql_request(
                    MUTATIONS["move_to_position"],
                    {
                        "sourceEntryIds": source_entry_ids,
                        "destinationFolderId": destination_folder_id,
                        "position": position,
                    },
                )
                return {"success": True, "action": "move_to_position", "organizer": data.get("moveDockerItemsToPosition")}

            if action == "rename_folder":
                if not folder_id:
                    raise ToolError("folder_id is required for 'rename_folder' action")
                if not new_folder_name:
                    raise ToolError("new_folder_name is required for 'rename_folder' action")
                data = await make_graphql_request(
                    MUTATIONS["rename_folder"], {"folderId": folder_id, "newName": new_folder_name}
                )
                return {"success": True, "action": "rename_folder", "organizer": data.get("renameDockerFolder")}

            if action == "create_folder_with_items":
                if not folder_name:
                    raise ToolError("folder_name is required for 'create_folder_with_items' action")
                vars_ = {"name": folder_name}
                if parent_id is not None:
                    vars_["parentId"] = parent_id
                if entry_ids is not None:
                    vars_["sourceEntryIds"] = entry_ids
                if position is not None:
                    vars_["position"] = position
                data = await make_graphql_request(MUTATIONS["create_folder_with_items"], vars_)
                return {"success": True, "action": "create_folder_with_items", "organizer": data.get("createDockerFolderWithItems")}

            if action == "update_view_prefs":
                if view_prefs is None:
                    raise ToolError("view_prefs is required for 'update_view_prefs' action")
                data = await make_graphql_request(
                    MUTATIONS["update_view_prefs"], {"viewId": view_id, "prefs": view_prefs}
                )
                return {"success": True, "action": "update_view_prefs", "organizer": data.get("updateDockerViewPreferences")}

            if action == "sync_templates":
                data = await make_graphql_request(MUTATIONS["sync_templates"])
                return {"success": True, "action": "sync_templates", "result": data.get("syncDockerTemplatePaths")}

            if action == "reset_template_mappings":
                data = await make_graphql_request(MUTATIONS["reset_template_mappings"])
                return {"success": True, "action": "reset_template_mappings", "result": data.get("resetDockerTemplateMappings")}

            if action == "refresh_digests":
                data = await make_graphql_request(MUTATIONS["refresh_digests"])
                return {"success": True, "action": "refresh_digests", "result": data.get("refreshDockerDigests")}
```

Update docstring to add the 11 new actions.

- [ ] **Step 8: Run all docker tests**

```bash
uv run pytest tests/test_docker.py -v 2>&1 | tail -30
```

Expected: All PASS.

- [ ] **Step 9: Lint**

```bash
uv run ruff check unraid_mcp/tools/docker.py && uv run ruff format --check unraid_mcp/tools/docker.py
```

- [ ] **Step 10: Commit**

```bash
git add unraid_mcp/tools/docker.py tests/test_docker.py
git commit -m "feat: add 11 Docker organizer mutations (folders, positions, templates, digests)"
```

---

## Chunk 4: New settings tool — 9 mutations

### Task 9: Create test_settings.py (RED)

**Files:**
- Create: `tests/test_settings.py`

- [ ] **Step 1: Create `tests/test_settings.py`**

```python
"""Tests for unraid_settings tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch(
        "unraid_mcp.tools.settings.make_graphql_request", new_callable=AsyncMock
    ) as mock:
        yield mock


def _make_tool():
    return make_tool_fn(
        "unraid_mcp.tools.settings", "register_settings_tool", "unraid_settings"
    )


class TestSettingsValidation:
    async def test_invalid_action_rejected(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="nonexistent")  # type: ignore[arg-type]

    async def test_configure_ups_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="configure_ups", ups_config={"service": "ENABLE"})

    async def test_setup_remote_access_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="setup_remote_access", access_type="ALWAYS")

    async def test_enable_dynamic_remote_access_requires_confirm(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(
                action="enable_dynamic_remote_access",
                access_url_type="LAN",
                dynamic_enabled=True,
            )


class TestSettingsUpdate:
    async def test_update_requires_settings_input(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="settings_input"):
            await tool_fn(action="update")

    async def test_update_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSettings": {"restartRequired": False, "values": {"key": "val"}, "warnings": []}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update", settings_input={"shareSmbEnabled": True})
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"] == {"shareSmbEnabled": True}


class TestTemperatureConfig:
    async def test_update_temperature_requires_config(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="temperature_config"):
            await tool_fn(action="update_temperature")

    async def test_update_temperature_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateTemperatureConfig": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="update_temperature",
            temperature_config={"enabled": True, "polling_interval": 30},
        )
        assert result["success"] is True


class TestSystemTime:
    async def test_update_time_requires_at_least_one_field(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="at least one"):
            await tool_fn(action="update_time")

    async def test_update_time_timezone_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSystemTime": {
                "currentTime": "2026-03-13T12:00:00Z",
                "timeZone": "America/New_York",
                "useNtp": True,
                "ntpServers": ["pool.ntp.org"],
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_time", time_zone="America/New_York")
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["timeZone"] == "America/New_York"

    async def test_update_time_ntp_servers(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateSystemTime": {"currentTime": "2026-03-13T12:00:00Z", "timeZone": "UTC", "useNtp": True, "ntpServers": ["0.pool.ntp.org"]}}
        tool_fn = _make_tool()
        await tool_fn(action="update_time", use_ntp=True, ntp_servers=["0.pool.ntp.org"])
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["useNtp"] is True
        assert call_args[0][1]["input"]["ntpServers"] == ["0.pool.ntp.org"]


class TestUpsConfig:
    async def test_configure_ups_requires_config(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ups_config"):
            await tool_fn(action="configure_ups", confirm=True)

    async def test_configure_ups_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"configureUps": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="configure_ups",
            confirm=True,
            ups_config={"service": "ENABLE", "upsCable": "USB"},
        )
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["config"]["service"] == "ENABLE"


class TestApiSettings:
    async def test_update_api_requires_at_least_one_field(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="at least one"):
            await tool_fn(action="update_api")

    async def test_update_api_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateApiSettings": {"accessType": "ALWAYS", "forwardType": None, "port": None}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_api", access_type="ALWAYS")
        assert result["success"] is True


class TestConnectActions:
    async def test_connect_sign_in_requires_api_key(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="api_key"):
            await tool_fn(action="connect_sign_in")

    async def test_connect_sign_in_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"connectSignIn": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="connect_sign_in",
            api_key="secret-key",
            username="jmagar",
            email="jmagar@gmail.com",
        )
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["apiKey"] == "secret-key"
        assert call_args[0][1]["input"]["userInfo"]["preferred_username"] == "jmagar"

    async def test_connect_sign_out_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"connectSignOut": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="connect_sign_out")
        assert result["success"] is True


class TestRemoteAccess:
    async def test_setup_remote_access_requires_access_type(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="access_type"):
            await tool_fn(action="setup_remote_access", confirm=True)

    async def test_setup_remote_access_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setupRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="setup_remote_access", confirm=True, access_type="ALWAYS"
        )
        assert result["success"] is True

    async def test_enable_dynamic_remote_access_requires_type_and_enabled(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="access_url_type"):
            await tool_fn(action="enable_dynamic_remote_access", confirm=True)

    async def test_enable_dynamic_remote_access_requires_enabled_field(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="dynamic_enabled"):
            await tool_fn(
                action="enable_dynamic_remote_access", confirm=True, access_url_type="LAN"
            )

    async def test_enable_dynamic_remote_access_success(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"enableDynamicRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="enable_dynamic_remote_access",
            confirm=True,
            access_url_type="LAN",
            access_url_ipv4="10.1.0.2",
            dynamic_enabled=True,
        )
        assert result["success"] is True
        call_args = _mock_graphql.call_args
        assert call_args[0][1]["input"]["enabled"] is True
        assert call_args[0][1]["input"]["url"]["type"] == "LAN"
```

- [ ] **Step 2: Run tests to confirm they fail (import error expected)**

```bash
uv run pytest tests/test_settings.py -v 2>&1 | tail -10
```

Expected: `ModuleNotFoundError` or `ImportError` — the file doesn't exist yet.

---

### Task 10: Create tools/settings.py (GREEN)

**Files:**
- Create: `unraid_mcp/tools/settings.py`

- [ ] **Step 3: Create `unraid_mcp/tools/settings.py`**

```python
"""System settings, time, UPS, and remote access mutations.

Provides the `unraid_settings` tool with 9 actions for updating system
configuration, time settings, UPS, API settings, and Unraid Connect.
"""

from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


MUTATIONS: dict[str, str] = {
    "update": """
        mutation UpdateSettings($input: JSON!) {
          updateSettings(input: $input) { restartRequired values warnings }
        }
    """,
    "update_temperature": """
        mutation UpdateTemperatureConfig($input: TemperatureConfigInput!) {
          updateTemperatureConfig(input: $input)
        }
    """,
    "update_time": """
        mutation UpdateSystemTime($input: UpdateSystemTimeInput!) {
          updateSystemTime(input: $input) { currentTime timeZone useNtp ntpServers }
        }
    """,
    "configure_ups": """
        mutation ConfigureUps($config: UPSConfigInput!) {
          configureUps(config: $config)
        }
    """,
    "update_api": """
        mutation UpdateApiSettings($input: ConnectSettingsInput!) {
          updateApiSettings(input: $input) { accessType forwardType port }
        }
    """,
    "connect_sign_in": """
        mutation ConnectSignIn($input: ConnectSignInInput!) {
          connectSignIn(input: $input)
        }
    """,
    "connect_sign_out": """
        mutation ConnectSignOut {
          connectSignOut
        }
    """,
    "setup_remote_access": """
        mutation SetupRemoteAccess($input: SetupRemoteAccessInput!) {
          setupRemoteAccess(input: $input)
        }
    """,
    "enable_dynamic_remote_access": """
        mutation EnableDynamicRemoteAccess($input: EnableDynamicRemoteAccessInput!) {
          enableDynamicRemoteAccess(input: $input)
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"configure_ups", "setup_remote_access", "enable_dynamic_remote_access"}
ALL_ACTIONS = set(MUTATIONS)

SETTINGS_ACTIONS = Literal[
    "update",
    "update_temperature",
    "update_time",
    "configure_ups",
    "update_api",
    "connect_sign_in",
    "connect_sign_out",
    "setup_remote_access",
    "enable_dynamic_remote_access",
]

if set(get_args(SETTINGS_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(SETTINGS_ACTIONS))
    _extra = set(get_args(SETTINGS_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"SETTINGS_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_settings_tool(mcp: FastMCP) -> None:
    """Register the unraid_settings tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_settings(
        action: SETTINGS_ACTIONS,
        confirm: bool = False,
        # updateSettings
        settings_input: dict[str, Any] | None = None,
        # updateTemperatureConfig
        temperature_config: dict[str, Any] | None = None,
        # updateSystemTime
        time_zone: str | None = None,
        use_ntp: bool | None = None,
        ntp_servers: list[str] | None = None,
        manual_datetime: str | None = None,
        # configureUps
        ups_config: dict[str, Any] | None = None,
        # updateApiSettings / setupRemoteAccess
        access_type: str | None = None,
        forward_type: str | None = None,
        port: int | None = None,
        # connectSignIn
        api_key: str | None = None,
        username: str | None = None,
        email: str | None = None,
        avatar: str | None = None,
        # enableDynamicRemoteAccess
        access_url_type: str | None = None,
        access_url_name: str | None = None,
        access_url_ipv4: str | None = None,
        access_url_ipv6: str | None = None,
        dynamic_enabled: bool | None = None,
    ) -> dict[str, Any]:
        """Update Unraid system settings, time, UPS, and remote access configuration.

        Actions:
          update - Update system settings (requires settings_input dict)
          update_temperature - Update temperature sensor config (requires temperature_config dict)
          update_time - Update system time/timezone/NTP (requires at least one of: time_zone, use_ntp, ntp_servers, manual_datetime)
          configure_ups - Configure UPS monitoring (requires ups_config dict, confirm=True)
          update_api - Update API/Connect settings (requires at least one of: access_type, forward_type, port)
          connect_sign_in - Sign in to Unraid Connect (requires api_key)
          connect_sign_out - Sign out from Unraid Connect
          setup_remote_access - Configure remote access (requires access_type, confirm=True)
          enable_dynamic_remote_access - Enable/disable dynamic remote access (requires access_url_type, dynamic_enabled, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("settings", action, logger):
            logger.info(f"Executing unraid_settings action={action}")

            if action == "update":
                if settings_input is None:
                    raise ToolError("settings_input is required for 'update' action")
                data = await make_graphql_request(MUTATIONS["update"], {"input": settings_input})
                return {"success": True, "action": "update", "data": data.get("updateSettings")}

            if action == "update_temperature":
                if temperature_config is None:
                    raise ToolError("temperature_config is required for 'update_temperature' action")
                data = await make_graphql_request(
                    MUTATIONS["update_temperature"], {"input": temperature_config}
                )
                return {"success": True, "action": "update_temperature", "result": data.get("updateTemperatureConfig")}

            if action == "update_time":
                time_input: dict[str, Any] = {}
                if time_zone is not None:
                    time_input["timeZone"] = time_zone
                if use_ntp is not None:
                    time_input["useNtp"] = use_ntp
                if ntp_servers is not None:
                    time_input["ntpServers"] = ntp_servers
                if manual_datetime is not None:
                    time_input["manualDateTime"] = manual_datetime
                if not time_input:
                    raise ToolError(
                        "update_time requires at least one of: time_zone, use_ntp, ntp_servers, manual_datetime"
                    )
                data = await make_graphql_request(MUTATIONS["update_time"], {"input": time_input})
                return {"success": True, "action": "update_time", "data": data.get("updateSystemTime")}

            if action == "configure_ups":
                if ups_config is None:
                    raise ToolError("ups_config is required for 'configure_ups' action")
                data = await make_graphql_request(MUTATIONS["configure_ups"], {"config": ups_config})
                return {"success": True, "action": "configure_ups", "result": data.get("configureUps")}

            if action == "update_api":
                api_input: dict[str, Any] = {}
                if access_type is not None:
                    api_input["accessType"] = access_type
                if forward_type is not None:
                    api_input["forwardType"] = forward_type
                if port is not None:
                    api_input["port"] = port
                if not api_input:
                    raise ToolError(
                        "update_api requires at least one of: access_type, forward_type, port"
                    )
                data = await make_graphql_request(MUTATIONS["update_api"], {"input": api_input})
                return {"success": True, "action": "update_api", "data": data.get("updateApiSettings")}

            if action == "connect_sign_in":
                if not api_key:
                    raise ToolError("api_key is required for 'connect_sign_in' action")
                sign_in_input: dict[str, Any] = {"apiKey": api_key}
                if username or email:
                    user_info: dict[str, Any] = {}
                    if username:
                        user_info["preferred_username"] = username
                    if email:
                        user_info["email"] = email
                    if avatar:
                        user_info["avatar"] = avatar
                    sign_in_input["userInfo"] = user_info
                data = await make_graphql_request(
                    MUTATIONS["connect_sign_in"], {"input": sign_in_input}
                )
                return {"success": True, "action": "connect_sign_in", "result": data.get("connectSignIn")}

            if action == "connect_sign_out":
                data = await make_graphql_request(MUTATIONS["connect_sign_out"])
                return {"success": True, "action": "connect_sign_out", "result": data.get("connectSignOut")}

            if action == "setup_remote_access":
                if not access_type:
                    raise ToolError("access_type is required for 'setup_remote_access' action")
                remote_input: dict[str, Any] = {"accessType": access_type}
                if forward_type is not None:
                    remote_input["forwardType"] = forward_type
                if port is not None:
                    remote_input["port"] = port
                data = await make_graphql_request(
                    MUTATIONS["setup_remote_access"], {"input": remote_input}
                )
                return {"success": True, "action": "setup_remote_access", "result": data.get("setupRemoteAccess")}

            if action == "enable_dynamic_remote_access":
                if not access_url_type:
                    raise ToolError("access_url_type is required for 'enable_dynamic_remote_access' action")
                if dynamic_enabled is None:
                    raise ToolError("dynamic_enabled is required for 'enable_dynamic_remote_access' action")
                url_input: dict[str, Any] = {"type": access_url_type}
                if access_url_name is not None:
                    url_input["name"] = access_url_name
                if access_url_ipv4 is not None:
                    url_input["ipv4"] = access_url_ipv4
                if access_url_ipv6 is not None:
                    url_input["ipv6"] = access_url_ipv6
                data = await make_graphql_request(
                    MUTATIONS["enable_dynamic_remote_access"],
                    {"input": {"url": url_input, "enabled": dynamic_enabled}},
                )
                return {"success": True, "action": "enable_dynamic_remote_access", "result": data.get("enableDynamicRemoteAccess")}

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Settings tool registered successfully")
```

- [ ] **Step 4: Run settings tests**

```bash
uv run pytest tests/test_settings.py -v 2>&1 | tail -30
```

Expected: All PASS.

- [ ] **Step 5: Lint**

```bash
uv run ruff check unraid_mcp/tools/settings.py && uv run ruff format --check unraid_mcp/tools/settings.py
```

- [ ] **Step 6: Commit**

```bash
git add unraid_mcp/tools/settings.py tests/test_settings.py
git commit -m "feat: add new unraid_settings tool with 9 mutations (settings, time, UPS, connect, remote access)"
```

---

### Task 11: Register settings tool in server.py

**Files:**
- Modify: `unraid_mcp/server.py`

- [ ] **Step 7: Add import** (after the existing `register_users_tool` import line)

```python
from .tools.settings import register_settings_tool
```

- [ ] **Step 8: Add to registrars list** (append inside the `registrars` list)

```python
            register_settings_tool,
```

- [ ] **Step 9: Verify server still starts cleanly**

```bash
uv run python -c "from unraid_mcp.server import register_all_modules, mcp; register_all_modules(); print('OK')" 2>&1
```

Expected: `OK` with no errors (note: this will fail on missing env vars — that's fine, we're only checking imports and registration).

Actually use:
```bash
uv run python -c "
import os; os.environ.setdefault('UNRAID_API_URL','http://fake'); os.environ.setdefault('UNRAID_API_KEY','fake')
from unraid_mcp.server import register_all_modules, mcp
register_all_modules()
tools = list(mcp._tool_manager._tools.keys())
print(f'Registered {len(tools)} tools: {tools}')
"
```

Expected: Output includes `unraid_settings` in the tools list.

- [ ] **Step 10: Run full test suite to confirm nothing broken**

```bash
uv run pytest --tb=short -q 2>&1 | tail -15
```

Expected: All tests PASS (598 original + ~63 new = ~661 total).

- [ ] **Step 11: Lint all modified files**

```bash
uv run ruff check unraid_mcp/ && uv run ruff format --check unraid_mcp/
```

- [ ] **Step 12: Commit**

```bash
git add unraid_mcp/server.py
git commit -m "feat: register unraid_settings tool in server — 11 tools, 104 actions total"
```

---

## Final Verification

- [ ] **Count total actions**

```bash
uv run python -c "
import os; os.environ.setdefault('UNRAID_API_URL','http://fake'); os.environ.setdefault('UNRAID_API_KEY','fake')
from unraid_mcp.tools.notifications import ALL_ACTIONS as n
from unraid_mcp.tools.storage import ALL_ACTIONS as s
from unraid_mcp.tools.info import ALL_ACTIONS as i
from unraid_mcp.tools.docker import ALL_ACTIONS as d
from unraid_mcp.tools.virtualization import ALL_ACTIONS as v
from unraid_mcp.tools.array import ALL_ACTIONS as a
from unraid_mcp.tools.rclone import ALL_ACTIONS as r
from unraid_mcp.tools.users import ALL_ACTIONS as u
from unraid_mcp.tools.keys import ALL_ACTIONS as k
from unraid_mcp.tools.health import HEALTH_ACTIONS
from unraid_mcp.tools.settings import ALL_ACTIONS as st
from typing import get_args
total = len(n)+len(s)+len(i)+len(d)+len(v)+len(a)+len(r)+len(u)+len(k)+len(get_args(HEALTH_ACTIONS))+len(st)
print(f'Total actions: {total}')
"
```

Expected output: `Total actions: 104`

- [ ] **Run full test suite one final time**

```bash
uv run pytest -v --tb=short 2>&1 | tail -20
```

Expected: All tests PASS.

- [ ] **Update MEMORY.md counts**

Update `/home/jmagar/.claude/projects/-home-jmagar-workspace-unraid-mcp/memory/MEMORY.md`:
- Change `10 tools, 76 actions` → `11 tools, 104 actions`
- Update test count to reflect new total
- Add `unraid_settings` row to the Tool Reference table
