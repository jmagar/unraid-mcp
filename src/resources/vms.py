"""Virtual Machine resources for Unraid MCP server"""
from typing import Dict, Any

def register_vm_resources(server, unraid_client):
    """Register VM-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://vms/list",
                    name="Virtual Machines",
                    description="List of all virtual machines and their status",
                    mime_type="application/json")
    async def virtual_machines():
        """List all virtual machines and their status"""
        try:
            # Use the client's method instead of raw GraphQL
            result = await unraid_client.get_vms()
            return result
        except Exception as e:
            return {"error": f"Failed to retrieve virtual machines: {str(e)}"}

    @server.resource("unraid://vms/{vm_name}",
                    name="Virtual Machine Details",
                    description="Get detailed information about a specific virtual machine",
                    mime_type="application/json")
    async def vm_details(vm_name: str):
        """Get details for a specific virtual machine
        
        Args:
            vm_name: The name of the virtual machine
        """
        query = """
        query ($name: String!) {
          vms(name: $name) {
            name
            status
            memory
            cores
            diskSize
            template
            description
            primaryGPU
            cpuMode
            machine
          }
        }
        """
        variables = {"name": vm_name}
        
        try:
            result = await unraid_client.execute_query(query, variables)
            return result["data"]["vms"]
        except Exception as e:
            return {"error": f"Failed to retrieve VM details for {vm_name}: {str(e)}"}
