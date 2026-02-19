"""Custom exceptions for Unraid MCP Server.

This module defines custom exception classes for consistent error handling
throughout the application, with proper integration to FastMCP's error system.
"""

import contextlib
import logging
from collections.abc import Iterator

from fastmcp.exceptions import ToolError as FastMCPToolError


class ToolError(FastMCPToolError):
    """User-facing error that MCP clients can handle.

    This is the main exception type used throughout the application for
    errors that should be presented to the user/LLM in a friendly way.

    Inherits from FastMCP's ToolError to ensure proper MCP protocol handling.
    """

    pass


@contextlib.contextmanager
def tool_error_handler(
    tool_name: str,
    action: str,
    logger: logging.Logger,
) -> Iterator[None]:
    """Context manager that standardizes tool error handling.

    Re-raises ToolError as-is. Gives TimeoutError a descriptive message.
    Catches all other exceptions, logs them with full traceback, and wraps them
    in ToolError with a descriptive message.

    Args:
        tool_name: The tool name for error messages (e.g., "docker", "vm").
        action: The current action being executed.
        logger: The logger instance to use for error logging.
    """
    try:
        yield
    except ToolError:
        raise
    except TimeoutError as e:
        logger.exception(f"Timeout in unraid_{tool_name} action={action}: request exceeded time limit")
        raise ToolError(
            f"Request timed out executing {tool_name}/{action}. The Unraid API did not respond in time."
        ) from e
    except Exception as e:
        logger.exception(f"Error in unraid_{tool_name} action={action}")
        raise ToolError(
            f"Failed to execute {tool_name}/{action}. Check server logs for details."
        ) from e
