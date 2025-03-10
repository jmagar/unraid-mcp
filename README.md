# Unraid MCP Server

A Python-based MCP (Model Context Protocol) server that enables AI assistants to interact with an Unraid server through the official Unraid GraphQL API.

## Features

- **System Information**: Query system status, CPU usage, memory, and uptime
- **Docker Management**: List, start, and stop Docker containers
- **Array Management**: Check array status, start/stop array operations
- **VM Management**: List, start, and stop virtual machines
- **Shares**: Browse user shares on the Unraid server
- **Plugins**: View installed plugins and their status
- **Error Handling**: Comprehensive error handling with diagnostic information
- **Logging**: Detailed logging for troubleshooting
- **Templated Resources**: Access specific containers and VMs by name

## Prerequisites

- Python 3.10 or later
- An Unraid server with the API enabled
- API key with appropriate permissions

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jmagar/unraid-mcp.git
   cd unraid-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Unraid API credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API URL and key
   ```

## Usage

### Running in Local Development Mode

For testing and development, you can run the server in stdio mode:

```bash
python server.py
```

### Running as a Production Server

For production use, you can run the server with SSE transport:

1. Configure server settings in `.env`:
   ```
   # Unraid API Configuration
   UNRAID_API_URL=https://your-unraid-server-ip/graphql
   UNRAID_API_KEY=your-api-key
   
   # MCP Server Configuration
   MCP_SERVER_HOST=0.0.0.0  # Listen on all interfaces
   MCP_SERVER_PORT=8000     # Port to serve MCP
   ```

2. Run the server with:
   ```bash
   python run_server.py
   ```

## Server Architecture

The server is built using the FastMCP framework and consists of:

1. **Unraid API Client** (`unraid_client.py`):
   - Handles GraphQL communication with the Unraid server
   - Manages authentication and error handling
   - Provides consistent error reporting

2. **MCP Server** (`server.py`):
   - Defines resources and tools according to MCP specification
   - Exposes Unraid functionality to AI assistants
   - Handles request validation and error diagnostics

## Available Resources

| Resource URI | Description |
|--------------|-------------|
| `unraid://system/info` | System information (CPU, memory, uptime) |
| `unraid://system/plugins` | Installed plugins |
| `unraid://docker/containers` | List of all Docker containers |
| `unraid://docker/{container_name}` | Details of a specific container |
| `unraid://array/status` | Current array status |
| `unraid://vms/list` | List of all virtual machines |
| `unraid://vms/{vm_name}` | Details of a specific VM |
| `unraid://storage/shares` | User shares information |

## Available Tools

| Tool Name | Description |
|-----------|-------------|
| `start_container` | Start a Docker container by name |
| `stop_container` | Stop a Docker container by name |
| `start_array` | Start the Unraid array |
| `stop_array` | Stop the Unraid array |
| `start_vm` | Start a virtual machine by name |
| `stop_vm` | Stop a virtual machine by name |

## Testing with MCP Inspector

You can test the server using the MCP Inspector tool:

```bash
pip install mcp-inspector
mcp-inspector --url http://localhost:8000
```

## Integration with Claude

1. Go to Claude Desktop
2. Navigate to Settings > Integrations
3. Add a new integration:
   - Name: Unraid MCP
   - URL: http://localhost:8000 (or your server URL)
4. Start asking Claude about your Unraid server

## Example Queries

- "What's the current CPU usage on my Unraid server?"
- "List all of my Docker containers"
- "Tell me about my Plex container" (uses container_details resource)
- "Start the Plex container"
- "What's the status of my array?"
- "How much free space do I have on my Unraid server?"
- "Show me details about my Windows VM" (uses vm_details resource)
- "What plugins do I have installed?"

## Troubleshooting

Check the log file (`unraid_mcp.log`) for detailed error information.

Common issues:
- Incorrect API URL or key in `.env` file
- Network connectivity issues to Unraid server
- Insufficient permissions for the API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Unraid API Documentation](https://docs.unraid.net/API/) 