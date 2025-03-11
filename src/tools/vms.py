"""Virtual Machine management tools for Unraid MCP server"""
from mcp.types import TextContent

def register_vm_tools(server, unraid_client):
    """Register VM-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.tool(description="Start a virtual machine by name")
    async def start_vm(
        vm_name: str, 
        ctx=None
    ):
        """Start a virtual machine by name
        
        Args:
            vm_name: The name of the virtual machine to start
        """
        if ctx:
            await ctx.info(f"Starting VM: {vm_name}")
        else:
            print(f"Starting VM: {vm_name}")
        
        mutation = """
        mutation ($name: String!) {
          vms {
            startVM(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": vm_name}
        
        try:
            result = await unraid_client.execute_query(mutation, variables)
            
            response = result["data"]["vms"]["startVM"]
            if response["success"]:
                return TextContent(type="text", text=f"✅ VM {vm_name} started successfully")
            else:
                return TextContent(type="text", text=f"❌ Failed to start VM: {response['message']}")
        except Exception as e:
            error_msg = f"Error starting VM: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")

    @server.tool(description="Stop a virtual machine by name")
    async def stop_vm(
        vm_name: str, 
        ctx=None
    ):
        """Stop a virtual machine by name
        
        Args:
            vm_name: The name of the virtual machine to stop
        """
        if ctx:
            await ctx.info(f"Stopping VM: {vm_name}")
        else:
            print(f"Stopping VM: {vm_name}")
        
        mutation = """
        mutation ($name: String!) {
          vms {
            stopVM(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": vm_name}
        
        try:
            result = await unraid_client.execute_query(mutation, variables)
            
            response = result["data"]["vms"]["stopVM"]
            if response["success"]:
                return TextContent(type="text", text=f"✅ VM {vm_name} stopped successfully")
            else:
                return TextContent(type="text", text=f"❌ Failed to stop VM: {response['message']}")
        except Exception as e:
            error_msg = f"Error stopping VM: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}")
