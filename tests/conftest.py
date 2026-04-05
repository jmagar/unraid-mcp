"""Shared test fixtures and helpers for Unraid MCP server tests."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP
from hypothesis import settings
from hypothesis.database import DirectoryBasedExampleDatabase


# Configure hypothesis to use the .cache directory for its database
settings.register_profile("default", database=DirectoryBasedExampleDatabase(".cache/.hypothesis"))
settings.load_profile("default")


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
    this avoids reliance on FastMCP's internal tool storage API in every
    test file.

    FastMCP 3.x removed `_tool_manager._tools`; use `await mcp.get_tool()`
    instead. We run a small event loop here to keep the helper synchronous
    so callers don't need to change.

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
    # FastMCP 3.x stores tools in providers[0]._components keyed as "tool:{name}@"
    # (the "@" suffix is the version separator with no version set).
    local_provider = test_mcp.providers[0]
    tool = local_provider._components[f"tool:{tool_name}@"]
    return tool.fn
