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
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("unraid_mcp")

# Get server configuration from environment variables
host = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
port = int(os.getenv("MCP_SERVER_PORT", "8000"))

if __name__ == "__main__":
    logger.info(f"Starting Unraid MCP Server on {host}:{port} with log level {log_level_name}")
    try:
        # Run server with SSE transport
        server.run(
            transport="sse",
            host=host,
            port=port
        )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise 