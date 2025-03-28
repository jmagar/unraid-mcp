# Unraid MCP Server

[![smithery badge](https://smithery.ai/badge/@jmagar/unraid-mcp)](https://smithery.ai/server/@jmagar/unraid-mcp)

A Python-based MCP (Model Context Protocol) server that enables AI assistants to interact with an Unraid server through the official Unraid GraphQL API.

## Disclaimer

**USE AT YOUR OWN RISK**: This software provides access to your Unraid server through AI assistants. While this implementation is configured as **read-only** to enhance safety, you should still exercise caution when using it.

- This is an unofficial tool and is not affiliated with or endorsed by Unraid, Inc.
- All operations are limited to read-only actions to prevent system modifications
- Always maintain proper backups of your data
- Review all information and suggestions provided by AI assistants before taking action
- The developers are not responsible for any issues that may arise from using this software

Even with read-only access, monitoring tools can potentially expose sensitive system information. By using this software, you acknowledge and accept these limitations and risks.

## Features

- **System Information**: Get detailed information about your Unraid server
- **Array Management**: Monitor array status
- **Docker Management**: List Docker containers and networks
- **VM Management**: List virtual machines
- **Disk Information**: Get detailed information about disks and unassigned devices
- **Notification Management**: View and manage system notifications
- **Share Management**: View and manage network shares
- **User Management**: List users
- **API Key Management**: List API keys
- **Parity History**: View parity check history
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

### Installing via Smithery

To install Unraid MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@jmagar/unraid-mcp):

```bash
npx -y @smithery/cli install @jmagar/unraid-mcp --client claude
```

### Manual Installation
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
   cp .env.template .env
   # Edit .env with your actual API URL and key
   ```

## Unraid API Setup

To use this MCP server, you need to set up the Unraid API on your Unraid server:

1. Enable developer mode and the GraphQL sandbox using the CLI:
   ```
   unraid-api developer
   ```
   Follow the prompts to enable the sandbox.

2. Create an API key with the necessary permissions:
   ```
   unraid-api apikey --create
   ```
   Follow the prompts to set the name, description, roles, and permissions.

3. Configure your `.env` file with:
   - `UNRAID_API_URL`: The GraphQL URL (e.g., `http://your-unraid-server-ip/graphql`)
   - `UNRAID_API_KEY`: The API key you created

4. Test the API using the GraphQL sandbox at `http://your-unraid-server-ip/graphql`

> **Note**: The Unraid API uses the `x-api-key` header for authentication, not Bearer tokens.

### Troubleshooting

- If you get CORS errors, make sure your client includes the correct `Origin` header that matches the server's URL.
- Ensure your API key has the necessary roles and permissions for the queries you're trying to execute.
- Check that the GraphQL sandbox is enabled and accessible.

## Usage

### Running the MCP Server

Run the server in stdio mode for integration with AI assistants:

```bash
# Run in stdio mode (for direct integration with AI assistants)
python run_server.py
```

The stdio mode is useful for:
- Direct integration with AI assistants that support the MCP protocol
- Testing with the Anthropic Python SDK
- Integration with Claude in Cursor

When running in stdio mode, the server reads from standard input and writes to standard output, following the MCP protocol format. This allows for direct communication with AI assistants without requiring HTTP transport.

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

### System Management
| Tool Name | Description |
|-----------|-------------|
| `get_system_info` | Get detailed system information |
| `get_network_info` | Get network interface information |

### Array Management
| Tool Name | Description |
|-----------|-------------|
| `get_array_status` | Get array status in a human-readable way |
| `get_parity_history` | Get parity check history |

### Docker Management
| Tool Name | Description |
|-----------|-------------|
| `get_docker_containers` | Get information about Docker containers |
| `get_docker_networks` | Get information about Docker networks |
| `list_containers` | List Docker containers in a human-readable way |

### VM Management
| Tool Name | Description |
|-----------|-------------|
| `get_vms` | Get information about virtual machines |
| `get_vm_details` | Get detailed information about a specific VM |
| `list_vms` | List virtual machines in a human-readable way |

### Notification Management
| Tool Name | Description |
|-----------|-------------|
| `get_notifications` | Get notifications from the Unraid server |
| `create_notification` | Create a new notification |
| `archive_notification` | Archive a notification |

### Share Management
| Tool Name | Description |
|-----------|-------------|
| `get_shares` | Get information about network shares |
| `get_share_details` | Get detailed information about a specific share |

### Disk Management
| Tool Name | Description |
|-----------|-------------|
| `get_disks` | Get information about all disks |
| `get_disk_details` | Get information about a specific disk |
| `get_unassigned_devices` | Get information about unassigned devices |

### User Management
| Tool Name | Description |
|-----------|-------------|
| `get_users` | Get information about all users |

### API Key Management
| Tool Name | Description |
|-----------|-------------|
| `get_api_keys` | Get information about all API keys |

## Integration with Claude

To use the MCP server with Claude API or other AI assistants that support stdio mode:

1. Create a configuration file (e.g., `unraid_mcp_config.json`):
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


> **Note**: For Windows users, make sure to use double backslashes in paths (e.g., `C:\\Users\\username\\unraid-mcp\\run_server.py`)

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
- Developer mode not enabled on Unraid server
- API key not having the necessary roles

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Unraid API Documentation](https://docs.unraid.net/API/) 