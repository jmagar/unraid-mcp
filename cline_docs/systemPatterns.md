# System Patterns: Unraid MCP Server

## System Architecture
The Unraid MCP server follows a clean, modular architecture designed to separate concerns:

1. **Client Layer** (`unraid_client.py`)
   - Handles communication with the Unraid GraphQL API
   - Manages authentication and API key handling
   - Abstracts GraphQL query execution
   
2. **MCP Server Layer** (`server.py`)
   - Implements the Model Context Protocol
   - Exposes resources (data sources) and tools (actions) for AI assistants
   - Handles request/response formatting

## Key Technical Decisions
1. **GraphQL for API Communication**
   - Using GraphQL to interact with the Unraid API for efficient data retrieval
   - Allows for precise querying of only needed data

2. **FastMCP Framework**
   - Using the FastMCP library for rapid MCP server implementation
   - Provides structured way to define resources and tools

3. **Asynchronous Programming**
   - Using `aiohttp` for asynchronous HTTP communication
   - Ensures responsive handling of concurrent requests

4. **Environment-based Configuration**
   - Using `.env` files for configuration
   - Keeps sensitive data like API keys separate from code

## Design Patterns
1. **Facade Pattern** 
   - The UnraidClient class acts as a facade to the complex GraphQL API
   
2. **Decorator Pattern**
   - Using FastMCP decorators to register resources and tools

3. **Async/Await Pattern**
   - Using modern Python async patterns for I/O-bound operations

4. **Factory Pattern**
   - Creating appropriate content types (TextContent, ImageContent) based on the data 