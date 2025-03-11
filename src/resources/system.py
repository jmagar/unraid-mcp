"""System resources for Unraid MCP server"""
from typing import Dict, Any, Callable

def register_system_resources(server, unraid_client):
    """Register system-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://system/info", 
                    name="System Information",
                    description="Current system information including CPU, memory, and uptime",
                    mime_type="application/json")
    async def system_info():
        """Get current system information from Unraid server"""
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.get_system_info()
            return result
        except Exception as e:
            return {"error": f"Failed to retrieve system information: {str(e)}"}

    @server.resource("unraid://system/plugins",
                    name="Plugins",
                    description="List of all installed plugins on the Unraid server",
                    mime_type="application/json")
    async def plugins():
        """List all installed plugins"""
        query = """
        query {
          plugins {
            name
            version
            author
            description
            status
          }
        }
        """
        try:
            result = await unraid_client.execute_query(query)
            return result["data"]["plugins"]
        except Exception as e:
            return {"error": f"Failed to retrieve plugins: {str(e)}"}
