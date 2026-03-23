"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import hmac
import sys
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, MultiAuth, TokenVerifier
from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.middleware.caching import CallToolSettings, ResponseCachingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware
from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

from .config.logging import logger
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
#   logging → error_handling → rate_limiter → response_limiter → cache → tool

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

# 3. Unraid API rate limit: 100 requests per 10 seconds.
#    SlidingWindowRateLimitingMiddleware only accepts window_minutes (int), so express
#    the 10-second budget as a 1-minute equivalent: 540 req/60 s to stay comfortably
#    under the 600 req/min ceiling.
_rate_limiter = SlidingWindowRateLimitingMiddleware(max_requests=540, window_minutes=1)

# 4. Cap tool responses at 512 KB to protect the client context window.
#    Oversized responses are truncated with a clear suffix rather than erroring.
_response_limiter = ResponseLimitingMiddleware(max_size=512_000)

# 5. Cache middleware — all call_tool caching is disabled for the `unraid` tool.
#    CallToolSettings supports excluded_tools/included_tools by tool name only; there
#    is no per-argument or per-subaction exclusion mechanism.  The cache key is
#    "{tool_name}:{arguments_str}", so a cached stop("nginx") result would be served
#    back on a retry within the TTL window even though the container is already stopped.
#    Mutation subactions (start, stop, restart, reboot, etc.) must never be cached.
#    Because the consolidated `unraid` tool mixes reads and mutations under one name,
#    the only safe option is to disable caching for the entire tool.
_cache_middleware = ResponseCachingMiddleware(
    call_tool_settings=CallToolSettings(
        enabled=False,
    ),
    # Disable caching for list/resource/prompt — those are cheap.
    list_tools_settings={"enabled": False},
    list_resources_settings={"enabled": False},
    list_prompts_settings={"enabled": False},
    read_resource_settings={"enabled": False},
    get_prompt_settings={"enabled": False},
)


class ApiKeyVerifier(TokenVerifier):
    """Bearer token verifier that validates against a static API key.

    Clients present the key as a standard OAuth bearer token:
        Authorization: Bearer <UNRAID_MCP_API_KEY>

    This allows machine-to-machine access (e.g. CI, scripts, other agents)
    without going through the Google OAuth browser flow.
    """

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self._api_key = api_key

    async def verify_token(self, token: str) -> AccessToken | None:
        if self._api_key and hmac.compare_digest(token.encode(), self._api_key.encode()):
            return AccessToken(
                token=token,
                client_id="api-key-client",
                scopes=[],
            )
        return None


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
        # Prefer short-lived access tokens without refresh-token rotation churn.
        # This reduces reconnect instability in MCP clients that re-auth frequently.
        "extra_authorize_params": {"access_type": "online", "prompt": "consent"},
        # Skip the FastMCP consent page — goes directly to Google.
        # The consent page has a CSRF double-load race: two concurrent GET requests
        # each regenerate the CSRF token, the second overwrites the first in the
        # transaction store, and the POST fails with "Invalid or expired consent token".
        "require_authorization_consent": False,
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


def _build_auth() -> "GoogleProvider | ApiKeyVerifier | MultiAuth | None":
    """Build the active auth stack from environment configuration.

    Returns:
        - MultiAuth(server=GoogleProvider, verifiers=[ApiKeyVerifier])
          when both GOOGLE_CLIENT_ID and UNRAID_MCP_API_KEY are set.
        - GoogleProvider alone when only Google OAuth vars are set.
        - ApiKeyVerifier alone when only UNRAID_MCP_API_KEY is set.
        - None when no auth vars are configured (open server).
    """
    from .config.settings import UNRAID_MCP_API_KEY, is_api_key_auth_configured

    google = _build_google_auth()
    api_key = ApiKeyVerifier(UNRAID_MCP_API_KEY) if is_api_key_auth_configured() else None

    if google and api_key:
        logger.info("Auth: Google OAuth + API key both enabled (MultiAuth)")
        return MultiAuth(server=google, verifiers=[api_key])
    if api_key:
        logger.info("Auth: API key authentication enabled")
        return api_key
    return google  # GoogleProvider or None


# Build auth stack — GoogleProvider, ApiKeyVerifier, MultiAuth, or None.
_auth = _build_auth()

# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=VERSION,
    auth=_auth,
    middleware=[
        _logging_middleware,
        _error_middleware,
        _rate_limiter,
        _response_limiter,
        _cache_middleware,
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

    if _auth is not None:
        from .config.settings import is_google_auth_configured

        if is_google_auth_configured():
            from .config.settings import UNRAID_MCP_BASE_URL

            logger.info(
                "Google OAuth ENABLED — clients must authenticate before calling tools. "
                f"Redirect URI: {UNRAID_MCP_BASE_URL}/auth/callback"
            )
        else:
            logger.info(
                "API key authentication ENABLED — present UNRAID_MCP_API_KEY as bearer token."
            )
    else:
        logger.warning(
            "No authentication configured — MCP server is open to all clients on the network. "
            "Set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET + UNRAID_MCP_BASE_URL to enable Google OAuth, "
            "or set UNRAID_MCP_API_KEY to enable bearer token authentication."
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
