#!/usr/bin/env python3
"""Unraid MCP Server - Entry Point.

This is the main entry point for the Unraid MCP Server. It imports and starts
the modular server implementation from unraid_mcp.server.
"""

import asyncio


async def shutdown_cleanup() -> None:
    """Cleanup resources on server shutdown."""
    try:
        from .core.client import close_http_client
        await close_http_client()
    except Exception as e:
        print(f"Error during cleanup: {e}")


def main() -> None:
    """Main entry point for the Unraid MCP Server."""
    try:
        from .server import run_server
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        try:
            asyncio.run(shutdown_cleanup())
        except RuntimeError:
            # Event loop already closed, skip cleanup
            pass
    except Exception as e:
        print(f"Server failed to start: {e}")
        try:
            asyncio.run(shutdown_cleanup())
        except RuntimeError:
            # Event loop already closed, skip cleanup
            pass
        raise


if __name__ == "__main__":
    main()
