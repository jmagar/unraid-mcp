"""Tests for unraid_health tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.core.utils import safe_display_url


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.health.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.health", "register_health_tool", "unraid_health")


class TestHealthValidation:
    async def test_invalid_action(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="invalid")


class TestHealthActions:
    async def test_test_connection(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"online": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="test_connection")
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
            "docker": {"containers": [{"id": "c1", "state": "running", "status": "Up 2 days"}]},
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="check")
        assert result["status"] == "healthy"
        assert "api_latency_ms" in result

    async def test_check_warning_on_alerts(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "info": {"machineId": "abc", "versions": {"unraid": "7.2"}, "os": {"uptime": 100}},
            "array": {"state": "STARTED"},
            "notifications": {"overview": {"unread": {"alert": 3, "warning": 0, "total": 3}}},
            "docker": {"containers": []},
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="check")
        assert result["status"] == "warning"
        assert any("alert" in i for i in result.get("issues", []))

    async def test_check_no_data(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {}
        tool_fn = _make_tool()
        result = await tool_fn(action="check")
        assert result["status"] == "unhealthy"

    async def test_check_api_error(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = Exception("Connection refused")
        tool_fn = _make_tool()
        result = await tool_fn(action="check")
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
        result = await tool_fn(action="check")
        # Missing info escalates to "degraded"; alerts only escalate to "warning"
        # Severity should stay at "degraded" (not downgrade to "warning")
        assert result["status"] == "degraded"

    async def test_diagnose_wraps_exception(self, _mock_graphql: AsyncMock) -> None:
        """When _diagnose_subscriptions raises, tool wraps in ToolError."""
        tool_fn = _make_tool()
        with (
            patch(
                "unraid_mcp.tools.health._diagnose_subscriptions",
                side_effect=RuntimeError("broken"),
            ),
            pytest.raises(ToolError, match="Failed to execute health/diagnose"),
        ):
            await tool_fn(action="diagnose")

    async def test_diagnose_success(self, _mock_graphql: AsyncMock) -> None:
        """Diagnose returns subscription status when modules are available."""
        tool_fn = _make_tool()
        mock_status = {
            "cpu_sub": {"runtime": {"connection_state": "connected", "last_error": None}},
        }
        with patch("unraid_mcp.tools.health._diagnose_subscriptions", return_value=mock_status):
            result = await tool_fn(action="diagnose")
        assert "cpu_sub" in result

    async def test_diagnose_import_error_internal(self) -> None:
        """_diagnose_subscriptions raises ToolError when subscription modules are unavailable."""
        import sys

        from unraid_mcp.tools.health import _diagnose_subscriptions

        # Remove cached subscription modules so the import is re-triggered
        cached = {k: v for k, v in sys.modules.items() if "unraid_mcp.subscriptions" in k}
        for k in cached:
            del sys.modules[k]

        try:
            # Replace the modules with objects that raise ImportError on access
            with (
                patch.dict(
                    sys.modules,
                    {
                        "unraid_mcp.subscriptions": None,
                        "unraid_mcp.subscriptions.manager": None,
                        "unraid_mcp.subscriptions.resources": None,
                    },
                ),
                pytest.raises(ToolError, match="Subscription modules not available"),
            ):
                await _diagnose_subscriptions()
        finally:
            # Restore cached modules
            sys.modules.update(cached)


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
        assert "path" not in result
        assert "query" not in result

    def test_strips_credentials(self) -> None:
        result = safe_display_url("https://user:password@unraid.local/graphql")
        assert "user" not in result
        assert "password" not in result
        assert result == "https://unraid.local"

    def test_strips_query_params(self) -> None:
        result = safe_display_url("http://host.local?token=abc&key=xyz")
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
        # urlparse("https://[invalid") parses without error, but accessing .hostname
        # raises ValueError: Invalid IPv6 URL — this triggers the except branch.
        result = safe_display_url("https://[invalid")
        assert result == "<unparseable>"
