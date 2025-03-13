"""Array management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.array_tools")

def register_array_tools(server, unraid_client):
    """Register array-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering array tools")
    
    # Note: The formatted array status tool is now provided by the formatting.py module
    # as format_array_status to avoid duplication
    
    # Log that tools were registered
    logger.info("Array tools registered successfully")
