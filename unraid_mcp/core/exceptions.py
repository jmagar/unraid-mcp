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


class CredentialsNotConfiguredError(Exception):
    """Raised when UNRAID_API_URL or UNRAID_API_KEY are not set.

    Used as a sentinel to trigger elicitation rather than a hard crash.
    """

    def __str__(self) -> str:
        return "Unraid credentials are not configured."


@contextlib.contextmanager
def tool_error_handler(
    tool_name: str,
    action: str,
    logger: logging.Logger,
) -> Iterator[None]:
    """Context manager that standardizes tool error handling.

    Re-raises ToolError as-is. Converts CredentialsNotConfiguredError to a ToolError
    with setup instructions including CREDENTIALS_ENV_PATH; does not log.
    Gives TimeoutError a descriptive message. Catches all other exceptions,
    logs them with full traceback, and wraps them in ToolError.

    Args:
        tool_name: The tool name for error messages (e.g., "docker", "vm").
        action: The current action being executed.
        logger: The logger instance to use for error logging.
    """
    try:
        yield
    except ToolError:
        raise
    except CredentialsNotConfiguredError as e:
        from ..config.settings import CREDENTIALS_ENV_PATH

        raise ToolError(
            f"Credentials not configured. Run unraid_health action=setup, "
            f"or create {CREDENTIALS_ENV_PATH} with UNRAID_API_URL and UNRAID_API_KEY "
            f"(cp .env.example {CREDENTIALS_ENV_PATH} to get started)."
        ) from e
    except TimeoutError as e:
        logger.exception(
            f"Timeout in unraid_{tool_name} action={action}: request exceeded time limit"
        )
        raise ToolError(
            f"Request timed out executing {tool_name}/{action}. The Unraid API did not respond in time."
        ) from e
    except Exception as e:
        logger.exception(f"Error in unraid_{tool_name} action={action}")
        raise ToolError(
            f"Failed to execute {tool_name}/{action}. Check server logs for details."
        ) from e
