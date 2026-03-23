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
from typing import Any

import websockets
from websockets.typing import Subprotocol

from ..config import settings as _settings
from ..config.logging import logger
from ..core.exceptions import ToolError
from .utils import build_ws_ssl_context, build_ws_url


async def subscribe_once(
    query: str,
    variables: dict[str, Any] | None = None,
    timeout: float = 10.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """Open a WebSocket subscription, receive the first data event, close, return it.

    Raises ToolError on auth failure, GraphQL errors, or timeout.
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
        sub_id = "snapshot-1"

        # Handshake
        init: dict[str, Any] = {"type": "connection_init"}
        if _settings.UNRAID_API_KEY:
            init["payload"] = {"x-api-key": _settings.UNRAID_API_KEY}
        await ws.send(json.dumps(init))

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
                    "id": sub_id,
                    "type": start_type,
                    "payload": {"query": query, "variables": variables or {}},
                }
            )
        )

        # Await first matching data event
        expected_type = "next" if proto == "graphql-transport-ws" else "data"

        try:
            async with asyncio.timeout(timeout):
                async for raw_msg in ws:
                    msg = json.loads(raw_msg)
                    if msg.get("type") == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        continue
                    if msg.get("type") == expected_type and msg.get("id") == sub_id:
                        payload = msg.get("payload", {})
                        if errors := payload.get("errors"):
                            msgs = "; ".join(e.get("message", str(e)) for e in errors)
                            raise ToolError(f"Subscription errors: {msgs}")
                        if data := payload.get("data"):
                            return data
                    elif msg.get("type") == "error" and msg.get("id") == sub_id:
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
    ws_url = build_ws_url()
    ssl_context = build_ws_ssl_context(ws_url)
    events: list[dict[str, Any]] = []

    async with websockets.connect(
        ws_url,
        subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
        open_timeout=timeout,
        ping_interval=20,
        ping_timeout=10,
        ssl=ssl_context,
    ) as ws:
        proto = ws.subprotocol or "graphql-transport-ws"
        sub_id = "snapshot-1"

        init: dict[str, Any] = {"type": "connection_init"}
        if _settings.UNRAID_API_KEY:
            init["payload"] = {"x-api-key": _settings.UNRAID_API_KEY}
        await ws.send(json.dumps(init))

        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        ack = json.loads(raw)
        if ack.get("type") == "connection_error":
            raise ToolError(f"Subscription auth failed: {ack.get('payload')}")
        if ack.get("type") != "connection_ack":
            raise ToolError(f"Unexpected handshake response: {ack.get('type')}")

        start_type = "subscribe" if proto == "graphql-transport-ws" else "start"
        await ws.send(
            json.dumps(
                {
                    "id": sub_id,
                    "type": start_type,
                    "payload": {"query": query, "variables": variables or {}},
                }
            )
        )

        expected_type = "next" if proto == "graphql-transport-ws" else "data"

        try:
            async with asyncio.timeout(collect_for):
                async for raw_msg in ws:
                    msg = json.loads(raw_msg)
                    if msg.get("type") == "ping":
                        await ws.send(json.dumps({"type": "pong"}))
                        continue
                    if msg.get("type") == expected_type and msg.get("id") == sub_id:
                        payload = msg.get("payload", {})
                        if errors := payload.get("errors"):
                            msgs = "; ".join(e.get("message", str(e)) for e in errors)
                            raise ToolError(f"Subscription errors: {msgs}")
                        if data := payload.get("data"):
                            events.append(data)
        except TimeoutError:
            pass  # Collection window expired — return whatever was collected

    logger.debug(f"[SNAPSHOT] Collected {len(events)} events in {collect_for}s window")
    return events
