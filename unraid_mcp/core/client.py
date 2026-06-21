"""GraphQL client for Unraid API communication.

This module provides the HTTP client interface for making GraphQL requests
to the Unraid API with proper timeout handling and error management.
"""

import asyncio
import json
import re
import time
from typing import Any, Final

import httpx

from ..config.logging import logger
from ..config.settings import (
    TIMEOUT_CONFIG,
    UNRAID_VERIFY_SSL,
    VERSION,
)
from ..core.exceptions import CredentialsNotConfiguredError, ToolError
from .utils import safe_display_url


# Sensitive keys to redact from debug logs (frozenset — immutable, Final — no accidental reassignment)
# Exact-match keys: short words that over-redact when used as substrings
# (e.g. "key" would match "keyFile", "monkey", "turkey")
_EXACT_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset({"key", "pin"})
# Substring-match keys: compound terms safe for substring matching.
# (Normalization strips _ and - before matching, so "client_secret" and
# "clientsecret" both reduce to "clientsecret" — only one normalized form is needed.)
_SUBSTRING_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "password",
        "secret",
        "clientsecret",
        "token",
        "apikey",
        "authorization",
        "credential",
        "passphrase",
        "jwt",
        "cookie",
        "session",
        "activationcode",
        "privatekey",
    }
)

# Length floor for treating an unkeyed string as a possible secret. Short values
# (UUIDs aside) rarely carry meaningful entropy and over-redacting normal text is
# worse than missing a tiny token, so be conservative.
_MIN_SECRET_VALUE_LEN: Final[int] = 20

# JWT-shaped: three base64url segments separated by dots (header.payload.signature),
# conventionally starting with the "eyJ" base64 of a JSON "{" header.
_JWT_RE: Final[re.Pattern[str]] = re.compile(r"^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
# OpenAI-style "sk-"-prefixed secret tokens (and sk-proj-/sk-ant- variants).
_SK_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"^sk-[A-Za-z0-9_-]{16,}$")
# High-entropy opaque token: a single long run of token-charset characters with no
# whitespace. Requires a mix of letters and digits to avoid masking ordinary words.
_TOKEN_CHARSET_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_\-./+=]+$")


def _is_sensitive_key(key: str) -> bool:
    """Check if a key name is sensitive (exact match or substring match).

    Normalizes by stripping underscores/hyphens so "api_key_value" matches "apikey".
    """
    k = key.lower()
    k_normalized = k.replace("_", "").replace("-", "")
    return k in _EXACT_SENSITIVE_KEYS or any(s in k_normalized for s in _SUBSTRING_SENSITIVE_KEYS)


def _is_sensitive_value(value: str) -> bool:
    """Heuristically detect a secret-shaped string regardless of its key.

    Conservatively flags obvious secret tokens — JWTs (``eyJ...`` three-segment),
    ``sk-`` prefixed API keys, and very-long high-entropy opaque tokens — while
    leaving ordinary prose untouched. Intended only to redact debug-log values, so
    a missed exotic format is preferable to clobbering normal text.
    """
    if _JWT_RE.match(value) or _SK_TOKEN_RE.match(value):
        return True
    # High-entropy opaque token: long, token-charset only, with both letters and
    # digits (rules out ordinary words, paths, and pure-numeric IDs/timestamps).
    return bool(
        len(value) >= _MIN_SECRET_VALUE_LEN
        and _TOKEN_CHARSET_RE.match(value)
        and any(c.isalpha() for c in value)
        and any(c.isdigit() for c in value)
    )


def redact_sensitive(obj: Any) -> Any:
    """Recursively redact sensitive data from nested dicts/lists.

    Scans both *keys* and *values*: a value is masked when its key name looks
    sensitive (see ``_is_sensitive_key``) OR when the value itself is a
    secret-shaped string (JWT, ``sk-`` token, or high-entropy opaque token — see
    ``_is_sensitive_value``), so secrets are caught even under innocuous keys.
    Pure function — returns a redacted copy and never mutates ``obj``.
    """
    if isinstance(obj, dict):
        return {k: ("***" if _is_sensitive_key(k) else redact_sensitive(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_sensitive(item) for item in obj]
    if isinstance(obj, str) and _is_sensitive_value(obj):
        return "***"
    return obj


# HTTP timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=30.0, connect=5.0)
DISK_TIMEOUT = httpx.Timeout(10.0, read=TIMEOUT_CONFIG["disk_operations"], connect=5.0)

# Global connection pool (module-level singleton)
# Python 3.12+ asyncio.Lock() is safe at module level — no running event loop required
_http_client: httpx.AsyncClient | None = None
_client_lock: Final[asyncio.Lock] = asyncio.Lock()


class _RateLimiter:
    """Token bucket rate limiter for Unraid API (100 req / 10s hard limit).

    Uses 90 tokens with 9.0 tokens/sec refill for 10% safety headroom.
    """

    def __init__(self, max_tokens: int = 90, refill_rate: float = 9.0) -> None:
        self.max_tokens = max_tokens
        self.tokens = float(max_tokens)
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.monotonic()
        # asyncio.Lock() is safe to create at __init__ time (Python 3.12+)
        self._lock: Final[asyncio.Lock] = asyncio.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    async def acquire(self) -> None:
        """Consume one token, waiting if necessary for refill."""
        while True:
            async with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait_time = (1 - self.tokens) / self.refill_rate

            # Sleep outside the lock so other coroutines aren't blocked
            await asyncio.sleep(wait_time)


_rate_limiter = _RateLimiter()


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
    if operation == "start":
        return (
            "already started" in error_lower
            or "container already running" in error_lower
            or "http code 304" in error_lower
        )
    if operation == "stop":
        return (
            "already stopped" in error_lower
            or "container already stopped" in error_lower
            or "container not running" in error_lower
            or "http code 304" in error_lower
        )

    return False


async def _create_http_client() -> httpx.AsyncClient:
    """Create a new HTTP client instance with connection pooling.

    Returns:
        A new AsyncClient configured for Unraid API communication
    """
    return httpx.AsyncClient(
        # Connection pool settings
        limits=httpx.Limits(
            max_keepalive_connections=20, max_connections=20, keepalive_expiry=30.0
        ),
        # Default timeout (can be overridden per-request)
        timeout=DEFAULT_TIMEOUT,
        # SSL verification
        verify=UNRAID_VERIFY_SSL,
        # Connection pooling headers
        headers={"Connection": "keep-alive", "User-Agent": f"UnraidMCPServer/{VERSION}"},
    )


async def get_http_client() -> httpx.AsyncClient:
    """Get or create shared HTTP client with connection pooling.

    Uses double-checked locking: fast-path skips the lock when the client
    is already initialized, only acquiring it for initial creation or
    recovery after close.

    Returns:
        Singleton AsyncClient instance with connection pooling enabled
    """
    global _http_client

    # Fast-path: skip lock if client is already initialized and open
    client = _http_client
    if client is not None and not client.is_closed:
        return client

    # Slow-path: acquire lock for initialization
    async with _client_lock:
        if _http_client is None or _http_client.is_closed:
            _http_client = await _create_http_client()
            logger.info(
                "Created shared HTTP client with connection pooling (20 keepalive, 20 max connections)"
            )
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
    operation_context: dict[str, str] | None = None,
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
        CredentialsNotConfiguredError: When UNRAID_API_URL or UNRAID_API_KEY are absent at call time
        ToolError: For HTTP errors, network errors, or non-idempotent GraphQL errors
    """
    # Local import to read the current values — module-level names are captured at import time
    # and would not reflect a settings reload.
    from ..config import settings as _settings

    if not _settings.UNRAID_API_URL or not _settings.UNRAID_API_KEY:
        raise CredentialsNotConfiguredError()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": _settings.UNRAID_API_KEY,
    }

    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    logger.debug(f"Making GraphQL request to {safe_display_url(_settings.UNRAID_API_URL)}:")
    logger.debug(f"Query: {query[:200]}{'...' if len(query) > 200 else ''}")  # Log truncated query
    if variables:
        logger.debug(f"Variables: {redact_sensitive(variables)}")

    try:
        # Rate limit: consume a token before making the request
        await _rate_limiter.acquire()

        # Get the shared HTTP client with connection pooling
        client = await get_http_client()

        # Retry loop for 429 rate limit responses
        post_kwargs: dict[str, Any] = {"json": payload, "headers": headers}
        if custom_timeout is not None:
            post_kwargs["timeout"] = custom_timeout

        response: httpx.Response | None = None
        for attempt in range(3):
            response = await client.post(_settings.UNRAID_API_URL, **post_kwargs)
            if response.status_code == 429:
                backoff = 2**attempt
                logger.warning(
                    f"Rate limited (429) by Unraid API, retrying in {backoff}s (attempt {attempt + 1}/3)"
                )
                await asyncio.sleep(backoff)
                continue
            break

        if response is None:  # pragma: no cover — guaranteed by loop
            raise ToolError("No response received after retry attempts")

        # Provide a clear message when all retries are exhausted on 429
        if response.status_code == 429:
            logger.error("Rate limit (429) persisted after 3 retries — request aborted")
            raise ToolError(
                "Unraid API is rate limiting requests. Wait ~10 seconds before retrying."
            )

        response.raise_for_status()  # Raise an exception for HTTP error codes 4xx/5xx

        response_data = response.json()
        if response_data.get("errors"):
            error_details = "; ".join(
                [err.get("message", str(err)) for err in response_data["errors"]]
            )

            # Check if this is an idempotent error that should be treated as success
            if operation_context and operation_context.get("operation"):
                operation = operation_context["operation"]
                if is_idempotent_error(error_details, operation):
                    logger.warning(
                        f"Idempotent operation '{operation}' - treating as success: {error_details}"
                    )
                    # Return a success response with the current state information
                    return {
                        "idempotent_success": True,
                        "operation": operation,
                        "message": error_details,
                        "original_errors": response_data["errors"],
                    }

            logger.error(f"GraphQL API returned errors: {response_data['errors']}")
            # Use ToolError for GraphQL errors to provide better feedback to LLM
            raise ToolError(f"GraphQL API error: {error_details}")

        logger.debug("GraphQL request successful.")
        data = response_data.get("data", {})
        return data if isinstance(data, dict) else {}  # Ensure we return dict

    except httpx.HTTPStatusError as e:
        # Log full details internally; only expose status code to MCP client
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise ToolError(
            f"Unraid API returned HTTP {e.response.status_code}. Check server logs for details."
        ) from e
    except httpx.RequestError as e:
        # Log full error internally; give safe summary to MCP client
        logger.error(f"Request error occurred: {e}")
        raise ToolError(f"Network error connecting to Unraid API: {type(e).__name__}") from e
    except json.JSONDecodeError as e:
        # Log full decode error; give safe summary to MCP client
        logger.error(f"Failed to decode JSON response: {e}")
        raise ToolError("Unraid API returned an invalid response (not valid JSON)") from e
