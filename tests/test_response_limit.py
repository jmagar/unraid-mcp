"""Tests for the structured response-size limiting middleware.

The middleware is unit-tested in isolation by driving ``on_call_tool`` with a stub
context and a stub ``call_next`` that returns a controlled ``ToolResult``. No
running server or GraphQL backend is needed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
from fastmcp.tools.base import ToolResult
from mcp.types import TextContent

from unraid_mcp.core.response_limit import StructuredResponseLimitingMiddleware


@dataclass
class _StubMessage:
    name: str = "unraid"


@dataclass
class _StubContext:
    message: _StubMessage


def _text_result(text: str) -> ToolResult:
    return ToolResult(content=[TextContent(type="text", text=text)])


def _call_next_returning(result: ToolResult):
    async def _call_next(_context):
        return result

    return _call_next


def _context(name: str = "unraid") -> _StubContext:
    return _StubContext(message=_StubMessage(name=name))


async def test_small_response_passes_through_unchanged():
    """A response under the cap is returned untouched."""
    mw = StructuredResponseLimitingMiddleware(max_size=131072)
    original = _text_result(json.dumps({"ok": True, "data": [1, 2, 3]}))

    out = await mw.on_call_tool(_context(), _call_next_returning(original))

    assert out is original
    block = out.content[0]
    assert isinstance(block, TextContent)
    assert json.loads(block.text) == {"ok": True, "data": [1, 2, 3]}


async def test_oversized_response_replaced_with_structured_marker():
    """An oversized response becomes a complete, parseable JSON marker."""
    cap = 2_000
    mw = StructuredResponseLimitingMiddleware(max_size=cap)
    # Build a large valid-JSON payload well over the cap.
    payload = json.dumps({"items": ["x" * 100 for _ in range(200)]})
    assert len(payload.encode("utf-8")) > cap
    original = _text_result(payload)

    out = await mw.on_call_tool(_context(), _call_next_returning(original))

    assert out is not original
    assert len(out.content) == 1
    block = out.content[0]
    assert isinstance(block, TextContent)

    # The replacement must be COMPLETE, valid JSON — not a mid-string byte cut.
    marker = json.loads(block.text)
    assert marker["error"] == "response_truncated"
    assert marker["truncated"] is True
    assert marker["limit_bytes"] == cap
    assert marker["original_bytes"] > cap
    assert marker.get("hint")
    # The marker must NOT contain a salvaged slice of the original payload.
    assert "xxxxxxxxxx" not in block.text


async def test_marker_text_is_smaller_than_limit():
    """The marker itself stays comfortably under the cap."""
    cap = 1_000
    mw = StructuredResponseLimitingMiddleware(max_size=cap)
    original = _text_result("y" * 5_000)

    out = await mw.on_call_tool(_context(), _call_next_returning(original))

    block = out.content[0]
    assert isinstance(block, TextContent)
    assert len(block.text.encode("utf-8")) < cap


async def test_other_tools_skipped_when_tools_filter_set():
    """When a tools allowlist is set, non-listed tools are not limited."""
    mw = StructuredResponseLimitingMiddleware(max_size=10, tools=["unraid"])
    original = _text_result("z" * 5_000)

    out = await mw.on_call_tool(_context(name="other_tool"), _call_next_returning(original))

    assert out is original


def test_non_positive_max_size_rejected():
    with pytest.raises(ValueError):
        StructuredResponseLimitingMiddleware(max_size=0)
