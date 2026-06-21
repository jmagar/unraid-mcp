"""One-shot GraphQL subscription helpers for MCP tool snapshot actions.

`subscribe_once(query, variables, timeout)` — connect, subscribe, return the
first event's data, then disconnect.

`subscribe_collect(query, variables, collect_for, timeout)` — connect,
subscribe, collect all events for `collect_for` seconds, return the list.

Neither function maintains a persistent connection — they open and close a
WebSocket per call. This is intentional: MCP tools are request-response.
Use the SubscriptionManager for long-lived monitoring resources.

Both helpers share the graphql-ws handshake + message-normalization primitive in
:mod:`.protocol` (``graphql_ws_session`` + ``iter_messages``): the handshake,
ping->pong keepalives, and malformed-frame skipping live there, so this module
only contains the snapshot-specific timeout + return-first / collect-window
semantics.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from ..config.logging import logger
from ..core.exceptions import ToolError
from .protocol import (
    DataEvent,
    ErrorEvent,
    ProtocolError,
    graphql_ws_session,
)
from .utils import build_ws_ssl_context, build_ws_url


_SUB_ID = "snapshot-1"


@asynccontextmanager
async def _ws_handshake(
    query: str,
    variables: dict[str, Any] | None = None,
    timeout: float = 10.0,  # noqa: ASYNC109
):
    """Connect, authenticate, and subscribe over WebSocket.

    Yields the live :class:`~.protocol.GraphqlWsSession` after the subscription
    is active. The caller iterates ``session.messages()`` for data events.

    Translates the protocol's :class:`~.protocol.ProtocolError` (auth failure /
    unexpected handshake frame) into a :class:`ToolError`, preserving the
    historical snapshot error messages.
    """
    ws_url = build_ws_url()
    ssl_context = build_ws_ssl_context(ws_url)

    try:
        async with graphql_ws_session(
            ws_url,
            query,
            sub_id=_SUB_ID,
            variables=variables,
            ssl_context=ssl_context,
            open_timeout=timeout,
            ack_timeout=timeout,
            ping_interval=20,
            ping_timeout=10,
        ) as session:
            yield session
    except ProtocolError as e:
        if e.kind == "connection_error":
            raise ToolError(f"Subscription auth failed: {e.payload}") from e
        raise ToolError(f"Unexpected handshake response: {e.ack_type}") from e


def _raise_on_errors(payload: dict[str, Any]) -> None:
    """Raise ToolError if a data payload carries GraphQL errors."""
    if errors := payload.get("errors"):
        msgs = "; ".join(e.get("message", str(e)) for e in errors)
        raise ToolError(f"Subscription errors: {msgs}")


async def subscribe_once(
    query: str,
    variables: dict[str, Any] | None = None,
    timeout: float = 10.0,  # noqa: ASYNC109
) -> dict[str, Any]:
    """Open a WebSocket subscription, receive the first data event, close, return it.

    Raises ToolError on auth failure, GraphQL errors, or timeout.
    """
    async with _ws_handshake(query, variables, timeout) as session:
        try:
            async with asyncio.timeout(timeout):
                async for event in session.messages():
                    if isinstance(event, DataEvent):
                        _raise_on_errors(event.payload)
                        if data := event.payload.get("data"):
                            return data
                    elif isinstance(event, ErrorEvent):
                        raise ToolError(f"Subscription error: {event.payload}")
                    # CompleteEvent: fall through; the websocket close that follows
                    # surfaces as "closed before data" below.
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

    async with _ws_handshake(query, variables, timeout) as session:
        try:
            async with asyncio.timeout(collect_for):
                async for event in session.messages():
                    if isinstance(event, DataEvent):
                        _raise_on_errors(event.payload)
                        if data := event.payload.get("data"):
                            events.append(data)
                    elif isinstance(event, ErrorEvent):
                        raise ToolError(f"Subscription error: {event.payload}")
                    # CompleteEvent is ignored: the historical loop kept collecting
                    # until the window expired or the socket closed, never breaking
                    # early on a server 'complete'. The ws close that follows ends
                    # the async-for and returns the collected events.
        except TimeoutError:
            pass  # Collection window expired — return whatever was collected

    logger.debug("Collected %d events in %.1fs window", len(events), collect_for)
    return events
