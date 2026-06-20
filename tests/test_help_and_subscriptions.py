"""Tests for the consolidated `unraid` tool's `help` and `subscriptions` actions.

These actions replaced the former standalone `unraid_help`, `diagnose_subscriptions`,
and `test_subscription_query` tools. They lock in the post-consolidation contract:
routing, the `subscription_query` requirement, and subaction validation.
"""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.unraid import _HELP_TEXT


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


class TestHelpAction:
    async def test_help_returns_markdown_reference(self) -> None:
        tool_fn = _make_tool()
        # `help` takes no subaction — the default empty subaction must be accepted.
        result = await tool_fn(action="help")
        assert result == _HELP_TEXT

    async def test_help_doc_mentions_new_actions(self) -> None:
        tool_fn = _make_tool()
        result = await tool_fn(action="help")
        assert isinstance(result, str)
        assert "# Unraid MCP Server" in result
        # The folded actions must be documented in the reference.
        assert "subscriptions" in result
        assert "test_query" in result

    async def test_help_ignores_subaction(self) -> None:
        tool_fn = _make_tool()
        # An incidental subaction must not break `help`.
        result = await tool_fn(action="help", subaction="anything")
        assert result == _HELP_TEXT


class TestSubscriptionsAction:
    async def test_diagnose_routes_to_handler(self) -> None:
        tool_fn = _make_tool()
        sentinel = {"ok": True, "subscriptions": {}}
        with patch(
            "unraid_mcp.subscriptions.diagnostics.diagnose_subscriptions",
            new_callable=AsyncMock,
            return_value=sentinel,
        ) as mock_diag:
            result = await tool_fn(action="subscriptions", subaction="diagnose")
        assert result is sentinel
        mock_diag.assert_awaited_once_with()

    async def test_test_query_routes_with_query(self) -> None:
        tool_fn = _make_tool()
        query = "subscription { cpu { used idle system } }"
        sentinel = {"success": True}
        with patch(
            "unraid_mcp.subscriptions.diagnostics.test_subscription_query",
            new_callable=AsyncMock,
            return_value=sentinel,
        ) as mock_test:
            result = await tool_fn(
                action="subscriptions",
                subaction="test_query",
                subscription_query=query,
            )
        assert result is sentinel
        mock_test.assert_awaited_once_with(query)

    async def test_test_query_requires_subscription_query(self) -> None:
        tool_fn = _make_tool()
        # Guard fires before any WebSocket work, so no patching is needed.
        with pytest.raises(ToolError, match="subscription_query is required"):
            await tool_fn(action="subscriptions", subaction="test_query")

    async def test_invalid_subaction_rejected(self) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid subaction"):
            await tool_fn(action="subscriptions", subaction="bogus")
