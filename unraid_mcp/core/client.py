"""GraphQL client for Unraid API communication.

This module provides the HTTP client interface for making GraphQL requests
to the Unraid API with proper timeout handling and error management.
"""

import asyncio
import json
from typing import Any

import httpx

from ..config.logging import logger
from ..config.settings import (
    TIMEOUT_CONFIG,
    UNRAID_API_KEY,
    UNRAID_API_URL,
    UNRAID_VERIFY_SSL,
    VERSION,
)
from ..core.exceptions import ToolError

# Sensitive keys to redact from debug logs
_SENSITIVE_KEYS = {"password", "key", "secret", "token", "apikey"}


def _redact_sensitive(obj: Any) -> Any:
    """Recursively redact sensitive values from nested dicts/lists."""
    if isinstance(obj, dict):
        return {k: ("***" if k.lower() in _SENSITIVE_KEYS else _redact_sensitive(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact_sensitive(item) for item in obj]
    return obj


# HTTP timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=30.0, connect=5.0)
DISK_TIMEOUT = httpx.Timeout(10.0, read=TIMEOUT_CONFIG['disk_operations'], connect=5.0)

# Global connection pool (module-level singleton)
_http_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


def is_idempotent_error(error_message: str, operation: str) -> bool:
    """Check if a GraphQL error represents an idempotent operation that should be treated as success.

    Args:
        error_message: The error message from GraphQL API
        operation: The operation being performed (e.g., 'start', 'stop')

    Returns:
        True if this is an idempotent error that should be treated as success
    """
    error_lower = error_message.lower()

    # Docker container operation patterns
    if operation == 'start':
        return (
            'already started' in error_lower or
            'container already running' in error_lower or
            'http code 304' in error_lower
        )
    elif operation == 'stop':
        return (
            'already stopped' in error_lower or
            'container already stopped' in error_lower or
            'container not running' in error_lower or
            'http code 304' in error_lower
        )

    return False


async def get_http_client() -> httpx.AsyncClient:
    """Get or create shared HTTP client with connection pooling.

    Returns:
        Singleton AsyncClient instance with connection pooling enabled
    """
    global _http_client

    async with _client_lock:
        if _http_client is None or _http_client.is_closed:
            _http_client = httpx.AsyncClient(
                # Connection pool settings
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                ),
                # Default timeout (can be overridden per-request)
                timeout=DEFAULT_TIMEOUT,
                # SSL verification
                verify=UNRAID_VERIFY_SSL,
                # Connection pooling headers
                headers={
                    "Connection": "keep-alive",
                    "User-Agent": f"UnraidMCPServer/{VERSION}"
                }
            )
            logger.info("Created shared HTTP client with connection pooling (20 keepalive, 100 max connections)")

        return _http_client


async def close_http_client() -> None:
    """Close the shared HTTP client (call on server shutdown)."""
    global _http_client

    async with _client_lock:
        if _http_client is not None:
            await _http_client.aclose()
            _http_client = None
            logger.info("Closed shared HTTP client")


async def make_graphql_request(
    query: str,
    variables: dict[str, Any] | None = None,
    custom_timeout: httpx.Timeout | None = None,
    operation_context: dict[str, str] | None = None
) -> dict[str, Any]:
    """Make GraphQL requests to the Unraid API.

    Args:
        query: GraphQL query string
        variables: Optional query variables
        custom_timeout: Optional custom timeout configuration
        operation_context: Optional context for operation-specific error handling
                          Should contain 'operation' key (e.g., 'start', 'stop')

    Returns:
        Dict containing the GraphQL response data

    Raises:
        ToolError: For HTTP errors, network errors, or non-idempotent GraphQL errors
    """
    if not UNRAID_API_URL:
        raise ToolError("UNRAID_API_URL not configured")

    if not UNRAID_API_KEY:
        raise ToolError("UNRAID_API_KEY not configured")

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": UNRAID_API_KEY,
        "User-Agent": f"UnraidMCPServer/{VERSION}"  # Custom user-agent
    }

    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    logger.debug(f"Making GraphQL request to {UNRAID_API_URL}:")
    logger.debug(f"Query: {query[:200]}{'...' if len(query) > 200 else ''}")  # Log truncated query
    if variables:
        logger.debug(f"Variables: {_redact_sensitive(variables)}")

    try:
        # Get the shared HTTP client with connection pooling
        client = await get_http_client()

        # Override timeout if custom timeout specified
        if custom_timeout is not None:
            response = await client.post(
                UNRAID_API_URL,
                json=payload,
                headers=headers,
                timeout=custom_timeout
            )
        else:
            response = await client.post(UNRAID_API_URL, json=payload, headers=headers)

        response.raise_for_status()  # Raise an exception for HTTP error codes 4xx/5xx

        response_data = response.json()
        if "errors" in response_data and response_data["errors"]:
            error_details = "; ".join([err.get("message", str(err)) for err in response_data["errors"]])

            # Check if this is an idempotent error that should be treated as success
            if operation_context and operation_context.get('operation'):
                operation = operation_context['operation']
                if is_idempotent_error(error_details, operation):
                    logger.warning(f"Idempotent operation '{operation}' - treating as success: {error_details}")
                    # Return a success response with the current state information
                    return {
                        "idempotent_success": True,
                        "operation": operation,
                        "message": error_details,
                        "original_errors": response_data["errors"]
                    }

            logger.error(f"GraphQL API returned errors: {response_data['errors']}")
            # Use ToolError for GraphQL errors to provide better feedback to LLM
            raise ToolError(f"GraphQL API error: {error_details}")

        logger.debug("GraphQL request successful.")
        data = response_data.get("data", {})
        return data if isinstance(data, dict) else {}  # Ensure we return dict

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise ToolError(f"HTTP error {e.response.status_code}: {e.response.text}") from e
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise ToolError(f"Network connection error: {str(e)}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise ToolError(f"Invalid JSON response from Unraid API: {str(e)}") from e


def get_timeout_for_operation(operation_type: str = "default") -> httpx.Timeout:
    """Get appropriate timeout configuration for different operation types.

    Args:
        operation_type: Type of operation ('default', 'disk_operations')

    Returns:
        httpx.Timeout configuration appropriate for the operation
    """
    if operation_type == "disk_operations":
        return DISK_TIMEOUT
    else:
        return DEFAULT_TIMEOUT
