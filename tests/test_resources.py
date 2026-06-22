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
        ts = "2026-04-04T12:00:00+00:00"
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=(cached, ts))
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        parsed = json.loads(result)
        assert parsed["_fetched_at"] == ts
        assert parsed["systemMetricsCpu"] == cached["systemMetricsCpu"]

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_resource_returns_connecting_when_no_cache_and_no_error(
        self, action: str
    ) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=None)
            mock_mgr.get_error_state = AsyncMock(return_value=(None, ""))
            mock_mgr.auto_start_enabled = True
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        parsed = json.loads(result)
        assert parsed["status"] == "connecting"

    @pytest.mark.parametrize("action", list(SNAPSHOT_ACTIONS.keys()))
    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_resource_returns_error_status_on_permanent_failure(self, action: str) -> None:
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=None)
            mock_mgr.get_error_state = AsyncMock(
                return_value=("WebSocket auth failed", "auth_failed")
            )
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
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=None)
            mcp = _make_resources()
            resource = _get_resource(mcp, "unraid://logs/stream")
            result = await resource.fn()
            parsed = json.loads(result)
            assert "status" in parsed

    @pytest.mark.usefixtures("_mock_ensure_started")
    async def test_logs_stream_returns_data_with_empty_dict(self) -> None:
        """Empty dict cache hit must return data with _fetched_at timestamp."""
        ts = "2026-04-04T12:00:00+00:00"
        with patch("unraid_mcp.subscriptions.resources.subscription_manager") as mock_mgr:
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=({}, ts))
            mcp = _make_resources()
            resource = _get_resource(mcp, "unraid://logs/stream")
            result = await resource.fn()
            parsed = json.loads(result)
            assert parsed["_fetched_at"] == ts


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
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=None)
            mock_mgr.get_error_state = AsyncMock(return_value=(None, ""))
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
            mock_mgr.get_resource_data_with_timestamp = AsyncMock(return_value=None)
            mock_mgr.get_error_state = AsyncMock(return_value=(None, ""))
            mock_mgr.auto_start_enabled = False
            mcp = _make_resources()
            resource = _get_resource(mcp, f"unraid://live/{action}")
            result = await resource.fn()
        assert json.loads(result)["status"] == "connecting"


class TestEnsureSubscriptionsStarted:
    """C1 / PERF-H1: a failed autostart must latch (no stampede) and surface the
    error, instead of being silently swallowed and re-attempted on every call."""

    @pytest.fixture
    def _reset_startup_state(self):
        import unraid_mcp.subscriptions.resources as res

        res._subscriptions_started = False
        res._last_startup_error = None
        try:
            yield res
        finally:
            res._subscriptions_started = False
            res._last_startup_error = None

    async def test_failed_autostart_latches_and_records_error(self, _reset_startup_state) -> None:
        res = _reset_startup_state
        mock = AsyncMock(side_effect=RuntimeError("ws backend down"))
        with patch.object(res, "autostart_subscriptions", mock):
            await res.ensure_subscriptions_started()
            await res.ensure_subscriptions_started()
            await res.ensure_subscriptions_started()
        # Latched after the first attempt — no per-call autostart stampede (PERF-H1).
        assert mock.call_count == 1
        # Error recorded and observable instead of swallowed (C1).
        err = res.get_last_startup_error()
        assert err is not None and "ws backend down" in err

    async def test_successful_autostart_clears_error(self, _reset_startup_state) -> None:
        res = _reset_startup_state
        mock = AsyncMock()
        with patch.object(res, "autostart_subscriptions", mock):
            await res.ensure_subscriptions_started()
            await res.ensure_subscriptions_started()
        assert mock.call_count == 1
        assert res.get_last_startup_error() is None

    async def test_cancellation_does_not_latch(self, _reset_startup_state) -> None:
        import asyncio

        res = _reset_startup_state
        mock = AsyncMock(side_effect=asyncio.CancelledError())
        with (
            patch.object(res, "autostart_subscriptions", mock),
            pytest.raises(asyncio.CancelledError),
        ):
            await res.ensure_subscriptions_started()
        # Shutdown path: flag NOT latched so a later call can retry.
        assert res._subscriptions_started is False
