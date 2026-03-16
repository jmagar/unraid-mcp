"""Tests for MCP subscription resources."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from unraid_mcp.subscriptions.resources import register_subscription_resources


def _make_resources():
    """Register resources on a test FastMCP instance and return it."""
    test_mcp = FastMCP("test")
    register_subscription_resources(test_mcp)
    return test_mcp


@pytest.fixture
def _mock_subscribe_once():
    with patch(
        "unraid_mcp.subscriptions.resources.subscribe_once",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


@pytest.fixture
def _mock_ensure_started():
    with patch(
        "unraid_mcp.subscriptions.resources.ensure_subscriptions_started",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


class TestLiveResources:
    @pytest.mark.parametrize(
        "action",
        [
            "cpu",
            "memory",
            "cpu_telemetry",
            "array_state",
            "parity_progress",
            "ups_status",
            "notifications_overview",
            "owner",
            "server_status",
        ],
    )
    async def test_resource_returns_json(
        self,
        action: str,
        _mock_subscribe_once: AsyncMock,
        _mock_ensure_started: AsyncMock,
    ) -> None:
        _mock_subscribe_once.return_value = {"data": "ok"}
        mcp = _make_resources()

        local_provider = mcp.providers[0]
        resource_key = f"resource:unraid://live/{action}@"
        resource = local_provider._components[resource_key]
        result = await resource.fn()

        parsed = json.loads(result)
        assert parsed == {"data": "ok"}

    async def test_resource_returns_error_dict_on_failure(
        self,
        _mock_subscribe_once: AsyncMock,
        _mock_ensure_started: AsyncMock,
    ) -> None:
        from fastmcp.exceptions import ToolError

        _mock_subscribe_once.side_effect = ToolError("WebSocket timeout")
        mcp = _make_resources()

        local_provider = mcp.providers[0]
        resource = local_provider._components["resource:unraid://live/cpu@"]
        result = await resource.fn()

        parsed = json.loads(result)
        assert "error" in parsed
        assert "WebSocket timeout" in parsed["error"]


class TestLogsStreamResource:
    async def test_logs_stream_no_data(self, _mock_ensure_started: AsyncMock) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mcp = _make_resources()
            local_provider = mcp.providers[0]
            resource = local_provider._components["resource:unraid://logs/stream@"]
            result = await resource.fn()
            parsed = json.loads(result)
            assert "status" in parsed
