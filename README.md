# Unraid MCP Server

A Python-based MCP (Model Context Protocol) server that enables AI assistants to interact with an Unraid server through the official Unraid GraphQL API.

## Features

- **System Information**: Query system status, CPU usage, memory, and uptime
- **Docker Management**: List, start, and stop Docker containers
- **Array Management**: Check array status, start/stop array
- **VM Management**: List, start, and stop virtual machines

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

1. Uncomment and configure the server settings in `.env`
2. Run the server with:
   ```bash
   python -c "from server import server; server.run(transport='sse')"
   ```

## Testing with MCP Inspector

You can test the server using the MCP Inspector tool:

```bash
pip install mcp-inspector
mcp-inspector --url http://localhost:8000
```

## Testing with Claude

1. Go to Claude Desktop
2. Navigate to Settings > Integrations
3. Add a new integration with your server URL
4. Start asking Claude about your Unraid server

## Example Queries

- "What's the current CPU usage on my Unraid server?"
- "List all of my Docker containers"
- "Start the Plex container"
- "What's the status of my array?"
- "How much free space do I have on my Unraid server?"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Unraid API Documentation](https://docs.unraid.net/API/) 