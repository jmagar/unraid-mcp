# tests/test_snapshot.py
"""Tests for subscribe_once() and subscribe_collect() snapshot helpers."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_ws_message(sub_id: str, data: dict, proto: str = "graphql-transport-ws") -> str:
    msg_type = "next" if proto == "graphql-transport-ws" else "data"
    return json.dumps({"id": sub_id, "type": msg_type, "payload": {"data": data}})


def _make_ws_recv_sequence(*messages: str):
    """Build an async iterator that yields strings then hangs."""

    async def _gen():
        for m in messages:
            yield m
        # hang — simulates no more messages
        await asyncio.Event().wait()

    return _gen()


@pytest.fixture
def mock_ws():
    ws = MagicMock()
    ws.subprotocol = "graphql-transport-ws"
    ws.send = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_subscribe_once_returns_first_event(mock_ws):
    """subscribe_once returns data from the first matching event."""
    from unraid_mcp.subscriptions.snapshot import subscribe_once

    ack = json.dumps({"type": "connection_ack"})
    data_msg = _make_ws_message("snapshot-1", {"systemMetricsCpu": {"percentTotal": 42.0}})
    mock_ws.__aiter__ = lambda s: aiter([data_msg])
    mock_ws.recv = AsyncMock(return_value=ack)

    async def aiter(items):
        for item in items:
            yield item

    with patch("unraid_mcp.subscriptions.snapshot.websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await subscribe_once("subscription { systemMetricsCpu { percentTotal } }")

    assert result == {"systemMetricsCpu": {"percentTotal": 42.0}}


@pytest.mark.asyncio
async def test_subscribe_once_raises_on_graphql_error(mock_ws):
    """subscribe_once raises ToolError when server returns GraphQL errors."""
    from unraid_mcp.core.exceptions import ToolError
    from unraid_mcp.subscriptions.snapshot import subscribe_once

    ack = json.dumps({"type": "connection_ack"})
    error_msg = json.dumps(
        {
            "id": "snapshot-1",
            "type": "next",
            "payload": {"errors": [{"message": "Not authorized"}]},
        }
    )

    async def aiter(items):
        for item in items:
            yield item

    mock_ws.__aiter__ = lambda s: aiter([error_msg])
    mock_ws.recv = AsyncMock(return_value=ack)

    with patch("unraid_mcp.subscriptions.snapshot.websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(ToolError, match="Not authorized"):
            await subscribe_once("subscription { systemMetricsCpu { percentTotal } }")


@pytest.mark.asyncio
async def test_subscribe_collect_returns_multiple_events(mock_ws):
    """subscribe_collect returns a list of events received within the window."""
    from unraid_mcp.subscriptions.snapshot import subscribe_collect

    ack = json.dumps({"type": "connection_ack"})
    msg1 = _make_ws_message("snapshot-1", {"notificationAdded": {"id": "1", "title": "A"}})
    msg2 = _make_ws_message("snapshot-1", {"notificationAdded": {"id": "2", "title": "B"}})

    async def aiter(items):
        for item in items:
            yield item
        await asyncio.sleep(10)  # hang after messages

    mock_ws.__aiter__ = lambda s: aiter([msg1, msg2])
    mock_ws.recv = AsyncMock(return_value=ack)

    with patch("unraid_mcp.subscriptions.snapshot.websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await subscribe_collect(
            "subscription { notificationAdded { id title } }",
            collect_for=0.1,
        )

    assert len(result) == 2
    assert result[0]["notificationAdded"]["id"] == "1"


def test_snapshot_actions_importable_from_subscriptions() -> None:
    from unraid_mcp.subscriptions.queries import COLLECT_ACTIONS, SNAPSHOT_ACTIONS

    assert "cpu" in SNAPSHOT_ACTIONS
    assert "log_tail" in COLLECT_ACTIONS
