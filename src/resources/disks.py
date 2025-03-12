"""Disk resources for Unraid MCP server"""
from typing import Dict, Any, Optional

def register_disk_resources(server, unraid_client):
    """Register disk-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://disks/all",
                    name="All Disks",
                    description="List of all disks in the system",
                    mime_type="application/json")
    async def all_disks():
        """Get information about all disks"""
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
                    interfaceType
                    partitions {
                        name
                        fsType
                        size
                    }
                }
            }
            """
            result = await unraid_client.execute_query(query)
            if "data" in result and "disks" in result["data"]:
                return result["data"]["disks"]
            else:
                return {"error": "Failed to retrieve disk information: Invalid response format"}
        except Exception as e:
            return {"error": f"Failed to retrieve disk information: {str(e)}"}

    @server.resource("unraid://disks/{disk_id}",
                    name="Disk Details",
                    description="Detailed information about a specific disk",
                    mime_type="application/json")
    async def disk_details(disk_id: str):
        """Get detailed information about a specific disk
        
        Args:
            disk_id: The ID of the disk
        """
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
                    interfaceType
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
                        fsType
                        size
                    }}
                }}
            }}
            """
            result = await unraid_client.execute_query(query)
            if "data" in result and "disk" in result["data"]:
                return result["data"]["disk"]
            else:
                return {"error": f"Failed to retrieve details for disk {disk_id}: Invalid response format"}
        except Exception as e:
            return {"error": f"Failed to retrieve details for disk {disk_id}: {str(e)}"} 