"""Docker resources for Unraid MCP server"""
from typing import Dict, Any

def register_docker_resources(server, unraid_client):
    """Register Docker-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://docker/containers",
                    name="Docker Containers",
                    description="List of all Docker containers with their status",
                    mime_type="application/json")
    async def docker_containers():
        """List all Docker containers and their status"""
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.get_docker_containers()
            return result
        except Exception as e:
            return {"error": f"Failed to retrieve Docker containers: {str(e)}"}

    @server.resource("unraid://docker/{container_name}",
                    name="Docker Container Details",
                    description="Get detailed information about a specific Docker container",
                    mime_type="application/json")
    async def container_details(container_name: str):
        """Get details for a specific Docker container
        
        Args:
            container_name: The name of the Docker container
        """
        query = """
        query ($name: String!) {
          docker {
            container(name: $name) {
              name
              status
              state
              image
              autostart
              created
              repository
              ports
              volumes
              environment
            }
          }
        }
        """
        variables = {"name": container_name}
        
        try:
            result = await unraid_client.execute_query(query, variables)
            return result["data"]["docker"]["container"]
        except Exception as e:
            return {"error": f"Failed to retrieve container details for {container_name}: {str(e)}"}
