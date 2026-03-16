"""Tests for health subactions of the consolidated unraid tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.core.utils import safe_display_url


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.unraid.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


class TestHealthValidation:
    async def test_invalid_subaction(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid subaction"):
            await tool_fn(action="health", subaction="invalid")


class TestHealthActions:
    async def test_test_connection(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"online": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="test_connection")
        assert result["status"] == "connected"
        assert result["online"] is True
        assert "latency_ms" in result

    async def test_check_healthy(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "info": {
                "machineId": "abc123",
                "time": "2026-02-08T12:00:00Z",
                "versions": {"unraid": "7.2.0"},
                "os": {"uptime": 86400},
            },
            "array": {"state": "STARTED"},
            "notifications": {"overview": {"unread": {"alert": 0, "warning": 0, "total": 3}}},
            "docker": {"containers": [{"id": "c1", "state": "RUNNING", "status": "Up 2 days"}]},
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        assert result["status"] == "healthy"
        assert "api_latency_ms" in result

    async def test_check_docker_counts_uppercase_states(self, _mock_graphql: AsyncMock) -> None:
        """ContainerState enum is UPPERCASE — running/stopped counts must use case-insensitive match."""
        _mock_graphql.return_value = {
            "info": {
                "machineId": "x",
                "versions": {"core": {"unraid": "7.0"}},
                "os": {"uptime": 1},
            },
            "array": {"state": "STARTED"},
            "notifications": {"overview": {"unread": {"alert": 0, "warning": 0, "total": 0}}},
            "docker": {
                "containers": [
                    {"id": "c1", "state": "RUNNING"},
                    {"id": "c2", "state": "RUNNING"},
                    {"id": "c3", "state": "EXITED"},
                ]
            },
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        svc = result["docker_services"]
        assert svc["total"] == 3
        assert svc["running"] == 2
        assert svc["stopped"] == 1

    async def test_check_warning_on_alerts(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "info": {"machineId": "abc", "versions": {"unraid": "7.2"}, "os": {"uptime": 100}},
            "array": {"state": "STARTED"},
            "notifications": {"overview": {"unread": {"alert": 3, "warning": 0, "total": 3}}},
            "docker": {"containers": []},
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        assert result["status"] == "warning"
        assert any("alert" in i for i in result.get("issues", []))

    async def test_check_no_data(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {}
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        assert result["status"] == "unhealthy"

    async def test_check_api_error(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = Exception("Connection refused")
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        assert result["status"] == "unhealthy"
        assert "Connection refused" in result["error"]

    async def test_check_severity_never_downgrades(self, _mock_graphql: AsyncMock) -> None:
        """Degraded from missing info should not be overwritten by warning from alerts."""
        _mock_graphql.return_value = {
            "info": {},
            "array": {"state": "STARTED"},
            "notifications": {"overview": {"unread": {"alert": 5, "warning": 0, "total": 5}}},
            "docker": {"containers": []},
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="health", subaction="check")
        # Missing info escalates to "degraded"; alerts only escalate to "warning"
        # Severity should stay at "degraded" (not downgrade to "warning")
        assert result["status"] == "degraded"

    async def test_diagnose_success(self, _mock_graphql: AsyncMock) -> None:
        """Diagnose returns subscription status."""
        tool_fn = _make_tool()
        mock_status = {"cpu": {"connection_state": "connected"}}
        mock_manager = MagicMock()
        mock_manager.get_subscription_status = AsyncMock(return_value=mock_status)
        mock_manager.auto_start_enabled = True
        mock_manager.max_reconnect_attempts = 3
        mock_manager.subscription_configs = {}
        mock_manager.active_subscriptions = {}
        mock_manager.resource_data = {}

        with (
            patch("unraid_mcp.subscriptions.manager.subscription_manager", mock_manager),
            patch("unraid_mcp.subscriptions.resources.ensure_subscriptions_started", AsyncMock()),
            patch(
                "unraid_mcp.subscriptions.utils._analyze_subscription_status",
                return_value=(0, []),
            ),
        ):
            result = await tool_fn(action="health", subaction="diagnose")
        assert "subscriptions" in result
        assert "summary" in result

    async def test_diagnose_wraps_exception(self, _mock_graphql: AsyncMock) -> None:
        """When subscription manager raises, tool wraps in ToolError."""
        tool_fn = _make_tool()
        mock_manager = MagicMock()
        mock_manager.get_subscription_status = AsyncMock(side_effect=RuntimeError("broken"))

        with (
            patch("unraid_mcp.subscriptions.manager.subscription_manager", mock_manager),
            patch("unraid_mcp.subscriptions.resources.ensure_subscriptions_started", AsyncMock()),
            patch(
                "unraid_mcp.subscriptions.utils._analyze_subscription_status",
                return_value=(0, []),
            ),
            pytest.raises(ToolError, match="Failed to execute health/diagnose"),
        ):
            await tool_fn(action="health", subaction="diagnose")


# ---------------------------------------------------------------------------
# _safe_display_url — URL redaction helper
# ---------------------------------------------------------------------------


class TestSafeDisplayUrl:
    """Verify that safe_display_url strips credentials/path and preserves scheme+host+port."""

    def test_none_returns_none(self) -> None:
        assert safe_display_url(None) is None

    def test_empty_string_returns_none(self) -> None:
        assert safe_display_url("") is None

    def test_simple_url_scheme_and_host(self) -> None:
        assert safe_display_url("https://unraid.local/graphql") == "https://unraid.local"

    def test_preserves_port(self) -> None:
        assert safe_display_url("https://10.1.0.2:31337/api/graphql") == "https://10.1.0.2:31337"

    def test_strips_path(self) -> None:
        result = safe_display_url("http://unraid.local/some/deep/path?query=1")
        assert result is not None
        assert "path" not in result
        assert "query" not in result

    def test_strips_credentials(self) -> None:
        result = safe_display_url("https://user:password@unraid.local/graphql")
        assert result is not None
        assert "user" not in result
        assert "password" not in result
        assert result == "https://unraid.local"

    def test_strips_query_params(self) -> None:
        result = safe_display_url("http://host.local?token=abc&key=xyz")
        assert result is not None
        assert "token" not in result
        assert "abc" not in result

    def test_http_scheme_preserved(self) -> None:
        result = safe_display_url("http://10.0.0.1:8080/api")
        assert result == "http://10.0.0.1:8080"

    def test_tailscale_url(self) -> None:
        result = safe_display_url("https://100.118.209.1:31337/graphql")
        assert result == "https://100.118.209.1:31337"

    def test_malformed_ipv6_url_returns_unparseable(self) -> None:
        """Malformed IPv6 brackets in netloc cause urlparse.hostname to raise ValueError."""
        result = safe_display_url("https://[invalid")
        assert result == "<unparseable>"


@pytest.mark.asyncio
async def test_health_setup_action_calls_elicitation() -> None:
    """setup subaction triggers elicit_and_configure when no credentials exist."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = False

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.core.setup.elicit_and_configure", new=AsyncMock(return_value=True)
        ) as mock_elicit,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    assert mock_elicit.called
    assert "configured" in result.lower() or "success" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_action_returns_declined_message() -> None:
    """setup subaction with declined elicitation returns appropriate message."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = False

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch("unraid_mcp.core.setup.elicit_and_configure", new=AsyncMock(return_value=False)),
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    assert (
        "not configured" in result.lower()
        or "declined" in result.lower()
        or "cancel" in result.lower()
    )


@pytest.mark.asyncio
async def test_health_setup_already_configured_and_working_no_reset() -> None:
    """setup returns early when credentials exist, connection works, and user declines reset."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = True

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.tools.unraid.make_graphql_request",
            new=AsyncMock(return_value={"online": True}),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_reset_confirmation",
            new=AsyncMock(return_value=False),
        ),
        patch("unraid_mcp.core.setup.elicit_and_configure") as mock_configure,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    mock_configure.assert_not_called()
    assert "already configured" in result.lower()
    assert "no changes" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_already_configured_user_confirms_reset() -> None:
    """setup proceeds with elicitation when credentials exist but user confirms reset."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = True

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.tools.unraid.make_graphql_request",
            new=AsyncMock(return_value={"online": True}),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_reset_confirmation",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_and_configure", new=AsyncMock(return_value=True)
        ) as mock_configure,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    mock_configure.assert_called_once()
    assert "configured" in result.lower() or "success" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_credentials_exist_but_connection_fails_user_confirms() -> None:
    """setup prompts for confirmation even on failed probe, then reconfigures if confirmed."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = True

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.tools.unraid.make_graphql_request",
            new=AsyncMock(side_effect=Exception("connection refused")),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_reset_confirmation",
            new=AsyncMock(return_value=True),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_and_configure", new=AsyncMock(return_value=True)
        ) as mock_configure,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    mock_configure.assert_called_once()
    assert "configured" in result.lower() or "success" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_credentials_exist_connection_fails_user_declines() -> None:
    """setup returns 'no changes' when credentials exist (even with failed probe) and user declines."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = True

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.tools.unraid.make_graphql_request",
            new=AsyncMock(side_effect=Exception("connection refused")),
        ),
        patch(
            "unraid_mcp.core.setup.elicit_reset_confirmation",
            new=AsyncMock(return_value=False),
        ),
        patch("unraid_mcp.core.setup.elicit_and_configure") as mock_configure,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    mock_configure.assert_not_called()
    assert "no changes" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_ctx_none_already_configured_returns_no_changes() -> None:
    """When ctx=None and credentials are working, setup returns 'already configured' gracefully."""
    tool_fn = _make_tool()

    mock_path = MagicMock()
    mock_path.exists.return_value = True

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch(
            "unraid_mcp.tools.unraid.make_graphql_request",
            new=AsyncMock(return_value={"online": True}),
        ),
        patch("unraid_mcp.core.setup.elicit_and_configure") as mock_configure,
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=None)

    mock_configure.assert_not_called()
    assert "already configured" in result.lower()
    assert "no changes" in result.lower()


@pytest.mark.asyncio
async def test_health_setup_declined_message_includes_manual_path() -> None:
    """Declined setup message includes the exact credentials file path and variable names."""
    from unraid_mcp.config.settings import CREDENTIALS_ENV_PATH

    tool_fn = _make_tool()

    real_path_str = str(CREDENTIALS_ENV_PATH)
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    type(mock_path).__str__ = lambda self: real_path_str  # type: ignore[method-assign]

    with (
        patch("unraid_mcp.config.settings.CREDENTIALS_ENV_PATH", mock_path),
        patch("unraid_mcp.core.setup.elicit_and_configure", new=AsyncMock(return_value=False)),
    ):
        result = await tool_fn(action="health", subaction="setup", ctx=MagicMock())

    assert real_path_str in result
    assert "UNRAID_API_URL=" in result
    assert "UNRAID_API_KEY=" in result
