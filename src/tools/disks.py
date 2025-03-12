"""Disk management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.disk_tools")

def register_disk_tools(server, unraid_client):
    """Register disk-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering disk tools")
    
    @server.tool(description="Get information about all disks")
    async def get_disks(
        ctx=None
    ):
        """Get information about all disks
        
        Returns:
            Information about all disks in the system
        """
        logger.info("Tool called: get_disks()")
        
        if ctx:
            await ctx.info("Retrieving disk information...")
        else:
            print("Retrieving disk information...")
        
        try:
            query = """
            query {
                disks {
                    device
                    name
                    type
                    size
                    vendor
                    temperature
                    smartStatus
                    partitions {
                        name
                        size
                        fsType
                        mountpoint
                        used
                        free
                    }
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Disks response: {response}")
            
            if "data" in response and "disks" in response["data"]:
                disks = response["data"]["disks"]
                logger.info(f"Retrieved information for {len(disks)} disks")
                return TextContent(type="text", text=json.dumps(disks, indent=2))
            else:
                logger.warning("Failed to retrieve disk information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve disk information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving disk information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Get information about a specific disk")
    async def get_disk_details(
        disk_id: str,
        ctx=None
    ):
        """Get detailed information about a specific disk
        
        Args:
            disk_id: The disk identifier (e.g., sda, nvme0n1)
            
        Returns:
            Detailed information about the specified disk
        """
        logger.info(f"Tool called: get_disk_details({disk_id})")
        
        if ctx:
            await ctx.info(f"Retrieving details for disk: {disk_id}")
        else:
            print(f"Retrieving details for disk: {disk_id}")
        
        try:
            query = """
            query {
                disks {
                    device
                    name
                    type
                    size
                    vendor
                    temperature
                    smartStatus
                    partitions {
                        name
                        size
                        fsType
                        mountpoint
                        used
                        free
                    }
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Disk details query result: {response}")
            
            if "data" in response and "disks" in response["data"]:
                disks = response["data"]["disks"]
                disk = next((d for d in disks if d["device"] == disk_id), None)
                
                if disk:
                    logger.info(f"Retrieved details for disk {disk_id}")
                    return TextContent(type="text", text=json.dumps(disk, indent=2))
                else:
                    logger.warning(f"Disk {disk_id} not found")
                    return TextContent(type="text", text=f"❌ Disk {disk_id} not found")
            else:
                logger.warning(f"Failed to retrieve details for disk {disk_id}: Invalid response format")
                return TextContent(type="text", text=f"❌ Failed to retrieve details for disk {disk_id}: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving disk details: {str(e)}"
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
    logger.info("Disk tools registered successfully")
