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

    async def test_list_caps_default(self, _mock_graphql: AsyncMock) -> None:
        # Tool param default is 20.
        _mock_graphql.return_value = {
            "docker": {"containers": [{"id": f"c{i}", "names": [f"ct{i}"]} for i in range(80)]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="list")
        assert len(result["containers"]) == 20
        assert result["page"]["truncated"] is True
        assert result["page"]["total"] == 80
        assert "hint" in result["page"]

    async def test_list_limit_widens(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {"containers": [{"id": f"c{i}", "names": [f"ct{i}"]} for i in range(80)]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="list", limit=50)
        assert len(result["containers"]) == 50

    async def test_list_limit_zero_returns_all(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "docker": {"containers": [{"id": f"c{i}", "names": [f"ct{i}"]} for i in range(80)]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="list", limit=0)
        assert len(result["containers"]) == 80
        assert result["page"]["truncated"] is False

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
        # details now fetches a single container by id: the first call resolves
        # the name → id, the second returns docker.container for that id.
        _mock_graphql.side_effect = [
            {"docker": {"containers": [{"id": "c1", "names": ["plex"]}]}},
            {
                "docker": {
                    "container": {
                        "id": "c1",
                        "names": ["plex"],
                        "state": "running",
                        "image": "plexinc/pms",
                    }
                }
            },
        ]
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="details", container_id="plex")
        assert result["names"] == ["plex"]
        # The details query must request a single container by id, not the full list.
        details_call = _mock_graphql.call_args_list[1]
        assert "container(id:" in details_call.args[0]
        assert details_call.args[1] == {"id": "c1"}

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


class TestDockerPortsAggregator:
    """Tests for the docker/ports aggregator subaction."""

    async def test_ports_aggregates_running_containers(self, _mock_graphql: AsyncMock) -> None:
        """Two RUNNING containers with single-port mappings each yield two
        bindings sorted by host port, with leading-slash names stripped."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/postgres"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 5432,
                                "publicPort": 5432,
                                "type": "TCP",
                            }
                        ],
                    },
                    {
                        "id": "c2",
                        "names": ["/redis"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 6379,
                                "publicPort": 6379,
                                "type": "TCP",
                            }
                        ],
                    },
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 2
        # Sorted by host_port ascending
        assert [b["host_port"] for b in result["bindings"]] == [5432, 6379]
        first = result["bindings"][0]
        assert first["container"] == "postgres"  # leading slash stripped
        assert first["container_port"] == 5432
        assert first["protocol"] == "TCP"
        assert first["host_ip"] == "0.0.0.0"

    async def test_ports_skips_exited_containers(self, _mock_graphql: AsyncMock) -> None:
        """Exited containers don't hold host ports — skip them even if ports[] is populated."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/postgres"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 5432,
                                "publicPort": 5432,
                                "type": "TCP",
                            }
                        ],
                    },
                    {
                        "id": "c2",
                        "names": ["/old-app"],
                        "state": "EXITED",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 80,
                                "publicPort": 8080,
                                "type": "TCP",
                            }
                        ],
                    },
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 1
        assert result["bindings"][0]["container"] == "postgres"

    async def test_ports_skips_internal_only_ports(self, _mock_graphql: AsyncMock) -> None:
        """Ports with publicPort=null are container-internal — skip them."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/glances"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 61208,
                                "publicPort": 61208,
                                "type": "TCP",
                            },
                            {
                                "ip": "",
                                "privatePort": 61209,
                                "publicPort": None,
                                "type": "TCP",
                            },
                        ],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 1
        assert result["bindings"][0]["host_port"] == 61208

    async def test_ports_handles_host_network_containers(self, _mock_graphql: AsyncMock) -> None:
        """Host-network containers have empty ports[] — they shouldn't crash or appear."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/plex"],
                        "state": "RUNNING",
                        "ports": [],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 0
        assert result["bindings"] == []

    async def test_ports_emits_one_binding_per_port(self, _mock_graphql: AsyncMock) -> None:
        """A container exposing multiple ports should emit a binding per public port."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/filezilla"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 3000,
                                "publicPort": 3014,
                                "type": "TCP",
                            },
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 3001,
                                "publicPort": 3042,
                                "type": "TCP",
                            },
                        ],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 2
        assert sorted(b["host_port"] for b in result["bindings"]) == [3014, 3042]

    async def test_ports_empty_when_no_containers(self, _mock_graphql: AsyncMock) -> None:
        """An empty container list returns an empty bindings list with count=0."""
        _mock_graphql.return_value = {"docker": {"containers": []}}
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result == {"bindings": [], "count": 0}

    async def test_ports_handles_unnamed_container(self, _mock_graphql: AsyncMock) -> None:
        """Container with empty names list falls back to '<unnamed>'."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": [],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 80,
                                "publicPort": 8080,
                                "type": "TCP",
                            }
                        ],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 1
        assert result["bindings"][0]["container"] == "<unnamed>"

    async def test_ports_uses_details_query_not_list(self, _mock_graphql: AsyncMock) -> None:
        """ports must call the details query (which carries port info), not list."""
        _mock_graphql.return_value = {"docker": {"containers": []}}
        tool_fn = _make_tool()
        await tool_fn(action="docker", subaction="ports")
        assert _mock_graphql.call_count == 1
        called_query = _mock_graphql.call_args.args[0]
        assert "ports" in called_query
        assert "publicPort" in called_query

    async def test_ports_protocol_tiebreak_orders_tcp_before_udp(
        self, _mock_graphql: AsyncMock
    ) -> None:
        """When two bindings share the same host port (e.g. a service exposing
        the same port on both TCP and UDP), the secondary sort key is
        ``protocol`` — alphabetical, so TCP precedes UDP."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/dnsmasq"],
                        "state": "RUNNING",
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 53,
                                "publicPort": 53,
                                "type": "UDP",
                            },
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 53,
                                "publicPort": 53,
                                "type": "TCP",
                            },
                        ],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 2
        # Same host port — ordered by protocol alphabetically (TCP < UDP)
        assert [b["protocol"] for b in result["bindings"]] == ["TCP", "UDP"]
        assert all(b["host_port"] == 53 for b in result["bindings"])

    @pytest.mark.parametrize("state_value", ["running", "Running", "RUNNING", "rUnNiNg"])
    async def test_ports_state_check_is_case_insensitive(
        self, _mock_graphql: AsyncMock, state_value: str
    ) -> None:
        """Container state values appear in mixed case across the codebase
        (compare _health.py which uses ``.upper()``); the aggregator must include
        a container regardless of case so a stylistic API change can't silently
        zero out the result."""
        _mock_graphql.return_value = {
            "docker": {
                "containers": [
                    {
                        "id": "c1",
                        "names": ["/postgres"],
                        "state": state_value,
                        "ports": [
                            {
                                "ip": "0.0.0.0",
                                "privatePort": 5432,
                                "publicPort": 5432,
                                "type": "TCP",
                            }
                        ],
                    }
                ]
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="docker", subaction="ports")
        assert result["count"] == 1, f"Expected 1 binding for state={state_value!r}"
        assert result["bindings"][0]["host_port"] == 5432
