"""Property-based tests for tool input validation.

Uses Hypothesis to fuzz tool inputs and verify the core invariant:
    Tools MUST only raise ToolError (or return normally).
    Any KeyError, AttributeError, TypeError, ValueError, IndexError, or
    other unhandled exception from arbitrary inputs is a bug.

Each test class targets a distinct tool domain and strategy profile:
- Docker: arbitrary container IDs, action names, numeric params
- Notifications: importance strings, list_type strings, field lengths
- Keys: arbitrary key IDs, role lists, name strings
- VM: arbitrary VM IDs, action names
- Info: invalid action names (cross-tool invariant for the action guard)
"""

import asyncio
import contextlib
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp.exceptions import ToolError
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


# Ensure tests/ is on sys.path so "from conftest import make_tool_fn" resolves
# the same way that top-level test files do.
_TESTS_DIR = str(Path(__file__).parent.parent)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from conftest import make_tool_fn  # noqa: E402


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_ALLOWED_EXCEPTION_TYPES = (ToolError,)
"""Only ToolError (or a clean return) is acceptable from any tool call.

Any other exception is a bug — it means the tool let an internal error
surface to the caller instead of wrapping it in a user-friendly ToolError.
"""


def _run(coro) -> Any:
    """Run a coroutine synchronously so Hypothesis @given works with async tools."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _assert_only_tool_error(exc: BaseException) -> None:
    """Assert that an exception is a ToolError, not an internal crash."""
    assert isinstance(exc, ToolError), (
        f"Tool raised {type(exc).__name__} instead of ToolError: {exc!r}\n"
        "This is a bug — all error paths must produce ToolError."
    )


# ---------------------------------------------------------------------------
# Docker: arbitrary container IDs
# ---------------------------------------------------------------------------


class TestDockerContainerIdFuzzing:
    """Fuzz the container_id parameter for Docker actions.

    Invariant: no matter what string is supplied as container_id,
    the tool must only raise ToolError or return normally — never crash
    with a KeyError, AttributeError, or other internal exception.
    """

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_details_arbitrary_container_id(self, container_id: str) -> None:
        """Arbitrary container IDs for 'details' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch(
                "unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"docker": {"containers": []}}
                with contextlib.suppress(ToolError):
                    # ToolError is the only acceptable exception — suppress it
                    await tool_fn(action="details", container_id=container_id)

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_start_arbitrary_container_id(self, container_id: str) -> None:
        """Arbitrary container IDs for 'start' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch(
                "unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"docker": {"containers": []}}
                with contextlib.suppress(ToolError):
                    await tool_fn(action="start", container_id=container_id)

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_stop_arbitrary_container_id(self, container_id: str) -> None:
        """Arbitrary container IDs for 'stop' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch(
                "unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"docker": {"containers": []}}
                with contextlib.suppress(ToolError):
                    await tool_fn(action="stop", container_id=container_id)

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_restart_arbitrary_container_id(self, container_id: str) -> None:
        """Arbitrary container IDs for 'restart' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch(
                "unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                # stop then start both need container list + mutation responses
                mock.return_value = {"docker": {"containers": []}}
                with contextlib.suppress(ToolError):
                    await tool_fn(action="restart", container_id=container_id)

        _run(_run_test())


# ---------------------------------------------------------------------------
# Docker: invalid action names
# ---------------------------------------------------------------------------


class TestDockerInvalidActions:
    """Fuzz the action parameter with arbitrary strings.

    Invariant: invalid action names raise ToolError, never KeyError or crash.
    This validates the action guard that sits at the top of every tool function.
    """

    @given(st.text())
    @settings(max_examples=200, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_action_raises_tool_error(self, action: str) -> None:
        """Any non-valid action string must raise ToolError, not crash."""
        valid_actions = {
            "list",
            "details",
            "start",
            "stop",
            "restart",
            "pause",
            "unpause",
            "remove",
            "update",
            "update_all",
            "logs",
            "networks",
            "network_details",
            "port_conflicts",
            "check_updates",
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
        }
        if action in valid_actions:
            return  # Skip valid actions — they have different semantics

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch("unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock):
                try:
                    await tool_fn(action=action)
                except ToolError:
                    pass  # Correct: invalid action raises ToolError
                except Exception as exc:
                    # Any other exception is a bug
                    pytest.fail(
                        f"Action '{action!r}' raised {type(exc).__name__} "
                        f"instead of ToolError: {exc!r}"
                    )

        _run(_run_test())


# ---------------------------------------------------------------------------
# Notifications: importance and list_type enum fuzzing
# ---------------------------------------------------------------------------


class TestNotificationsEnumFuzzing:
    """Fuzz notification enum parameters.

    Invariant: invalid enum values must produce ToolError with a helpful message,
    never crash with an AttributeError or unhandled exception.
    """

    @given(st.text())
    @settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_importance_raises_tool_error(self, importance: str) -> None:
        """Arbitrary importance strings must raise ToolError or be accepted if valid."""
        valid_importances = {"INFO", "WARNING", "ALERT"}
        if importance.upper() in valid_importances:
            return  # Skip valid values

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {
                    "createNotification": {"id": "1", "title": "t", "importance": "INFO"}
                }
                try:
                    await tool_fn(
                        action="create",
                        title="Test",
                        subject="Sub",
                        description="Desc",
                        importance=importance,
                    )
                except ToolError:
                    pass  # Expected for invalid importance
                except Exception as exc:
                    pytest.fail(f"importance={importance!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_list_type_raises_tool_error(self, list_type: str) -> None:
        """Arbitrary list_type strings must raise ToolError or proceed if valid."""
        valid_list_types = {"UNREAD", "ARCHIVE"}
        if list_type.upper() in valid_list_types:
            return  # Skip valid values

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {"notifications": {"list": []}}
                try:
                    await tool_fn(action="list", list_type=list_type)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"list_type={list_type!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(
        st.text(max_size=300),  # title: limit is 200
        st.text(max_size=600),  # subject: limit is 500
        st.text(max_size=2500),  # description: limit is 2000
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_create_notification_field_lengths(
        self, title: str, subject: str, description: str
    ) -> None:
        """Oversized title/subject/description must raise ToolError, not crash.

        This tests the length-guard invariant: tools that have max-length checks
        must raise ToolError for oversized values, never truncate silently or crash.
        """

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {
                    "createNotification": {"id": "1", "title": "t", "importance": "INFO"}
                }
                try:
                    await tool_fn(
                        action="create",
                        title=title,
                        subject=subject,
                        description=description,
                        importance="INFO",
                    )
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"create with oversized fields raised {type(exc).__name__}: {exc!r}"
                    )

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_notification_type_raises_tool_error(self, notif_type: str) -> None:
        """Arbitrary notification_type strings must raise ToolError or proceed if valid."""
        valid_types = {"UNREAD", "ARCHIVE"}
        if notif_type.upper() in valid_types:
            return

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {"deleteNotification": {}}
                try:
                    await tool_fn(
                        action="delete",
                        notification_id="some-id",
                        notification_type=notif_type,
                        confirm=True,
                    )
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"notification_type={notif_type!r} raised {type(exc).__name__}: {exc!r}"
                    )

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_action_raises_tool_error(self, action: str) -> None:
        """Invalid action names for notifications tool raise ToolError."""
        valid_actions = {
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
        }
        if action in valid_actions:
            return

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ):
                try:
                    await tool_fn(action=action)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"Action {action!r} raised {type(exc).__name__} "
                        f"instead of ToolError: {exc!r}"
                    )

        _run(_run_test())


# ---------------------------------------------------------------------------
# Keys: arbitrary key IDs and role lists
# ---------------------------------------------------------------------------


class TestKeysInputFuzzing:
    """Fuzz API key management parameters.

    Invariant: arbitrary key_id strings, names, and role lists never crash
    the keys tool — only ToolError or clean return values are acceptable.
    """

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_get_arbitrary_key_id(self, key_id: str) -> None:
        """Arbitrary key_id for 'get' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
            with patch(
                "unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"apiKey": None}
                try:
                    await tool_fn(action="get", key_id=key_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"key_id={key_id!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_create_arbitrary_key_name(self, name: str) -> None:
        """Arbitrary name strings for 'create' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
            with patch(
                "unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {
                    "apiKey": {"create": {"id": "1", "name": name, "key": "k", "roles": []}}
                }
                try:
                    await tool_fn(action="create", name=name)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"name={name!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.lists(st.text(), min_size=1, max_size=10))
    @settings(max_examples=80, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_add_role_arbitrary_roles(self, roles: list[str]) -> None:
        """Arbitrary role lists for 'add_role' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
            with patch(
                "unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"apiKey": {"addRole": True}}
                try:
                    await tool_fn(action="add_role", key_id="some-key-id", roles=roles)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"roles={roles!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_action_raises_tool_error(self, action: str) -> None:
        """Invalid action names for keys tool raise ToolError."""
        valid_actions = {"list", "get", "create", "update", "delete", "add_role", "remove_role"}
        if action in valid_actions:
            return

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
            with patch("unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock):
                try:
                    await tool_fn(action=action)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"Action {action!r} raised {type(exc).__name__} "
                        f"instead of ToolError: {exc!r}"
                    )

        _run(_run_test())


# ---------------------------------------------------------------------------
# VM: arbitrary VM IDs and action names
# ---------------------------------------------------------------------------


class TestVMInputFuzzing:
    """Fuzz VM management parameters.

    Invariant: arbitrary vm_id strings and action names must never crash
    the VM tool — only ToolError or clean return values are acceptable.
    """

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_start_arbitrary_vm_id(self, vm_id: str) -> None:
        """Arbitrary vm_id for 'start' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"
            )
            with patch(
                "unraid_mcp.tools.virtualization.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {"vm": {"start": True}}
                try:
                    await tool_fn(action="start", vm_id=vm_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"vm_id={vm_id!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_stop_arbitrary_vm_id(self, vm_id: str) -> None:
        """Arbitrary vm_id for 'stop' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"
            )
            with patch(
                "unraid_mcp.tools.virtualization.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {"vm": {"stop": True}}
                try:
                    await tool_fn(action="stop", vm_id=vm_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"vm_id={vm_id!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_details_arbitrary_vm_id(self, vm_id: str) -> None:
        """Arbitrary vm_id for 'details' must not crash the tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"
            )
            with patch(
                "unraid_mcp.tools.virtualization.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                # Return an empty VM list so the lookup gracefully fails
                mock.return_value = {"vms": {"domains": []}}
                try:
                    await tool_fn(action="details", vm_id=vm_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"vm_id={vm_id!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(st.text())
    @settings(max_examples=200, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_action_raises_tool_error(self, action: str) -> None:
        """Invalid action names for VM tool raise ToolError."""
        valid_actions = {
            "list",
            "details",
            "start",
            "stop",
            "pause",
            "resume",
            "force_stop",
            "reboot",
            "reset",
        }
        if action in valid_actions:
            return

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.virtualization", "register_vm_tool", "unraid_vm"
            )
            with patch(
                "unraid_mcp.tools.virtualization.make_graphql_request",
                new_callable=AsyncMock,
            ):
                try:
                    await tool_fn(action=action)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"Action {action!r} raised {type(exc).__name__} "
                        f"instead of ToolError: {exc!r}"
                    )

        _run(_run_test())


# ---------------------------------------------------------------------------
# Cross-tool: boundary-value and unicode stress tests
# ---------------------------------------------------------------------------


class TestBoundaryValues:
    """Boundary-value and adversarial string tests across multiple tools.

    These tests probe specific edge cases that have historically caused bugs
    in similar systems: null bytes, very long strings, unicode surrogates,
    and empty strings.
    """

    @given(
        st.one_of(
            st.just(""),
            st.just("\x00"),
            st.just("\xff\xfe"),
            st.just("a" * 10_001),
            st.just("/" * 500),
            st.just("'; DROP TABLE containers; --"),
            st.just("${7*7}"),
            st.just("\u0000\uffff"),
            st.just("\n\r\t"),
            st.binary().map(lambda b: b.decode("latin-1")),
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_docker_details_adversarial_inputs(self, container_id: str) -> None:
        """Adversarial container_id values must not crash the Docker tool."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker"
            )
            with patch(
                "unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"docker": {"containers": []}}
                try:
                    await tool_fn(action="details", container_id=container_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"Adversarial input {container_id!r} raised {type(exc).__name__}: {exc!r}"
                    )

        _run(_run_test())

    @given(
        st.one_of(
            st.just(""),
            st.just("\x00"),
            st.just("a" * 100_000),
            st.just("ALERT\x00"),
            st.just("info"),  # wrong case
            st.just("Info"),  # mixed case
            st.just("UNKNOWN"),
            st.just(" INFO "),  # padded
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_notifications_importance_adversarial(self, importance: str) -> None:
        """Adversarial importance values must raise ToolError, not crash."""

        async def _run_test():
            tool_fn = make_tool_fn(
                "unraid_mcp.tools.notifications",
                "register_notifications_tool",
                "unraid_notifications",
            )
            with patch(
                "unraid_mcp.tools.notifications.make_graphql_request",
                new_callable=AsyncMock,
            ) as mock:
                mock.return_value = {
                    "createNotification": {"id": "1", "title": "t", "importance": "INFO"}
                }
                try:
                    await tool_fn(
                        action="create",
                        title="t",
                        subject="s",
                        description="d",
                        importance=importance,
                    )
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"importance={importance!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())

    @given(
        st.one_of(
            st.just(""),
            st.just("\x00"),
            st.just("a" * 1_000_000),  # extreme length
            st.just("key with spaces"),
            st.just("key\nnewline"),
        )
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_keys_get_adversarial_key_ids(self, key_id: str) -> None:
        """Adversarial key_id values must not crash the keys get action."""

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.keys", "register_keys_tool", "unraid_keys")
            with patch(
                "unraid_mcp.tools.keys.make_graphql_request", new_callable=AsyncMock
            ) as mock:
                mock.return_value = {"apiKey": None}
                try:
                    await tool_fn(action="get", key_id=key_id)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(f"key_id={key_id!r} raised {type(exc).__name__}: {exc!r}")

        _run(_run_test())


# ---------------------------------------------------------------------------
# Info: action guard (invalid actions on a read-only tool)
# ---------------------------------------------------------------------------


class TestInfoActionGuard:
    """Fuzz the action parameter on unraid_info.

    Invariant: the info tool exposes no mutations and its action guard must
    reject any invalid action with a ToolError rather than a KeyError crash.
    """

    @given(st.text())
    @settings(max_examples=200, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_action_raises_tool_error(self, action: str) -> None:
        """Invalid action names for the info tool raise ToolError."""
        valid_actions = {
            "overview",
            "array",
            "network",
            "registration",
            "variables",
            "metrics",
            "services",
            "display",
            "config",
            "online",
            "owner",
            "settings",
            "server",
            "servers",
            "flash",
            "ups_devices",
            "ups_device",
            "ups_config",
        }
        if action in valid_actions:
            return

        async def _run_test():
            tool_fn = make_tool_fn("unraid_mcp.tools.info", "register_info_tool", "unraid_info")
            with patch("unraid_mcp.tools.info.make_graphql_request", new_callable=AsyncMock):
                try:
                    await tool_fn(action=action)
                except ToolError:
                    pass
                except Exception as exc:
                    pytest.fail(
                        f"Action {action!r} raised {type(exc).__name__} "
                        f"instead of ToolError: {exc!r}"
                    )

        _run(_run_test())
