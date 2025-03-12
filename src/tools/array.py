"""Array management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging

# Get logger
logger = logging.getLogger("unraid_mcp.array_tools")

def register_array_tools(server, unraid_client):
    """Register array-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering array tools")
    
    @server.tool(description="Start the Unraid array")
    async def start_array(ctx=None):
        """Start the Unraid array"""
        logger.info("Tool called: start_array()")
        
        if ctx:
            await ctx.info("Starting array...")
        else:
            print("Starting array...")
        
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.start_array()
            logger.debug(f"Start array response: {result}")
            logger.info("Array started successfully")
            return TextContent(type="text", text="✅ Array started successfully")
        except Exception as e:
            error_msg = f"Error starting array: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")

    @server.tool(description="Stop the Unraid array")
    async def stop_array(ctx=None):
        """Stop the Unraid array"""
        logger.info("Tool called: stop_array()")
        
        if ctx:
            await ctx.info("Stopping array...")
        else:
            print("Stopping array...")
        
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.stop_array()
            logger.debug(f"Stop array response: {result}")
            logger.info("Array stopped successfully")
            return TextContent(type="text", text="✅ Array stopped successfully")
        except Exception as e:
            error_msg = f"Error stopping array: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
    
    # Log that tools were registered
    logger.info("Array tools registered successfully")
