"""API key management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback
from typing import Optional, List

# Get logger
logger = logging.getLogger("unraid_mcp.apikey_tools")

def register_apikey_tools(server, unraid_client):
    """Register API key-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering API key management tools")
    
    @server.tool(description="Get information about all API keys")
    async def get_api_keys(
        ctx=None
    ):
        """Get information about all API keys
        
        Returns:
            Information about all API keys
        """
        logger.info("Tool called: get_api_keys()")
        
        if ctx:
            await ctx.info("Retrieving API key information...")
        else:
            print("Retrieving API key information...")
        
        try:
            api_keys = await unraid_client.get_api_keys()
            logger.debug(f"API keys: {api_keys}")
            
            if api_keys:
                logger.info(f"Retrieved information for {len(api_keys)} API keys")
                return TextContent(type="text", text=json.dumps(api_keys, indent=2))
            else:
                logger.warning("Failed to retrieve API key information or no API keys found")
                return TextContent(type="text", text="❌ Failed to retrieve API key information or no API keys found")
        except Exception as e:
            error_msg = f"Error retrieving API key information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    # API key creation tool has been removed for security reasons
    
    # Log that tools were registered
    logger.info("API key management tools registered successfully") 