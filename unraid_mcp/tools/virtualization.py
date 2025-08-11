"""Virtual machine management tools.

This module provides tools for VM lifecycle management and monitoring
including listing VMs, VM operations (start/stop/pause/reboot/etc),
and detailed VM information retrieval.
"""

from typing import Any, Dict, List

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_vm_tools(mcp: FastMCP):
    """Register all VM tools with the FastMCP instance.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    async def list_vms() -> List[Dict[str, Any]]:
        """Lists all Virtual Machines (VMs) on the Unraid system and their current state.
        
        Returns:
            List of VM information dictionaries with UUID, name, and state
        """
        query = """
        query ListVMs {
          vms {
            id
            domains {
              id
              name
              state
              uuid
            }
          }
        }
        """
        try:
            logger.info("Executing list_vms tool")
            response_data = await make_graphql_request(query)
            logger.info(f"VM query response: {response_data}")
            if response_data.get("vms") and response_data["vms"].get("domains"):
                vms = response_data["vms"]["domains"]
                logger.info(f"Found {len(vms)} VMs")
                return vms
            else:
                logger.info("No VMs found in domains field")
                return []
        except Exception as e:
            logger.error(f"Error in list_vms: {e}", exc_info=True)
            error_msg = str(e)
            if "VMs are not available" in error_msg:
                raise ToolError("VMs are not available on this Unraid server. This could mean: 1) VM support is not enabled, 2) VM service is not running, or 3) no VMs are configured. Check Unraid VM settings.")
            else:
                raise ToolError(f"Failed to list virtual machines: {error_msg}")

    @mcp.tool()
    async def manage_vm(vm_uuid: str, action: str) -> Dict[str, Any]:
        """Manages a VM: start, stop, pause, resume, force_stop, reboot, reset. Uses VM UUID.
        
        Args:
            vm_uuid: UUID of the VM to manage
            action: Action to perform - one of: start, stop, pause, resume, forceStop, reboot, reset
            
        Returns:
            Dict containing operation success status and details
        """
        valid_actions = ["start", "stop", "pause", "resume", "forceStop", "reboot", "reset"] # Added reset operation
        if action not in valid_actions:
            logger.warning(f"Invalid action '{action}' for manage_vm")
            raise ToolError(f"Invalid action. Must be one of {valid_actions}.")

        mutation_name = action
        query = f"""
        mutation ManageVM($id: PrefixedID!) {{
          vm {{
            {mutation_name}(id: $id)
          }}
        }}
        """
        variables = {"id": vm_uuid}
        try:
            logger.info(f"Executing manage_vm tool: action={action}, uuid={vm_uuid}")
            response_data = await make_graphql_request(query, variables)
            if response_data.get("vm") and mutation_name in response_data["vm"]:
                # Mutations for VM return Boolean for success
                success = response_data["vm"][mutation_name]
                return {"success": success, "action": action, "vm_uuid": vm_uuid}
            raise ToolError(f"Failed to {action} VM or unexpected response structure.")
        except Exception as e:
            logger.error(f"Error in manage_vm ({action}): {e}", exc_info=True)
            raise ToolError(f"Failed to {action} virtual machine: {str(e)}")

    @mcp.tool()
    async def get_vm_details(vm_identifier: str) -> Dict[str, Any]:
        """Retrieves detailed information for a specific VM by its UUID or name.
        
        Args:
            vm_identifier: VM UUID or name to retrieve details for
            
        Returns:
            Dict containing detailed VM information
        """
        # Make direct GraphQL call instead of calling list_vms() tool
        query = """
        query GetVmDetails {
          vms {
            domains {
              id
              name
              state
              uuid
            }
            domain {
              id
              name
              state
              uuid
            }
          }
        }
        """
        try:
            logger.info(f"Executing get_vm_details for identifier: {vm_identifier}")
            response_data = await make_graphql_request(query)
            
            if response_data.get("vms"):
                vms_data = response_data["vms"]
                # Try to get VMs from either domains or domain field
                vms = vms_data.get("domains") or vms_data.get("domain") or []
                
                if vms:
                    for vm_data in vms:
                        if (vm_data.get("uuid") == vm_identifier or 
                            vm_data.get("id") == vm_identifier or 
                            vm_data.get("name") == vm_identifier):
                            logger.info(f"Found VM {vm_identifier}")
                            return vm_data
                    
                    logger.warning(f"VM with identifier '{vm_identifier}' not found.")
                    available_vms = [f"{vm.get('name')} (UUID: {vm.get('uuid')}, ID: {vm.get('id')})" for vm in vms]
                    raise ToolError(f"VM '{vm_identifier}' not found. Available VMs: {', '.join(available_vms)}")
                else:
                    raise ToolError("No VMs available or VMs not accessible")
            else:
                raise ToolError("No VMs data returned from server")

        except Exception as e:
            logger.error(f"Error in get_vm_details: {e}", exc_info=True)
            error_msg = str(e)
            if "VMs are not available" in error_msg:
                raise ToolError("VMs are not available on this Unraid server. This could mean: 1) VM support is not enabled, 2) VM service is not running, or 3) no VMs are configured. Check Unraid VM settings.")
            else:
                raise ToolError(f"Failed to retrieve VM details: {error_msg}")

    logger.info("VM tools registered successfully")