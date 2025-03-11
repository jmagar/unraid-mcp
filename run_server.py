#!/usr/bin/env python3
"""
Unraid MCP Server - Entry Point
This script is the main entry point for running the Unraid MCP server.
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables before importing config
load_dotenv()

# Import the server
from src.server import UnraidMCPServer
from src.config import Config, setup_logging

if __name__ == "__main__":
    # Set up logging
    logger = setup_logging("unraid_mcp_runner")
    logger.info("Starting Unraid MCP Server (Runner)")
    
    try:
        # Create and run the server
        transport = None
        
        # Check command line args for transport override
        if len(sys.argv) > 1:
            if sys.argv[1].lower() in ("stdio", "sse"):
                transport = sys.argv[1].lower()
                logger.info(f"Transport overridden from command line: {transport}")
        
        # Log key configuration
        logger.info(f"Claude mode: {Config.CLAUDE_MODE}")
        if Config.CLAUDE_MODE:
            logger.info(f"Using stdio transport for Claude integration")
        else:
            logger.info(f"Using SSE transport on {Config.SERVER_HOST}:{Config.SERVER_PORT}")
        
        # Start the server with the appropriate transport
        server = UnraidMCPServer()
        server.run(transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)
