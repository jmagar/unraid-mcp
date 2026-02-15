"""Tests for unraid_docker tool."""

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
def _mock_graphql() -> AsyncMock:
    with patch("unraid_mcp.tools.docker.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.docker", "register_docker_tool", "unraid_docker")


class TestDockerValidation:
    async def test_remove_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="remove", container_id="abc123")

    async def test_container_actions_require_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        for action in ("start", "stop", "details", "logs", "pause", "unpause"):
            with pytest.raises(ToolError, match="container_id"):
                await tool_fn(action=action)

    async def test_network_details_requires_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="network_id"):
            await tool_fn(action="network_details")


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
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": "abc123def456" * 4 + "abcd1234abcd1234:local", "names": ["plex"]}]}},
            {"docker": {"start": {"id": "abc123def456" * 4 + "abcd1234abcd1234:local", "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="start", container_id="plex")
        assert result["success"] is True

    async def test_networks(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"dockerNetworks": [{"id": "net:1", "name": "bridge"}]}
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
            "docker": {"containerUpdateStatuses": [{"id": "c1", "name": "plex", "updateAvailable": True}]}
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
        result = await tool_fn(action="update_all")
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
            "docker": {"containers": [{"id": "c1", "names": ["plex"], "state": "running", "image": "plexinc/pms"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="details", container_id="plex")
        assert result["names"] == ["plex"]

    async def test_logs(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {"logs": "2026-02-08 log line here"}},
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
        with pytest.raises(ToolError, match="unexpected failure"):
            await tool_fn(action="list")
