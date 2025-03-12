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
    
    @server.tool(description="Set up remote access")
    async def setup_remote_access(
        url: str,
        ctx=None
    ):
        """Set up remote access for the Unraid server
        
        Args:
            url: The remote access URL
            
        Returns:
            Success or failure message
        """
        logger.info(f"Tool called: setup_remote_access({url})")
        
        if ctx:
            await ctx.info(f"Setting up remote access with URL: {url}")
        else:
            print(f"Setting up remote access with URL: {url}")
        
        try:
            result = await unraid_client.setup_remote_access(url)
            logger.debug(f"Setup remote access result: {result}")
            
            if result:
                success_msg = f"✅ Successfully set up remote access with URL: {url}"
                logger.info(success_msg)
                
                if ctx:
                    await ctx.info(success_msg)
                else:
                    print(success_msg)
                return TextContent(type="text", text=success_msg)
            else:
                error_msg = "Failed to set up remote access"
                logger.warning(error_msg)
                
                if ctx:
                    await ctx.error(error_msg)
                else:
                    print(error_msg)
                return TextContent(type="text", text=f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Error setting up remote access: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Enable or disable dynamic remote access")
    async def enable_dynamic_remote_access(
        enable: bool = True,
        ctx=None
    ):
        """Enable or disable dynamic remote access for the Unraid server
        
        Args:
            enable: Whether to enable (True) or disable (False) dynamic remote access
            
        Returns:
            Success or failure message
        """
        logger.info(f"Tool called: enable_dynamic_remote_access({enable})")
        
        if ctx:
            await ctx.info(f"{'Enabling' if enable else 'Disabling'} dynamic remote access")
        else:
            print(f"{'Enabling' if enable else 'Disabling'} dynamic remote access")
        
        try:
            result = await unraid_client.enable_dynamic_remote_access(enable)
            logger.debug(f"Enable dynamic remote access result: {result}")
            
            if result:
                success_msg = f"✅ Successfully {'enabled' if enable else 'disabled'} dynamic remote access"
                logger.info(success_msg)
                
                if ctx:
                    await ctx.info(success_msg)
                else:
                    print(success_msg)
                return TextContent(type="text", text=success_msg)
            else:
                error_msg = f"Failed to {'enable' if enable else 'disable'} dynamic remote access"
                logger.warning(error_msg)
                
                if ctx:
                    await ctx.error(error_msg)
                else:
                    print(error_msg)
                return TextContent(type="text", text=f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Error {'enabling' if enable else 'disabling'} dynamic remote access: {str(e)}"
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
    logger.info("Remote access configuration tools registered successfully") 