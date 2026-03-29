"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import sys

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

from .config.logging import log_configuration_status, logger
from .config.settings import (
    LOG_LEVEL_STR,
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


# Initialize FastMCP instance — no built-in auth.
# Authentication is delegated to an external OAuth gateway (nginx, Caddy,
# Authelia, Authentik, etc.) placed in front of this server.
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


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    # Validate required configuration before anything else
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

    if UNRAID_MCP_TRANSPORT in ("streamable-http", "sse"):
        logger.warning(
            "⚠️  NO AUTHENTICATION — HTTP server is open to all clients on the network. "
            "Protect this server with an external OAuth gateway (nginx, Caddy, Authelia, Authentik) "
            "or restrict access at the network layer (firewall, VPN, Tailscale)."
        )

    logger.info(
        f"Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} using {UNRAID_MCP_TRANSPORT} transport..."
    )

    try:
        if UNRAID_MCP_TRANSPORT in ("streamable-http", "sse"):
            if UNRAID_MCP_TRANSPORT == "sse":
                logger.warning(
                    "SSE transport is deprecated. Consider switching to 'streamable-http'."
                )
            mcp.run(
                transport=UNRAID_MCP_TRANSPORT,
                host=UNRAID_MCP_HOST,
                port=UNRAID_MCP_PORT,
                path="/mcp",
            )
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
