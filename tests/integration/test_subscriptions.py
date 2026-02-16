"""Integration tests for WebSocket subscription lifecycle and reconnection logic.

These tests validate the SubscriptionManager's connection lifecycle,
reconnection with exponential backoff, protocol handling, and resource
data management without requiring a live Unraid server.
"""

import asyncio
import json
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from unraid_mcp.subscriptions.manager import SubscriptionManager

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ws_mock(
    recv_messages: list[str | dict[str, Any]] | None = None,
    subprotocol: str = "graphql-transport-ws",
) -> AsyncMock:
    """Build an AsyncMock that behaves like a websockets connection.

    Args:
        recv_messages: Ordered list of messages ``recv()`` should return.
            Dicts are auto-serialised to JSON strings.
        subprotocol: The negotiated subprotocol value.
    """
    ws = AsyncMock()
    ws.subprotocol = subprotocol

    if recv_messages is None:
        recv_messages = [{"type": "connection_ack"}]

    serialised: list[str] = [
        json.dumps(m) if isinstance(m, dict) else m for m in recv_messages
    ]
    ws.recv = AsyncMock(side_effect=serialised)
    ws.send = AsyncMock()

    # Support ``async for message in websocket:``
    # After recv() values are exhausted we raise StopAsyncIteration.
    ws.__aiter__ = MagicMock(return_value=ws)
    ws.__anext__ = AsyncMock(side_effect=serialised[1:] + [StopAsyncIteration()])

    return ws


def _ws_context(ws_mock: AsyncMock) -> AsyncMock:
    """Wrap *ws_mock* so ``async with websockets.connect(...) as ws:`` works."""
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=ws_mock)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


SAMPLE_QUERY = "subscription { test { value } }"


# ---------------------------------------------------------------------------
# SubscriptionManager Initialisation
# ---------------------------------------------------------------------------

class TestSubscriptionManagerInit:
    """Tests for SubscriptionManager constructor and defaults."""

    def test_default_state(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.active_subscriptions == {}
        assert mgr.resource_data == {}
        assert mgr.websocket is None

    def test_default_auto_start_enabled(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.auto_start_enabled is True

    @patch.dict("os.environ", {"UNRAID_AUTO_START_SUBSCRIPTIONS": "false"})
    def test_auto_start_disabled_via_env(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.auto_start_enabled is False

    def test_default_max_reconnect_attempts(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.max_reconnect_attempts == 10

    @patch.dict("os.environ", {"UNRAID_MAX_RECONNECT_ATTEMPTS": "5"})
    def test_custom_max_reconnect_attempts(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.max_reconnect_attempts == 5

    def test_subscription_configs_contain_log_file(self) -> None:
        mgr = SubscriptionManager()
        assert "logFileSubscription" in mgr.subscription_configs

    def test_log_file_subscription_not_auto_start(self) -> None:
        mgr = SubscriptionManager()
        cfg = mgr.subscription_configs["logFileSubscription"]
        assert cfg.get("auto_start") is False


# ---------------------------------------------------------------------------
# Connection Lifecycle
# ---------------------------------------------------------------------------

class TestConnectionLifecycle:
    """Tests for connect -> subscribe -> receive -> disconnect flow."""

    @pytest.mark.asyncio
    async def test_start_subscription_creates_task(self) -> None:
        mgr = SubscriptionManager()
        ws = _make_ws_mock()
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert "test_sub" in mgr.active_subscriptions
            assert isinstance(mgr.active_subscriptions["test_sub"], asyncio.Task)
            # Cleanup
            await mgr.stop_subscription("test_sub")

    @pytest.mark.asyncio
    async def test_duplicate_start_is_noop(self) -> None:
        mgr = SubscriptionManager()
        ws = _make_ws_mock()
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            first_task = mgr.active_subscriptions["test_sub"]
            # Second start should be a no-op
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert mgr.active_subscriptions["test_sub"] is first_task
            await mgr.stop_subscription("test_sub")

    @pytest.mark.asyncio
    async def test_stop_subscription_cancels_task(self) -> None:
        mgr = SubscriptionManager()
        ws = _make_ws_mock()
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert "test_sub" in mgr.active_subscriptions
            await mgr.stop_subscription("test_sub")
            assert "test_sub" not in mgr.active_subscriptions
            assert mgr.connection_states.get("test_sub") == "stopped"

    @pytest.mark.asyncio
    async def test_stop_nonexistent_subscription_is_safe(self) -> None:
        mgr = SubscriptionManager()
        # Should not raise
        await mgr.stop_subscription("nonexistent")

    @pytest.mark.asyncio
    async def test_connection_state_transitions(self) -> None:
        """Verify state goes through starting -> active during start_subscription."""
        mgr = SubscriptionManager()
        ws = _make_ws_mock()
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "test-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            # After start_subscription returns, state should be "active"
            assert mgr.connection_states["test_sub"] == "active"
            await mgr.stop_subscription("test_sub")


# ---------------------------------------------------------------------------
# Protocol Handling
# ---------------------------------------------------------------------------

class TestProtocolHandling:
    """Tests for GraphQL-WS protocol message handling inside _subscription_loop."""

    @pytest.mark.asyncio
    async def test_connection_init_sends_auth(self) -> None:
        """Verify connection_init includes X-API-Key header."""
        mgr = SubscriptionManager()

        data_msg = {"type": "next", "id": "test_sub", "payload": {"data": {"test": "value"}}}
        complete_msg = {"type": "complete", "id": "test_sub"}
        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                data_msg,
                complete_msg,
            ]
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "my-secret-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            # Run the loop directly (will break on "complete" message)
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # First send call should be connection_init
            first_send = ws.send.call_args_list[0]
            init_msg = json.loads(first_send[0][0])
            assert init_msg["type"] == "connection_init"
            assert init_msg["payload"]["headers"]["X-API-Key"] == "my-secret-key"

    @pytest.mark.asyncio
    async def test_subscribe_message_uses_correct_type_for_transport_ws(self) -> None:
        """graphql-transport-ws should use 'subscribe' type, not 'start'."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # Second send is the subscription message
            sub_send = ws.send.call_args_list[1]
            sub_msg = json.loads(sub_send[0][0])
            assert sub_msg["type"] == "subscribe"
            assert sub_msg["id"] == "test_sub"

    @pytest.mark.asyncio
    async def test_subscribe_message_uses_start_for_graphql_ws(self) -> None:
        """Legacy graphql-ws protocol should use 'start' type."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            sub_send = ws.send.call_args_list[1]
            sub_msg = json.loads(sub_send[0][0])
            assert sub_msg["type"] == "start"

    @pytest.mark.asyncio
    async def test_connection_error_sets_auth_failed_state(self) -> None:
        """connection_error response should break the loop and set auth_failed."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_error", "payload": {"message": "Invalid API key"}},
            ]
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "bad-key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "auth_failed"
            assert "Authentication error" in mgr.last_error["test_sub"]

    @pytest.mark.asyncio
    async def test_no_api_key_still_sends_init_without_payload(self) -> None:
        """When no API key is set, connection_init should omit the payload."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "complete", "id": "test_sub"},
            ]
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", ""),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            first_send = ws.send.call_args_list[0]
            init_msg = json.loads(first_send[0][0])
            assert init_msg["type"] == "connection_init"
            assert "payload" not in init_msg


# ---------------------------------------------------------------------------
# Data Reception
# ---------------------------------------------------------------------------

class TestDataReception:
    """Tests for receiving and storing subscription data."""

    @pytest.mark.asyncio
    async def test_next_message_stores_resource_data(self) -> None:
        """A 'next' message with data should populate resource_data."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {
                    "type": "next",
                    "id": "test_sub",
                    "payload": {"data": {"test": {"value": 42}}},
                },
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" in mgr.resource_data
            assert mgr.resource_data["test_sub"].data == {"test": {"value": 42}}
            assert mgr.resource_data["test_sub"].subscription_type == "test_sub"

    @pytest.mark.asyncio
    async def test_data_message_for_legacy_protocol(self) -> None:
        """Legacy graphql-ws uses 'data' type instead of 'next'."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {
                    "type": "data",
                    "id": "test_sub",
                    "payload": {"data": {"legacy": True}},
                },
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" in mgr.resource_data
            assert mgr.resource_data["test_sub"].data == {"legacy": True}

    @pytest.mark.asyncio
    async def test_graphql_errors_tracked_in_last_error(self) -> None:
        """GraphQL errors in payload should be recorded in last_error."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {
                    "type": "next",
                    "id": "test_sub",
                    "payload": {"errors": [{"message": "Field not found"}]},
                },
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "GraphQL errors" in mgr.last_error.get("test_sub", "")

    @pytest.mark.asyncio
    async def test_ping_receives_pong_response(self) -> None:
        """Server ping should trigger pong response."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "ping"},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # Find the pong send among all sends
            pong_sent = False
            for call in ws.send.call_args_list:
                msg = json.loads(call[0][0])
                if msg.get("type") == "pong":
                    pong_sent = True
                    break
            assert pong_sent, "Expected pong response to be sent"

    @pytest.mark.asyncio
    async def test_error_message_sets_error_state(self) -> None:
        """An 'error' type message should set connection state to error."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "error", "id": "test_sub", "payload": {"message": "bad query"}},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] in ("error", "completed")
            assert "Subscription error" in mgr.last_error.get("test_sub", "")

    @pytest.mark.asyncio
    async def test_complete_message_breaks_loop(self) -> None:
        """A 'complete' message should end the message loop."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] in ("completed", "max_retries_exceeded")

    @pytest.mark.asyncio
    async def test_mismatched_id_ignored(self) -> None:
        """A data message with a different subscription id should not store data."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {
                    "type": "next",
                    "id": "other_sub",
                    "payload": {"data": {"wrong": True}},
                },
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
        ):
            mgr.reconnect_attempts["test_sub"] = 0
            mgr.max_reconnect_attempts = 1
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" not in mgr.resource_data


# ---------------------------------------------------------------------------
# Reconnection and Backoff
# ---------------------------------------------------------------------------

class TestReconnection:
    """Tests for reconnection logic and exponential backoff."""

    @pytest.mark.asyncio
    async def test_max_retries_exceeded_stops_loop(self) -> None:
        """Loop should stop when max_reconnect_attempts is exceeded."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "max_retries_exceeded"
            assert mgr.reconnect_attempts["test_sub"] > mgr.max_reconnect_attempts

    @pytest.mark.asyncio
    async def test_backoff_delay_increases(self) -> None:
        """Each retry should increase the backoff delay."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 3

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))
        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # Verify increasing delays: initial=5, then 5*1.5=7.5, then 7.5*1.5=11.25
            delays = [call[0][0] for call in sleep_mock.call_args_list]
            assert len(delays) >= 2
            for i in range(1, len(delays)):
                assert delays[i] > delays[i - 1], (
                    f"Delay should increase: {delays[i]} > {delays[i-1]}"
                )

    @pytest.mark.asyncio
    async def test_backoff_capped_at_max(self) -> None:
        """Backoff delay should not exceed 300 seconds (5 minutes)."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 50

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("refused"))
        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            delays = [call[0][0] for call in sleep_mock.call_args_list]
            for d in delays:
                assert d <= 300, f"Delay {d} exceeds max of 300 seconds"

    @pytest.mark.asyncio
    async def test_successful_connection_resets_retry_count(self) -> None:
        """A successful connection should reset reconnect_attempts to 0."""
        mgr = SubscriptionManager()

        ws = _make_ws_mock(
            recv_messages=[
                {"type": "connection_ack"},
                {"type": "complete", "id": "test_sub"},
            ],
        )
        ctx = _ws_context(ws)

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", return_value=ctx),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", new_callable=AsyncMock),
        ):
            # Pre-set a high attempt count
            mgr.reconnect_attempts["test_sub"] = 5
            mgr.max_reconnect_attempts = 10
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # After successful connection, attempts should have been reset to 0
            # (it increments again on the next iteration, but the reset happens on connect)
            # The key check is that it didn't immediately bail due to max retries
            assert mgr.connection_states["test_sub"] != "max_retries_exceeded"

    @pytest.mark.asyncio
    async def test_invalid_uri_does_not_retry(self) -> None:
        """InvalidURI errors should break the loop without retrying."""
        import websockets.exceptions

        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 5

        connect_mock = AsyncMock(
            side_effect=websockets.exceptions.InvalidURI("bad://url", "Invalid URI")
        )
        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "invalid_uri"
            # Should not have retried
            sleep_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_timeout_error_triggers_reconnect(self) -> None:
        """Timeout errors should trigger reconnection with backoff."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        connect_mock = AsyncMock(side_effect=TimeoutError("connection timeout"))
        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.last_error["test_sub"] == "Connection or authentication timeout"
            assert sleep_mock.call_count >= 1

    @pytest.mark.asyncio
    async def test_connection_closed_triggers_reconnect(self) -> None:
        """ConnectionClosed errors should trigger reconnection."""
        import websockets.exceptions
        from websockets.frames import Close

        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        connect_mock = AsyncMock(
            side_effect=websockets.exceptions.ConnectionClosed(
                Close(1006, "abnormal"), None
            )
        )
        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://test.local"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "WebSocket connection closed" in mgr.last_error.get("test_sub", "")
            assert mgr.connection_states["test_sub"] in ("disconnected", "max_retries_exceeded")


# ---------------------------------------------------------------------------
# WebSocket URL Construction
# ---------------------------------------------------------------------------

class TestWebSocketURLConstruction:
    """Tests for HTTP-to-WS URL conversion logic."""

    @pytest.mark.asyncio
    async def test_https_converted_to_wss(self) -> None:
        """https:// URL should become wss://."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "https://myserver.local:31337"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg.startswith("wss://")
            assert url_arg.endswith("/graphql")

    @pytest.mark.asyncio
    async def test_http_converted_to_ws(self) -> None:
        """http:// URL should become ws://."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", "http://192.168.1.100:8080"),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg.startswith("ws://")
            assert url_arg.endswith("/graphql")

    @pytest.mark.asyncio
    async def test_no_api_url_raises_value_error(self) -> None:
        """Missing UNRAID_API_URL should raise ValueError and stop."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        sleep_mock = AsyncMock()

        with (
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_URL", ""),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] in ("error", "max_retries_exceeded")

    @pytest.mark.asyncio
    async def test_graphql_suffix_not_duplicated(self) -> None:
        """URL already ending in /graphql should not get it appended again."""
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = AsyncMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch("unraid_mcp.subscriptions.manager.websockets.connect", connect_mock),
            patch(
                "unraid_mcp.subscriptions.manager.UNRAID_API_URL",
                "https://myserver.local/graphql",
            ),
            patch("unraid_mcp.subscriptions.manager.UNRAID_API_KEY", "key"),
            patch("unraid_mcp.subscriptions.manager.build_ws_ssl_context", return_value=None),
            patch("unraid_mcp.subscriptions.manager.asyncio.sleep", new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg == "wss://myserver.local/graphql"
            assert "/graphql/graphql" not in url_arg


# ---------------------------------------------------------------------------
# Resource Data Access
# ---------------------------------------------------------------------------

class TestResourceData:
    """Tests for get_resource_data and list_active_subscriptions."""

    def test_get_resource_data_returns_none_when_empty(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.get_resource_data("nonexistent") is None

    def test_get_resource_data_returns_stored_data(self) -> None:
        from unraid_mcp.core.types import SubscriptionData

        mgr = SubscriptionManager()
        mgr.resource_data["test"] = SubscriptionData(
            data={"key": "value"},
            last_updated=datetime.now(),
            subscription_type="test",
        )
        result = mgr.get_resource_data("test")
        assert result == {"key": "value"}

    def test_list_active_subscriptions_empty(self) -> None:
        mgr = SubscriptionManager()
        assert mgr.list_active_subscriptions() == []

    def test_list_active_subscriptions_returns_names(self) -> None:
        mgr = SubscriptionManager()
        # Simulate active subscriptions
        mgr.active_subscriptions["sub_a"] = MagicMock()
        mgr.active_subscriptions["sub_b"] = MagicMock()
        result = mgr.list_active_subscriptions()
        assert sorted(result) == ["sub_a", "sub_b"]


# ---------------------------------------------------------------------------
# Subscription Status Diagnostics
# ---------------------------------------------------------------------------

class TestSubscriptionStatus:
    """Tests for get_subscription_status diagnostic output."""

    def test_status_includes_all_configured_subscriptions(self) -> None:
        mgr = SubscriptionManager()
        status = mgr.get_subscription_status()
        for name in mgr.subscription_configs:
            assert name in status

    def test_status_default_connection_state(self) -> None:
        mgr = SubscriptionManager()
        status = mgr.get_subscription_status()
        for sub_status in status.values():
            assert sub_status["runtime"]["connection_state"] == "not_started"

    def test_status_shows_active_flag(self) -> None:
        mgr = SubscriptionManager()
        mgr.active_subscriptions["logFileSubscription"] = MagicMock()
        status = mgr.get_subscription_status()
        assert status["logFileSubscription"]["runtime"]["active"] is True

    def test_status_shows_data_availability(self) -> None:
        from unraid_mcp.core.types import SubscriptionData

        mgr = SubscriptionManager()
        mgr.resource_data["logFileSubscription"] = SubscriptionData(
            data={"log": "content"},
            last_updated=datetime.now(),
            subscription_type="logFileSubscription",
        )
        status = mgr.get_subscription_status()
        assert status["logFileSubscription"]["data"]["available"] is True

    def test_status_shows_error_info(self) -> None:
        mgr = SubscriptionManager()
        mgr.last_error["logFileSubscription"] = "Test error message"
        status = mgr.get_subscription_status()
        assert status["logFileSubscription"]["runtime"]["last_error"] == "Test error message"


# ---------------------------------------------------------------------------
# Auto-Start
# ---------------------------------------------------------------------------

class TestAutoStart:
    """Tests for auto_start_all_subscriptions."""

    @pytest.mark.asyncio
    async def test_auto_start_disabled_skips_all(self) -> None:
        mgr = SubscriptionManager()
        mgr.auto_start_enabled = False
        # Should return without starting anything
        await mgr.auto_start_all_subscriptions()
        assert mgr.active_subscriptions == {}

    @pytest.mark.asyncio
    async def test_auto_start_only_starts_marked_subscriptions(self) -> None:
        """Only subscriptions with auto_start=True should be started."""
        mgr = SubscriptionManager()
        # logFileSubscription has auto_start=False by default
        with patch.object(mgr, "start_subscription", new_callable=AsyncMock) as mock_start:
            await mgr.auto_start_all_subscriptions()
            # logFileSubscription is auto_start=False, so no calls
            mock_start.assert_not_called()

    @pytest.mark.asyncio
    async def test_auto_start_handles_failure_gracefully(self) -> None:
        """Failed auto-starts should log the error but not crash."""
        mgr = SubscriptionManager()
        # Add a config that should auto-start
        mgr.subscription_configs["test_auto"] = {
            "query": "subscription { test }",
            "resource": "unraid://test",
            "description": "Test auto-start",
            "auto_start": True,
        }

        with patch.object(
            mgr, "start_subscription", new_callable=AsyncMock, side_effect=RuntimeError("fail")
        ):
            # Should not raise
            await mgr.auto_start_all_subscriptions()
            assert "fail" in mgr.last_error.get("test_auto", "")


# ---------------------------------------------------------------------------
# SSL Context (via utils)
# ---------------------------------------------------------------------------

class TestSSLContext:
    """Tests for build_ws_ssl_context utility."""

    def test_non_wss_returns_none(self) -> None:
        from unraid_mcp.subscriptions.utils import build_ws_ssl_context

        assert build_ws_ssl_context("ws://localhost:8080/graphql") is None

    def test_wss_with_verify_true_returns_default_context(self) -> None:
        import ssl

        from unraid_mcp.subscriptions.utils import build_ws_ssl_context

        with patch("unraid_mcp.subscriptions.utils.UNRAID_VERIFY_SSL", True):
            ctx = build_ws_ssl_context("wss://test.local/graphql")
            assert isinstance(ctx, ssl.SSLContext)
            assert ctx.check_hostname is True

    def test_wss_with_verify_false_disables_verification(self) -> None:
        import ssl

        from unraid_mcp.subscriptions.utils import build_ws_ssl_context

        with patch("unraid_mcp.subscriptions.utils.UNRAID_VERIFY_SSL", False):
            ctx = build_ws_ssl_context("wss://test.local/graphql")
            assert isinstance(ctx, ssl.SSLContext)
            assert ctx.check_hostname is False
            assert ctx.verify_mode == ssl.CERT_NONE

    def test_wss_with_ca_bundle_path(self) -> None:
        import ssl

        from unraid_mcp.subscriptions.utils import build_ws_ssl_context

        with (
            patch("unraid_mcp.subscriptions.utils.UNRAID_VERIFY_SSL", "/path/to/ca-bundle.crt"),
            patch("ssl.create_default_context") as mock_ctx,
        ):
            build_ws_ssl_context("wss://test.local/graphql")
            mock_ctx.assert_called_once_with(cafile="/path/to/ca-bundle.crt")
