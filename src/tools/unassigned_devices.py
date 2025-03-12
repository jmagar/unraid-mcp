"""Unassigned devices tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback

# Get logger
logger = logging.getLogger("unraid_mcp.unassigned_devices_tools")

def register_unassigned_devices_tools(server, unraid_client):
    """Register unassigned devices-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering unassigned devices tools")
    
    @server.tool(description="Get information about unassigned devices")
    async def get_unassigned_devices(
        ctx=None
    ):
        """Get information about unassigned devices
        
        Returns:
            Information about all unassigned devices
        """
        logger.info("Tool called: get_unassigned_devices()")
        
        if ctx:
            await ctx.info("Retrieving unassigned devices information...")
        else:
            print("Retrieving unassigned devices information...")
        
        try:
            devices = await unraid_client.get_unassigned_devices()
            logger.debug(f"Unassigned devices: {devices}")
            
            if devices:
                logger.info(f"Retrieved information for {len(devices)} unassigned devices")
                return TextContent(type="text", text=json.dumps(devices, indent=2))
            else:
                logger.warning("No unassigned devices found")
                return TextContent(type="text", text="No unassigned devices found")
        except Exception as e:
            error_msg = f"Error retrieving unassigned devices information: {str(e)}"
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
    logger.info("Unassigned devices tools registered successfully") 