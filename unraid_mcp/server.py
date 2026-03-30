"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import os
import secrets
import sys
from typing import Literal

from dotenv import set_key
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware
from starlette.middleware import Middleware as ASGIMiddleware

from .config import settings as _settings
from .config.logging import log_configuration_status, logger
from .config.settings import (
    CREDENTIALS_DIR,
    CREDENTIALS_ENV_PATH,
    LOG_LEVEL_STR,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_VERIFY_SSL,
    VERSION,
    apply_bearer_token,
    validate_required_config,
)
from .core import middleware_refs as _middleware_refs
from .core.auth import BearerAuthMiddleware
from .subscriptions.diagnostics import register_diagnostic_tools
from .subscriptions.resources import register_subscription_resources
from .tools.unraid import register_unraid_tool


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

# 3. Rate limiting: 540 requests per 60-second sliding window.
#    SlidingWindowRateLimitingMiddleware only supports window_minutes (int), so the
#    upstream Unraid "100 req/10 s" burst limit cannot be enforced exactly here.
#    540 req/min is a conservative 1-minute equivalent that prevents sustained
#    overload while staying well under the 600 req/min ceiling.
#    Note: this does NOT cap bursts within a 10 s window; a client can still send
#    up to 540 requests in the first 10 s of a window. Add a sub-minute rate limiter
#    in front of this server (e.g. nginx limit_req) if tighter burst control is needed.
_rate_limiter = SlidingWindowRateLimitingMiddleware(max_requests=540, window_minutes=1)

# 4. Cap tool responses at 512 KB to protect the client context window.
#    Oversized responses are truncated with a clear suffix rather than erroring.
_response_limiter = ResponseLimitingMiddleware(max_size=512_000)

# Note: ResponseCachingMiddleware was removed because all caching was disabled for
# the `unraid` tool. The consolidated tool mixes reads and mutations under one name,
# making per-subaction cache exclusion impossible. A fully disabled middleware
# adds overhead with no benefit. Caching can be re-added if/when the tool is split
# into separate read/write tools.


# Initialize FastMCP instance — ASGI-level bearer auth added at run time via
# mcp.run(middleware=[...]) so it fires before any MCP protocol processing.
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=VERSION,
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
        # Register subscription resources and diagnostic tools
        register_subscription_resources(mcp)
        register_diagnostic_tools(mcp)
        logger.info("Subscription resources and diagnostic tools registered")

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

    # Ensure credentials dir exists with restricted permissions
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_DIR.chmod(0o700)

    # Touch the file first so set_key has a target (no-op if already exists)
    if not CREDENTIALS_ENV_PATH.exists():
        CREDENTIALS_ENV_PATH.touch()
        CREDENTIALS_ENV_PATH.chmod(0o600)

    # In-place .env write — preserves comments and existing keys
    set_key(str(CREDENTIALS_ENV_PATH), "UNRAID_MCP_BEARER_TOKEN", token, quote_mode="auto")
    CREDENTIALS_ENV_PATH.chmod(0o600)

    # Print once to STDERR so the user can copy it into their MCP client config
    print(
        f"\n[unraid-mcp] Generated HTTP bearer token (saved to {CREDENTIALS_ENV_PATH}):\n"
        f"  UNRAID_MCP_BEARER_TOKEN={token}\n"
        "  Add this to your MCP client's Authorization header: Bearer <token>\n",
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

    # Auto-generate token before the startup guard so a fresh install
    # can start without manual intervention.
    if is_http:
        ensure_token_exists()

    # Hard stop: HTTP mode with no token and auth not explicitly disabled.
    # We deliberately do NOT mention DISABLE_HTTP_AUTH in the error message to
    # avoid inadvertently guiding users toward disabling auth.
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

    # Validate Unraid API credentials
    is_valid, missing = validate_required_config()
    if not is_valid:
        logger.warning(
            f"Missing configuration: {', '.join(missing)}. "
            "Server will prompt for credentials on first tool call via elicitation."
        )

    log_configuration_status(logger)

    if UNRAID_VERIFY_SSL is False:
        logger.warning(
            "SSL VERIFICATION DISABLED (UNRAID_VERIFY_SSL=false). "
            "Connections to Unraid API are vulnerable to man-in-the-middle attacks. "
            "Only use this in trusted networks or for development."
        )

    if is_http:
        if _settings.UNRAID_MCP_DISABLE_HTTP_AUTH:
            logger.warning(
                "HTTP auth disabled (UNRAID_MCP_DISABLE_HTTP_AUTH=true). "
                "Ensure an upstream gateway enforces authentication."
            )
        else:
            logger.info("HTTP bearer token authentication enabled.")

    logger.info(
        f"Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} "
        f"using {_settings.UNRAID_MCP_TRANSPORT} transport..."
    )

    try:
        if is_http:
            if _settings.UNRAID_MCP_TRANSPORT == "sse":
                logger.warning(
                    "SSE transport is deprecated. Consider switching to 'streamable-http'."
                )
            # ASGI-level bearer auth wraps the entire HTTP stack — fires before any
            # MCP protocol processing and before the MCP-level middleware chain.
            transport_literal: Literal["stdio", "http", "sse", "streamable-http"] = (
                _settings.UNRAID_MCP_TRANSPORT  # type: ignore[assignment]
            )
            mcp.run(
                transport=transport_literal,
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",
                middleware=[
                    ASGIMiddleware(
                        BearerAuthMiddleware,
                        token=_settings.UNRAID_MCP_BEARER_TOKEN or "",
                        disabled=_settings.UNRAID_MCP_DISABLE_HTTP_AUTH,
                    )
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
        logger.critical(f"Failed to start Unraid MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
