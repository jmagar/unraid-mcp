# This file makes the resources directory a Python package

# Import all resource registration functions
from src.resources.system import register_system_resources
from src.resources.docker import register_docker_resources
from src.resources.array import register_array_resources
from src.resources.vms import register_vm_resources

# Expose all registration functions in a single function
def register_all_resources(server, unraid_client):
    """Register all resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    register_system_resources(server, unraid_client)
    register_docker_resources(server, unraid_client) 
    register_array_resources(server, unraid_client)
    register_vm_resources(server, unraid_client)
