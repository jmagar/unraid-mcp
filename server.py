from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from unraid_client import UnraidClient

# Initialize the client and server
unraid = UnraidClient()
server = FastMCP(
    name="Unraid MCP Server",
    instructions="Access and manage your Unraid server through natural language commands."
)

# Define resources

@server.resource("unraid://system-info", 
                name="System Information",
                description="Current system information including CPU, memory, and uptime",
                mime_type="application/json")
async def system_info():
    """Get current system information from Unraid server"""
    query = """
    query {
      system {
        hostname
        version
        cpuModel
        cpuCount
        cpuFrequency
        cpuUsage
        memoryTotal
        memoryUsed
        uptime
      }
    }
    """
    result = await unraid.execute_query(query)
    return result["data"]["system"]

@server.resource("unraid://docker/containers",
                name="Docker Containers",
                description="List of all Docker containers with their status",
                mime_type="application/json")
async def docker_containers():
    """List all Docker containers and their status"""
    query = """
    query {
      docker {
        containers {
          name
          status
          state
          image
          autostart
          created
        }
      }
    }
    """
    result = await unraid.execute_query(query)
    return result["data"]["docker"]["containers"]

# Define tools

@server.tool(description="Start a Docker container by name")
async def start_container(container_name: str, ctx):
    """Start a Docker container by name"""
    await ctx.info(f"Starting container: {container_name}")
    
    mutation = """
    mutation ($name: String!) {
      docker {
        startContainer(name: $name) {
          success
          message
        }
      }
    }
    """
    variables = {"name": container_name}
    result = await unraid.execute_query(mutation, variables)
    
    response = result["data"]["docker"]["startContainer"]
    if response["success"]:
        return TextContent(text=f"✅ Container {container_name} started successfully")
    else:
        return TextContent(text=f"❌ Failed to start container: {response['message']}")

@server.tool(description="Stop a Docker container by name")
async def stop_container(container_name: str, ctx):
    """Stop a Docker container by name"""
    await ctx.info(f"Stopping container: {container_name}")
    
    mutation = """
    mutation ($name: String!) {
      docker {
        stopContainer(name: $name) {
          success
          message
        }
      }
    }
    """
    variables = {"name": container_name}
    result = await unraid.execute_query(mutation, variables)
    
    response = result["data"]["docker"]["stopContainer"]
    if response["success"]:
        return TextContent(text=f"✅ Container {container_name} stopped successfully")
    else:
        return TextContent(text=f"❌ Failed to stop container: {response['message']}")

@server.resource("unraid://array-status",
                name="Array Status",
                description="Current array status information",
                mime_type="application/json")
async def array_status():
    """Get current array status information"""
    query = """
    query {
      array {
        status
        started
        protected
        size
        used
        free
        disks {
          name
          size
          free
          device
          status
        }
      }
    }
    """
    result = await unraid.execute_query(query)
    return result["data"]["array"]

@server.resource("unraid://virtual-machines",
                name="Virtual Machines",
                description="List of all virtual machines and their status",
                mime_type="application/json")
async def virtual_machines():
    """List all virtual machines and their status"""
    query = """
    query {
      vms {
        name
        status
        memory
        cores
        diskSize
        template
      }
    }
    """
    result = await unraid.execute_query(query)
    return result["data"]["vms"]

@server.tool(description="Start the Unraid array")
async def start_array(ctx):
    """Start the Unraid array"""
    await ctx.info("Starting array...")
    
    mutation = """
    mutation {
      array {
        start {
          success
          message
        }
      }
    }
    """
    result = await unraid.execute_query(mutation)
    
    response = result["data"]["array"]["start"]
    if response["success"]:
        return TextContent(text="✅ Array started successfully")
    else:
        return TextContent(text=f"❌ Failed to start array: {response['message']}")

@server.tool(description="Stop the Unraid array")
async def stop_array(ctx):
    """Stop the Unraid array"""
    await ctx.info("Stopping array...")
    
    mutation = """
    mutation {
      array {
        stop {
          success
          message
        }
      }
    }
    """
    result = await unraid.execute_query(mutation)
    
    response = result["data"]["array"]["stop"]
    if response["success"]:
        return TextContent(text="✅ Array stopped successfully")
    else:
        return TextContent(text=f"❌ Failed to stop array: {response['message']}")

@server.tool(description="Start a virtual machine by name")
async def start_vm(vm_name: str, ctx):
    """Start a virtual machine by name"""
    await ctx.info(f"Starting VM: {vm_name}")
    
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
    result = await unraid.execute_query(mutation, variables)
    
    response = result["data"]["vms"]["startVM"]
    if response["success"]:
        return TextContent(text=f"✅ VM {vm_name} started successfully")
    else:
        return TextContent(text=f"❌ Failed to start VM: {response['message']}")

@server.tool(description="Stop a virtual machine by name")
async def stop_vm(vm_name: str, ctx):
    """Stop a virtual machine by name"""
    await ctx.info(f"Stopping VM: {vm_name}")
    
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
    result = await unraid.execute_query(mutation, variables)
    
    response = result["data"]["vms"]["stopVM"]
    if response["success"]:
        return TextContent(text=f"✅ VM {vm_name} stopped successfully")
    else:
        return TextContent(text=f"❌ Failed to stop VM: {response['message']}")

# Run the server
if __name__ == "__main__":
    # For local development, use stdio transport
    server.run(transport="stdio") 