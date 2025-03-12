"""
Unraid MCP Server - Main Server Module
Provides MCP functionality for Unraid server management
"""
import asyncio
import logging
import os

from mcp.server.fastmcp import FastMCP
from unraid_client import UnraidClient

# Import our modular components
from src.config import Config, setup_logging
from src.resources import register_all_resources
from src.tools import register_all_tools


class UnraidMCPServer:
    """Unraid MCP Server class that manages all components"""
    
    def __init__(self):
        """Initialize the Unraid MCP server"""
        # Set up logging
        self.logger = setup_logging()
        self.logger.info("Initializing Unraid MCP Server")
        
        # Validate configuration
        Config.validate()
        
        # Initialize the client
        self.unraid = UnraidClient()
        
        # We'll configure logging via our setup_logging function
        # MCP framework logging will be controlled through the debug parameter
        
        # Initialize the MCP server
        self.server = FastMCP(
            name="Unraid MCP Server",
            instructions="Access and manage your Unraid server through natural language commands. You can query system information, manage Docker containers, VMs, and array operations.",
            debug=False  # Disable debug printing
        )
        
        # Register all resources and tools
        self._register_resources_and_tools()
        
        self.logger.info("Unraid MCP Server initialized successfully")
    
    def _register_resources_and_tools(self):
        """Register all resources and tools with the MCP server"""
        self.logger.info("Registering resources and tools")
        
        # Register all resources and tools using the helper functions
        register_all_resources(self.server, self.unraid)
        register_all_tools(self.server, self.unraid)
    
    def run(self, transport=None):
        """Run the MCP server with the specified transport
        
        Args:
            transport: The transport type to use (defaults to stdio)
        """
        # Always use stdio transport by default
        if transport is None:
            transport = "stdio"
        
        self.logger.info(f"Starting Unraid MCP Server with {transport} transport")
        
        # Set up error handling
        self.server.onerror = lambda error: self.logger.error(f"MCP Error: {error}")
        
        # Run the server with stdio transport
        self.logger.info("Using stdio transport (for Claude/Cline)")
        self.server.run(transport="stdio")
        
        # SSE transport code is commented out as we're using stdio by default
        # if transport == "stdio":
        #     self.logger.info("Using stdio transport (for Claude/Cline)")
        #     self.server.run(transport="stdio")
        # else:
        #     # For SSE transport, we need to set environment variables for the host and port
        #     # FastMCP uses these environment variables for SSE configuration
        #     os.environ["MCP_HOST"] = Config.SERVER_HOST
        #     os.environ["MCP_PORT"] = str(Config.SERVER_PORT)
        #     
        #     self.logger.info(f"Using SSE transport on {Config.SERVER_HOST}:{Config.SERVER_PORT}")
        #     self.logger.debug(f"SSE transport configuration: MCP_HOST={os.environ.get('MCP_HOST')}, MCP_PORT={os.environ.get('MCP_PORT')}")
        #     
        #     try:
        #         self.server.run(transport="sse")
        #     except Exception as e:
        #         self.logger.error(f"Error starting SSE transport: {str(e)}", exc_info=True)
        #         raise


def main():
    """Main entry point for the Unraid MCP Server"""
    try:
        # Create and run the server
        server = UnraidMCPServer()
        server.run()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
