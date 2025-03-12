"""Remote access configuration tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback
from typing import Optional

# Get logger
logger = logging.getLogger("unraid_mcp.remote_access_tools")

def register_remote_access_tools(server, unraid_client):
    """Register remote access-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering remote access configuration tools")
    
    # Remote access tools have been removed for security reasons
    
    # Log that tools were registered
    logger.info("Remote access configuration tools registered successfully") 