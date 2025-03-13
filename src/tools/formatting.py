"""Display tools for Unraid MCP server"""
from mcp.types import TextContent
import logging

# Get logger
logger = logging.getLogger("unraid_mcp.display_tools")

def register_formatting_tools(server, unraid_client):
    """Register formatting tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering display tools")
    
    @server.tool(description="Get system information in a human-readable format")
    async def get_system_info(ctx=None):
        """Get system information from Unraid server in a readable format"""
        logger.info("Tool called: get_system_info()")
        
        if ctx:
            await ctx.info("Retrieving system information...")
        else:
            print("Retrieving system information...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_system_info()
            logger.debug(f"System info result received with keys: {list(result.keys())}")
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error in system info response: {result['error']}")
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
            formatted_text += "🐧 OPERATING SYSTEM\n"
            formatted_text += f"  • Distro: {result['os']['distro']}\n"
            formatted_text += f"  • Release: {result['os']['release']}\n"
            formatted_text += f"  • Kernel: {result['os']['kernel']}\n"
            formatted_text += f"  • Uptime: {result['os']['uptime']}\n\n"
            
            # Unraid version
            formatted_text += "🔄 UNRAID VERSION\n"
            formatted_text += f"  • Version: {result['versions']['unraid']}\n"
            
            logger.info("System info formatted successfully")
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_message = f"❌ Error retrieving system information: {str(e)}"
            logger.error(f"Error formatting system info: {str(e)}", exc_info=True)
            return TextContent(type="text", text=error_message)
    
    @server.tool(description="List Docker containers in a human-readable way")
    async def list_containers(ctx=None):
        """List Docker containers in a readable format"""
        logger.info("Tool called: list_containers()")
        
        if ctx:
            await ctx.info("Retrieving Docker containers...")
        else:
            print("Retrieving Docker containers...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_docker_containers()
            logger.debug(f"Retrieved {len(result)} Docker containers")
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error in Docker containers response: {result['error']}")
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
            
            # Format the data nicely
            formatted_text = "🐳 DOCKER CONTAINERS\n"
            formatted_text += "══════════════════\n\n"
            
            # Count running and total containers
            running_count = sum(1 for container in result if container['state'] == 'RUNNING')
            total_count = len(result)
            
            formatted_text += f"📊 Status: {running_count} running out of {total_count} total containers\n\n"
            
            # Sort containers by state (running first) and then by name
            sorted_containers = sorted(
                result,
                key=lambda c: (0 if c['state'] == 'RUNNING' else 1, c['names'][0].lower() if c['names'] else '')
            )
            
            # Group containers by state
            for container in sorted_containers:
                # Get the first name (usually the main name)
                name = container['names'][0] if container['names'] else 'Unnamed'
                
                # Status emoji based on state
                status_emoji = "🟢" if container['state'] == 'RUNNING' else "🔴"
                
                # Format container info
                formatted_text += f"{status_emoji} {name}\n"
                formatted_text += f"  • State: {container['state']}\n"
                formatted_text += f"  • Image: {container['image']}\n"
                
                # Add port mappings if available
                if container['ports'] and len(container['ports']) > 0:
                    formatted_text += "  • Ports: "
                    port_mappings = []
                    for port in container['ports']:
                        if 'publicPort' in port and port['publicPort']:
                            mapping = f"{port['publicPort']}:{port['privatePort']}"
                            if 'ip' in port and port['ip']:
                                mapping = f"{port['ip']}:{mapping}"
                            port_mappings.append(mapping)
                    
                    if port_mappings:
                        formatted_text += ", ".join(port_mappings)
                    else:
                        formatted_text += "None"
                    formatted_text += "\n"
                
                # Add auto-start info
                auto_start = "Yes" if container.get('autoStart', False) else "No"
                formatted_text += f"  • Auto-start: {auto_start}\n\n"
            
            logger.info("Docker containers formatted successfully")
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_message = f"❌ Error retrieving Docker containers: {str(e)}"
            logger.error(f"Error formatting Docker containers: {str(e)}", exc_info=True)
            return TextContent(type="text", text=error_message)
    
    @server.tool(description="Get formatted array status in a human-readable way")
    async def format_array_status(ctx=None):
        """Get array status in a readable, formatted display"""
        logger.info("Tool called: format_array_status()")
        
        if ctx:
            await ctx.info("Retrieving array status...")
        else:
            print("Retrieving array status...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_array_status()
            logger.debug(f"Array status result received with keys: {list(result.keys())}")
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error in array status response: {result['error']}")
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
            
            # Format the data nicely
            formatted_text = "💾 UNRAID ARRAY STATUS\n"
            formatted_text += "═════════════════════\n\n"
            
            # Array state
            state_emoji = "🟢" if result['state'] == 'STARTED' else "🔴"
            formatted_text += f"{state_emoji} Array State: {result['state']}\n\n"
            
            # Array capacity
            if 'capacity' in result and 'kilobytes' in result['capacity']:
                capacity = result['capacity']['kilobytes']
                # Convert to more readable units (GB)
                total_gb = round(float(capacity['total']) / (1024 * 1024), 2)
                used_gb = round(float(capacity['used']) / (1024 * 1024), 2)
                free_gb = round(float(capacity['free']) / (1024 * 1024), 2)
                
                # Calculate usage percentage
                usage_percent = round((used_gb / total_gb) * 100, 1) if total_gb > 0 else 0
                
                formatted_text += "💽 CAPACITY\n"
                formatted_text += f"  • Total: {total_gb} TB\n"
                formatted_text += f"  • Used: {used_gb} TB ({usage_percent}%)\n"
                formatted_text += f"  • Free: {free_gb} TB\n\n"
            
            # Parity disks
            if 'parities' in result and result['parities']:
                formatted_text += "🛡️ PARITY DISKS\n"
                for parity in result['parities']:
                    size_tb = round(parity['size'] / (1024 * 1024 * 1024), 2)
                    formatted_text += f"  • {parity['name']}: {size_tb} TB"
                    
                    if 'temp' in parity and parity['temp'] is not None:
                        formatted_text += f", {parity['temp']}°C"
                    
                    if 'numErrors' in parity:
                        error_text = f", Errors: {parity['numErrors']}"
                        formatted_text += error_text
                    
                    formatted_text += "\n"
                formatted_text += "\n"
            
            # Data disks
            if 'disks' in result and result['disks']:
                formatted_text += "💿 DATA DISKS\n"
                for disk in result['disks']:
                    # Skip if no name (might be an empty slot)
                    if not disk.get('name'):
                        continue
                    
                    # Get disk size in TB
                    size_tb = round(disk['size'] / (1024 * 1024 * 1024), 2)
                    
                    # Calculate usage if available
                    usage_info = ""
                    if 'fsSize' in disk and disk['fsSize'] and 'fsUsed' in disk and disk['fsUsed']:
                        usage_percent = round((disk['fsUsed'] / disk['fsSize']) * 100, 1)
                        usage_info = f", Used: {usage_percent}%"
                    
                    # Format disk info
                    formatted_text += f"  • {disk['name']}: {size_tb} TB{usage_info}"
                    
                    # Add temperature if available
                    if 'temp' in disk and disk['temp'] is not None:
                        formatted_text += f", {disk['temp']}°C"
                    
                    # Add error count if available
                    if 'numErrors' in disk:
                        error_text = f", Errors: {disk['numErrors']}"
                        formatted_text += error_text
                    
                    formatted_text += "\n"
                formatted_text += "\n"
            
            # Cache pools
            if 'caches' in result and result['caches']:
                formatted_text += "🔄 CACHE POOLS\n"
                for cache in result['caches']:
                    # Skip if no name (might be an empty slot)
                    if not cache.get('name'):
                        continue
                    
                    # Get cache size in TB
                    size_tb = round(cache['size'] / (1024 * 1024 * 1024), 2)
                    
                    # Format cache info
                    formatted_text += f"  • {cache['name']}: {size_tb} TB"
                    
                    # Add temperature if available
                    if 'temp' in cache and cache['temp'] is not None:
                        formatted_text += f", {cache['temp']}°C"
                    
                    # Add error count if available
                    if 'numErrors' in cache:
                        error_text = f", Errors: {cache['numErrors']}"
                        formatted_text += error_text
                    
                    formatted_text += "\n"
            
            logger.info("Array status formatted successfully")
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_message = f"❌ Error retrieving array status: {str(e)}"
            logger.error(f"Error formatting array status: {str(e)}", exc_info=True)
            return TextContent(type="text", text=error_message)
    
    @server.tool(description="List virtual machines in a human-readable way")
    async def list_vms(ctx=None):
        """List virtual machines in a readable format"""
        logger.info("Tool called: list_vms()")
        
        if ctx:
            await ctx.info("Retrieving virtual machines...")
        else:
            print("Retrieving virtual machines...")
        
        try:
            # Get the data directly from the client
            result = await unraid_client.get_vms()
            logger.debug(f"VM result received: {result}")
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Error in VMs response: {result['error']}")
                return TextContent(type="text", text=f"❌ Error: {result['error']}")
            
            # Format the data nicely
            formatted_text = "🖥️ VIRTUAL MACHINES\n"
            formatted_text += "══════════════════\n\n"
            
            # Check if we have any VMs
            if not result or not result.get('domain'):
                logger.info("No virtual machines found")
                return TextContent(type="text", text=formatted_text + "No virtual machines found.")
            
            # Count running and total VMs
            vms = result['domain']
            running_count = sum(1 for vm in vms if vm['state'] == 'RUNNING')
            total_count = len(vms)
            
            formatted_text += f"📊 Status: {running_count} running out of {total_count} total VMs\n\n"
            
            # Sort VMs by state (running first) and then by name
            sorted_vms = sorted(
                vms,
                key=lambda vm: (0 if vm['state'] == 'RUNNING' else 1, vm.get('name', '').lower())
            )
            
            # List each VM with its status
            for vm in sorted_vms:
                # Status emoji based on state
                status_emoji = "🟢" if vm['state'] == 'RUNNING' else "🔴"
                
                # VM name or UUID if name is not available
                name = vm.get('name', vm['uuid'])
                
                # Format VM info
                formatted_text += f"{status_emoji} {name}\n"
                formatted_text += f"  • State: {vm['state']}\n"
                formatted_text += f"  • UUID: {vm['uuid']}\n\n"
            
            logger.info("VMs formatted successfully")
            return TextContent(type="text", text=formatted_text)
        except Exception as e:
            error_message = f"❌ Error retrieving virtual machines: {str(e)}"
            logger.error(f"Error formatting VMs: {str(e)}", exc_info=True)
            return TextContent(type="text", text=error_message)
    
    # Log that tools were registered
    logger.info("Display tools registered successfully")
