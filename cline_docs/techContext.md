# Technical Context: Unraid MCP Server

## Technologies Used

### Core Technologies
- **Python 3.9+**: Primary development language
- **MCP Protocol**: Model Context Protocol for AI assistant integration
- **GraphQL**: Query language for API communication
- **FastMCP**: Python library for building MCP servers

### Dependencies
- **mcp>=1.3.0**: Python MCP SDK with FastMCP implementation
- **aiohttp**: Asynchronous HTTP client/server for API requests
- **python-dotenv**: For environment variable management
- **logging**: Enhanced Python logging with multiple handlers
- **json**: JSON parsing for API responses

### External APIs
- **Unraid GraphQL API**: Core API for interacting with Unraid server
  - Documentation: https://docs.unraid.net/API/
  - GraphQL Sandbox: https://docs.unraid.net/API/how-to-use-the-api/#accessing-the-graphql-sandbox
  - Supported features (read-only):
    - System information
    - Array status
    - Docker containers and networks
    - Virtual machines
    - Disk information
    - Notifications
    - Shares
    - User information
    - API key information
    - Unassigned devices
    - Parity history

## Development Setup
1. Python 3.9+ environment with pip
2. Required packages installed: `pip install -r requirements.txt`
3. Environment variables configured in `.env` file:
   - `UNRAID_API_URL`: URL of the Unraid GraphQL API (e.g., `https://your-unraid-server-ip/graphql`)
   - `UNRAID_API_KEY`: API key for authentication with Unraid
   - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
   - `LOG_FILE`: Path to log file (default: unraid_mcp.log)
4. MCP configuration for Cline/Claude integration:
   - Configuration file: `unraid_mcp_config.json`
   - Format:
     ```json
     {
       "mcpServers": {
         "unraid": {
           "command": "/path/to/python",
           "args": ["/path/to/unraid-mcp/run_server.py"],
           "env": {
             "UNRAID_API_URL": "http://your-unraid-server:port/graphql",
             "UNRAID_API_KEY": "your-api-key",
             "LOG_LEVEL": "INFO",
             "CLAUDE_MCP_SERVER": "true"
           },
           "disabled": false,
           "autoApprove": []
         }
       }
     }
     ```

## Technical Constraints
1. **API Access**: Requires valid API key with appropriate permissions on the Unraid server
2. **Network Access**: MCP server needs network access to the Unraid server
3. **Rate Limiting**: Be mindful of potential rate limits on the Unraid API
4. **Security**: API keys and sensitive data should be properly secured
5. **Error Handling**: Must handle API failures and network issues gracefully
6. **Schema Compatibility**: GraphQL schema may have nullable fields that require careful query design
7. **Timeout Configuration**: Some operations (particularly disk-related) may take longer and require extended timeouts
8. **Logging System**: Comprehensive logging needed for debugging and monitoring
9. **Read-Only Operations**: Limited to read-only operations for security reasons

## Technical Implementation Details
1. **Enhanced Error Handling**:
   - Proper handling of GraphQL errors from the Unraid API
   - Timeout management for longer operations
   - Validation of nested fields in responses
   - Graceful degradation when fields are missing

2. **Logging System**:
   - Console and file outputs for comprehensive visibility
   - Multi-level logging (DEBUG, INFO, WARNING, ERROR)
   - Detailed context in log messages
   - Stack traces for error diagnostics

3. **Query Optimization**:
   - Simplified queries to avoid schema incompatibilities
   - Only requesting essential fields to minimize errors
   - Handling nested fields properly

4. **Timeout Management**:
   - Extended timeouts (60 seconds) for disk operations
   - Appropriate error handling for timeout conditions
   - Clear error messages for timeout situations

5. **User Information**:
   - Tools for listing users (read-only)
   - No user modification capabilities for security

6. **API Key Information**:
   - Tools for listing API keys (read-only)
   - No key creation capabilities for security

7. **Unassigned Devices Information**:
   - Tools for listing and viewing unassigned devices
   - Detailed device information including partitions

8. **Parity History**:
   - Tools for retrieving and analyzing parity check history
   - Historical data on parity check performance and errors

9. **Read-Only Design**:
   - All operations limited to queries, not mutations
   - Removed potentially dangerous methods from client
   - Focus on information retrieval rather than system modification
   - Enhanced security for AI assistant integration

10. **Stdio Transport Mode**:
    - Exclusive use of stdio transport for direct integration with AI assistants
    - Support for the MCP protocol over standard input/output
    - Compatible with Anthropic API and Cursor integration
    - Default and only transport mode used in the application

11. **Human-Readable Formatting**:
    - Consistent formatting patterns across all tools
    - Use of emojis and clear section headers for better readability
    - Organized information in a logical, easy-to-read format
    - Status indicators (🟢/🔴) for running/stopped services
    - Summary statistics where applicable
    - Enhanced error messages with more context
    - Standardized formatting for all tools:
      - Headers with title and separator
      - Sections with emoji indicators
      - List items with bullet points
      - Status indicators using colored emoji
      - Category indicators for different types of information
      - Consistent error handling with emoji indicators
      - Proper numerical formatting with units

12. **Tool Consolidation**:
    - Removed duplicate tools to simplify the codebase
    - Kept only the nicely formatted versions of tools
    - Standardized tool naming conventions
    - Improved tool organization by functionality

## Integration Methods
- **Anthropic Python SDK**: Using the `mcp_config_file` parameter
- **Cursor**: Using the MCP Configuration in Claude settings
- **Direct Stdio**: Running the server directly and communicating via stdin/stdout

## Testing Tools
- **Direct Testing**: Running the server and interacting via stdin/stdout
- **Claude API**: Testing with the Anthropic Python SDK
