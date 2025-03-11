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

# Add user-friendly formatting tools that wrap resources

@server.tool(description="Get formatted system information in a human-readable format")
async def get_formatted_system_info(ctx=None):
    """Get system information from Unraid server in a readable format"""
    if ctx:
        await ctx.info("Retrieving system information...")
    else:
        print("Retrieving system information...")
    
    try:
        # Get the data from the resource
        result = await system_info()
        
        if "error" in result:
            return TextContent(text=f"❌ Error: {result['error']}")
            
        # Format the data nicely
        formatted_text = "📊 UNRAID SYSTEM INFORMATION\n"
        formatted_text += "══════════════════════════\n\n"
        
        # System info
        formatted_text += "🖥️  SYSTEM\n"
        formatted_text += f"  • Manufacturer: {result['system']['manufacturer']}\n"
        formatted_text += f"  • Model: {result['system']['model']}\n"
        formatted_text += f"  • Hostname: {result['os']['hostname']}\n\n"
        
        # CPU info
        formatted_text += "🔄 CPU\n"
        formatted_text += f"  • {result['cpu']['brand']}\n"
        formatted_text += f"  • {result['cpu']['cores']} cores, {result['cpu']['threads']} threads\n"
        formatted_text += f"  • Base speed: {result['cpu']['speed']} GHz\n"
        formatted_text += f"  • Max speed: {result['cpu']['speedmax']} GHz\n\n"
        
        # Memory info - convert to GB for readability
        total_gb = round(result['memory']['total'] / (1024**3), 1)
        free_gb = round(result['memory']['free'] / (1024**3), 1)
        used_gb = round(result['memory']['used'] / (1024**3), 1)
        available_gb = round(result['memory']['available'] / (1024**3), 1)
        
        formatted_text += "🧠 MEMORY\n"
        formatted_text += f"  • Total: {total_gb} GB\n"
        formatted_text += f"  • Used: {used_gb} GB\n"
        formatted_text += f"  • Free: {free_gb} GB\n"
        formatted_text += f"  • Available: {available_gb} GB\n\n"
        
        # OS info
        formatted_text += "💻 OPERATING SYSTEM\n"
        formatted_text += f"  • {result['os']['distro']} {result['os']['release']}\n"
        formatted_text += f"  • Unraid Version: {result['versions']['unraid']}\n"
        formatted_text += f"  • Kernel: {result['versions']['kernel']}\n"
        formatted_text += f"  • Docker Version: {result['versions']['docker']}\n"
        
        return TextContent(text=formatted_text)
    except Exception as e:
        error_msg = f"Error formatting system information: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error: {str(e)}")

@server.tool(description="List Docker containers in a formatted, human-readable way")
async def list_formatted_containers(ctx=None):
    """List all Docker containers with their status in a readable format"""
    if ctx:
        await ctx.info("Retrieving Docker containers...")
    else:
        print("Retrieving Docker containers...")
    
    try:
        # Get the data from the resource
        result = await docker_containers()
        
        if isinstance(result, dict) and "error" in result:
            return TextContent(text=f"❌ Error: {result['error']}")
            
        # Format the data nicely
        formatted_text = "🐳 DOCKER CONTAINERS\n"
        formatted_text += "══════════════════\n\n"
        
        # Group containers by state
        running = []
        stopped = []
        other = []
        
        for container in result:
            if container["state"] == "RUNNING":
                running.append(container)
            elif container["state"] == "EXITED":
                stopped.append(container)
            else:
                other.append(container)
        
        # Display running containers
        formatted_text += f"✅ RUNNING CONTAINERS ({len(running)})\n"
        if running:
            for container in running:
                name = container["names"][0].replace("/", "") if container["names"] else "Unnamed"
                image = container["image"]
                status = container["status"]
                ports = []
                for port in container.get("ports", []):
                    if port.get("publicPort"):
                        ports.append(f"{port['publicPort']}:{port.get('privatePort', '?')}")
                ports_str = ", ".join(ports) if ports else "No published ports"
                
                formatted_text += f"  • {name}\n"
                formatted_text += f"    Image: {image}\n"
                formatted_text += f"    Status: {status}\n"
                formatted_text += f"    Ports: {ports_str}\n\n"
        else:
            formatted_text += "  None\n\n"
            
        # Display stopped containers
        formatted_text += f"❌ STOPPED CONTAINERS ({len(stopped)})\n"
        if stopped:
            for container in stopped:
                name = container["names"][0].replace("/", "") if container["names"] else "Unnamed"
                image = container["image"]
                status = container["status"]
                
                formatted_text += f"  • {name}\n"
                formatted_text += f"    Image: {image}\n"
                formatted_text += f"    Status: {status}\n\n"
        else:
            formatted_text += "  None\n\n"
            
        # Display other containers
        if other:
            formatted_text += f"⚠️ OTHER CONTAINERS ({len(other)})\n"
            for container in other:
                name = container["names"][0].replace("/", "") if container["names"] else "Unnamed"
                state = container["state"]
                status = container["status"]
                
                formatted_text += f"  • {name}\n"
                formatted_text += f"    State: {state}\n"
                formatted_text += f"    Status: {status}\n\n"
        
        return TextContent(text=formatted_text)
    except Exception as e:
        error_msg = f"Error formatting container list: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error: {str(e)}")

@server.tool(description="Get formatted array status in a human-readable way")
async def get_formatted_array_status(ctx=None):
    """Get array status information in a readable format"""
    if ctx:
        await ctx.info("Retrieving array status...")
    else:
        print("Retrieving array status...")
    
    try:
        # Get the data from the resource
        result = await array_status()
        
        if isinstance(result, dict) and "error" in result:
            return TextContent(text=f"❌ Error: {result['error']}")
            
        # Format the data nicely
        formatted_text = "💾 UNRAID ARRAY STATUS\n"
        formatted_text += "═══════════════════\n\n"
        
        # Array state
        state = result["state"]
        state_emoji = "✅" if state == "STARTED" else "⚠️"
        formatted_text += f"Array State: {state_emoji} {state}\n\n"
        
        # Capacity information
        if "capacity" in result:
            capacity = result["capacity"]
            # Convert KB to GB
            total_gb = round(int(capacity["kilobytes"]["total"]) / (1024**2), 2)
            used_gb = round(int(capacity["kilobytes"]["used"]) / (1024**2), 2)
            free_gb = round(int(capacity["kilobytes"]["free"]) / (1024**2), 2)
            
            used_percent = round((used_gb / total_gb) * 100) if total_gb > 0 else 0
            
            formatted_text += "CAPACITY\n"
            formatted_text += f"  • Total Size: {total_gb:.2f} TB\n"
            formatted_text += f"  • Used: {used_gb:.2f} TB ({used_percent}%)\n"
            formatted_text += f"  • Free: {free_gb:.2f} TB\n"
            formatted_text += f"  • Disks: {capacity['disks']['used']}/{capacity['disks']['total']} disks used\n\n"
        
        # Disk information
        if "disks" in result:
            disks = result["disks"]
            formatted_text += f"ARRAY DISKS ({len(disks)})\n"
            
            for disk in disks:
                # Convert bytes to GB/TB
                size_tb = round(disk["size"] / (1024**3), 2)
                
                if "fsSize" in disk and "fsFree" in disk and "fsUsed" in disk:
                    fs_size_tb = round(disk["fsSize"] / (1024**3), 2)
                    fs_used_tb = round(disk["fsUsed"] / (1024**3), 2)
                    fs_free_tb = round(disk["fsFree"] / (1024**3), 2)
                    used_percent = round((fs_used_tb / fs_size_tb) * 100) if fs_size_tb > 0 else 0
                    
                    formatted_text += f"  • {disk['name']} - {size_tb:.2f} TB ({disk['status']})\n"
                    formatted_text += f"    {used_percent}% used ({fs_used_tb:.2f} TB used, {fs_free_tb:.2f} TB free)\n"
                    if "temp" in disk and disk["temp"] is not None:
                        formatted_text += f"    Temperature: {disk['temp']}°C\n"
                    formatted_text += "\n"
                else:
                    formatted_text += f"  • {disk['name']} - {size_tb:.2f} TB ({disk['status']})\n"
                    if "temp" in disk and disk["temp"] is not None:
                        formatted_text += f"    Temperature: {disk['temp']}°C\n"
                    formatted_text += "\n"
        
        # Cache information
        if "caches" in result:
            caches = result["caches"]
            formatted_text += f"CACHE DEVICES ({len(caches)})\n"
            
            for cache in caches:
                # Convert bytes to GB
                size_gb = round(cache["size"] / (1024**2), 2)
                formatted_text += f"  • {cache['name']} - {size_gb:.2f} GB ({cache['status']})\n"
                if "temp" in cache and cache["temp"] is not None:
                    formatted_text += f"    Temperature: {cache['temp']}°C\n"
                formatted_text += "\n"
        
        return TextContent(text=formatted_text)
    except Exception as e:
        error_msg = f"Error formatting array status: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error: {str(e)}")

@server.tool(description="List virtual machines in a formatted, human-readable way")
async def list_formatted_vms(ctx=None):
    """List all virtual machines with their status in a readable format"""
    if ctx:
        await ctx.info("Retrieving virtual machines...")
    else:
        print("Retrieving virtual machines...")
    
    try:
        # Get the data from the resource
        result = await virtual_machines()
        
        if isinstance(result, dict) and "error" in result:
            return TextContent(text=f"❌ Error: {result['error']}")
            
        # Format the data nicely
        formatted_text = "🖥️ UNRAID VIRTUAL MACHINES\n"
        formatted_text += "═════════════════════\n\n"
        
        # Group VMs by status
        running = []
        stopped = []
        
        for vm in result:
            if vm.get("status") == "running":
                running.append(vm)
            else:
                stopped.append(vm)
        
        # Display running VMs
        formatted_text += f"✅ RUNNING VMs ({len(running)})\n"
        if running:
            for vm in running:
                name = vm.get("name", "Unnamed")
                memory = vm.get("memory", "Unknown")
                cores = vm.get("cores", "Unknown")
                
                # Format memory as GB if it's a number
                memory_text = f"{int(memory)/1024:.1f} GB" if isinstance(memory, (int, float)) else memory
                
                formatted_text += f"  • {name}\n"
                if "template" in vm:
                    formatted_text += f"    Template: {vm['template']}\n"
                formatted_text += f"    Memory: {memory_text}\n"
                formatted_text += f"    Cores: {cores}\n\n"
        else:
            formatted_text += "  None\n\n"
            
        # Display stopped VMs
        formatted_text += f"❌ STOPPED VMs ({len(stopped)})\n"
        if stopped:
            for vm in stopped:
                name = vm.get("name", "Unnamed")
                memory = vm.get("memory", "Unknown")
                cores = vm.get("cores", "Unknown")
                
                # Format memory as GB if it's a number
                memory_text = f"{int(memory)/1024:.1f} GB" if isinstance(memory, (int, float)) else memory
                
                formatted_text += f"  • {name}\n"
                if "template" in vm:
                    formatted_text += f"    Template: {vm['template']}\n"
                formatted_text += f"    Memory: {memory_text}\n"
                formatted_text += f"    Cores: {cores}\n\n"
        else:
            formatted_text += "  None\n\n"
        
        return TextContent(text=formatted_text)
    except Exception as e:
        error_msg = f"Error formatting VM list: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            print(error_msg)
        return TextContent(text=f"❌ Error: {str(e)}")

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
