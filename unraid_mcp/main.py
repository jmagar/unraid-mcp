#!/usr/bin/env python3
"""Unraid MCP Server - Entry Point.

This is the main entry point for the Unraid MCP Server. It imports and starts
the modular server implementation from unraid_mcp.server.
"""

import asyncio
import sys


async def shutdown_cleanup() -> None:
    """Cleanup resources on server shutdown."""
    try:
        from .core.client import close_http_client

        await close_http_client()
    except Exception as e:
        print(f"Error during cleanup: {e}")


def _run_shutdown_cleanup() -> None:
    """Run shutdown cleanup, suppressing expected event loop errors."""
    try:
        asyncio.run(shutdown_cleanup())
    except RuntimeError as e:
        msg = str(e).lower()
        if "event loop is closed" in msg or "no running event loop" in msg:
            pass  # Expected during shutdown
        else:
            print(f"WARNING: Unexpected error during cleanup: {e}", file=sys.stderr)


def main() -> None:
    """Main entry point for the Unraid MCP Server."""
    try:
        from .server import run_server

        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        _run_shutdown_cleanup()
    except Exception as e:
        print(f"Server failed to start: {e}")
        _run_shutdown_cleanup()
        raise


if __name__ == "__main__":
    main()
