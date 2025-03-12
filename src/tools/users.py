"""User management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback
from typing import Optional

# Get logger
logger = logging.getLogger("unraid_mcp.user_tools")

def register_user_tools(server, unraid_client):
    """Register user-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering user management tools")
    
    @server.tool(description="Get information about all users")
    async def get_users(
        ctx=None
    ):
        """Get information about all users
        
        Returns:
            Information about all users including their roles
        """
        logger.info("Tool called: get_users()")
        
        if ctx:
            await ctx.info("Retrieving user information...")
        else:
            print("Retrieving user information...")
        
        try:
            users = await unraid_client.get_users()
            logger.debug(f"Users: {users}")
            
            if users:
                logger.info(f"Retrieved information for {len(users)} users")
                return TextContent(type="text", text=json.dumps(users, indent=2))
            else:
                logger.warning("Failed to retrieve user information or no users found")
                return TextContent(type="text", text="❌ Failed to retrieve user information or no users found")
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
    
    @server.tool(description="Add a new user")
    async def add_user(
        username: str,
        password: str,
        description: str = "",
        ctx=None
    ):
        """Add a new user to the Unraid server
        
        Args:
            username: The username for the new user
            password: The password for the new user
            description: Optional description for the user
            
        Returns:
            Information about the newly created user
        """
        logger.info(f"Tool called: add_user({username}, [password], {description})")
        
        if ctx:
            await ctx.info(f"Adding new user: {username}")
        else:
            print(f"Adding new user: {username}")
        
        try:
            result = await unraid_client.add_user(username, password, description)
            logger.debug(f"Add user result: {result}")
            
            if "error" in result:
                error_msg = f"Failed to add user: {result['error']}"
                logger.warning(error_msg)
                
                if ctx:
                    await ctx.error(error_msg)
                else:
                    print(error_msg)
                return TextContent(type="text", text=f"❌ {error_msg}")
            else:
                success_msg = f"✅ Successfully added user: {username}"
                logger.info(success_msg)
                
                if ctx:
                    await ctx.info(success_msg)
                else:
                    print(success_msg)
                return TextContent(type="text", text=f"{success_msg}\n\n{json.dumps(result, indent=2)}")
        except Exception as e:
            error_msg = f"Error adding user: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Delete a user")
    async def delete_user(
        user_id: str,
        ctx=None
    ):
        """Delete a user from the Unraid server
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            Information about the deleted user
        """
        logger.info(f"Tool called: delete_user({user_id})")
        
        if ctx:
            await ctx.info(f"Deleting user with ID: {user_id}")
        else:
            print(f"Deleting user with ID: {user_id}")
        
        try:
            result = await unraid_client.delete_user(user_id)
            logger.debug(f"Delete user result: {result}")
            
            if "error" in result:
                error_msg = f"Failed to delete user: {result['error']}"
                logger.warning(error_msg)
                
                if ctx:
                    await ctx.error(error_msg)
                else:
                    print(error_msg)
                return TextContent(type="text", text=f"❌ {error_msg}")
            else:
                success_msg = f"✅ Successfully deleted user with ID: {user_id}"
                logger.info(success_msg)
                
                if ctx:
                    await ctx.info(success_msg)
                else:
                    print(success_msg)
                return TextContent(type="text", text=f"{success_msg}\n\n{json.dumps(result, indent=2)}")
        except Exception as e:
            error_msg = f"Error deleting user: {str(e)}"
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
    logger.info("User management tools registered successfully") 