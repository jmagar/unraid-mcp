# This file makes the tools directory a Python package

# Import all tool registration functions
from src.tools.docker import register_docker_tools
from src.tools.array import register_array_tools
from src.tools.vms import register_vm_tools
from src.tools.formatting import register_formatting_tools
from src.tools.system import register_system_tools
from src.tools.notifications import register_notification_tools
from src.tools.shares import register_share_tools
from src.tools.disks import register_disk_tools
from src.tools.users import register_user_tools
from src.tools.apikeys import register_apikey_tools
from src.tools.remote_access import register_remote_access_tools
from src.tools.unassigned_devices import register_unassigned_devices_tools
from src.tools.parity import register_parity_tools

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
    register_system_tools(server, unraid_client)
    register_notification_tools(server, unraid_client)
    register_share_tools(server, unraid_client)
    register_disk_tools(server, unraid_client)
    register_user_tools(server, unraid_client)
    register_apikey_tools(server, unraid_client)
    register_remote_access_tools(server, unraid_client)
    register_unassigned_devices_tools(server, unraid_client)
    register_parity_tools(server, unraid_client)
