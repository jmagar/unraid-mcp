"""GraphQL client for Unraid API communication.

This module provides the HTTP client interface for making GraphQL requests
to the Unraid API with proper timeout handling and error management.
"""

import asyncio
import hashlib
import json
import time
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
_SENSITIVE_KEYS = {
    "password",
    "key",
    "secret",
    "token",
    "apikey",
    "authorization",
    "cookie",
    "session",
    "credential",
    "passphrase",
    "jwt",
}


def _is_sensitive_key(key: str) -> bool:
    """Check if a key name contains any sensitive substring."""
    key_lower = key.lower()
    return any(s in key_lower for s in _SENSITIVE_KEYS)


def _redact_sensitive(obj: Any) -> Any:
    """Recursively redact sensitive values from nested dicts/lists."""
    if isinstance(obj, dict):
        return {
            k: ("***" if _is_sensitive_key(k) else _redact_sensitive(v)) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact_sensitive(item) for item in obj]
    return obj


# HTTP timeout configuration
DEFAULT_TIMEOUT = httpx.Timeout(10.0, read=30.0, connect=5.0)
DISK_TIMEOUT = httpx.Timeout(10.0, read=TIMEOUT_CONFIG["disk_operations"], connect=5.0)

# Named timeout profiles
_TIMEOUT_PROFILES: dict[str, httpx.Timeout] = {
    "default": DEFAULT_TIMEOUT,
    "disk_operations": DISK_TIMEOUT,
}


def get_timeout_for_operation(profile: str) -> httpx.Timeout:
    """Get a timeout configuration by profile name.

    Args:
        profile: Timeout profile name (e.g., "default", "disk_operations")

    Returns:
        The matching httpx.Timeout, falling back to DEFAULT_TIMEOUT for unknown profiles
    """
    return _TIMEOUT_PROFILES.get(profile, DEFAULT_TIMEOUT)


# Global connection pool (module-level singleton)
_http_client: httpx.AsyncClient | None = None
_client_lock: asyncio.Lock | None = None


def _get_client_lock() -> asyncio.Lock:
    """Get or create the client lock (lazy init to avoid event loop issues)."""
    global _client_lock
    if _client_lock is None:
        _client_lock = asyncio.Lock()
    return _client_lock


class _RateLimiter:
    """Token bucket rate limiter for Unraid API (100 req / 10s hard limit).

    Uses 90 tokens with 9.0 tokens/sec refill for 10% safety headroom.
    """

    def __init__(self, max_tokens: int = 90, refill_rate: float = 9.0) -> None:
        self.max_tokens = max_tokens
        self.tokens = float(max_tokens)
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.monotonic()
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    async def acquire(self) -> None:
        """Consume one token, waiting if necessary for refill."""
        while True:
            async with self._get_lock():
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait_time = (1 - self.tokens) / self.refill_rate

            # Sleep outside the lock so other coroutines aren't blocked
            await asyncio.sleep(wait_time)


_rate_limiter = _RateLimiter()


# --- TTL Cache for stable read-only queries ---

# Queries whose results change infrequently and are safe to cache.
# Mutations and volatile queries (metrics, docker, array state) are excluded.
_CACHEABLE_QUERY_PREFIXES = frozenset(
    {
        "GetNetworkConfig",
        "GetRegistrationInfo",
        "GetOwner",
        "GetFlash",
    }
)

_CACHE_TTL_SECONDS = 60.0


class _QueryCache:
    """Simple TTL cache for GraphQL query responses.

    Keyed by a hash of (query, variables). Entries expire after _CACHE_TTL_SECONDS.
    Only caches responses for queries whose operation name is in _CACHEABLE_QUERY_PREFIXES.
    Mutation requests always bypass the cache.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, dict[str, Any]]] = {}

    @staticmethod
    def _cache_key(query: str, variables: dict[str, Any] | None) -> str:
        raw = query + json.dumps(variables or {}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def is_cacheable(query: str) -> bool:
        """Check if a query is eligible for caching based on its operation name."""
        if query.lstrip().startswith("mutation"):
            return False
        return any(prefix in query for prefix in _CACHEABLE_QUERY_PREFIXES)

    def get(self, query: str, variables: dict[str, Any] | None) -> dict[str, Any] | None:
        """Return cached result if present and not expired, else None."""
        key = self._cache_key(query, variables)
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, data = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return data

    def put(self, query: str, variables: dict[str, Any] | None, data: dict[str, Any]) -> None:
        """Store a query result with TTL expiry."""
        key = self._cache_key(query, variables)
        self._store[key] = (time.monotonic() + _CACHE_TTL_SECONDS, data)

    def invalidate_all(self) -> None:
        """Clear the entire cache (called after mutations)."""
        self._store.clear()


_query_cache = _QueryCache()


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
    async with _get_client_lock():
        if _http_client is None or _http_client.is_closed:
            _http_client = await _create_http_client()
            logger.info(
                "Created shared HTTP client with connection pooling (20 keepalive, 20 max connections)"
            )
        return _http_client


async def close_http_client() -> None:
    """Close the shared HTTP client (call on server shutdown)."""
    global _http_client

    async with _get_client_lock():
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
        ToolError: For HTTP errors, network errors, or non-idempotent GraphQL errors
    """
    if not UNRAID_API_URL:
        raise ToolError("UNRAID_API_URL not configured")

    if not UNRAID_API_KEY:
        raise ToolError("UNRAID_API_KEY not configured")

    # Check TTL cache for stable read-only queries
    is_mutation = query.lstrip().startswith("mutation")
    if not is_mutation and _query_cache.is_cacheable(query):
        cached = _query_cache.get(query, variables)
        if cached is not None:
            logger.debug("Returning cached response for query")
            return cached

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": UNRAID_API_KEY,
    }

    payload: dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    logger.debug(f"Making GraphQL request to {UNRAID_API_URL}:")
    logger.debug(f"Query: {query[:200]}{'...' if len(query) > 200 else ''}")  # Log truncated query
    if variables:
        logger.debug(f"Variables: {_redact_sensitive(variables)}")

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
            response = await client.post(UNRAID_API_URL, **post_kwargs)
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
        result = data if isinstance(data, dict) else {}  # Ensure we return dict

        # Invalidate cache on mutations; cache eligible query results
        if is_mutation:
            _query_cache.invalidate_all()
        elif _query_cache.is_cacheable(query):
            _query_cache.put(query, variables, result)

        return result

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
