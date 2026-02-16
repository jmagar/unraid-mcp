"""Custom exceptions for Unraid MCP Server.

This module defines custom exception classes for consistent error handling
throughout the application, with proper integration to FastMCP's error system.
"""

from fastmcp.exceptions import ToolError as FastMCPToolError


class ToolError(FastMCPToolError):
    """User-facing error that MCP clients can handle.

    This is the main exception type used throughout the application for
    errors that should be presented to the user/LLM in a friendly way.

    Inherits from FastMCP's ToolError to ensure proper MCP protocol handling.
    """

    pass


class ConfigurationError(ToolError):
    """Raised when there are configuration-related errors."""

    pass


class UnraidAPIError(ToolError):
    """Raised when the Unraid API returns an error or is unreachable."""

    pass


class SubscriptionError(ToolError):
    """Raised when there are WebSocket subscription-related errors."""

    pass


class ValidationError(ToolError):
    """Raised when input validation fails."""

    pass


class IdempotentOperationError(ToolError):
    """Raised when an operation is idempotent (already in desired state).

    This is used internally to signal that an operation was already complete,
    which should typically be converted to a success response rather than
    propagated as an error to the user.
    """

    pass
