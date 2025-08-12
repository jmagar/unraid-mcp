#!/usr/bin/env python3
"""Unraid MCP Server - Entry Point.

This is the main entry point for the Unraid MCP Server. It imports and starts
the modular server implementation from unraid_mcp.server.
"""


def main() -> None:
    """Main entry point for the Unraid MCP Server."""
    try:
        from .server import run_server
        run_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server failed to start: {e}")
        raise


if __name__ == "__main__":
    main()
