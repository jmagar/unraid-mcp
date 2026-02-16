"""Safety audit tests for destructive action confirmation guards.

Verifies that all destructive operations across every tool require
explicit `confirm=True` before execution, and that the DESTRUCTIVE_ACTIONS
registries are complete and consistent.
"""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from unraid_mcp.core.exceptions import ToolError

# Import DESTRUCTIVE_ACTIONS sets from every tool module that defines one
from unraid_mcp.tools.docker import DESTRUCTIVE_ACTIONS as DOCKER_DESTRUCTIVE
from unraid_mcp.tools.docker import MUTATIONS as DOCKER_MUTATIONS
from unraid_mcp.tools.keys import DESTRUCTIVE_ACTIONS as KEYS_DESTRUCTIVE
from unraid_mcp.tools.keys import MUTATIONS as KEYS_MUTATIONS
from unraid_mcp.tools.notifications import DESTRUCTIVE_ACTIONS as NOTIF_DESTRUCTIVE
from unraid_mcp.tools.notifications import MUTATIONS as NOTIF_MUTATIONS
from unraid_mcp.tools.rclone import DESTRUCTIVE_ACTIONS as RCLONE_DESTRUCTIVE
from unraid_mcp.tools.rclone import MUTATIONS as RCLONE_MUTATIONS
from unraid_mcp.tools.virtualization import DESTRUCTIVE_ACTIONS as VM_DESTRUCTIVE
from unraid_mcp.tools.virtualization import MUTATIONS as VM_MUTATIONS

# Centralized import for make_tool_fn helper
# conftest.py sits in tests/ and is importable without __init__.py
from conftest import make_tool_fn


# ---------------------------------------------------------------------------
# Known destructive actions registry (ground truth for this audit)
# ---------------------------------------------------------------------------

# Every destructive action in the codebase, keyed by (tool_module, tool_name)
KNOWN_DESTRUCTIVE: dict[str, dict[str, set[str]]] = {
    "docker": {
        "module": "unraid_mcp.tools.docker",
        "register_fn": "register_docker_tool",
        "tool_name": "unraid_docker",
        "actions": {"remove"},
        "runtime_set": DOCKER_DESTRUCTIVE,
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
            f"{tool_key}: DESTRUCTIVE_ACTIONS is {info['runtime_set']}, "
            f"expected {info['actions']}"
        )

    @pytest.mark.parametrize("tool_key", list(KNOWN_DESTRUCTIVE.keys()))
    def test_destructive_actions_are_valid_mutations(self, tool_key: str) -> None:
        """Every destructive action must correspond to an actual mutation."""
        info = KNOWN_DESTRUCTIVE[tool_key]
        mutations_map = {
            "docker": DOCKER_MUTATIONS,
            "vm": VM_MUTATIONS,
            "notifications": NOTIF_MUTATIONS,
            "rclone": RCLONE_MUTATIONS,
            "keys": KEYS_MUTATIONS,
        }
        mutations = mutations_map[tool_key]
        for action in info["actions"]:
            assert action in mutations, (
                f"{tool_key}: destructive action '{action}' is not in MUTATIONS"
            )

    def test_no_delete_or_remove_mutations_missing_from_destructive(self) -> None:
        """Any mutation with 'delete' or 'remove' in its name should be destructive."""
        all_mutations = {
            "docker": DOCKER_MUTATIONS,
            "vm": VM_MUTATIONS,
            "notifications": NOTIF_MUTATIONS,
            "rclone": RCLONE_MUTATIONS,
            "keys": KEYS_MUTATIONS,
        }
        all_destructive = {
            "docker": DOCKER_DESTRUCTIVE,
            "vm": VM_DESTRUCTIVE,
            "notifications": NOTIF_DESTRUCTIVE,
            "rclone": RCLONE_DESTRUCTIVE,
            "keys": KEYS_DESTRUCTIVE,
        }
        missing: list[str] = []
        for tool_key, mutations in all_mutations.items():
            destructive = all_destructive[tool_key]
            for action_name in mutations:
                if ("delete" in action_name or "remove" in action_name) and action_name not in destructive:
                    missing.append(f"{tool_key}/{action_name}")
        assert not missing, (
            f"Mutations with 'delete'/'remove' not in DESTRUCTIVE_ACTIONS: {missing}"
        )


# ---------------------------------------------------------------------------
# Confirmation guard tests: calling without confirm=True raises ToolError
# ---------------------------------------------------------------------------

# Build parametrized test cases: (tool_key, action, kwargs_without_confirm)
# Each destructive action needs the minimum required params (minus confirm)
_DESTRUCTIVE_TEST_CASES: list[tuple[str, str, dict]] = [
    # Docker
    ("docker", "remove", {"container_id": "abc123"}),
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
]


_CASE_IDS = [f"{c[0]}/{c[1]}" for c in _DESTRUCTIVE_TEST_CASES]


@pytest.fixture
def _mock_docker_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock) as m:
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


# Map tool_key -> (fixture name, module path, register fn, tool name)
_TOOL_REGISTRY = {
    "docker": ("unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"),
    "vm": ("unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"),
    "notifications": ("unraid_mcp.tools.notifications", "register_notifications_tool", "unraid_notifications"),
    "rclone": ("unraid_mcp.tools.rclone", "register_rclone_tool", "unraid_rclone"),
    "keys": ("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys"),
}


class TestConfirmationGuards:
    """Every destructive action must reject calls without confirm=True."""

    @pytest.mark.parametrize("tool_key,action,kwargs", _DESTRUCTIVE_TEST_CASES, ids=_CASE_IDS)
    async def test_rejects_without_confirm(
        self,
        tool_key: str,
        action: str,
        kwargs: dict,
        _mock_docker_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
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
        _mock_docker_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
    ) -> None:
        """Explicitly passing confirm=False must still raise ToolError."""
        module_path, register_fn, tool_name = _TOOL_REGISTRY[tool_key]
        tool_fn = make_tool_fn(module_path, register_fn, tool_name)

        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action=action, confirm=False, **kwargs)

    @pytest.mark.parametrize("tool_key,action,kwargs", _DESTRUCTIVE_TEST_CASES, ids=_CASE_IDS)
    async def test_error_message_includes_action_name(
        self,
        tool_key: str,
        action: str,
        kwargs: dict,
        _mock_docker_graphql: AsyncMock,
        _mock_vm_graphql: AsyncMock,
        _mock_notif_graphql: AsyncMock,
        _mock_rclone_graphql: AsyncMock,
        _mock_keys_graphql: AsyncMock,
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

    async def test_docker_remove_with_confirm(self, _mock_docker_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_docker_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["old-app"]}]}},
            {"docker": {"removeContainer": True}},
        ]
        tool_fn = make_tool_fn("unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker")
        result = await tool_fn(action="remove", container_id="old-app", confirm=True)
        assert result["success"] is True

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
        _mock_notif_graphql.return_value = {"notifications": {"deleteNotification": True}}
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

    async def test_notifications_delete_archived_with_confirm(self, _mock_notif_graphql: AsyncMock) -> None:
        _mock_notif_graphql.return_value = {"notifications": {"deleteArchivedNotifications": True}}
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
        _mock_keys_graphql.return_value = {"deleteApiKeys": True}
        tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
        result = await tool_fn(action="delete", key_id="key-123", confirm=True)
        assert result["success"] is True
