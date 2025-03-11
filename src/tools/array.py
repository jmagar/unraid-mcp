"""Array management tools for Unraid MCP server"""
from mcp.types import TextContent

def register_array_tools(server, unraid_client):
    """Register array-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.tool(description="Start the Unraid array")
    async def start_array(ctx=None):
        """Start the Unraid array"""
        if ctx:
            await ctx.info("Starting array...")
        else:
            print("Starting array...")
        
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.start_array()
            return TextContent(type="text", text="✅ Array started successfully")
        except Exception as e:
            error_msg = f"Error starting array: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")

    @server.tool(description="Stop the Unraid array")
    async def stop_array(ctx=None):
        """Stop the Unraid array"""
        if ctx:
            await ctx.info("Stopping array...")
        else:
            print("Stopping array...")
        
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.stop_array()
            return TextContent(type="text", text="✅ Array stopped successfully")
        except Exception as e:
            error_msg = f"Error stopping array: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
