"""Docker management tools for Unraid MCP server"""
from mcp.types import TextContent
from typing import Optional
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.docker_tools")

def register_docker_tools(server, unraid_client):
    """Register Docker-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering Docker tools")
    
    @server.tool(description="Get information about Docker containers")
    async def get_docker_containers(
        ctx=None
    ):
        """Get information about all Docker containers
        
        Returns:
            Information about all Docker containers including their status
        """
        logger.info("Tool called: get_docker_containers()")
        
        if ctx:
            await ctx.info("Retrieving Docker container information...")
        else:
            print("Retrieving Docker container information...")
        
        try:
            # Use execute_query directly to bypass field validation
            query = """
            query {
                docker {
                    containers {
                        id
                        names
                        image
                        state
                        status
                        ports {
                            ip
                            privatePort
                            publicPort
                            type
                        }
                        autoStart
                        created
                        command
                    }
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Docker containers response: {response}")
            
            if "data" in response and "docker" in response["data"] and "containers" in response["data"]["docker"]:
                containers = response["data"]["docker"]["containers"]
                logger.info(f"Retrieved information for {len(containers)} Docker containers")
                return TextContent(type="text", text=json.dumps(containers, indent=2))
            else:
                logger.warning("Failed to retrieve Docker container information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve Docker container information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving Docker container information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")

    @server.tool(description="Get information about Docker networks")
    async def get_docker_networks(
        ctx=None
    ):
        """Get information about all Docker networks
        
        Returns:
            Information about all Docker networks
        """
        logger.info("Tool called: get_docker_networks()")
        
        if ctx:
            await ctx.info("Retrieving Docker network information...")
        else:
            print("Retrieving Docker network information...")
        
        try:
            # Use the client method directly
            query = """
            query {
                dockerNetworks {
                    id
                    name
                    driver
                    scope
                    internal
                    attachable
                    ingress
                    options
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Docker networks response: {response}")
            
            if "data" in response and "dockerNetworks" in response["data"]:
                networks = response["data"]["dockerNetworks"]
                logger.info(f"Retrieved information for {len(networks)} Docker networks")
                return TextContent(type="text", text=json.dumps(networks, indent=2))
            else:
                logger.warning("Failed to retrieve Docker network information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve Docker network information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving Docker network information: {str(e)}"
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
    logger.info("Docker tools registered successfully")
