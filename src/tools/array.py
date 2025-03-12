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
    
    @server.tool(description="Get array status in a human-readable way")
    async def get_array_status(
        ctx=None
    ):
        """Get the current status of the Unraid array
        
        Returns:
            Human-readable array status information
        """
        logger.info("Tool called: get_array_status()")
        
        if ctx:
            await ctx.info("Retrieving array status...")
        else:
            print("Retrieving array status...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_array_status()
            logger.debug(f"Array status response: {response}")
            
            if "data" in response and "array" in response["data"]:
                array = response["data"]["array"]
                logger.info("Retrieved array status successfully")
                return TextContent(type="text", text=json.dumps(array, indent=2))
            else:
                logger.warning("Failed to retrieve array status: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve array status: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving array status: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    # Log that tools were registered
    logger.info("Array tools registered successfully")
