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
    # Set up logging with debug level
    logger = setup_logging("unraid_mcp_runner", logging.DEBUG)
    logger.info("Starting Unraid MCP Server (Runner)")
    
    # Log environment and configuration
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    logger.debug(f"Log file: {Config.LOG_FILE}")
    logger.debug(f"Log level: {logging.getLevelName(logger.level)}")
    
    try:
        # Create and run the server
        transport = "stdio"  # Always use stdio transport by default
        
        # Check command line args for transport override (only for stdio)
        if len(sys.argv) > 1:
            if sys.argv[1].lower() == "stdio":
                transport = "stdio"
                logger.info(f"Transport confirmed from command line: {transport}")
            # SSE transport is commented out as we're using stdio by default
            # elif sys.argv[1].lower() == "sse":
            #     transport = "sse"
            #     logger.info(f"Transport overridden from command line: {transport}")
        
        # Log key configuration
        logger.info(f"Claude mode: {Config.CLAUDE_MODE}")
        logger.info(f"Using stdio transport for AI assistant integration")
        
        # SSE transport logging is commented out as we're using stdio by default
        # if Config.CLAUDE_MODE:
        #     logger.info(f"Using stdio transport for Claude integration")
        # else:
        #     logger.info(f"Using SSE transport on {Config.SERVER_HOST}:{Config.SERVER_PORT}")
        
        # Start the server with stdio transport
        server = UnraidMCPServer()
        logger.info("Server initialized, starting transport...")
        server.run(transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)
