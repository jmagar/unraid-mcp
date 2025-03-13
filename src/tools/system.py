"""System management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.system_tools")

def register_system_tools(server, unraid_client):
    """Register system-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering system tools")
    
    @server.tool(description="Get detailed system information")
    async def get_system_info(
        ctx=None
    ):
        """Get detailed system information including CPU, memory, and system details
        
        Returns:
            Detailed system information
        """
        logger.info("Tool called: get_system_info()")
        
        if ctx:
            await ctx.info("Retrieving system information...")
        else:
            print("Retrieving system information...")
        
        try:
            # Use the client method directly
            response = await unraid_client.get_system_info()
            logger.debug(f"System info response: {response}")
            
            if "data" in response and "info" in response["data"]:
                info = response["data"]["info"]
                logger.info("Retrieved system information successfully")
                
                # Format the system information in a human-readable way
                formatted_text = "📊 UNRAID SYSTEM INFORMATION\n"
                formatted_text += "══════════════════════════\n\n"
                
                # System info
                formatted_text += "🖥️  SYSTEM\n"
                if "system" in info:
                    system = info["system"]
                    if "manufacturer" in system:
                        formatted_text += f"  • Manufacturer: {system['manufacturer']}\n"
                    if "model" in system:
                        formatted_text += f"  • Model: {system['model']}\n"
                    if "os" in info and "hostname" in info["os"]:
                        formatted_text += f"  • Hostname: {info['os']['hostname']}\n"
                formatted_text += "\n"
                
                # CPU info
                if "cpu" in info:
                    cpu = info["cpu"]
                    formatted_text += "🔄 CPU\n"
                    if "brand" in cpu:
                        formatted_text += f"  • {cpu['brand']}\n"
                    if "cores" in cpu and "threads" in cpu:
                        formatted_text += f"  • {cpu['cores']} cores, {cpu['threads']} threads\n"
                    if "speed" in cpu:
                        formatted_text += f"  • Base speed: {cpu['speed']} GHz\n"
                    if "speedmax" in cpu:
                        formatted_text += f"  • Max speed: {cpu['speedmax']} GHz\n"
                    formatted_text += "\n"
                
                # Memory info
                if "memory" in info:
                    memory = info["memory"]
                    formatted_text += "🧠 MEMORY\n"
                    
                    # Convert to GB for readability
                    total_gb = round(memory.get('total', 0) / (1024**3), 1)
                    used_gb = round(memory.get('used', 0) / (1024**3), 1)
                    free_gb = round(memory.get('free', 0) / (1024**3), 1)
                    available_gb = round(memory.get('available', 0) / (1024**3), 1)
                    
                    formatted_text += f"  • Total: {total_gb} GB\n"
                    formatted_text += f"  • Used: {used_gb} GB\n"
                    formatted_text += f"  • Free: {free_gb} GB\n"
                    formatted_text += f"  • Available: {available_gb} GB\n\n"
                
                # OS info
                if "os" in info:
                    os_info = info["os"]
                    formatted_text += "🐧 OPERATING SYSTEM\n"
                    if "distro" in os_info:
                        formatted_text += f"  • Distro: {os_info['distro']}\n"
                    if "release" in os_info:
                        formatted_text += f"  • Release: {os_info['release']}\n"
                    if "kernel" in os_info:
                        formatted_text += f"  • Kernel: {os_info['kernel']}\n"
                    if "uptime" in os_info:
                        formatted_text += f"  • Uptime: {os_info['uptime']}\n\n"
                
                # Unraid version
                if "versions" in info and "unraid" in info["versions"]:
                    formatted_text += "🔄 UNRAID VERSION\n"
                    formatted_text += f"  • Version: {info['versions']['unraid']}\n"
                
                return TextContent(type="text", text=formatted_text)
            else:
                logger.warning("Failed to retrieve system information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve system information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving system information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Get network information")
    async def get_network_info(
        ctx=None
    ):
        """Get network information
        
        Returns:
            Network information
        """
        logger.info("Tool called: get_network_info()")
        
        if ctx:
            await ctx.info("Retrieving network information...")
        else:
            print("Retrieving network information...")
        
        try:
            query = """
            query {
                network {
                    iface
                    ifaceName
                    ipv4
                    ipv6
                    mac
                    operstate
                    type
                    duplex
                    speed
                    accessUrls {
                        type
                        name
                        ipv4
                        ipv6
                    }
                }
            }
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Network info response: {response}")
            
            if "data" in response and "network" in response["data"]:
                network = response["data"]["network"]
                logger.info("Retrieved network information successfully")
                
                # Format the network information in a human-readable way
                formatted_text = "🌐 NETWORK INFORMATION\n"
                formatted_text += "═══════════════════\n\n"
                
                # Network interface details
                if network.get('iface') or network.get('ifaceName'):
                    formatted_text += "📡 INTERFACE\n"
                    if network.get('ifaceName'):
                        formatted_text += f"  • Name: {network.get('ifaceName')}\n"
                    if network.get('iface'):
                        formatted_text += f"  • Interface: {network.get('iface')}\n"
                    if network.get('type'):
                        formatted_text += f"  • Type: {network.get('type')}\n"
                    if network.get('operstate'):
                        formatted_text += f"  • State: {network.get('operstate')}\n"
                    if network.get('mac'):
                        formatted_text += f"  • MAC: {network.get('mac')}\n"
                    if network.get('speed'):
                        formatted_text += f"  • Speed: {network.get('speed')} Mbps\n"
                    if network.get('duplex'):
                        formatted_text += f"  • Duplex: {network.get('duplex')}\n"
                    formatted_text += "\n"
                
                # IP addresses
                ip_section_added = False
                if network.get('ipv4') or network.get('ipv6'):
                    formatted_text += "🔢 IP ADDRESSES\n"
                    ip_section_added = True
                    if network.get('ipv4'):
                        formatted_text += f"  • IPv4: {network.get('ipv4')}\n"
                    if network.get('ipv6'):
                        formatted_text += f"  • IPv6: {network.get('ipv6')}\n"
                
                if ip_section_added:
                    formatted_text += "\n"
                
                # Access URLs
                if network.get('accessUrls') and len(network.get('accessUrls')) > 0:
                    formatted_text += "🔗 ACCESS URLS\n"
                    
                    # Group URLs by type
                    url_types = {}
                    for url in network.get('accessUrls'):
                        url_type = url.get('type', 'OTHER')
                        if url_type not in url_types:
                            url_types[url_type] = []
                        url_types[url_type].append(url)
                    
                    # Display URLs by type
                    for url_type, urls in url_types.items():
                        formatted_text += f"  • {url_type}:\n"
                        for url in urls:
                            formatted_text += f"    - {url.get('name', 'Unnamed')}: "
                            if url.get('ipv4'):
                                formatted_text += f"{url.get('ipv4')}"
                            if url.get('ipv6'):
                                if url.get('ipv4'):
                                    formatted_text += f", {url.get('ipv6')}"
                                else:
                                    formatted_text += f"{url.get('ipv6')}"
                            formatted_text += "\n"
                
                return TextContent(type="text", text=formatted_text)
            else:
                logger.warning("Failed to retrieve network information: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve network information: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving network information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    # Log that tools were registered
    logger.info("System tools registered successfully")
