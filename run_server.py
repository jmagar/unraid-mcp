#!/usr/bin/env python3
"""
Run the Unraid MCP server with Server-Sent Events (SSE) transport for production use.
This allows the server to be used with Claude and other MCP clients over HTTP.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from server import server

# Load environment variables first
load_dotenv()

# Get logging configuration from environment
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "unraid_mcp.log")

# Convert string log level to logging constant
log_level = getattr(logging, log_level_name.upper(), logging.INFO)

# Configure logging
# Set up root logger for all modules
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

# Set up our specific logger
logger = logging.getLogger("unraid_mcp")
logger.setLevel(log_level)

# Set MCP library logging to WARNING level to reduce console spam
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Get server configuration from environment variables
host = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
port = int(os.getenv("MCP_SERVER_PORT", "8400"))

if __name__ == "__main__":
    logger.info(f"Starting Unraid MCP Server (MCP 1.3.0 uses default host/port) with log level {log_level_name}")
    try:
        # Detect if we're running through Cline/Claude MCP by checking environment
        # If CLAUDE_MCP_SERVER is set, use stdio transport, otherwise use SSE
        if os.environ.get("CLAUDE_MCP_SERVER"):
            logger.info("Running in Cline/Claude MCP integration mode with stdio transport")
            
            # We can't monkey-patch the FastMCP server, but we can redirect stdout/stderr
            # to prevent noise in the Cline console
            import sys
            
            # Configure a file handler to ensure logs go to the log file
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
            
            # Log the fact we're running in Cline mode
            logger.info(f"Running under Cline with stdio transport, logging to {log_file}")
            
            server.run(transport="stdio")
        else:
            # Run server with SSE transport for normal operation
            # Note: MCP 1.3.0 doesn't support host or port parameters
            # The server will use its default configuration
            server.run(transport="sse")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise
