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

### External APIs
- **Unraid GraphQL API**: Core API for interacting with Unraid server
  - Documentation: https://docs.unraid.net/API/
  - GraphQL Sandbox: https://docs.unraid.net/API/how-to-use-the-api/#accessing-the-graphql-sandbox

## Development Setup
1. Python 3.9+ environment with pip
2. Required packages installed: `pip install -r requirements.txt`
3. Environment variables configured in `.env` file:
   - `UNRAID_API_URL`: URL of the Unraid GraphQL API (e.g., `https://your-unraid-server-ip/graphql`)
   - `UNRAID_API_KEY`: API key for authentication with Unraid
   - `MCP_SERVER_HOST`: Host address for SSE transport (default: 127.0.0.1)
   - `MCP_SERVER_PORT`: Port number for SSE transport (default: 8400)
   - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
   - `LOG_FILE`: Path to log file (default: unraid_mcp.log)
4. MCP configuration for Cline/Claude integration:
   - Configuration file: `cline_mcp_settings.json`
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
             "MCP_SERVER_HOST": "127.0.0.1",
             "MCP_SERVER_PORT": "8400",
             "LOG_LEVEL": "DEBUG",
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

## Testing Tools
- **MCP Inspector**: For testing MCP server implementation (`pip install mcp-inspector`)
- **Claude Desktop**: For integration testing with an AI assistant
