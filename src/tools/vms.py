"""Virtual Machine management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import json
import traceback

# Get logger
logger = logging.getLogger("unraid_mcp.vm_tools")

def register_vm_tools(server, unraid_client):
    """Register VM-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering VM tools")
    
    @server.tool(description="Get detailed information about a specific virtual machine")
    async def get_vm_details(
        vm_name: str,
        ctx=None
    ):
        """Get detailed information about a specific virtual machine
        
        Args:
            vm_name: The name of the virtual machine
            
        Returns:
            Detailed information about the specified virtual machine
        """
        logger.info(f"Tool called: get_vm_details({vm_name})")
        
        if ctx:
            await ctx.info(f"Retrieving details for VM: {vm_name}")
        else:
            print(f"Retrieving details for VM: {vm_name}")
        
        # The API doesn't support filtering by name directly, so get all VMs and filter in code
        query = """
        query {
          vms {
            domain {
              uuid
              name
              state
            }
          }
        }
        """
        
        try:
            # Get all VMs and filter by name in code
            result = await unraid_client.execute_query(query)
            logger.debug(f"VM details query result: {result}")
            
            # More robust response handling with safer access methods
            if isinstance(result, dict):
                # If there's an error, return it
                if "error" in result:
                    logger.error(f"Error in VM details response: {result['error']}")
                    return TextContent(type="text", text=f"❌ Error: {result['error']}")
                
                # Check for VM data in different possible locations
                vm_details = None
                
                # Try different possible response structures
                if "data" in result and "vms" in result.get("data", {}) and "domain" in result.get("data", {}).get("vms", {}):
                    vm_details = result["data"]["vms"]["domain"]
                elif "vms" in result and "domain" in result.get("vms", {}):
                    vm_details = result["vms"]["domain"]
                
                if vm_details:
                    # Filter by name (case-insensitive)
                    matching_vms = [vm for vm in vm_details if vm.get('name', '').lower() == vm_name.lower()]
                    
                    if matching_vms:
                        logger.info(f"Found VM matching name: {vm_name}")
                        vm = matching_vms[0]
                        
                        # Format the VM details in a human-readable way
                        formatted_text = f"🖥️ VIRTUAL MACHINE: {vm.get('name', 'Unknown')}\n"
                        formatted_text += "══════════════════════════════\n\n"
                        
                        # Status with emoji
                        status_emoji = "🟢" if vm.get('state') == 'RUNNING' else "🔴"
                        formatted_text += f"{status_emoji} Status: {vm.get('state', 'Unknown')}\n\n"
                        
                        # Basic information
                        formatted_text += "📋 DETAILS\n"
                        formatted_text += f"  • UUID: {vm.get('uuid', 'Unknown')}\n"
                        
                        # Add any additional fields that might be available
                        if 'memory' in vm:
                            memory_gb = round(vm.get('memory', 0) / 1024 / 1024, 2)
                            formatted_text += f"  • Memory: {memory_gb} GB\n"
                        
                        if 'vcpus' in vm:
                            formatted_text += f"  • vCPUs: {vm.get('vcpus', 'Unknown')}\n"
                            
                        if 'diskSize' in vm:
                            disk_gb = round(vm.get('diskSize', 0) / 1024 / 1024 / 1024, 2)
                            formatted_text += f"  • Disk Size: {disk_gb} GB\n"
                        
                        return TextContent(type="text", text=formatted_text)
                    else:
                        logger.warning(f"VM with name '{vm_name}' not found")
                        # Show list of available VMs
                        available_vms = [vm.get('name', vm.get('uuid', 'Unknown')) for vm in vm_details]
                        formatted_text = f"❌ VM '{vm_name}' not found\n\n"
                        formatted_text += "Available VMs:\n"
                        for vm_name in available_vms:
                            formatted_text += f"  • {vm_name}\n"
                        return TextContent(type="text", text=formatted_text)
            
            # If we've reached here, we couldn't find usable data
            logger.warning(f"Failed to retrieve details for VM {vm_name}: Invalid response format")
            # Return as much data as we can rather than just an error
            return TextContent(type="text", text=f"⚠️ VM details may be incomplete or in unexpected format:\n{json.dumps(result, indent=2)}")
        except Exception as e:
            error_msg = f"Error retrieving VM details: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
    
    # Log that tools were registered
    logger.info("VM tools registered successfully")
