"""Formatted display tools for Unraid MCP server"""
from mcp.types import TextContent

def register_formatting_tools(server, unraid_client):
    """Register formatting tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.tool(description="Get formatted system information in a human-readable format")
    async def get_formatted_system_info(ctx=None):
        """Get system information from Unraid server in a readable format"""
        if ctx:
            await ctx.info("Retrieving system information...")
        else:
            print("Retrieving system information...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_system_info()
            
            if isinstance(result, dict) and "error" in result:
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
                
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
            
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_msg = f"Error formatting system information: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    @server.tool(description="List Docker containers in a formatted, human-readable way")
    async def list_formatted_containers(ctx=None):
        """List all Docker containers with their status in a readable format"""
        if ctx:
            await ctx.info("Retrieving Docker containers...")
        else:
            print("Retrieving Docker containers...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_docker_containers()
            
            if isinstance(result, dict) and "error" in result:
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
                
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
            
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_msg = f"Error formatting container list: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    @server.tool(description="Get formatted array status in a human-readable way")
    async def get_formatted_array_status(ctx=None):
        """Get array status information in a readable format"""
        if ctx:
            await ctx.info("Retrieving array status...")
        else:
            print("Retrieving array status...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_array_status()
            
            if isinstance(result, dict) and "error" in result:
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
                
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
            
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_msg = f"Error formatting array status: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    @server.tool(description="List virtual machines in a formatted, human-readable way")
    async def list_formatted_vms(ctx=None):
        """List all virtual machines with their status in a readable format"""
        if ctx:
            await ctx.info("Retrieving virtual machines...")
        else:
            print("Retrieving virtual machines...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_vms()
            
            if isinstance(result, dict) and "error" in result:
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
                
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
            
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_msg = f"Error formatting VM list: {str(e)}"
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error: {str(e)}")
