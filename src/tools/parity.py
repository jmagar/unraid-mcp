"""Parity history tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback

# Get logger
logger = logging.getLogger("unraid_mcp.parity_tools")

def register_parity_tools(server, unraid_client):
    """Register parity-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering parity history tools")
    
    @server.tool(description="Get parity check history")
    async def get_parity_history(
        ctx=None
    ):
        """Get parity check history
        
        Returns:
            Information about parity check history
        """
        logger.info("Tool called: get_parity_history()")
        
        if ctx:
            await ctx.info("Retrieving parity check history...")
        else:
            print("Retrieving parity check history...")
        
        try:
            history = await unraid_client.get_parity_history()
            logger.debug(f"Parity history: {history}")
            
            if history:
                logger.info(f"Retrieved {len(history)} parity check history entries")
                return TextContent(type="text", text=json.dumps(history, indent=2))
            else:
                logger.warning("No parity check history found")
                return TextContent(type="text", text="No parity check history found")
        except Exception as e:
            error_msg = f"Error retrieving parity check history: {str(e)}"
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
    logger.info("Parity history tools registered successfully") 