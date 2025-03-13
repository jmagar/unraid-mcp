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
            # Update query to match the actual API schema - using 'networks' is more likely to work
            # but we'll also handle the original field name in our response parsing
            query = """
            query {
                docker {
                    networks {
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
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Docker networks response: {response}")
            
            # More robust response handling with safer access methods
            if isinstance(response, dict):
                # If there's an error, return it but don't fail completely
                if "error" in response:
                    error_msg = response.get("error", "Unknown error")
                    logger.error(f"Error in Docker networks response: {error_msg}")
                    
                    # API error message suggests 'networks' field exists under 'docker'
                    if "Cannot query field \"dockerNetworks\"" in str(error_msg):
                        logger.info("Attempting to use alternative query structure based on error message")
                        try:
                            # Try the alternative query structure
                            alt_query = """
                            query {
                                docker {
                                    networks {
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
                            }
                            """
                            response = await unraid_client.execute_query(alt_query)
                            logger.debug(f"Alternative Docker networks response: {response}")
                        except Exception as alt_error:
                            logger.error(f"Alternative query also failed: {str(alt_error)}")
                    else:
                        # Return a message with suggestions from the error
                        return TextContent(type="text", text=f"⚠️ Docker networks API may not be available in this Unraid version:\n{error_msg}")
                
                # Check for network data in different possible locations
                networks_data = None
                
                # Try different possible response structures
                if "data" in response and "docker" in response.get("data", {}) and "networks" in response.get("data", {}).get("docker", {}):
                    networks_data = response["data"]["docker"]["networks"]
                elif "data" in response and "dockerNetworks" in response.get("data", {}):
                    networks_data = response["data"]["dockerNetworks"]
                elif "docker" in response and "networks" in response.get("docker", {}):
                    networks_data = response["docker"]["networks"]
                elif "dockerNetworks" in response:
                    networks_data = response["dockerNetworks"]
                elif "networks" in response:
                    networks_data = response["networks"]
                
                if networks_data:
                    logger.info(f"Retrieved information for {len(networks_data)} Docker networks")
                    
                    # Format the networks data in a human-readable way
                    formatted_text = "🌐 DOCKER NETWORKS\n"
                    formatted_text += "══════════════════\n\n"
                    
                    if len(networks_data) == 0:
                        formatted_text += "No Docker networks found.\n"
                    else:
                        formatted_text += f"📊 Total Networks: {len(networks_data)}\n\n"
                        
                        # Sort networks by name
                        sorted_networks = sorted(networks_data, key=lambda n: n.get('name', '').lower())
                        
                        for network in sorted_networks:
                            # Network name
                            name = network.get('name', 'Unnamed')
                            formatted_text += f"🔹 {name}\n"
                            
                            # Network details
                            formatted_text += f"  • ID: {network.get('id', 'Unknown')}\n"
                            
                            if 'driver' in network:
                                formatted_text += f"  • Driver: {network.get('driver', 'Unknown')}\n"
                                
                            if 'scope' in network:
                                formatted_text += f"  • Scope: {network.get('scope', 'Unknown')}\n"
                            
                            # Network flags
                            flags = []
                            if network.get('internal', False):
                                flags.append("Internal")
                            if network.get('attachable', False):
                                flags.append("Attachable")
                            if network.get('ingress', False):
                                flags.append("Ingress")
                                
                            if flags:
                                formatted_text += f"  • Flags: {', '.join(flags)}\n"
                            
                            # Network options
                            if 'options' in network and network['options']:
                                formatted_text += "  • Options:\n"
                                for key, value in network['options'].items():
                                    formatted_text += f"    - {key}: {value}\n"
                            
                            formatted_text += "\n"
                    
                    return TextContent(type="text", text=formatted_text)
            
            # If we've reached here, we couldn't find usable data
            logger.warning("Docker network information structure doesn't match expected format")
            
            # Format the warning message nicely
            formatted_text = "🌐 DOCKER NETWORKS\n"
            formatted_text += "══════════════════\n\n"
            
            if "data" in response and "docker" in response.get("data", {}) and response.get("data", {}).get("docker", {}).get("networks") is None:
                formatted_text += "⚠️ No Docker networks available or API returned null data.\n"
            else:
                formatted_text += "⚠️ Docker network data may be incomplete or in unexpected format.\n"
            
            return TextContent(type="text", text=formatted_text)
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
