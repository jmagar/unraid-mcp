# System Patterns: Unraid MCP Server

## System Architecture
The Unraid MCP server follows a clean, modular architecture designed to separate concerns:

1. **Client Layer** (`unraid_client.py`)
   - Handles communication with the Unraid GraphQL API
   - Manages authentication and API key handling
   - Abstracts GraphQL query execution
   - Implements robust error handling for API responses
   - Handles timeout management for longer operations
   - Provides enhanced logging and diagnostics
   
2. **MCP Server Layer** (`server.py`)
   - Implements the Model Context Protocol
   - Exposes resources (data sources) and tools (actions) for AI assistants
   - Handles request/response formatting
   - Manages error reporting and recovery
   
3. **Server Runner** (`run_server.py`)
   - Handles server configuration and initialization
   - Manages transport mode detection (stdio vs SSE)
   - Configures and manages logging
   - Provides graceful startup and shutdown

## Key Technical Decisions
1. **GraphQL for API Communication**
   - Using GraphQL to interact with the Unraid API for efficient data retrieval
   - Implements query simplification to handle schema inconsistencies
   - Allows for precise querying of only needed data
   - Manages nested field validation and error handling

2. **FastMCP Framework**
   - Using the FastMCP library for rapid MCP server implementation
   - Provides structured way to define resources and tools
   - Supports both stdio and SSE transport modes

3. **Asynchronous Programming**
   - Using `aiohttp` for asynchronous HTTP communication
   - Configures appropriate timeouts for different operations
   - Ensures responsive handling of concurrent requests
   - Provides comprehensive error handling for async operations

4. **Environment-based Configuration**
   - Using `.env` files for configuration
   - Keeps sensitive data like API keys separate from code
   - Allows for easy deployment in different environments

5. **Enhanced Logging System**
   - Dual output to console and files for better visibility
   - Multi-level logging with detailed context
   - Structured error reporting with stack traces
   - Operation tracing for debugging complex issues

## Design Patterns
1. **Facade Pattern** 
   - The UnraidClient class acts as a facade to the complex GraphQL API
   - Simplifies interaction with the Unraid API
   - Abstracts error handling and recovery
   
2. **Decorator Pattern**
   - Using FastMCP decorators to register resources and tools
   - Clean separation of tool definitions and implementation

3. **Async/Await Pattern**
   - Using modern Python async patterns for I/O-bound operations
   - Proper timeout handling for long-running operations

4. **Factory Pattern**
   - Creating appropriate content types (TextContent, ImageContent) based on the data

5. **Strategy Pattern**
   - Flexible query structure based on schema compatibility
   - Adapts to different Unraid API versions and capabilities
