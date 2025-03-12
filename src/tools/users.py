"""User management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.user_tools")

def register_user_tools(server, unraid_client):
    """Register user-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering user tools")
    
    @server.tool(description="Get information about all users")
    async def get_users(
        ctx=None
    ):
        """Get information about all users
        
        Returns:
            Information about all users on the Unraid server
        """
        logger.info("Tool called: get_users()")
        
        if ctx:
            await ctx.info("Retrieving user information...")
        else:
            print("Retrieving user information...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_users()
            logger.debug(f"Users response: {response}")
            
            if "data" in response and "users" in response["data"]:
                users = response["data"]["users"]
                logger.info(f"Retrieved information for {len(users)} users")
                return TextContent(type="text", text=json.dumps(users, indent=2))
            else:
                logger.warning("Failed to retrieve user information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve user information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving user information: {str(e)}"
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
    logger.info("User tools registered successfully") 