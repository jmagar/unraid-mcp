"""System management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.system_tools")

def register_system_tools(server, unraid_client):
    """Register system-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering system tools")
    
    @server.tool(description="Get detailed system information")
    async def get_system_info(
        ctx=None
    ):
        """Get detailed system information including CPU, memory, and system details
        
        Returns:
            Detailed system information
        """
        logger.info("Tool called: get_system_info()")
        
        if ctx:
            await ctx.info("Retrieving system information...")
        else:
            print("Retrieving system information...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_system_info()
            logger.debug(f"System info response: {response}")
            
            if "data" in response and "info" in response["data"]:
                info = response["data"]["info"]
                logger.info("Retrieved system information successfully")
                return TextContent(type="text", text=json.dumps(info, indent=2))
            else:
                logger.warning("Failed to retrieve system information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve system information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving system information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Reboot the Unraid server")
    async def reboot_server(
        ctx=None
    ):
        """Reboot the Unraid server
        
        Returns:
            Status of the reboot operation
        """
        logger.info("Tool called: reboot_server()")
        
        if ctx:
            await ctx.info("Rebooting the Unraid server...")
        else:
            print("Rebooting the Unraid server...")
        
        try:
            mutation = """
            mutation {
                reboot
            }
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Reboot response: {response}")
            
            if "data" in response and "reboot" in response["data"]:
                logger.info("Server reboot initiated successfully")
                return TextContent(type="text", text="✅ Server reboot initiated successfully")
            else:
                logger.warning("Failed to initiate server reboot: Invalid response format")
                return TextContent(type="text", text="❌ Failed to initiate server reboot: Invalid response format")
        except Exception as e:
            error_msg = f"Error initiating server reboot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Shutdown the Unraid server")
    async def shutdown_server(
        ctx=None
    ):
        """Shutdown the Unraid server
        
        Returns:
            Status of the shutdown operation
        """
        logger.info("Tool called: shutdown_server()")
        
        if ctx:
            await ctx.info("Shutting down the Unraid server...")
        else:
            print("Shutting down the Unraid server...")
        
        try:
            mutation = """
            mutation {
                shutdown
            }
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Shutdown response: {response}")
            
            if "data" in response and "shutdown" in response["data"]:
                logger.info("Server shutdown initiated successfully")
                return TextContent(type="text", text="✅ Server shutdown initiated successfully")
            else:
                logger.warning("Failed to initiate server shutdown: Invalid response format")
                return TextContent(type="text", text="❌ Failed to initiate server shutdown: Invalid response format")
        except Exception as e:
            error_msg = f"Error initiating server shutdown: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Get network information")
    async def get_network_info(
        ctx=None
    ):
        """Get network interface information
        
        Returns:
            Information about network interfaces
        """
        logger.info("Tool called: get_network_info()")
        
        if ctx:
            await ctx.info("Retrieving network information...")
        else:
            print("Retrieving network information...")
        
        try:
            query = """
            query {
                network {
                    iface
                    ifaceName
                    ipv4
                    ipv6
                    mac
                    operstate
                    type
                    duplex
                    speed
                    accessUrls {
                        type
                        name
                        ipv4
                        ipv6
                    }
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Network info response: {response}")
            
            if "data" in response and "network" in response["data"]:
                network = response["data"]["network"]
                logger.info("Retrieved network information successfully")
                return TextContent(type="text", text=json.dumps(network, indent=2))
            else:
                logger.warning("Failed to retrieve network information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve network information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving network information: {str(e)}"
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
    logger.info("System tools registered successfully") 