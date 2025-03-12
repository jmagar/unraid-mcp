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
    
    @server.tool(description="Get information about virtual machines")
    async def get_vms(
        ctx=None
    ):
        """Get information about all virtual machines
        
        Returns:
            Information about all virtual machines including their status
        """
        logger.info("Tool called: get_vms()")
        
        if ctx:
            await ctx.info("Retrieving virtual machine information...")
        else:
            print("Retrieving virtual machine information...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_vms()
            logger.debug(f"VM query result: {response}")
            
            if "data" in response and "vms" in response["data"] and "domain" in response["data"]["vms"]:
                vms = response["data"]["vms"]["domain"]
                logger.info(f"Retrieved information for {len(vms)} virtual machines")
                return TextContent(type="text", text=json.dumps(vms, indent=2))
            else:
                logger.warning("Failed to retrieve VM information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve VM information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving VM information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
    
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
        
        query = """
        query ($name: String!) {
          vms {
            domain(name: $name) {
              uuid
              name
              state
            }
          }
        }
        """
        variables = {"name": vm_name}
        
        try:
            result = await unraid_client.execute_query(query, variables)
            logger.debug(f"VM details query result: {result}")
            
            if "data" in result and "vms" in result["data"] and "domain" in result["data"]["vms"]:
                vm_details = result["data"]["vms"]["domain"]
                if vm_details:
                    logger.info(f"Retrieved details for VM {vm_name}")
                    return TextContent(type="text", text=json.dumps(vm_details, indent=2))
                else:
                    logger.warning(f"VM {vm_name} not found")
                    return TextContent(type="text", text=f"❌ VM {vm_name} not found")
            else:
                logger.warning(f"Failed to retrieve details for VM {vm_name}: Invalid response format")
                return TextContent(type="text", text=f"❌ Failed to retrieve details for VM {vm_name}: Invalid response format")
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
