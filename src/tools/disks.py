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
                    # Make interfaceType optional by removing it from query
                    partitions {
                        name
                        # Make fsType optional by removing it from query
                        size
                    }
                }
            }
            """
            # Use direct execute_query with a longer timeout for disk operations
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
            disk_id: The ID of the disk
            
        Returns:
            Detailed information about the specified disk
        """
        logger.info(f"Tool called: get_disk_details({disk_id})")
        
        if ctx:
            await ctx.info(f"Retrieving details for disk: {disk_id}")
        else:
            print(f"Retrieving details for disk: {disk_id}")
        
        try:
            query = f"""
            query {{
                disk(id: "{disk_id}") {{
                    device
                    name
                    type
                    size
                    vendor
                    temperature
                    smartStatus
                    # Remove interfaceType which can be null
                    bytesPerSector
                    totalCylinders
                    totalHeads
                    totalSectors
                    totalTracks
                    tracksPerCylinder
                    sectorsPerTrack
                    firmwareRevision
                    serialNum
                    partitions {{
                        name
                        # Remove fsType which can be null
                        size
                    }}
                }}
            }}
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Disk details query result: {response}")
            
            if "data" in response and "disk" in response["data"]:
                disk = response["data"]["disk"]
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
    
    @server.tool(description="Mount a disk")
    async def mount_disk(
        disk_id: str,
        ctx=None
    ):
        """Mount a disk
        
        Args:
            disk_id: The ID of the disk to mount
            
        Returns:
            Status of the mount operation
        """
        logger.info(f"Tool called: mount_disk({disk_id})")
        
        if ctx:
            await ctx.info(f"Mounting disk: {disk_id}")
        else:
            print(f"Mounting disk: {disk_id}")
        
        try:
            mutation = f"""
            mutation {{
                mountArrayDisk(id: "{disk_id}") {{
                    device
                    name
                }}
            }}
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Mount disk response: {response}")
            
            if "data" in response and "mountArrayDisk" in response["data"]:
                disk = response["data"]["mountArrayDisk"]
                logger.info(f"Disk {disk_id} mounted successfully")
                return TextContent(type="text", text=json.dumps(disk, indent=2))
            else:
                logger.warning(f"Failed to mount disk {disk_id}: Invalid response format")
                return TextContent(type="text", text=f"❌ Failed to mount disk {disk_id}: Invalid response format")
        except Exception as e:
            error_msg = f"Error mounting disk: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Unmount a disk")
    async def unmount_disk(
        disk_id: str,
        ctx=None
    ):
        """Unmount a disk
        
        Args:
            disk_id: The ID of the disk to unmount
            
        Returns:
            Status of the unmount operation
        """
        logger.info(f"Tool called: unmount_disk({disk_id})")
        
        if ctx:
            await ctx.info(f"Unmounting disk: {disk_id}")
        else:
            print(f"Unmounting disk: {disk_id}")
        
        try:
            mutation = f"""
            mutation {{
                unmountArrayDisk(id: "{disk_id}") {{
                    device
                    name
                }}
            }}
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Unmount disk response: {response}")
            
            if "data" in response and "unmountArrayDisk" in response["data"]:
                disk = response["data"]["unmountArrayDisk"]
                logger.info(f"Disk {disk_id} unmounted successfully")
                return TextContent(type="text", text=json.dumps(disk, indent=2))
            else:
                logger.warning(f"Failed to unmount disk {disk_id}: Invalid response format")
                return TextContent(type="text", text=f"❌ Failed to unmount disk {disk_id}: Invalid response format")
        except Exception as e:
            error_msg = f"Error unmounting disk: {str(e)}"
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
