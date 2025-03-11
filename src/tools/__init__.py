# This file makes the tools directory a Python package

# Import all tool registration functions
from src.tools.docker import register_docker_tools
from src.tools.array import register_array_tools
from src.tools.vms import register_vm_tools
from src.tools.formatting import register_formatting_tools

# Expose all registration functions in a single function
def register_all_tools(server, unraid_client):
    """Register all tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    register_docker_tools(server, unraid_client)
    register_array_tools(server, unraid_client)
    register_vm_tools(server, unraid_client)
    register_formatting_tools(server, unraid_client)
