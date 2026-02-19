"""Modular Unraid MCP Server.

This is the main server implementation using the modular architecture with
separate modules for configuration, core functionality, subscriptions, and tools.
"""

import sys

from fastmcp import FastMCP

from .config.logging import logger
from .config.settings import (
    UNRAID_API_KEY,
    UNRAID_API_URL,
    UNRAID_MCP_HOST,
    UNRAID_MCP_PORT,
    UNRAID_MCP_TRANSPORT,
    UNRAID_VERIFY_SSL,
    VERSION,
    validate_required_config,
)
from .subscriptions.diagnostics import register_diagnostic_tools
from .subscriptions.resources import register_subscription_resources
from .tools.array import register_array_tool
from .tools.docker import register_docker_tool
from .tools.health import register_health_tool
from .tools.info import register_info_tool
from .tools.keys import register_keys_tool
from .tools.notifications import register_notifications_tool
from .tools.rclone import register_rclone_tool
from .tools.storage import register_storage_tool
from .tools.users import register_users_tool
from .tools.virtualization import register_vm_tool


# Initialize FastMCP instance
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version=VERSION,
)

# Note: SubscriptionManager singleton is defined in subscriptions/manager.py
# and imported by resources.py - no duplicate instance needed here


def register_all_modules() -> None:
    """Register all tools and resources with the MCP instance."""
    try:
        # Register subscription resources and diagnostic tools
        register_subscription_resources(mcp)
        register_diagnostic_tools(mcp)
        logger.info("Subscription resources and diagnostic tools registered")

        # Register all consolidated tools
        registrars = [
            register_info_tool,
            register_array_tool,
            register_storage_tool,
            register_docker_tool,
            register_vm_tool,
            register_notifications_tool,
            register_rclone_tool,
            register_users_tool,
            register_keys_tool,
            register_health_tool,
        ]
        for registrar in registrars:
            registrar(mcp)

        logger.info(f"All {len(registrars)} tools registered successfully - Server ready!")

    except Exception as e:
        logger.error(f"Failed to register modules: {e}", exc_info=True)
        raise


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    # Validate required configuration before anything else
    is_valid, missing = validate_required_config()
    if not is_valid:
        logger.critical(
            f"Missing required configuration: {', '.join(missing)}. "
            "Set these environment variables or add them to your .env file."
        )
        sys.exit(1)

    # Log configuration
    if UNRAID_API_URL:
        logger.info(f"UNRAID_API_URL loaded: {UNRAID_API_URL[:20]}...")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")

    if UNRAID_API_KEY:
        logger.info("UNRAID_API_KEY loaded: ****")
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")

    logger.info(f"UNRAID_MCP_PORT set to: {UNRAID_MCP_PORT}")
    logger.info(f"UNRAID_MCP_HOST set to: {UNRAID_MCP_HOST}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {UNRAID_MCP_TRANSPORT}")

    if UNRAID_VERIFY_SSL is False:
        logger.warning(
            "SSL VERIFICATION DISABLED (UNRAID_VERIFY_SSL=false). "
            "Connections to Unraid API are vulnerable to man-in-the-middle attacks. "
            "Only use this in trusted networks or for development."
        )

    # Register all modules
    register_all_modules()

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
