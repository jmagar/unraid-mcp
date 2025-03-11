"""Array resources for Unraid MCP server"""
from typing import Dict, Any

def register_array_resources(server, unraid_client):
    """Register array-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://array/status",
                    name="Array Status",
                    description="Current array status information",
                    mime_type="application/json")
    async def array_status():
        """Get current array status information"""
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.get_array_status()
            return result
        except Exception as e:
            return {"error": f"Failed to retrieve array status: {str(e)}"}

    @server.resource("unraid://storage/shares",
                    name="Shares",
                    description="List of all user shares on the Unraid server",
                    mime_type="application/json")
    async def shares():
        """List all user shares"""
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.get_shares()
            return result
        except Exception as e:
            return {"error": f"Failed to retrieve shares: {str(e)}"}
