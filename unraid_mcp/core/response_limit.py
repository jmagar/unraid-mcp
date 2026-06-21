"""Structured response-size limiting middleware.

fastmcp's stock ``ResponseLimitingMiddleware`` joins all text blocks and hard-cuts
the UTF-8 byte string mid-content, then appends a plain-text suffix. The ``unraid``
tool returns its payload as a JSON string in a single text block, so a mid-string
cut yields **invalid JSON** with no structured signal telling the agent to narrow
its query.

This middleware keeps the same trigger semantics (replace the result when its
serialized size exceeds ``max_size``) but, instead of salvaging a partial JSON
slice, returns a clean, complete, valid JSON marker the agent can parse:

    {
        "error": "response_truncated",
        "truncated": true,
        "original_bytes": <n>,
        "limit_bytes": <cap>,
        "hint": "Response exceeded the size limit. Narrow the query: ..."
    }
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import pydantic_core
from fastmcp.server.middleware.middleware import Middleware
from fastmcp.tools.base import ToolResult
from mcp.types import TextContent


if TYPE_CHECKING:
    import mcp.types as mt
    from fastmcp.server.middleware.middleware import CallNext, MiddlewareContext

__all__ = ["StructuredResponseLimitingMiddleware"]

logger = logging.getLogger(__name__)

_TRUNCATION_HINT = (
    "Response exceeded the size limit. Narrow the query: pass limit=, "
    "level=/context= for logs, or a more specific subaction/id."
)


class StructuredResponseLimitingMiddleware(Middleware):
    """Cap tool responses, replacing oversized ones with a parseable JSON marker.

    Unlike fastmcp's ``ResponseLimitingMiddleware``, this does not attempt to
    salvage a partial slice of the original payload (which produces invalid JSON).
    When a response exceeds ``max_size`` it is replaced wholesale with a small,
    complete JSON object carrying ``truncated: true`` and a remediation hint, so
    the agent gets a structured signal to narrow its query.

    Args:
        max_size: Maximum serialized response size in bytes.
        tools: Optional set of tool names to apply limiting to. If ``None``,
            applies to all tools.
    """

    def __init__(
        self,
        *,
        max_size: int = 40000,
        tools: list[str] | None = None,
    ) -> None:
        if max_size <= 0:
            raise ValueError(f"max_size must be positive, got {max_size}")
        self.max_size = max_size
        self.tools = set(tools) if tools is not None else None

    @staticmethod
    def _measure(result: ToolResult) -> int:
        """Return the serialized byte size of a ToolResult.

        The ``unraid`` tool's payload is a JSON string in a single ``TextContent``
        block — by far the common case. For that shape we measure the text bytes
        directly instead of re-serializing the whole ``ToolResult`` via
        ``pydantic_core.to_json`` on every call (the full serialization is only a
        few bytes larger — the content wrapper — so the cap behavior is unchanged).
        Multi-content or other result shapes fall back to full serialization.
        """
        content = result.content
        if len(content) == 1 and isinstance(content[0], TextContent):
            return len(content[0].text.encode())
        return len(pydantic_core.to_json(result, fallback=str))

    def _marker_result(self, original_bytes: int) -> ToolResult:
        """Build a ToolResult wrapping the structured truncation marker."""
        marker = {
            "error": "response_truncated",
            "truncated": True,
            "original_bytes": original_bytes,
            "limit_bytes": self.max_size,
            "hint": _TRUNCATION_HINT,
        }
        # meta={} ensures to_mcp_result() returns a CallToolResult, bypassing MCP
        # SDK outputSchema validation — a truncation marker is not the tool's
        # declared structured output shape.
        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(marker))],
            meta={},
        )

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """Intercept tool calls and replace oversized responses with a marker."""
        result = await call_next(context)

        if self.tools is not None and context.message.name not in self.tools:
            return result

        size = self._measure(result)
        if size <= self.max_size:
            return result

        logger.warning(
            "Tool %r response exceeds size limit: %d bytes > %d bytes, "
            "replacing with structured truncation marker",
            context.message.name,
            size,
            self.max_size,
        )
        return self._marker_result(size)
