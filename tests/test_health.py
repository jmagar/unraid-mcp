"""Tests for unraid_health tool."""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> AsyncMock:
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
            "notifications": {
                "overview": {"unread": {"alert": 0, "warning": 0, "total": 3}}
            },
            "docker": {
                "containers": [{"id": "c1", "state": "running", "status": "Up 2 days"}]
            },
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="check")
        assert result["status"] == "healthy"
        assert "api_latency_ms" in result

    async def test_check_warning_on_alerts(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "info": {"machineId": "abc", "versions": {"unraid": "7.2"}, "os": {"uptime": 100}},
            "array": {"state": "STARTED"},
            "notifications": {
                "overview": {"unread": {"alert": 3, "warning": 0, "total": 3}}
            },
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
            "notifications": {
                "overview": {"unread": {"alert": 5, "warning": 0, "total": 5}}
            },
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
        with patch(
            "unraid_mcp.tools.health._diagnose_subscriptions",
            side_effect=RuntimeError("broken"),
        ):
            with pytest.raises(ToolError, match="broken"):
                await tool_fn(action="diagnose")

    async def test_diagnose_import_error_internal(self) -> None:
        """_diagnose_subscriptions catches ImportError and returns error dict."""
        import builtins

        from unraid_mcp.tools.health import _diagnose_subscriptions

        real_import = builtins.__import__

        def fail_subscriptions(name, *args, **kwargs):
            if "subscriptions" in name:
                raise ImportError("no module")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fail_subscriptions):
            result = await _diagnose_subscriptions()
            assert "error" in result
