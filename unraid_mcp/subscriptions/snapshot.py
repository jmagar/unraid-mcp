"""One-shot GraphQL subscription helpers for MCP tool snapshot actions.

`subscribe_once(query, variables, timeout)` — connect, subscribe, return the
first event's data, then disconnect.

`subscribe_collect(query, variables, collect_for, timeout)` — connect,
subscribe, collect all events for `collect_for` seconds, return the list.

Neither function maintains a persistent connection — they open and close a
WebSocket per call. This is intentional: MCP tools are request-response.
Use the SubscriptionManager for long-lived monitoring resources.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

import websockets
from websockets.typing import Subprotocol

from ..config.logging import logger
from ..core.exceptions import ToolError
from .utils import build_connection_init, build_ws_ssl_context, build_ws_url


_SUB_ID = "snapshot-1"


@asynccontextmanager
async def _ws_handshake(
    query: str,
    variables: dict[str, Any] | None = None,
    timeout: float = 10.0,  # noqa: ASYNC109
):
    """Connect, authenticate, and subscribe over WebSocket.

    Yields (ws, proto, expected_type) after the subscription is active.
    The caller iterates on ws for data events.
    """
    ws_url = build_ws_url()
    ssl_context = build_ws_ssl_context(ws_url)

    async with websockets.connect(
        ws_url,
        subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
        open_timeout=timeout,
        ping_interval=20,
        ping_timeout=10,
        ssl=ssl_context,
    ) as ws:
        proto = ws.subprotocol or "graphql-transport-ws"

        # Handshake
        await ws.send(json.dumps(build_connection_init()))

        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        ack = json.loads(raw)
        if ack.get("type") == "connection_error":
            raise ToolError(f"Subscription auth failed: {ack.get('payload')}")
        if ack.get("type") != "connection_ack":
            raise ToolError(f"Unexpected handshake response: {ack.get('type')}")

        # Subscribe
        start_type = "subscribe" if proto == "graphql-transport-ws" else "start"
        await ws.send(
            json.dumps(
                {
                    "id": _SUB_ID,
                    "type": start_type,
                    "payload": {"query": query, "variables": variables or {}},
                }
            )
        )

        expected_type = "next" if proto == "graphql-transport-ws" else "data"
        yield ws, expected_type


async def subscribe_once(
    query: str,
    variables: dict[str, Any] | None = None,
    timeout: float = 10.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """Open a WebSocket subscription, receive the first data event, close, return it.

    Raises ToolError on auth failure, GraphQL errors, or timeout.
    """
    async with _ws_handshake(query, variables, timeout) as (ws, expected_type):
        try:
            async with asyncio.timeout(timeout):
                async for raw_msg in ws:
                    msg = json.loads(raw_msg)
                    if msg.get("type") == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        continue
                    if msg.get("type") == expected_type and msg.get("id") == _SUB_ID:
                        payload = msg.get("payload", {})
                        if errors := payload.get("errors"):
                            msgs = "; ".join(e.get("message", str(e)) for e in errors)
                            raise ToolError(f"Subscription errors: {msgs}")
                        if data := payload.get("data"):
                            return data
                    elif msg.get("type") == "error" and msg.get("id") == _SUB_ID:
                        raise ToolError(f"Subscription error: {msg.get('payload')}")
        except TimeoutError:
            raise ToolError(f"Subscription timed out after {timeout:.0f}s") from None

    raise ToolError("WebSocket closed before receiving subscription data")


async def subscribe_collect(
    query: str,
    variables: dict[str, Any] | None = None,
    collect_for: float = 5.0,
    timeout: float = 10.0,  # noqa: ASYNC109
) -> list[dict[str, Any]]:
    """Open a subscription, collect events for `collect_for` seconds, close, return list.

    Returns an empty list if no events arrive within the window.
    Always closes the connection after the window expires.
    """
    events: list[dict[str, Any]] = []

    async with _ws_handshake(query, variables, timeout) as (ws, expected_type):
        try:
            async with asyncio.timeout(collect_for):
                async for raw_msg in ws:
                    msg = json.loads(raw_msg)
                    if msg.get("type") == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        continue
                    if msg.get("type") == expected_type and msg.get("id") == _SUB_ID:
                        payload = msg.get("payload", {})
                        if errors := payload.get("errors"):
                            msgs = "; ".join(e.get("message", str(e)) for e in errors)
                            raise ToolError(f"Subscription errors: {msgs}")
                        if data := payload.get("data"):
                            events.append(data)
        except TimeoutError:
            pass  # Collection window expired — return whatever was collected

    logger.debug("Collected %d events in %.1fs window", len(events), collect_for)
    return events
