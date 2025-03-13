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
   - Implements read-only operations for safety
   
2. **MCP Server Layer** (`server.py`)
   - Implements the Model Context Protocol
   - Exposes resources (data sources) and tools (actions) for AI assistants
   - Handles request/response formatting
   - Manages error reporting and recovery
   - Uses stdio transport exclusively for AI assistant integration
   - Enforces read-only operations for security
   
3. **Server Runner** (`run_server.py`)
   - Handles server configuration and initialization
   - Manages stdio transport mode exclusively
   - Configures and manages logging
   - Provides graceful startup and shutdown

4. **Tools Layer** (`src/tools/`)
   - Modular organization of tools by functionality
   - Each module focuses on a specific aspect of Unraid monitoring:
     - `array.py`: Array monitoring tools
     - `docker.py`: Docker container information
     - `vms.py`: Virtual machine information
     - `system.py`: System information
     - `notifications.py`: Notification management
     - `shares.py`: Share information
     - `disks.py`: Disk information
     - `users.py`: User information (read-only)
     - `apikeys.py`: API key information (read-only)
     - `unassigned_devices.py`: Unassigned devices information
     - `parity.py`: Parity history tools
     - `formatting.py`: Formatted display tools
   - Centralized registration through `__init__.py`
   - All tools are read-only for security
   - Consistent human-readable formatting across all tools

## Key Technical Decisions
1. **GraphQL for API Communication**
   - Using GraphQL to interact with the Unraid API for efficient data retrieval
   - Implements query simplification to handle schema inconsistencies
   - Allows for precise querying of only needed data
   - Manages nested field validation and error handling

2. **FastMCP Framework**
   - Using the FastMCP library for rapid MCP server implementation
   - Provides structured way to define resources and tools
   - Uses stdio transport mode exclusively for AI assistant integration

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

6. **Modular Tool Organization**
   - Tools organized by functional domain
   - Consistent registration pattern for all tools
   - Standardized error handling and response formatting
   - Unified context handling for AI assistant interaction

7. **Stdio Transport Mode**
   - Exclusive use of stdio transport for direct integration with AI assistants
   - Follows the MCP protocol specification for message exchange
   - Compatible with Anthropic API and Cursor integration
   - Simplified deployment without requiring HTTP server setup
   - Default and only transport mode used in the application

8. **Read-Only Design Pattern**
   - All tools and methods are read-only for security
   - Removed potentially dangerous tools that could modify the system
   - Focused on information retrieval rather than system modification
   - Enhanced safety for AI assistant integration

9. **Human-Readable Formatting**
   - Consistent formatting patterns across all tools
   - Use of emojis and clear section headers for better readability
   - Organized information in a logical, easy-to-read format
   - Status indicators (🟢/🔴) for running/stopped services
   - Summary statistics where applicable
   - Enhanced error messages with more context

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

6. **Module Pattern**
   - Organizing tools into domain-specific modules
   - Consistent interface across different tool types
   - Centralized registration through `register_all_tools`

7. **Adapter Pattern**
   - Adapting the MCP protocol to work over stdio
   - Converting between MCP messages and JSON-serialized data
   - Handling input/output streams for communication

8. **Read-Only Pattern**
   - Implementing only query operations, not mutations
   - Focusing on data retrieval rather than modification
   - Enhancing security by preventing system changes

9. **Formatting Pattern**
   - Consistent formatting structure across all tools
   - Standard header with title and separator
   - Emoji indicators for status and categories
   - Hierarchical information organization with bullet points
   - Consistent indentation and spacing
   - Status indicators using colored emoji (🟢/🔴)
   - Summary statistics at the top of listings
   - Fallback handling for missing or null data
   - Consistent error message formatting with emoji indicators

## Formatting Standards
All tools follow these formatting standards for human-readable output:

1. **Headers**
   - Title with relevant emoji indicator
   - Separator line using "═" characters
   - Blank line after header

2. **Sections**
   - Section headers with emoji indicators
   - Indented content under sections
   - Blank line between sections

3. **List Items**
   - Bullet points using "•" character
   - Consistent indentation (2 spaces)
   - Key-value pairs with colon separator

4. **Status Indicators**
   - Running/active: 🟢
   - Stopped/inactive: 🔴
   - Warning: ⚠️
   - Error: ❌
   - Information: ℹ️

5. **Category Indicators**
   - System: 🖥️
   - Memory: 🧠
   - CPU: 🔄
   - Disk: 💾
   - Network: 🌐
   - Docker: 🐳
   - Virtual Machine: 🖥️
   - Notification: 🔔
   - Array: 💽
   - Statistics: 📊

6. **Error Handling**
   - Clear error messages with ❌ indicator
   - Warning messages with ⚠️ indicator
   - Fallback text for missing data
   - Context information for troubleshooting

7. **Numerical Formatting**
   - Consistent units (GB, TB, etc.)
   - Rounded to appropriate precision
   - Percentage values where applicable
   - Proper spacing between numbers and units
