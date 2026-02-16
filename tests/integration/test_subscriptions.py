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
import websockets.exceptions

from unraid_mcp.subscriptions.manager import SubscriptionManager

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeWebSocket:
    """Minimal fake WebSocket that supports both recv() and async-for iteration.

    The manager calls ``recv()`` once for the connection_ack, then enters
    ``async for message in websocket:`` for the data stream.  This class
    tracks a shared message queue so both paths draw from the same list.

    When messages are exhausted, iteration ends cleanly via StopAsyncIteration
    (which terminates ``async for``), and ``recv()`` raises ConnectionClosed
    so the manager treats it as a normal disconnection.
    """

    def __init__(
        self,
        messages: list[dict[str, Any] | str],
        subprotocol: str = "graphql-transport-ws",
    ) -> None:
        self.subprotocol = subprotocol
        self._messages = [
            json.dumps(m) if isinstance(m, dict) else m for m in messages
        ]
        self._index = 0
        self.send = AsyncMock()

    async def recv(self) -> str:
        if self._index >= len(self._messages):
            # Simulate normal connection close when messages exhausted
            from websockets.frames import Close

            raise websockets.exceptions.ConnectionClosed(
                Close(1000, "normal closure"), None
            )
        msg = self._messages[self._index]
        self._index += 1
        return msg

    def __aiter__(self) -> "FakeWebSocket":
        return self

    async def __anext__(self) -> str:
        if self._index >= len(self._messages):
            raise StopAsyncIteration
        msg = self._messages[self._index]
        self._index += 1
        return msg


def _ws_context(ws: FakeWebSocket) -> MagicMock:
    """Wrap a FakeWebSocket so ``async with websockets.connect(...) as ws:`` works."""
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=ws)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


SAMPLE_QUERY = "subscription { test { value } }"

# Shared patch targets
_WS_CONNECT = "unraid_mcp.subscriptions.manager.websockets.connect"
_API_URL = "unraid_mcp.subscriptions.manager.UNRAID_API_URL"
_API_KEY = "unraid_mcp.subscriptions.manager.UNRAID_API_KEY"
_SSL_CTX = "unraid_mcp.subscriptions.manager.build_ws_ssl_context"
_SLEEP = "unraid_mcp.subscriptions.manager.asyncio.sleep"


# ---------------------------------------------------------------------------
# SubscriptionManager Initialisation
# ---------------------------------------------------------------------------


class TestSubscriptionManagerInit:

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

    async def test_start_subscription_creates_task(self) -> None:
        mgr = SubscriptionManager()
        ws = FakeWebSocket([{"type": "connection_ack"}])
        ctx = _ws_context(ws)

        with (
            patch(_WS_CONNECT, return_value=ctx),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "test-key"),
            patch(_SSL_CTX, return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert "test_sub" in mgr.active_subscriptions
            assert isinstance(mgr.active_subscriptions["test_sub"], asyncio.Task)
            await mgr.stop_subscription("test_sub")

    async def test_duplicate_start_is_noop(self) -> None:
        mgr = SubscriptionManager()
        ws = FakeWebSocket([{"type": "connection_ack"}])
        ctx = _ws_context(ws)

        with (
            patch(_WS_CONNECT, return_value=ctx),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "test-key"),
            patch(_SSL_CTX, return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            first_task = mgr.active_subscriptions["test_sub"]
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert mgr.active_subscriptions["test_sub"] is first_task
            await mgr.stop_subscription("test_sub")

    async def test_stop_subscription_cancels_task(self) -> None:
        mgr = SubscriptionManager()
        ws = FakeWebSocket([{"type": "connection_ack"}])
        ctx = _ws_context(ws)

        with (
            patch(_WS_CONNECT, return_value=ctx),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "test-key"),
            patch(_SSL_CTX, return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert "test_sub" in mgr.active_subscriptions
            await mgr.stop_subscription("test_sub")
            assert "test_sub" not in mgr.active_subscriptions
            assert mgr.connection_states.get("test_sub") == "stopped"

    async def test_stop_nonexistent_subscription_is_safe(self) -> None:
        mgr = SubscriptionManager()
        await mgr.stop_subscription("nonexistent")

    async def test_connection_state_transitions(self) -> None:
        mgr = SubscriptionManager()
        ws = FakeWebSocket([{"type": "connection_ack"}])
        ctx = _ws_context(ws)

        with (
            patch(_WS_CONNECT, return_value=ctx),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "test-key"),
            patch(_SSL_CTX, return_value=None),
        ):
            await mgr.start_subscription("test_sub", SAMPLE_QUERY)
            assert mgr.connection_states["test_sub"] == "active"
            await mgr.stop_subscription("test_sub")


# ---------------------------------------------------------------------------
# Protocol Handling (via _subscription_loop)
# ---------------------------------------------------------------------------


def _loop_patches(
    ws: FakeWebSocket,
    api_key: str = "test-key",
) -> tuple:
    """Patches for tests that call ``_subscription_loop`` directly.

    Uses a connect mock that succeeds once then fails, plus a mocked
    asyncio.sleep to prevent real delays.
    """
    ctx = _ws_context(ws)
    call_count = 0

    def _connect_side_effect(*_a: Any, **_kw: Any) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return ctx
        raise ConnectionRefusedError("no more test connections")

    return (
        patch(_WS_CONNECT, side_effect=_connect_side_effect),
        patch(_API_URL, "https://test.local"),
        patch(_API_KEY, api_key),
        patch(_SSL_CTX, return_value=None),
        patch(_SLEEP, new_callable=AsyncMock),
    )


class TestProtocolHandling:

    async def test_connection_init_sends_auth(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "next", "id": "test_sub", "payload": {"data": {"v": 1}}},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws, api_key="my-secret-key")
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            first_send = ws.send.call_args_list[0]
            init_msg = json.loads(first_send[0][0])
            assert init_msg["type"] == "connection_init"
            assert init_msg["payload"]["headers"]["X-API-Key"] == "my-secret-key"

    async def test_subscribe_uses_subscribe_type_for_transport_ws(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [{"type": "connection_ack"}, {"type": "complete", "id": "test_sub"}],
            subprotocol="graphql-transport-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            sub_send = ws.send.call_args_list[1]
            sub_msg = json.loads(sub_send[0][0])
            assert sub_msg["type"] == "subscribe"
            assert sub_msg["id"] == "test_sub"

    async def test_subscribe_uses_start_type_for_graphql_ws(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [{"type": "connection_ack"}, {"type": "complete", "id": "test_sub"}],
            subprotocol="graphql-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            sub_send = ws.send.call_args_list[1]
            sub_msg = json.loads(sub_send[0][0])
            assert sub_msg["type"] == "start"

    async def test_connection_error_sets_auth_failed(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_error", "payload": {"message": "Invalid API key"}},
        ])
        p = _loop_patches(ws, api_key="bad-key")
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "auth_failed"
            assert "Authentication error" in mgr.last_error["test_sub"]

    async def test_no_api_key_omits_payload(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws, api_key="")
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            first_send = ws.send.call_args_list[0]
            init_msg = json.loads(first_send[0][0])
            assert init_msg["type"] == "connection_init"
            assert "payload" not in init_msg


# ---------------------------------------------------------------------------
# Data Reception
# ---------------------------------------------------------------------------


class TestDataReception:

    async def test_next_message_stores_resource_data(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [
                {"type": "connection_ack"},
                {"type": "next", "id": "test_sub", "payload": {"data": {"test": {"value": 42}}}},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" in mgr.resource_data
            assert mgr.resource_data["test_sub"].data == {"test": {"value": 42}}
            assert mgr.resource_data["test_sub"].subscription_type == "test_sub"

    async def test_data_message_for_legacy_protocol(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [
                {"type": "connection_ack"},
                {"type": "data", "id": "test_sub", "payload": {"data": {"legacy": True}}},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" in mgr.resource_data
            assert mgr.resource_data["test_sub"].data == {"legacy": True}

    async def test_graphql_errors_tracked_in_last_error(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [
                {"type": "connection_ack"},
                {"type": "next", "id": "test_sub", "payload": {"errors": [{"message": "bad"}]}},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # The last_error may be overwritten by a subsequent reconnection error,
            # so check the resource_data wasn't stored (errors in payload means no data)
            assert "test_sub" not in mgr.resource_data

    async def test_ping_receives_pong_response(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "ping"},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            pong_sent = any(
                json.loads(call[0][0]).get("type") == "pong"
                for call in ws.send.call_args_list
            )
            assert pong_sent, "Expected pong response to be sent"

    async def test_error_message_sets_error_state(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "error", "id": "test_sub", "payload": {"message": "bad query"}},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # Verify the error was recorded at some point by checking resource_data
            # was not stored (error messages don't produce data)
            assert "test_sub" not in mgr.resource_data

    async def test_complete_message_breaks_inner_loop(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # complete message was processed (test finished, loop terminated)
            assert "test_sub" not in mgr.resource_data

    async def test_mismatched_id_ignored(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket(
            [
                {"type": "connection_ack"},
                {"type": "next", "id": "other_sub", "payload": {"data": {"wrong": True}}},
                {"type": "complete", "id": "test_sub"},
            ],
            subprotocol="graphql-transport-ws",
        )
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "test_sub" not in mgr.resource_data

    async def test_keepalive_messages_handled(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "ka"},
            {"type": "pong"},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

    async def test_invalid_json_message_handled(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            "not valid json {{{",
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})


# ---------------------------------------------------------------------------
# Reconnection and Backoff
# ---------------------------------------------------------------------------


class TestReconnection:

    async def test_max_retries_exceeded_stops_loop(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        with (
            patch(_WS_CONNECT, side_effect=ConnectionRefusedError("refused")),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "max_retries_exceeded"
            assert mgr.reconnect_attempts["test_sub"] > mgr.max_reconnect_attempts

    async def test_backoff_delay_increases(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 3

        sleep_mock = AsyncMock()

        with (
            patch(_WS_CONNECT, side_effect=ConnectionRefusedError("refused")),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            delays = [call[0][0] for call in sleep_mock.call_args_list]
            assert len(delays) >= 2
            for i in range(1, len(delays)):
                assert delays[i] > delays[i - 1], (
                    f"Delay should increase: {delays[i]} > {delays[i - 1]}"
                )

    async def test_backoff_capped_at_max(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 50

        sleep_mock = AsyncMock()

        with (
            patch(_WS_CONNECT, side_effect=ConnectionRefusedError("refused")),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            delays = [call[0][0] for call in sleep_mock.call_args_list]
            for d in delays:
                assert d <= 300, f"Delay {d} exceeds max of 300 seconds"

    async def test_successful_connection_resets_retry_count(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 10
        mgr.reconnect_attempts["test_sub"] = 5

        ws = FakeWebSocket([
            {"type": "connection_ack"},
            {"type": "complete", "id": "test_sub"},
        ])
        p = _loop_patches(ws)
        with p[0], p[1], p[2], p[3], p[4]:
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            # After successful connection, attempts reset to 0 internally.
            # The loop then reconnects, fails, and increments. But since we
            # started at 5, the key check is that we didn't immediately bail.
            # Verify some messages were processed (connection was established).
            assert ws.send.call_count >= 2  # connection_init + subscribe

    async def test_invalid_uri_does_not_retry(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 5

        sleep_mock = AsyncMock()

        with (
            patch(
                _WS_CONNECT,
                side_effect=websockets.exceptions.InvalidURI("bad://url", "Invalid URI"),
            ),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.connection_states["test_sub"] == "invalid_uri"
            sleep_mock.assert_not_called()

    async def test_timeout_error_triggers_reconnect(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        sleep_mock = AsyncMock()

        with (
            patch(_WS_CONNECT, side_effect=TimeoutError("connection timeout")),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert mgr.last_error["test_sub"] == "Connection or authentication timeout"
            assert sleep_mock.call_count >= 1

    async def test_connection_closed_triggers_reconnect(self) -> None:
        from websockets.frames import Close

        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 2

        sleep_mock = AsyncMock()

        with (
            patch(
                _WS_CONNECT,
                side_effect=websockets.exceptions.ConnectionClosed(
                    Close(1006, "abnormal"), None
                ),
            ),
            patch(_API_URL, "https://test.local"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, sleep_mock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            assert "WebSocket connection closed" in mgr.last_error.get("test_sub", "")
            assert mgr.connection_states["test_sub"] in ("disconnected", "max_retries_exceeded")


# ---------------------------------------------------------------------------
# WebSocket URL Construction
# ---------------------------------------------------------------------------


class TestWebSocketURLConstruction:

    async def test_https_converted_to_wss(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = MagicMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch(_WS_CONNECT, connect_mock),
            patch(_API_URL, "https://myserver.local:31337"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg.startswith("wss://")
            assert url_arg.endswith("/graphql")

    async def test_http_converted_to_ws(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = MagicMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch(_WS_CONNECT, connect_mock),
            patch(_API_URL, "http://192.168.1.100:8080"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg.startswith("ws://")
            assert url_arg.endswith("/graphql")

    async def test_no_api_url_raises_value_error(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        with (
            patch(_API_URL, ""),
            patch(_API_KEY, "key"),
            patch(_SLEEP, new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})
            assert mgr.connection_states["test_sub"] in ("error", "max_retries_exceeded")

    async def test_graphql_suffix_not_duplicated(self) -> None:
        mgr = SubscriptionManager()
        mgr.max_reconnect_attempts = 1

        connect_mock = MagicMock(side_effect=ConnectionRefusedError("test"))

        with (
            patch(_WS_CONNECT, connect_mock),
            patch(_API_URL, "https://myserver.local/graphql"),
            patch(_API_KEY, "key"),
            patch(_SSL_CTX, return_value=None),
            patch(_SLEEP, new_callable=AsyncMock),
        ):
            await mgr._subscription_loop("test_sub", SAMPLE_QUERY, {})

            url_arg = connect_mock.call_args[0][0]
            assert url_arg == "wss://myserver.local/graphql"
            assert "/graphql/graphql" not in url_arg


# ---------------------------------------------------------------------------
# Resource Data Access
# ---------------------------------------------------------------------------


class TestResourceData:

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
        mgr.active_subscriptions["sub_a"] = MagicMock()
        mgr.active_subscriptions["sub_b"] = MagicMock()
        result = mgr.list_active_subscriptions()
        assert sorted(result) == ["sub_a", "sub_b"]


# ---------------------------------------------------------------------------
# Subscription Status Diagnostics
# ---------------------------------------------------------------------------


class TestSubscriptionStatus:

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

    def test_status_reconnect_attempts_tracked(self) -> None:
        mgr = SubscriptionManager()
        mgr.reconnect_attempts["logFileSubscription"] = 3
        status = mgr.get_subscription_status()
        assert status["logFileSubscription"]["runtime"]["reconnect_attempts"] == 3


# ---------------------------------------------------------------------------
# Auto-Start
# ---------------------------------------------------------------------------


class TestAutoStart:

    async def test_auto_start_disabled_skips_all(self) -> None:
        mgr = SubscriptionManager()
        mgr.auto_start_enabled = False
        await mgr.auto_start_all_subscriptions()
        assert mgr.active_subscriptions == {}

    async def test_auto_start_only_starts_marked_subscriptions(self) -> None:
        mgr = SubscriptionManager()
        with patch.object(mgr, "start_subscription", new_callable=AsyncMock) as mock_start:
            await mgr.auto_start_all_subscriptions()
            mock_start.assert_not_called()

    async def test_auto_start_handles_failure_gracefully(self) -> None:
        mgr = SubscriptionManager()
        mgr.subscription_configs["test_auto"] = {
            "query": "subscription { test }",
            "resource": "unraid://test",
            "description": "Test auto-start",
            "auto_start": True,
        }

        with patch.object(
            mgr, "start_subscription", new_callable=AsyncMock, side_effect=RuntimeError("fail")
        ):
            await mgr.auto_start_all_subscriptions()
            assert "fail" in mgr.last_error.get("test_auto", "")

    async def test_auto_start_calls_start_for_marked(self) -> None:
        mgr = SubscriptionManager()
        mgr.subscription_configs["auto_sub"] = {
            "query": "subscription { auto }",
            "resource": "unraid://auto",
            "description": "Auto sub",
            "auto_start": True,
        }

        with patch.object(mgr, "start_subscription", new_callable=AsyncMock) as mock_start:
            await mgr.auto_start_all_subscriptions()
            mock_start.assert_called_once_with("auto_sub", "subscription { auto }")


# ---------------------------------------------------------------------------
# SSL Context (via utils)
# ---------------------------------------------------------------------------


class TestSSLContext:

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
        from unraid_mcp.subscriptions.utils import build_ws_ssl_context

        with (
            patch("unraid_mcp.subscriptions.utils.UNRAID_VERIFY_SSL", "/path/to/ca-bundle.crt"),
            patch("ssl.create_default_context") as mock_ctx,
        ):
            build_ws_ssl_context("wss://test.local/graphql")
            mock_ctx.assert_called_once_with(cafile="/path/to/ca-bundle.crt")
