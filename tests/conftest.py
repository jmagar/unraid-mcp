"""Shared test fixtures and helpers for Unraid MCP server tests."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mock_graphql_request() -> Generator[AsyncMock, None, None]:
    """Fixture that patches make_graphql_request at the core module.

    NOTE: Since each tool file imports make_graphql_request into its own
    namespace, tool-specific tests should patch at the tool module level
    (e.g., "unraid_mcp.tools.info.make_graphql_request") instead of using
    this fixture. This fixture is useful for testing the core client
    or for integration tests that reload modules.
    """
    with patch("unraid_mcp.core.client.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def make_tool_fn(
    module_path: str,
    register_fn_name: str,
    tool_name: str,
) -> Any:
    """Extract a tool function from a FastMCP registration for testing.

    This wraps the repeated pattern of creating a test FastMCP instance,
    registering a tool, and extracting the inner function. Centralizing
    this avoids reliance on FastMCP's private `_tool_manager._tools` API
    in every test file.

    Args:
        module_path: Dotted import path to the tool module (e.g., "unraid_mcp.tools.info")
        register_fn_name: Name of the registration function (e.g., "register_info_tool")
        tool_name: Name of the registered tool (e.g., "unraid_info")

    Returns:
        The async tool function callable
    """
    import importlib

    module = importlib.import_module(module_path)
    register_fn = getattr(module, register_fn_name)
    test_mcp = FastMCP("test")
    register_fn(test_mcp)
    return test_mcp._tool_manager._tools[tool_name].fn  # type: ignore[union-attr]
