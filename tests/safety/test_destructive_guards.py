"""Safety audit tests for destructive action confirmation guards.

Verifies that all destructive operations across every tool require
explicit `confirm=True` before execution, and that the DESTRUCTIVE_ACTIONS
registries are complete and consistent.
"""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

# conftest.py is the shared test-helper module for this project.
# pytest automatically adds tests/ to sys.path, making it importable here
# without a package __init__.py. Do NOT add tests/__init__.py — it breaks
# conftest.py's fixture auto-discovery.
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError

# Import DESTRUCTIVE_ACTIONS sets from every tool module that defines one
from unraid_mcp.tools.array import DESTRUCTIVE_ACTIONS as ARRAY_DESTRUCTIVE
from unraid_mcp.tools.array import MUTATIONS as ARRAY_MUTATIONS
from unraid_mcp.tools.keys import DESTRUCTIVE_ACTIONS as KEYS_DESTRUCTIVE
from unraid_mcp.tools.keys import MUTATIONS as KEYS_MUTATIONS
from unraid_mcp.tools.notifications import DESTRUCTIVE_ACTIONS as NOTIF_DESTRUCTIVE
from unraid_mcp.tools.notifications import MUTATIONS as NOTIF_MUTATIONS
from unraid_mcp.tools.rclone import DESTRUCTIVE_ACTIONS as RCLONE_DESTRUCTIVE
from unraid_mcp.tools.rclone import MUTATIONS as RCLONE_MUTATIONS
from unraid_mcp.tools.settings import DESTRUCTIVE_ACTIONS as SETTINGS_DESTRUCTIVE
from unraid_mcp.tools.settings import MUTATIONS as SETTINGS_MUTATIONS
from unraid_mcp.tools.storage import DESTRUCTIVE_ACTIONS as STORAGE_DESTRUCTIVE
from unraid_mcp.tools.storage import MUTATIONS as STORAGE_MUTATIONS
from unraid_mcp.tools.virtualization import DESTRUCTIVE_ACTIONS as VM_DESTRUCTIVE
from unraid_mcp.tools.virtualization import MUTATIONS as VM_MUTATIONS


# ---------------------------------------------------------------------------
# Known destructive actions registry (ground truth for this audit)
# ---------------------------------------------------------------------------

# Every destructive action in the codebase, keyed by (tool_module, tool_name)
KNOWN_DESTRUCTIVE: dict[str, dict[str, set[str] | str]] = {
    "array": {
        "module": "unraid_mcp.tools.array",
        "register_fn": "register_array_tool",
        "tool_name": "unraid_array",
        "actions": {"remove_disk", "clear_disk_stats"},
        "runtime_set": ARRAY_DESTRUCTIVE,
    },
    "vm": {
        "module": "unraid_mcp.tools.virtualization",
        "register_fn": "register_vm_tool",
        "tool_name": "unraid_vm",
        "actions": {"force_stop", "reset"},
        "runtime_set": VM_DESTRUCTIVE,
    },
    "notifications": {
        "module": "unraid_mcp.tools.notifications",
        "register_fn": "register_notifications_tool",
        "tool_name": "unraid_notifications",
        "actions": {"delete", "delete_archived"},
        "runtime_set": NOTIF_DESTRUCTIVE,
    },
    "rclone": {
        "module": "unraid_mcp.tools.rclone",
        "register_fn": "register_rclone_tool",
        "tool_name": "unraid_rclone",
        "actions": {"delete_remote"},
        "runtime_set": RCLONE_DESTRUCTIVE,
    },
    "keys": {
        "module": "unraid_mcp.tools.keys",
        "register_fn": "register_keys_tool",
        "tool_name": "unraid_keys",
        "actions": {"delete"},
        "runtime_set": KEYS_DESTRUCTIVE,
    },
    "storage": {
        "module": "unraid_mcp.tools.storage",
        "register_fn": "register_storage_tool",
        "tool_name": "unraid_storage",
        "actions": {"flash_backup"},
        "runtime_set": STORAGE_DESTRUCTIVE,
    },
    "settings": {
        "module": "unraid_mcp.tools.settings",
        "register_fn": "register_settings_tool",
        "tool_name": "unraid_settings",
        "actions": {"configure_ups"},
        "runtime_set": SETTINGS_DESTRUCTIVE,
    },
}


# ---------------------------------------------------------------------------
# Registry validation: DESTRUCTIVE_ACTIONS sets match ground truth
# ---------------------------------------------------------------------------


class TestDestructiveActionRegistries:
    """Verify that DESTRUCTIVE_ACTIONS sets in source code match the audit."""

    @pytest.mark.parametrize("tool_key", list(KNOWN_DESTRUCTIVE.keys()))
    def test_destructive_set_matches_audit(self, tool_key: str) -> None:
        """Each tool's DESTRUCTIVE_ACTIONS must exactly match the audited set."""
        info = KNOWN_DESTRUCTIVE[tool_key]
        assert info["runtime_set"] == info["actions"], (
            f"{tool_key}: DESTRUCTIVE_ACTIONS is {info['runtime_set']}, expected {info['actions']}"
        )

    @pytest.mark.parametrize("tool_key", list(KNOWN_DESTRUCTIVE.keys()))
    def test_destructive_actions_are_valid_mutations(self, tool_key: str) -> None:
        """Every destructive action must correspond to an actual mutation."""
        info = KNOWN_DESTRUCTIVE[tool_key]
        mutations_map = {
            "array": ARRAY_MUTATIONS,
            "vm": VM_MUTATIONS,
            "notifications": NOTIF_MUTATIONS,
            "rclone": RCLONE_MUTATIONS,
            "keys": KEYS_MUTATIONS,
            "storage": STORAGE_MUTATIONS,
            "settings": SETTINGS_MUTATIONS,
        }
        mutations = mutations_map[tool_key]
        for action in info["actions"]:
            assert action in mutations, (
                f"{tool_key}: destructive action '{action}' is not in MUTATIONS"
            )

    def test_no_delete_or_remove_mutations_missing_from_destructive(self) -> None:
        """Any mutation with 'delete' or 'remove' in its name should be destructive."""
        all_mutations = {
            "array": ARRAY_MUTATIONS,
            "vm": VM_MUTATIONS,
            "notifications": NOTIF_MUTATIONS,
            "rclone": RCLONE_MUTATIONS,
            "keys": KEYS_MUTATIONS,
            "storage": STORAGE_MUTATIONS,
            "settings": SETTINGS_MUTATIONS,
        }
        all_destructive = {
            "array": ARRAY_DESTRUCTIVE,
            "vm": VM_DESTRUCTIVE,
            "notifications": NOTIF_DESTRUCTIVE,
            "rclone": RCLONE_DESTRUCTIVE,
            "keys": KEYS_DESTRUCTIVE,
            "storage": STORAGE_DESTRUCTIVE,
            "settings": SETTINGS_DESTRUCTIVE,
        }
        missing: list[str] = []
        for tool_key, mutations in all_mutations.items():
            destructive = all_destructive[tool_key]
            missing.extend(
                f"{tool_key}/{action_name}"
                for action_name in mutations
                if ("delete" in action_name or "remove" in action_name)
                and action_name not in destructive
            )
        assert not missing, (
            f"Mutations with 'delete'/'remove' not in DESTRUCTIVE_ACTIONS: {missing}"
        )


# ---------------------------------------------------------------------------
# Confirmation guard tests: calling without confirm=True raises ToolError
# ---------------------------------------------------------------------------

# Build parametrized test cases: (tool_key, action, kwargs_without_confirm)
# Each destructive action needs the minimum required params (minus confirm)
_DESTRUCTIVE_TEST_CASES: list[tuple[str, str, dict]] = [
    # Array
    ("array", "remove_disk", {"disk_id": "abc123:local"}),
    ("array", "clear_disk_stats", {"disk_id": "abc123:local"}),
    # VM
    ("vm", "force_stop", {"vm_id": "test-vm-uuid"}),
    ("vm", "reset", {"vm_id": "test-vm-uuid"}),
    # Notifications
    ("notifications", "delete", {"notification_id": "notif-1", "notification_type": "UNREAD"}),
    ("notifications", "delete_archived", {}),
    # RClone
    ("rclone", "delete_remote", {"name": "my-remote"}),
    # Keys
    ("keys", "delete", {"key_id": "key-123"}),
    # Storage
    (
        "storage",
        "flash_backup",
        {"remote_name": "r", "source_path": "/boot", "destination_path": "r:b"},
    ),
    # Settings
    ("settings", "configure_ups", {"ups_config": {"mode": "slave"}}),
]


_CASE_IDS = [f"{c[0]}/{c[1]}" for c in _DESTRUCTIVE_TEST_CASES]


@pytest.fixture
def _mock_array_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.array.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_vm_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.virtualization.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_notif_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.notifications.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_rclone_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.rclone.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_keys_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_storage_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.storage.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


@pytest.fixture
def _mock_settings_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.settings.make_graphql_request", new_callable=AsyncMock) as m:
        yield m


# Map tool_key -> (module path, register fn, tool name)
_TOOL_REGISTRY = {
    "array": ("unraid_mcp.tools.array", "register_array_tool", "unraid_array"),
    "vm": ("unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"),
    "notifications": (
        "unraid_mcp.tools.notifications",
        "register_notifications_tool",
        "unraid_notifications",
    ),
    "rclone": ("unraid_mcp.tools.rclone", "register_rclone_tool", "unraid_rclone"),
    "keys": ("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys"),
    "storage": ("unraid_mcp.tools.storage", "register_storage_tool", "unraid_storage"),
    "settings": ("unraid_mcp.tools.settings", "register_settings_tool", "unraid_settings"),
}


class TestConfirmationGuards:
    """Every destructive action must reject calls without confirm=True."""

    @pytest.mark.parametrize("tool_key,action,kwargs", _DESTRUCTIVE_TEST_CASES, ids=_CASE_IDS)
    async def test_rejects_without_confirm(
        self,
        tool_key: str,
        action: str,
        kwargs: dict,
        _mock_array_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
        _mock_storage_graphql: AsyncMock,
        _mock_settings_graphql: AsyncMock,
    ) -> None:
        """Calling a destructive action without confirm=True must raise ToolError."""
        module_path, register_fn, tool_name = _TOOL_REGISTRY[tool_key]
        tool_fn = make_tool_fn(module_path, register_fn, tool_name)

        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action=action, **kwargs)

    @pytest.mark.parametrize("tool_key,action,kwargs", _DESTRUCTIVE_TEST_CASES, ids=_CASE_IDS)
    async def test_rejects_with_confirm_false(
        self,
        tool_key: str,
        action: str,
        kwargs: dict,
        _mock_array_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
        _mock_storage_graphql: AsyncMock,
        _mock_settings_graphql: AsyncMock,
    ) -> None:
        """Explicitly passing confirm=False must still raise ToolError."""
        module_path, register_fn, tool_name = _TOOL_REGISTRY[tool_key]
        tool_fn = make_tool_fn(module_path, register_fn, tool_name)

        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action=action, confirm=False, **kwargs)

    @pytest.mark.parametrize("tool_key,action,kwargs", _DESTRUCTIVE_TEST_CASES, ids=_CASE_IDS)
    async def test_error_message_includes_action_name(
        self,
        tool_key: str,
        action: str,
        kwargs: dict,
        _mock_array_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
        _mock_storage_graphql: AsyncMock,
        _mock_settings_graphql: AsyncMock,
    ) -> None:
        """The error message should include the action name for clarity."""
        module_path, register_fn, tool_name = _TOOL_REGISTRY[tool_key]
        tool_fn = make_tool_fn(module_path, register_fn, tool_name)

        with pytest.raises(ToolError, match=action):
            await tool_fn(action=action, **kwargs)


# ---------------------------------------------------------------------------
# Positive tests: destructive actions proceed when confirm=True
# ---------------------------------------------------------------------------


class TestConfirmAllowsExecution:
    """Destructive actions with confirm=True should reach the GraphQL layer."""

    async def test_vm_force_stop_with_confirm(self, _mock_vm_graphql: AsyncMock) -> None:
        _mock_vm_graphql.return_value = {"vm": {"forceStop": True}}
        tool_fn = make_tool_fn("unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm")
        result = await tool_fn(action="force_stop", vm_id="test-uuid", confirm=True)
        assert result["success"] is True

    async def test_vm_reset_with_confirm(self, _mock_vm_graphql: AsyncMock) -> None:
        _mock_vm_graphql.return_value = {"vm": {"reset": True}}
        tool_fn = make_tool_fn("unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm")
        result = await tool_fn(action="reset", vm_id="test-uuid", confirm=True)
        assert result["success"] is True

    async def test_notifications_delete_with_confirm(self, _mock_notif_graphql: AsyncMock) -> None:
        _mock_notif_graphql.return_value = {
            "deleteNotification": {
                "unread": {"info": 0, "warning": 0, "alert": 0, "total": 0},
                "archive": {"info": 0, "warning": 0, "alert": 0, "total": 0},
            }
        }
        tool_fn = make_tool_fn(
            "unraid_mcp.tools.notifications", "register_notifications_tool", "unraid_notifications"
        )
        result = await tool_fn(
            action="delete",
            notification_id="notif-1",
            notification_type="UNREAD",
            confirm=True,
        )
        assert result["success"] is True

    async def test_notifications_delete_archived_with_confirm(
        self, _mock_notif_graphql: AsyncMock
    ) -> None:
        _mock_notif_graphql.return_value = {
            "deleteArchivedNotifications": {
                "unread": {"info": 0, "warning": 0, "alert": 0, "total": 0},
                "archive": {"info": 0, "warning": 0, "alert": 0, "total": 0},
            }
        }
        tool_fn = make_tool_fn(
            "unraid_mcp.tools.notifications", "register_notifications_tool", "unraid_notifications"
        )
        result = await tool_fn(action="delete_archived", confirm=True)
        assert result["success"] is True

    async def test_rclone_delete_remote_with_confirm(self, _mock_rclone_graphql: AsyncMock) -> None:
        _mock_rclone_graphql.return_value = {"rclone": {"deleteRCloneRemote": True}}
        tool_fn = make_tool_fn("unraid_mcp.tools.rclone", "register_rclone_tool", "unraid_rclone")
        result = await tool_fn(action="delete_remote", name="my-remote", confirm=True)
        assert result["success"] is True

    async def test_keys_delete_with_confirm(self, _mock_keys_graphql: AsyncMock) -> None:
        _mock_keys_graphql.return_value = {"apiKey": {"delete": True}}
        tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
        result = await tool_fn(action="delete", key_id="key-123", confirm=True)
        assert result["success"] is True

    async def test_storage_flash_backup_with_confirm(
        self, _mock_storage_graphql: AsyncMock
    ) -> None:
        _mock_storage_graphql.return_value = {
            "initiateFlashBackup": {"status": "started", "jobId": "j:1"}
        }
        tool_fn = make_tool_fn(
            "unraid_mcp.tools.storage", "register_storage_tool", "unraid_storage"
        )
        result = await tool_fn(
            action="flash_backup",
            confirm=True,
            remote_name="r",
            source_path="/boot",
            destination_path="r:b",
        )
        assert result["success"] is True

    async def test_settings_configure_ups_with_confirm(
        self, _mock_settings_graphql: AsyncMock
    ) -> None:
        _mock_settings_graphql.return_value = {"configureUps": True}
        tool_fn = make_tool_fn(
            "unraid_mcp.tools.settings", "register_settings_tool", "unraid_settings"
        )
        result = await tool_fn(
            action="configure_ups", confirm=True, ups_config={"mode": "master", "cable": "usb"}
        )
        assert result["success"] is True

    async def test_array_remove_disk_with_confirm(self, _mock_array_graphql: AsyncMock) -> None:
        _mock_array_graphql.return_value = {"array": {"removeDiskFromArray": {"state": "STOPPED"}}}
        tool_fn = make_tool_fn("unraid_mcp.tools.array", "register_array_tool", "unraid_array")
        result = await tool_fn(action="remove_disk", disk_id="abc:local", confirm=True)
        assert result["success"] is True

    async def test_array_clear_disk_stats_with_confirm(
        self, _mock_array_graphql: AsyncMock
    ) -> None:
        _mock_array_graphql.return_value = {"array": {"clearArrayDiskStatistics": True}}
        tool_fn = make_tool_fn("unraid_mcp.tools.array", "register_array_tool", "unraid_array")
        result = await tool_fn(action="clear_disk_stats", disk_id="abc:local", confirm=True)
        assert result["success"] is True
