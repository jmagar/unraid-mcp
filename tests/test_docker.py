"""Tests for unraid_docker tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.docker import find_container_by_identifier, get_available_container_names


# --- Unit tests for helpers ---


class TestFindContainerByIdentifier:
    def test_by_exact_id(self) -> None:
        containers = [{"id": "abc123", "names": ["plex"]}]
        assert find_container_by_identifier("abc123", containers) == containers[0]

    def test_by_exact_name(self) -> None:
        containers = [{"id": "abc123", "names": ["plex"]}]
        assert find_container_by_identifier("plex", containers) == containers[0]

    def test_fuzzy_match(self) -> None:
        containers = [{"id": "abc123", "names": ["plex-media-server"]}]
        result = find_container_by_identifier("plex", containers)
        assert result == containers[0]

    def test_not_found(self) -> None:
        containers = [{"id": "abc123", "names": ["plex"]}]
        assert find_container_by_identifier("sonarr", containers) is None

    def test_empty_list(self) -> None:
        assert find_container_by_identifier("plex", []) is None


class TestGetAvailableContainerNames:
    def test_extracts_names(self) -> None:
        containers = [
            {"names": ["plex"]},
            {"names": ["sonarr", "sonarr-v3"]},
        ]
        names = get_available_container_names(containers)
        assert "plex" in names
        assert "sonarr" in names
        assert "sonarr-v3" in names

    def test_empty(self) -> None:
        assert get_available_container_names([]) == []


# --- Integration tests ---


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker")


class TestDockerValidation:
    async def test_remove_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="remove", container_id="abc123")

    @pytest.mark.parametrize("action", ["start", "stop", "details", "logs", "pause", "unpause"])
    async def test_container_actions_require_id(
        self, _mock_graphql: AsyncMock, action: str
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="container_id"):
            await tool_fn(action=action)

    async def test_network_details_requires_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="network_id"):
            await tool_fn(action="network_details")

    async def test_non_logs_action_ignores_tail_lines_validation(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"docker": {"containers": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="list", tail_lines=0)
        assert result["containers"] == []


class TestDockerActions:
    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {"containers": [{"id": "c1", "names": ["plex"], "state": "running"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="list")
        assert len(result["containers"]) == 1

    async def test_start_container(self, _mock_graphql: AsyncMock) -> None:
        # First call resolves ID, second performs start
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {
                "docker": {
                    "start": {
                        "id": cid,
                        "state": "running",
                    }
                }
            },
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="start", container_id="plex")
        assert result["success"] is True

    async def test_networks(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"docker": {"networks": [{"id": "net:1", "name": "bridge"}]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="networks")
        assert len(result["networks"]) == 1

    async def test_port_conflicts(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"docker": {"portConflicts": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="port_conflicts")
        assert result["port_conflicts"] == []

    async def test_check_updates(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {
                "containerUpdateStatuses": [{"id": "c1", "name": "plex", "updateAvailable": True}]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="check_updates")
        assert len(result["update_statuses"]) == 1

    async def test_idempotent_start(self, _mock_graphql: AsyncMock) -> None:
        # Resolve + idempotent success
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": "a" * 64 + ":local", "names": ["plex"]}]}},
            {"idempotent_success": True, "docker": {}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="start", container_id="plex")
        assert result["idempotent"] is True

    async def test_restart(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {"stop": {"id": cid, "state": "exited"}}},
            {"docker": {"start": {"id": cid, "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="restart", container_id="plex")
        assert result["success"] is True
        assert result["action"] == "restart"

    async def test_restart_idempotent_stop(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"idempotent_success": True},
            {"docker": {"start": {"id": cid, "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="restart", container_id="plex")
        assert result["success"] is True
        assert "note" in result

    async def test_update_all(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {"updateAllContainers": [{"id": "c1", "state": "running"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_all", confirm=True)
        assert result["success"] is True
        assert len(result["containers"]) == 1

    async def test_remove_with_confirm(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["old-app"]}]}},
            {"docker": {"removeContainer": True}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="remove", container_id="old-app", confirm=True)
        assert result["success"] is True

    async def test_details_found(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {"id": "c1", "names": ["plex"], "state": "running", "image": "plexinc/pms"}
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="details", container_id="plex")
        assert result["names"] == ["plex"]

    async def test_logs(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {
                "docker": {
                    "logs": {
                        "containerId": cid,
                        "lines": [{"timestamp": "2026-02-08", "message": "log line here"}],
                        "cursor": None,
                    }
                }
            },
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="logs", container_id="plex")
        assert "log line" in result["logs"]

    async def test_pause_container(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {"pause": {"id": cid, "state": "paused"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="pause", container_id="plex")
        assert result["success"] is True

    async def test_generic_exception_wraps_in_tool_error(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("unexpected failure")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Failed to execute docker/list"):
            await tool_fn(action="list")

    async def test_short_id_prefix_ambiguous_rejected(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "abcdef1234560000000000000000000000000000000000000000000000000000:local",
                        "names": ["plex"],
                    },
                    {
                        "id": "abcdef1234561111111111111111111111111111111111111111111111111111:local",
                        "names": ["sonarr"],
                    },
                ]
            }
        }
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ambiguous"):
            await tool_fn(action="logs", container_id="abcdef123456")


class TestDockerMutationFailures:
    """Tests for mutation responses that indicate failure or unexpected shapes."""

    async def test_remove_mutation_returns_null(self, _mock_graphql: AsyncMock) -> None:
        """removeContainer returning null instead of True."""
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["old-app"]}]}},
            {"docker": {"removeContainer": None}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="remove", container_id="old-app", confirm=True)
        assert result["success"] is True
        assert result["container"] is None

    async def test_start_mutation_empty_docker_response(self, _mock_graphql: AsyncMock) -> None:
        """docker field returning empty object (missing the action sub-field)."""
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="start", container_id="plex")
        assert result["success"] is True
        assert result["container"] is None

    async def test_stop_mutation_returns_false_state(self, _mock_graphql: AsyncMock) -> None:
        """Stop mutation returning a container with unexpected state."""
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {"stop": {"id": cid, "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="stop", container_id="plex")
        assert result["success"] is True
        assert result["container"]["state"] == "running"

    async def test_update_all_returns_empty_list(self, _mock_graphql: AsyncMock) -> None:
        """update_all with no containers to update."""
        _mock_graphql.return_value = {"docker": {"updateAllContainers": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="update_all", confirm=True)
        assert result["success"] is True
        assert result["containers"] == []

    async def test_update_all_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        """update_all is destructive and requires confirm=True."""
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="update_all")

    async def test_mutation_timeout(self, _mock_graphql: AsyncMock) -> None:
        """Mid-operation timeout during a docker mutation."""

        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            TimeoutError("operation timed out"),
        ]
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="timed out"):
            await tool_fn(action="start", container_id="plex")


class TestDockerNetworkErrors:
    """Tests for network-level failures in docker operations."""

    async def test_list_connection_refused(self, _mock_graphql: AsyncMock) -> None:
        """Connection refused when listing containers should be wrapped in ToolError."""
        _mock_graphql.side_effect = ToolError(
            "Network connection error: [Errno 111] Connection refused"
        )
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Connection refused"):
            await tool_fn(action="list")

    async def test_list_http_401_unauthorized(self, _mock_graphql: AsyncMock) -> None:
        """HTTP 401 should propagate as ToolError."""
        _mock_graphql.side_effect = ToolError("HTTP error 401: Unauthorized")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="401"):
            await tool_fn(action="list")

    async def test_json_decode_error_on_list(self, _mock_graphql: AsyncMock) -> None:
        """Invalid JSON response should be wrapped in ToolError."""
        _mock_graphql.side_effect = ToolError(
            "Invalid JSON response from Unraid API: Expecting value: line 1 column 1"
        )
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid JSON"):
            await tool_fn(action="list")


_ORGANIZER_RESPONSE = {
    "version": 1.0,
    "views": [{"id": "default", "name": "Default", "rootId": "root", "flatEntries": []}],
}


class TestDockerOrganizerMutations:
    async def test_create_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"createDockerFolder": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="create_folder", folder_name="Media")
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["name"] == "Media"

    async def test_create_folder_requires_name(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="folder_name"):
            await _make_tool()(action="create_folder")

    async def test_set_folder_children_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setDockerFolderChildren": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="set_folder_children", children_ids=["c1"])
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["childrenIds"] == ["c1"]

    async def test_set_folder_children_requires_children(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="children_ids"):
            await _make_tool()(action="set_folder_children")

    async def test_delete_entries_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="destructive"):
            await _make_tool()(action="delete_entries", entry_ids=["e1"])

    async def test_delete_entries_requires_ids(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="entry_ids"):
            await _make_tool()(action="delete_entries", confirm=True)

    async def test_delete_entries_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"deleteDockerEntries": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="delete_entries", entry_ids=["e1", "e2"], confirm=True)
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["entryIds"] == ["e1", "e2"]

    async def test_move_to_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"moveDockerEntriesToFolder": _ORGANIZER_RESPONSE}
        result = await _make_tool()(
            action="move_to_folder", source_entry_ids=["e1"], destination_folder_id="f1"
        )
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["sourceEntryIds"] == ["e1"]
        assert call_vars["destinationFolderId"] == "f1"

    async def test_move_to_folder_requires_source_ids(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="source_entry_ids"):
            await _make_tool()(action="move_to_folder", destination_folder_id="f1")

    async def test_move_to_folder_requires_destination(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="destination_folder_id"):
            await _make_tool()(action="move_to_folder", source_entry_ids=["e1"])

    async def test_move_to_position_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"moveDockerItemsToPosition": _ORGANIZER_RESPONSE}
        result = await _make_tool()(
            action="move_to_position",
            source_entry_ids=["e1"],
            destination_folder_id="f1",
            position=2.0,
        )
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["sourceEntryIds"] == ["e1"]
        assert call_vars["destinationFolderId"] == "f1"
        assert call_vars["position"] == 2.0

    async def test_move_to_position_requires_position(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="position"):
            await _make_tool()(
                action="move_to_position", source_entry_ids=["e1"], destination_folder_id="f1"
            )

    async def test_rename_folder_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"renameDockerFolder": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="rename_folder", folder_id="f1", new_folder_name="New")
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["folderId"] == "f1"
        assert call_vars["newName"] == "New"

    async def test_rename_folder_requires_folder_id(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="folder_id"):
            await _make_tool()(action="rename_folder", new_folder_name="New")

    async def test_rename_folder_requires_new_name(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="new_folder_name"):
            await _make_tool()(action="rename_folder", folder_id="f1")

    async def test_create_folder_with_items_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"createDockerFolderWithItems": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="create_folder_with_items", folder_name="New")
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["name"] == "New"
        assert "sourceEntryIds" not in call_vars  # not forwarded when not provided

    async def test_create_folder_with_items_with_source_ids(self, _mock_graphql: AsyncMock) -> None:
        """Passing source_entry_ids must forward sourceEntryIds to the mutation."""
        _mock_graphql.return_value = {"createDockerFolderWithItems": _ORGANIZER_RESPONSE}
        result = await _make_tool()(
            action="create_folder_with_items",
            folder_name="Media",
            source_entry_ids=["c1", "c2"],
        )
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["name"] == "Media"
        assert call_vars["sourceEntryIds"] == ["c1", "c2"]

    async def test_create_folder_with_items_requires_name(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="folder_name"):
            await _make_tool()(action="create_folder_with_items")

    async def test_update_view_prefs_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateDockerViewPreferences": _ORGANIZER_RESPONSE}
        result = await _make_tool()(action="update_view_prefs", view_prefs={"sort": "name"})
        assert result["success"] is True
        call_vars = _mock_graphql.call_args[0][1]
        assert call_vars["prefs"] == {"sort": "name"}

    async def test_update_view_prefs_requires_prefs(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="view_prefs"):
            await _make_tool()(action="update_view_prefs")

    async def test_sync_templates_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "syncDockerTemplatePaths": {"scanned": 5, "matched": 4, "skipped": 1, "errors": []}
        }
        result = await _make_tool()(action="sync_templates")
        assert result["success"] is True

    async def test_reset_template_mappings_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="destructive"):
            await _make_tool()(action="reset_template_mappings")

    async def test_reset_template_mappings_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"resetDockerTemplateMappings": True}
        result = await _make_tool()(action="reset_template_mappings", confirm=True)
        assert result["success"] is True

    async def test_refresh_digests_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"refreshDockerDigests": True}
        result = await _make_tool()(action="refresh_digests")
        assert result["success"] is True
