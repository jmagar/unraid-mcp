"""Docker management tools for Unraid MCP server"""
from mcp.types import TextContent
from typing import Optional

def register_docker_tools(server, unraid_client):
    """Register Docker-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.tool(description="Start a Docker container by name")
    async def start_container(
        container_name: str, 
        ctx=None
    ):
        """Start a Docker container by name
        
        Args:
            container_name: The name of the container to start
        """
        if ctx:
            await ctx.info(f"Starting container: {container_name}")
        else:
            print(f"Starting container: {container_name}")
        
        mutation = """
        mutation ($name: String!) {
          docker {
            startContainer(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": container_name}
        
        try:
            result = await unraid_client.execute_query(mutation, variables)
            
            response = result["data"]["docker"]["startContainer"]
            if response["success"]:
                return TextContent(type="text", text=f"✅ Container {container_name} started successfully")
            else:
                return TextContent(type="text", text=f"❌ Failed to start container: {response['message']}")
        except Exception as e:
            error_msg = f"Error starting container: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")

    @server.tool(description="Stop a Docker container by name")
    async def stop_container(
        container_name: str,
        ctx=None
    ):
        """Stop a Docker container by name
        
        Args:
            container_name: The name of the container to stop
        """
        if ctx:
            await ctx.info(f"Stopping container: {container_name}")
        else:
            print(f"Stopping container: {container_name}")
        
        mutation = """
        mutation ($name: String!) {
          docker {
            stopContainer(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": container_name}
        
        try:
            result = await unraid_client.execute_query(mutation, variables)
            
            response = result["data"]["docker"]["stopContainer"]
            if response["success"]:
                return TextContent(type="text", text=f"✅ Container {container_name} stopped successfully")
            else:
                return TextContent(type="text", text=f"❌ Failed to stop container: {response['message']}")
        except Exception as e:
            error_msg = f"Error stopping container: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
