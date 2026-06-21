"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import ipaddress
import os
import secrets
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal, cast

from dotenv import set_key
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from starlette.middleware import Middleware as ASGIMiddleware

from .config import settings as _settings
from .config.logging import log_configuration_status, logger
from .config.settings import (
    CREDENTIALS_DIR,
    CREDENTIALS_ENV_PATH,
    LOG_LEVEL_STR,
    UNRAID_MCP_HOST,
    UNRAID_MCP_MAX_RESPONSE_BYTES,
    UNRAID_MCP_PORT,
    UNRAID_VERIFY_SSL,
    VERSION,
    apply_bearer_token,
    validate_required_config,
)
from .core import middleware_refs as _middleware_refs
from .core.auth import BearerAuthMiddleware, HealthMiddleware, WellKnownMiddleware
from .core.client import close_http_client
from .core.response_limit import StructuredResponseLimitingMiddleware
from .subscriptions.manager import subscription_manager
from .subscriptions.resources import register_subscription_resources
from .tools.unraid import register_unraid_tool


_LOOPBACK_HOSTNAMES = frozenset({"localhost"})


def _is_loopback_host(host: str) -> bool:
    """Return True if *host* binds only a loopback interface.

    Loopback binds (``127.0.0.0/8``, ``::1``, ``localhost``) keep an
    unauthenticated endpoint off the network. Bind-all addresses
    (``0.0.0.0``, ``::``), LAN IPs, and non-localhost hostnames are treated as
    non-loopback (fail closed — unknown names could resolve anywhere). Used by
    the startup guard for finding S-H3.
    """
    h = host.strip().lower().strip("[]")
    if not h:
        return False
    if h in _LOOPBACK_HOSTNAMES:
        return True
    try:
        addr = ipaddress.ip_address(h)
    except ValueError:
        return False
    if addr.is_loopback:
        return True
    mapped = getattr(addr, "ipv4_mapped", None)
    return bool(mapped is not None and mapped.is_loopback)


def _chmod_safe(path: object, mode: int, *, strict: bool = False) -> None:
    """Best-effort chmod, with optional fail-closed behavior for secrets."""
    try:
        path.chmod(mode)  # type: ignore[union-attr]
    except PermissionError as exc:
        if strict:
            raise RuntimeError(f"Failed to secure permissions on {path}") from exc
        logger.debug("Could not chmod %s (volume mount?) — skipping", path)


# Middleware chain order matters — each layer wraps everything inside it:
#   logging → error_handling → rate_limiter → response_limiter → tool

# 1. Log every tools/call and resources/read: method, duration, errors.
#    Outermost so it captures errors after they've been converted by error_handling.
_logging_middleware = LoggingMiddleware(
    logger=logger,
    methods=["tools/call", "resources/read"],
)

# 2. Catch any unhandled exceptions and convert to proper MCP errors.
#    Tracks error_counts per (exception_type:method) for health diagnose.
_error_middleware = ErrorHandlingMiddleware(
    logger=logger,
    include_traceback=LOG_LEVEL_STR == "DEBUG",
)
# Expose via neutral module to break the circular import between server.py
# (which imports tools/unraid.py) and health/diagnose (which needs error stats).
# tools/unraid.py imports middleware_refs, not server, avoiding the cycle.
_middleware_refs.error_middleware = _error_middleware

# 3. Inbound-abuse / DoS guard: 540 requests per 60-second sliding window.
#    This is NOT the authoritative upstream rate limiter. SlidingWindowRateLimitingMiddleware
#    only supports window_minutes (int) granularity, so it cannot bound the upstream
#    Unraid "100 req/10 s" burst limit — a client can still send up to 540 requests in
#    the first 10 s of a window, far exceeding what Unraid accepts. Its only job here is
#    to cap sustained inbound request volume so a misbehaving or hostile client cannot
#    flood this server.
#    The AUTHORITATIVE upstream limiter is the client-side token bucket (`_RateLimiter`
#    in core/client.py): 90 tokens at 9.0 tokens/sec models Unraid's 100 req/10 s with
#    10% headroom and is what actually prevents the Unraid API from being overrun.
_rate_limiter = SlidingWindowRateLimitingMiddleware(max_requests=540, window_minutes=1)

# 4. Cap tool responses (default 40 KB / ~10K tokens, override via UNRAID_MCP_MAX_RESPONSE_BYTES)
#    to protect the client context window. Unlike fastmcp's stock limiter — which
#    hard-cuts the UTF-8 byte string mid-JSON and appends a plain-text suffix,
#    yielding invalid JSON — oversized responses are replaced wholesale with a
#    complete, parseable JSON marker ({"error": "response_truncated", ...}) that
#    signals the agent to narrow its query. See core/response_limit.py.
_response_limiter = StructuredResponseLimitingMiddleware(max_size=UNRAID_MCP_MAX_RESPONSE_BYTES)

# Note: there is no response/query caching anywhere in this server. The only thing
# ever removed was FastMCP's ResponseCachingMiddleware: the consolidated `unraid`
# tool mixes reads and mutations under one name, making per-subaction cache
# exclusion impossible, so a fully disabled middleware added overhead with no
# benefit. Caching can be re-added if/when the tool is split into separate
# read/write tools.


@asynccontextmanager
async def lifespan(_server: "FastMCP") -> AsyncIterator[None]:
    """Server lifespan: run shutdown cleanup inside the server's own event loop.

    FastMCP enters this context manager on startup (before the transport begins
    serving) and exits it on shutdown — on every transport and every exit path,
    including a normal ``mcp.run()`` return and SIGTERM (the container stop
    signal). Putting teardown here guarantees WebSocket subscription tasks and the
    shared httpx connection pool are released in the SAME loop that created them,
    instead of the old ``asyncio.run(...)``-in-a-fresh-loop dance in ``main.py``
    that swallowed "event loop is closed" errors and never ran on SIGTERM.

    Startup work (subscription auto-start) is unchanged: it is triggered lazily on
    the first resource read via ``ensure_subscriptions_started()`` in
    ``subscriptions/resources.py`` — nothing to do here on the startup side.
    """
    try:
        yield
    finally:
        try:
            await subscription_manager.stop_all()
        except Exception:
            logger.error("Error stopping subscriptions during shutdown", exc_info=True)
        try:
            await close_http_client()
        except Exception:
            logger.error("Error closing HTTP client during shutdown", exc_info=True)


# Initialize FastMCP instance — ASGI-level bearer auth added at run time via
# mcp.run(middleware=[...]) so it fires before any MCP protocol processing.
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=VERSION,
    lifespan=lifespan,
    middleware=[
        _logging_middleware,
        _error_middleware,
        _rate_limiter,
        _response_limiter,
    ],
)

# Note: SubscriptionManager singleton is defined in subscriptions/manager.py
# and imported by resources.py - no duplicate instance needed here

# Register all modules at import time so `fastmcp run server.py --reload` can
# discover the fully-configured `mcp` object without going through run_server().
# run_server() no longer calls this — tools are registered exactly once here.


def register_all_modules() -> None:
    """Register all tools and resources with the MCP instance."""
    try:
        # Register subscription resources (live data caches). The subscription
        # diagnostics are exposed through the consolidated `unraid` tool's
        # `subscriptions` action, not as standalone tools.
        register_subscription_resources(mcp)
        logger.info("Subscription resources registered")

        # Register the consolidated unraid tool
        register_unraid_tool(mcp)
        logger.info("unraid tool registered successfully - Server ready!")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise


register_all_modules()


def ensure_token_exists() -> None:
    """Auto-generate a bearer token on first HTTP startup if none is configured.

    Writes the token to ``~/.unraid-mcp/.env`` via ``dotenv.set_key`` (in-place,
    preserves existing comments and key order), then applies it to the module
    global via ``apply_bearer_token()`` and removes it from ``os.environ`` so it
    is no longer readable by subprocess spawns.

    No-op when:
    - ``UNRAID_MCP_BEARER_TOKEN`` is already set (token was loaded at startup).
    - ``UNRAID_MCP_DISABLE_HTTP_AUTH=true`` (gateway-delegated auth).
    """
    if _settings.UNRAID_MCP_BEARER_TOKEN or _settings.UNRAID_MCP_DISABLE_HTTP_AUTH:
        return

    token = secrets.token_urlsafe(32)

    # Ensure credentials dir exists with restricted permissions.
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    _chmod_safe(CREDENTIALS_DIR, 0o700, strict=True)

    # Touch the file and restrict permissions BEFORE writing the token.
    # This closes the window where the file has default umask permissions.
    if not CREDENTIALS_ENV_PATH.exists():
        CREDENTIALS_ENV_PATH.touch(mode=0o600)
    _chmod_safe(CREDENTIALS_ENV_PATH, 0o600, strict=True)

    # In-place .env write — preserves comments and existing keys.
    # File is already 0o600 so the token is never world-readable.
    set_key(str(CREDENTIALS_ENV_PATH), "UNRAID_MCP_BEARER_TOKEN", token, quote_mode="auto")

    print(
        f"\n[unraid-mcp] Generated HTTP bearer token and saved it to {CREDENTIALS_ENV_PATH}.\n"
        "Configure your MCP client to send Authorization: Bearer <token> using that stored value.\n",
        file=sys.stderr,
        flush=True,
    )

    # Store in module global; pop from os.environ so subprocesses cannot inherit it
    apply_bearer_token(token)
    os.environ.pop("UNRAID_MCP_BEARER_TOKEN", None)

    logger.info("Bearer token generated and written to %s", CREDENTIALS_ENV_PATH)


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    is_http = _settings.UNRAID_MCP_TRANSPORT in ("streamable-http", "sse")

    try:
        if is_http:
            ensure_token_exists()

        if (
            is_http
            and not _settings.UNRAID_MCP_DISABLE_HTTP_AUTH
            and not _settings.UNRAID_MCP_BEARER_TOKEN
        ):
            print(
                "FATAL: HTTP transport requires a bearer token. "
                "Set UNRAID_MCP_BEARER_TOKEN in ~/.unraid-mcp/.env or restart to auto-generate.",
                file=sys.stderr,
            )
            sys.exit(1)

        # S-H3: disabling auth is only safe behind a trusted gateway or on
        # loopback. Refuse to expose an unauthenticated MCP endpoint on a
        # public/LAN interface — that would let anyone on the network drive the
        # Unraid API. Operators fronting the server with SWAG/Authelia opt in
        # via UNRAID_MCP_TRUST_PROXY=true.
        if (
            is_http
            and _settings.UNRAID_MCP_DISABLE_HTTP_AUTH
            and not _settings.UNRAID_MCP_TRUST_PROXY
            and not _is_loopback_host(_settings.UNRAID_MCP_HOST)
        ):
            print(
                "FATAL: UNRAID_MCP_DISABLE_HTTP_AUTH=true with a non-loopback bind host "
                f"({_settings.UNRAID_MCP_HOST}) would expose an unauthenticated MCP endpoint "
                "on the network. Refusing to start. Either bind to 127.0.0.1, re-enable "
                "bearer-token auth, or set UNRAID_MCP_TRUST_PROXY=true if an upstream gateway "
                "enforces authentication.",
                file=sys.stderr,
            )
            sys.exit(1)

        is_valid, missing = validate_required_config()
        if not is_valid:
            logger.warning(
                "Missing configuration: %s. Set the plugin's userConfig fields "
                "(or UNRAID_API_URL / UNRAID_API_KEY in ~/.unraid-mcp/.env), then restart. "
                "Tools will return a setup message until configured.",
                ", ".join(missing),
            )

        log_configuration_status(logger)

        if UNRAID_VERIFY_SSL is False:
            logger.warning(
                "SSL VERIFICATION DISABLED (UNRAID_VERIFY_SSL=false, "
                "UNRAID_ALLOW_INSECURE_TLS=true). Connections to the Unraid API are "
                "vulnerable to man-in-the-middle attacks. The API key is sent to an "
                "unverified peer over BOTH the HTTP GraphQL client AND the WebSocket "
                "subscription connection, so a MITM can capture it. Prefer a CA-bundle "
                "path for self-signed certs. Only use this in trusted networks or for "
                "development."
            )

        if is_http:
            if _settings.UNRAID_MCP_DISABLE_HTTP_AUTH:
                logger.warning(
                    "HTTP auth disabled (UNRAID_MCP_DISABLE_HTTP_AUTH=true). "
                    "Ensure an upstream gateway enforces authentication."
                )
            else:
                logger.info("HTTP bearer token authentication enabled.")

        if is_http:
            logger.info(
                "Starting Unraid MCP Server on %s:%s using %s transport...",
                UNRAID_MCP_HOST,
                UNRAID_MCP_PORT,
                _settings.UNRAID_MCP_TRANSPORT,
            )
        else:
            logger.info("Starting Unraid MCP Server using stdio transport...")

        if is_http:
            if _settings.UNRAID_MCP_TRANSPORT == "sse":
                logger.warning(
                    "SSE transport is deprecated. Consider switching to 'streamable-http'."
                )
            # ASGI-level bearer auth wraps the entire HTTP stack — fires before any
            # MCP protocol processing and before the MCP-level middleware chain.
            transport_literal = cast(
                "Literal['stdio', 'http', 'sse', 'streamable-http']",
                _settings.UNRAID_MCP_TRANSPORT,
            )
            mcp.run(
                transport=transport_literal,
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",
                middleware=[
                    # Middleware order (outermost → innermost):
                    # 1. HealthMiddleware   — GET /health → 200, no auth.
                    # 2. WellKnownMiddleware — GET /.well-known/oauth-protected-resource → 200,
                    #    no auth.  MCP clients probe this after a 401 to discover how to
                    #    authenticate; responding correctly stops the 401 cascade.
                    # 3. BearerAuthMiddleware — all other HTTP requests require a valid token.
                    ASGIMiddleware(HealthMiddleware),  # type: ignore
                    ASGIMiddleware(WellKnownMiddleware),  # type: ignore
                    ASGIMiddleware(
                        BearerAuthMiddleware,  # type: ignore
                        token=_settings.UNRAID_MCP_BEARER_TOKEN or "",
                        disabled=_settings.UNRAID_MCP_DISABLE_HTTP_AUTH,
                    ),
                ],
            )
        elif _settings.UNRAID_MCP_TRANSPORT == "stdio":
            mcp.run()
        else:
            logger.error(
                f"Unsupported MCP_TRANSPORT: {_settings.UNRAID_MCP_TRANSPORT}. "
                "Choose 'streamable-http', 'sse', or 'stdio'."
            )
            sys.exit(1)
    except Exception as e:
        logger.critical("Unraid MCP server crashed: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Unraid MCP server stopped")


if __name__ == "__main__":
    run_server()
