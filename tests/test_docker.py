"""Tests for docker subactions of the consolidated unraid tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


# --- Integration tests ---


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.core.client.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


class TestDockerValidation:
    @pytest.mark.parametrize("subaction", ["start", "stop", "details"])
    async def test_container_actions_require_id(
        self, _mock_graphql: AsyncMock, subaction: str
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="container_id"):
            await tool_fn(action="docker", subaction=subaction)

    async def test_network_details_requires_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="network_id"):
            await tool_fn(action="docker", subaction="network_details")

    async def test_non_logs_action_ignores_tail_lines_validation(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"docker": {"containers": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="list")
        assert result["containers"] == []


class TestDockerActions:
    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {"containers": [{"id": "c1", "names": ["plex"], "state": "running"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="list")
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
        result = await tool_fn(action="docker", subaction="start", container_id="plex")
        assert result["success"] is True

    async def test_networks(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"docker": {"networks": [{"id": "net:1", "name": "bridge"}]}}
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="networks")
        assert len(result["networks"]) == 1

    async def test_idempotent_start(self, _mock_graphql: AsyncMock) -> None:
        # Resolve + idempotent success
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": "a" * 64 + ":local", "names": ["plex"]}]}},
            {"idempotent_success": True, "docker": {}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="start", container_id="plex")
        assert result["idempotent"] is True

    async def test_restart(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {"stop": {"id": cid, "state": "exited"}}},
            {"docker": {"start": {"id": cid, "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="restart", container_id="plex")
        assert result["success"] is True
        assert result["subaction"] == "restart"

    async def test_restart_idempotent_stop(self, _mock_graphql: AsyncMock) -> None:
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"idempotent_success": True},
            {"docker": {"start": {"id": cid, "state": "running"}}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="restart", container_id="plex")
        assert result["success"] is True
        assert "note" in result

    async def test_details_found(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {"id": "c1", "names": ["plex"], "state": "running", "image": "plexinc/pms"}
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="details", container_id="plex")
        assert result["names"] == ["plex"]

    async def test_generic_exception_wraps_in_tool_error(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("unexpected failure")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Failed to execute docker/list"):
            await tool_fn(action="docker", subaction="list")

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
            await tool_fn(action="docker", subaction="details", container_id="abcdef123456")


class TestDockerMutationFailures:
    """Tests for mutation responses that indicate failure or unexpected shapes."""

    async def test_start_mutation_empty_docker_response(self, _mock_graphql: AsyncMock) -> None:
        """docker field returning empty object (missing the action sub-field)."""
        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            {"docker": {}},
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="start", container_id="plex")
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
        result = await tool_fn(action="docker", subaction="stop", container_id="plex")
        assert result["success"] is True
        assert result["container"]["state"] == "running"

    async def test_mutation_timeout(self, _mock_graphql: AsyncMock) -> None:
        """Mid-operation timeout during a docker mutation."""

        cid = "a" * 64 + ":local"
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": cid, "names": ["plex"]}]}},
            TimeoutError("operation timed out"),
        ]
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="timed out"):
            await tool_fn(action="docker", subaction="start", container_id="plex")


class TestDockerNetworkErrors:
    """Tests for network-level failures in docker operations."""

    async def test_list_connection_refused(self, _mock_graphql: AsyncMock) -> None:
        """Connection refused when listing containers should be wrapped in ToolError."""
        _mock_graphql.side_effect = ToolError(
            "Network connection error: [Errno 111] Connection refused"
        )
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Connection refused"):
            await tool_fn(action="docker", subaction="list")

    async def test_list_http_401_unauthorized(self, _mock_graphql: AsyncMock) -> None:
        """HTTP 401 should propagate as ToolError."""
        _mock_graphql.side_effect = ToolError("HTTP error 401: Unauthorized")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="401"):
            await tool_fn(action="docker", subaction="list")

    async def test_json_decode_error_on_list(self, _mock_graphql: AsyncMock) -> None:
        """Invalid JSON response should be wrapped in ToolError."""
        _mock_graphql.side_effect = ToolError(
            "Invalid JSON response from Unraid API: Expecting value: line 1 column 1"
        )
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid JSON"):
            await tool_fn(action="docker", subaction="list")
