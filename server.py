from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from unraid_client import UnraidClient, UnraidApiError
import json
import asyncio
from typing import Optional, List, Dict, Any, Union
import os
from dotenv import load_dotenv

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
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.get_system_info()
        return result
    except UnraidApiError as e:
        # Return error as JSON instead of using ErrorDiagnostic
        return {"error": f"Failed to retrieve system information: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving system information: {str(e)}"}

@server.resource("unraid://docker/containers",
                name="Docker Containers",
                description="List of all Docker containers with their status",
                mime_type="application/json")
async def docker_containers():
    """List all Docker containers and their status"""
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.get_docker_containers()
        return result
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve Docker containers: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving Docker containers: {str(e)}"}

# Define tools

@server.tool(description="Start a Docker container by name")
async def start_container(
    container_name: str, 
    ctx=None
):
    """Start a Docker container by name
    
    Args:
        container_name: The name of the container to start
    """
    if ctx:
        await ctx.info(f"Starting container: {container_name}")
    else:
        print(f"Starting container: {container_name}")
    
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
    except UnraidApiError as e:
        error_msg = f"API error starting container: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error starting container: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.tool(description="Stop a Docker container by name")
async def stop_container(
    container_name: str,
    ctx=None
):
    """Stop a Docker container by name
    
    Args:
        container_name: The name of the container to stop
    """
    if ctx:
        await ctx.info(f"Stopping container: {container_name}")
    else:
        print(f"Stopping container: {container_name}")
    
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
    except UnraidApiError as e:
        error_msg = f"API error stopping container: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error stopping container: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.resource("unraid://array/status",
                name="Array Status",
                description="Current array status information",
                mime_type="application/json")
async def array_status():
    """Get current array status information"""
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.get_array_status()
        return result
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve array status: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving array status: {str(e)}"}

@server.resource("unraid://vms/list",
                name="Virtual Machines",
                description="List of all virtual machines and their status",
                mime_type="application/json")
async def virtual_machines():
    """List all virtual machines and their status"""
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.get_vms()
        return result
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve virtual machines: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving virtual machines: {str(e)}"}

@server.tool(description="Start the Unraid array")
async def start_array(ctx=None):
    """Start the Unraid array"""
    if ctx:
        await ctx.info("Starting array...")
    else:
        print("Starting array...")
    
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.start_array()
        return TextContent(text="✅ Array started successfully")
    except UnraidApiError as e:
        error_msg = f"API error starting array: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error starting array: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.tool(description="Stop the Unraid array")
async def stop_array(ctx=None):
    """Stop the Unraid array"""
    if ctx:
        await ctx.info("Stopping array...")
    else:
        print("Stopping array...")
    
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.stop_array()
        return TextContent(text="✅ Array stopped successfully")
    except UnraidApiError as e:
        error_msg = f"API error stopping array: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error stopping array: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

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
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["vms"]["startVM"]
        if response["success"]:
            return TextContent(text=f"✅ VM {vm_name} started successfully")
        else:
            return TextContent(text=f"❌ Failed to start VM: {response['message']}")
    except UnraidApiError as e:
        error_msg = f"API error starting VM: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error starting VM: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

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
        result = await unraid.execute_query(mutation, variables)
        
        response = result["data"]["vms"]["stopVM"]
        if response["success"]:
            return TextContent(text=f"✅ VM {vm_name} stopped successfully")
        else:
            return TextContent(text=f"❌ Failed to stop VM: {response['message']}")
    except UnraidApiError as e:
        error_msg = f"API error stopping VM: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ API error: {str(e)}")
    except Exception as e:
        error_msg = f"Error stopping VM: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error occurred: {str(e)}")

@server.resource("unraid://storage/shares",
                name="Shares",
                description="List of all user shares on the Unraid server",
                mime_type="application/json")
async def shares():
    """List all user shares"""
    try:
        # Use the client's method instead of raw GraphQL
        result = await unraid.get_shares()
        return result
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve shares: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving shares: {str(e)}"}

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
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve plugins: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving plugins: {str(e)}"}

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
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve VM details for {vm_name}: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving VM details for {vm_name}: {str(e)}"}

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
    except UnraidApiError as e:
        return {"error": f"Failed to retrieve container details for {container_name}: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving container details for {container_name}: {str(e)}"}

# Set up logging for the server
import logging
logger = logging.getLogger("unraid_mcp")
logger.info("Initialized Unraid MCP Server")

# Run the server with appropriate transport
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get server configuration from environment variables
    host = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_SERVER_PORT", "8400"))
    
    print(f"Starting Unraid MCP Server (MCP 1.3.0 uses default host/port)")
    
    # Set up logging for the server
    import logging
    logger = logging.getLogger("unraid_mcp")
    logger.info("Server initialization complete, ready to process requests")
    
    # Detect if running under Claude/Cline
    claude_mode = os.getenv("CLAUDE_MCP_SERVER", "false").lower() in ("true", "1", "yes")
    
    if claude_mode:
        print("Detected Claude/Cline environment, using stdio transport")
        server.run(transport="stdio")
    else:
        print("Using SSE transport on port", port)
        server.run(transport="sse")
