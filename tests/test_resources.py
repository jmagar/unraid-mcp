"""Tests for MCP subscription resources."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from unraid_mcp.subscriptions.queries import SNAPSHOT_ACTIONS
from unraid_mcp.subscriptions.resources import register_subscription_resources


def _make_resources():
    """Register resources on a test FastMCP instance and return it."""
    test_mcp = FastMCP("test")
    register_subscription_resources(test_mcp)
    return test_mcp


def _get_resource(mcp: FastMCP, uri: str):
    """Look up a registered resource by URI.

    Accesses FastMCP provider internals. If this breaks after a FastMCP upgrade,
    check whether a public resource-lookup API has been added upstream.
    """
    key = f"resource:{uri}@"
    return mcp.providers[0]._components[key]


@pytest.fixture
def _mock_ensure_started():
    with patch(
        "unraid_mcp.subscriptions.resources.ensure_subscriptions_started",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


class TestLiveResourcesUseManagerCache:
    """All live resources must read from the persistent SubscriptionManager cache."""

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_resource_returns_cached_data(self, action: str) -> None:
        cached = {"systemMetricsCpu": {"percentTotal": 12.5}}
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value=cached)
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        assert json.loads(result) == cached

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_resource_returns_connecting_when_no_cache_and_no_error(
        self, action: str
    ) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mock_mgr.last_error = {}
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        parsed = json.loads(result)
        assert parsed["status"] == "connecting"

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_resource_returns_error_status_on_permanent_failure(self, action: str) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mock_mgr.last_error = {action: "WebSocket auth failed"}
            mock_mgr.connection_states = {action: "auth_failed"}
            mock_mgr.auto_start_enabled = True
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        parsed = json.loads(result)
        assert parsed["status"] == "error"
        assert "auth failed" in parsed["message"]


class TestSnapshotSubscriptionsRegistered:
    """All SNAPSHOT_ACTIONS must be registered in the SubscriptionManager with auto_start=True."""

    def test_all_snapshot_actions_in_configs(self) -> None:
        from unraid_mcp.subscriptions.manager import subscription_manager

        for action in SNAPSHOT_ACTIONS:
            assert action in subscription_manager.subscription_configs, (
                f"'{action}' not registered in subscription_configs"
            )

    def test_all_snapshot_actions_autostart(self) -> None:
        from unraid_mcp.subscriptions.manager import subscription_manager

        for action in SNAPSHOT_ACTIONS:
            config = subscription_manager.subscription_configs[action]
            assert config.get("auto_start") is True, (
                f"'{action}' missing auto_start=True in subscription_configs"
            )


class TestLogsStreamResource:
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_logs_stream_no_data(self) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mcp = _make_resources()
            resource = _get_resource(mcp, "unraid://logs/stream")
            result = await resource.fn()
            parsed = json.loads(result)
            assert "status" in parsed

    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_logs_stream_returns_data_with_empty_dict(self) -> None:
        """Empty dict cache hit must return data, not 'connecting' status."""
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data = AsyncMock(return_value={})
            mcp = _make_resources()
            resource = _get_resource(mcp, "unraid://logs/stream")
            result = await resource.fn()
            assert json.loads(result) == {}


class TestAutoStartDisabledFallback:
    """When auto_start is disabled, resources fall back to on-demand subscribe_once."""

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_fallback_returns_subscribe_once_data(self, action: str) -> None:
        fallback_data = {"systemMetricsCpu": {"percentTotal": 42.0}}
        with (
            patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr,
            patch(
                "unraid_mcp.subscriptions.resources.subscribe_once",
                new=AsyncMock(return_value=fallback_data),
            ),
        ):
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mock_mgr.last_error = {}
            mock_mgr.auto_start_enabled = False
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        assert json.loads(result) == fallback_data

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_fallback_failure_returns_connecting(self, action: str) -> None:
        """When on-demand fallback itself fails, still return 'connecting' status."""
        with (
            patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr,
            patch(
                "unraid_mcp.subscriptions.resources.subscribe_once",
                new=AsyncMock(side_effect=Exception("WebSocket failed")),
            ),
        ):
            mock_mgr.get_resource_data = AsyncMock(return_value=None)
            mock_mgr.last_error = {}
            mock_mgr.auto_start_enabled = False
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        assert json.loads(result)["status"] == "connecting"
