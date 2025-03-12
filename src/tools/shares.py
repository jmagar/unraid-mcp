"""Share management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.share_tools")

def register_share_tools(server, unraid_client):
    """Register share-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering share tools")
    
    @server.tool(description="Get information about network shares")
    async def get_shares(
        ctx=None
    ):
        """Get information about network shares
        
        Returns:
            Information about all network shares
        """
        logger.info("Tool called: get_shares()")
        
        if ctx:
            await ctx.info("Retrieving share information...")
        else:
            print("Retrieving share information...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_shares()
            logger.debug(f"Shares response: {response}")
            
            if "data" in response and "shares" in response["data"]:
                shares = response["data"]["shares"]
                logger.info(f"Retrieved information for {len(shares)} shares")
                return TextContent(type="text", text=json.dumps(shares, indent=2))
            else:
                logger.warning("Failed to retrieve share information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve share information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving share information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Get detailed information about a specific share")
    async def get_share_details(
        share_name: str,
        ctx=None
    ):
        """Get detailed information about a specific share
        
        Args:
            share_name: The name of the share
            
        Returns:
            Detailed information about the specified share
        """
        logger.info(f"Tool called: get_share_details({share_name})")
        
        if ctx:
            await ctx.info(f"Retrieving details for share: {share_name}")
        else:
            print(f"Retrieving details for share: {share_name}")
        
        try:
            query = """
            query {
                shares {
                    name
                    free
                    used
                    size
                    include
                    exclude
                    cache
                    comment
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Share details query result: {response}")
            
            if "data" in response and "shares" in response["data"]:
                shares = response["data"]["shares"]
                share = next((s for s in shares if s["name"] == share_name), None)
                
                if share:
                    logger.info(f"Retrieved details for share {share_name}")
                    return TextContent(type="text", text=json.dumps(share, indent=2))
                else:
                    logger.warning(f"Share {share_name} not found")
                    return TextContent(type="text", text=f"❌ Share {share_name} not found")
            else:
                logger.warning(f"Failed to retrieve details for share {share_name}: Invalid response format")
                return TextContent(type="text", text=f"❌ Failed to retrieve details for share {share_name}: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving share details: {str(e)}"
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
    logger.info("Share tools registered successfully") 