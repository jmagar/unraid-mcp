"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import sys
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

from .config.logging import logger
from .config.settings import (
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
    UNRAID_VERIFY_SSL,
    VERSION,
    validate_required_config,
)
from .subscriptions.diagnostics import register_diagnostic_tools
from .subscriptions.resources import register_subscription_resources
from .tools.unraid import register_unraid_tool


# Middleware chain order matters — each layer wraps everything inside it:
#   logging → error_handling → rate_limiter → response_limiter → cache → tool

# 1. Log every tools/call and resources/read: method, duration, errors.
#    Outermost so it captures errors after they've been converted by error_handling.
_logging_middleware = LoggingMiddleware(
    logger=logger,
    methods=["tools/call", "resources/read"],
)

# 2. Catch any unhandled exceptions and convert to proper MCP errors.
#    Tracks error_counts per (exception_type:method) for health diagnose.
error_middleware = ErrorHandlingMiddleware(
    logger=logger,
    include_traceback=True,
)

# 3. Unraid API rate limit: 100 requests per 10 seconds.
#    Use a sliding window that stays comfortably under that cap.
_rate_limiter = SlidingWindowRateLimitingMiddleware(max_requests=90, window_minutes=1)

# 4. Cap tool responses at 512 KB to protect the client context window.
#    Oversized responses are truncated with a clear suffix rather than erroring.
_response_limiter = ResponseLimitingMiddleware(max_size=512_000)

# 5. Cache tool calls in-memory (MemoryStore default — no extra deps).
#    Short 30 s TTL absorbs burst duplicate requests while keeping data fresh.
#    Destructive calls won't hit the cache in practice (unique confirm=True + IDs).
cache_middleware = ResponseCachingMiddleware(
    call_tool_settings=CallToolSettings(
        ttl=30,
        included_tools=["unraid"],
    ),
    # Disable caching for list/resource/prompt — those are cheap.
    list_tools_settings={"enabled": False},
    list_resources_settings={"enabled": False},
    list_prompts_settings={"enabled": False},
    read_resource_settings={"enabled": False},
    get_prompt_settings={"enabled": False},
)


def _build_google_auth() -> "GoogleProvider | None":
    """Build GoogleProvider when OAuth env vars are configured, else return None.

    Returns None (no auth) when GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET are absent,
    preserving backward compatibility for existing unprotected setups.
    """
    from .config.settings import (
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        UNRAID_MCP_BASE_URL,
        UNRAID_MCP_JWT_SIGNING_KEY,
        UNRAID_MCP_TRANSPORT,
        is_google_auth_configured,
    )

    if not is_google_auth_configured():
        return None

    if UNRAID_MCP_TRANSPORT == "stdio":
        logger.warning(
            "Google OAuth is configured but UNRAID_MCP_TRANSPORT=stdio. "
            "OAuth requires HTTP transport (streamable-http or sse). "
            "Auth will be applied but may not work as expected."
        )

    kwargs: dict[str, Any] = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "base_url": UNRAID_MCP_BASE_URL,
    }
    if UNRAID_MCP_JWT_SIGNING_KEY:
        kwargs["jwt_signing_key"] = UNRAID_MCP_JWT_SIGNING_KEY
    else:
        logger.warning(
            "UNRAID_MCP_JWT_SIGNING_KEY is not set. FastMCP will derive a key automatically, "
            "but tokens may be invalidated on server restart. "
            "Set UNRAID_MCP_JWT_SIGNING_KEY to a stable secret."
        )

    logger.info(
        f"Google OAuth enabled — base_url={UNRAID_MCP_BASE_URL}, "
        f"redirect_uri={UNRAID_MCP_BASE_URL}/auth/callback"
    )
    return GoogleProvider(**kwargs)


# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=VERSION,
    middleware=[
        _logging_middleware,
        error_middleware,
        _rate_limiter,
        _response_limiter,
        cache_middleware,
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


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    # Validate required configuration before anything else
    is_valid, missing = validate_required_config()
    if not is_valid:
        logger.warning(
            f"Missing configuration: {', '.join(missing)}. "
            "Server will prompt for credentials on first tool call via elicitation."
        )

    # Log configuration (delegated to shared function)
    from .config.logging import log_configuration_status

    log_configuration_status(logger)

    if UNRAID_VERIFY_SSL is False:
        logger.warning(
            "SSL VERIFICATION DISABLED (UNRAID_VERIFY_SSL=false). "
            "Connections to Unraid API are vulnerable to man-in-the-middle attacks. "
            "Only use this in trusted networks or for development."
        )

    logger.info(
        f"Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} using {UNRAID_MCP_TRANSPORT} transport..."
    )

    try:
        if UNRAID_MCP_TRANSPORT == "streamable-http":
            mcp.run(
                transport="streamable-http", host=UNRAID_MCP_HOST, port=UNRAID_MCP_PORT, path="/mcp"
            )
        elif UNRAID_MCP_TRANSPORT == "sse":
            logger.warning("SSE transport is deprecated. Consider switching to 'streamable-http'.")
            mcp.run(transport="sse", host=UNRAID_MCP_HOST, port=UNRAID_MCP_PORT, path="/mcp")
        elif UNRAID_MCP_TRANSPORT == "stdio":
            mcp.run()
        else:
            logger.error(
                f"Unsupported MCP_TRANSPORT: {UNRAID_MCP_TRANSPORT}. Choose 'streamable-http', 'sse', or 'stdio'."
            )
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to start Unraid MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_server()
