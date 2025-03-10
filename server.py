from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, ErrorDiagnostic
from unraid_client import UnraidClient
import json
import asyncio
from typing import Optional, List, Dict, Any, Union

# Initialize the client and server
unraid = UnraidClient()
server = FastMCP(
    name="Unraid MCP Server",
    instructions="Access and manage your Unraid server through natural language commands. You can query system information, manage Docker containers, VMs, and array operations."
)

# Define resources

@server.resource("unraid://system/info", 
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
    try:
        result = await unraid.execute_query(query)
        return result["data"]["system"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve system information: {str(e)}",
            code="SYSTEM_INFO_ERROR"
        )

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
    try:
        result = await unraid.execute_query(query)
        return result["data"]["docker"]["containers"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve Docker containers: {str(e)}",
            code="DOCKER_CONTAINERS_ERROR"
        )

# Define tools

@server.tool(description="Start a Docker container by name")
async def start_container(
    container_name: str, 
    ctx
):
    """Start a Docker container by name
    
    Args:
        container_name: The name of the container to start
    """
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
    
    try:
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["docker"]["startContainer"]
        if response["success"]:
            return TextContent(text=f"✅ Container {container_name} started successfully")
        else:
            return TextContent(text=f"❌ Failed to start container: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error starting container: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.tool(description="Stop a Docker container by name")
async def stop_container(
    container_name: str,
    ctx
):
    """Stop a Docker container by name
    
    Args:
        container_name: The name of the container to stop
    """
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
    
    try:
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["docker"]["stopContainer"]
        if response["success"]:
            return TextContent(text=f"✅ Container {container_name} stopped successfully")
        else:
            return TextContent(text=f"❌ Failed to stop container: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error stopping container: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.resource("unraid://array/status",
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
    try:
        result = await unraid.execute_query(query)
        return result["data"]["array"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve array status: {str(e)}",
            code="ARRAY_STATUS_ERROR"
        )

@server.resource("unraid://vms/list",
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
    try:
        result = await unraid.execute_query(query)
        return result["data"]["vms"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve virtual machines: {str(e)}",
            code="VM_LIST_ERROR"
        )

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
    try:
        result = await unraid.execute_query(mutation)
        
        response = result["data"]["array"]["start"]
        if response["success"]:
            return TextContent(text="✅ Array started successfully")
        else:
            return TextContent(text=f"❌ Failed to start array: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error starting array: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

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
    try:
        result = await unraid.execute_query(mutation)
        
        response = result["data"]["array"]["stop"]
        if response["success"]:
            return TextContent(text="✅ Array stopped successfully")
        else:
            return TextContent(text=f"❌ Failed to stop array: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error stopping array: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.tool(description="Start a virtual machine by name")
async def start_vm(
    vm_name: str, 
    ctx
):
    """Start a virtual machine by name
    
    Args:
        vm_name: The name of the virtual machine to start
    """
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
    
    try:
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["vms"]["startVM"]
        if response["success"]:
            return TextContent(text=f"✅ VM {vm_name} started successfully")
        else:
            return TextContent(text=f"❌ Failed to start VM: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error starting VM: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.tool(description="Stop a virtual machine by name")
async def stop_vm(
    vm_name: str, 
    ctx
):
    """Stop a virtual machine by name
    
    Args:
        vm_name: The name of the virtual machine to stop
    """
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
    
    try:
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["vms"]["stopVM"]
        if response["success"]:
            return TextContent(text=f"✅ VM {vm_name} stopped successfully")
        else:
            return TextContent(text=f"❌ Failed to stop VM: {response['message']}")
    except Exception as e:
        await ctx.error(f"Error stopping VM: {str(e)}")
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.resource("unraid://storage/shares",
                name="Shares",
                description="List of all user shares on the Unraid server",
                mime_type="application/json")
async def shares():
    """List all user shares"""
    query = """
    query {
      shares {
        name
        comment
        free
        size
        cache
        exportEnabled
      }
    }
    """
    try:
        result = await unraid.execute_query(query)
        return result["data"]["shares"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve shares: {str(e)}",
            code="SHARES_LIST_ERROR"
        )

@server.resource("unraid://system/plugins",
                name="Plugins",
                description="List of all installed plugins on the Unraid server",
                mime_type="application/json")
async def plugins():
    """List all installed plugins"""
    query = """
    query {
      plugins {
        name
        version
        author
        description
        status
      }
    }
    """
    try:
        result = await unraid.execute_query(query)
        return result["data"]["plugins"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve plugins: {str(e)}",
            code="PLUGINS_LIST_ERROR"
        )

# Add a resource for getting information about a specific VM by name
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
        result = await unraid.execute_query(query, variables)
        return result["data"]["vms"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve VM details for {vm_name}: {str(e)}",
            code="VM_DETAILS_ERROR"
        )

# Add a resource for getting information about a specific Docker container by name
@server.resource("unraid://docker/{container_name}",
                name="Docker Container Details",
                description="Get detailed information about a specific Docker container",
                mime_type="application/json")
async def container_details(container_name: str):
    """Get details for a specific Docker container
    
    Args:
        container_name: The name of the Docker container
    """
    query = """
    query ($name: String!) {
      docker {
        container(name: $name) {
          name
          status
          state
          image
          autostart
          created
          repository
          ports
          volumes
          environment
        }
      }
    }
    """
    variables = {"name": container_name}
    
    try:
        result = await unraid.execute_query(query, variables)
        return result["data"]["docker"]["container"]
    except Exception as e:
        return ErrorDiagnostic(
            message=f"Failed to retrieve container details for {container_name}: {str(e)}",
            code="CONTAINER_DETAILS_ERROR"
        )

# Run the server with appropriate transport
if __name__ == "__main__":
    # For local development, use stdio transport
    # In production, you might use the SSE transport instead
    server.run(transport="stdio") 