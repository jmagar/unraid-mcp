# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an MCP (Model Context Protocol) server that provides tools to interact with an Unraid server's GraphQL API. The server is built using FastMCP and supports multiple transport methods (streamable-http, SSE, stdio).

## Development Commands

### Setup
```bash
# Initialize uv virtual environment and install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

### Running the Server
```bash
# Local development with uv
uv run unraid-mcp-server

# Direct Python execution (if venv is activated)
python unraid_mcp_server.py
```

### Code Quality
```bash
# Format code with black
uv run black unraid_mcp_server.py

# Lint with ruff
uv run ruff check unraid_mcp_server.py

# Type checking with mypy
uv run mypy unraid_mcp_server.py

# Run tests
uv run pytest
```

### Docker Development
```bash
# Build the Docker image
docker build -t unraid-mcp-server .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f unraid-mcp

# Stop service
docker-compose down
```

### Environment Setup
- Copy `.env.example` to `.env` and configure:
  - `UNRAID_API_URL`: Unraid GraphQL endpoint (required)
  - `UNRAID_API_KEY`: Unraid API key (required)
  - `UNRAID_MCP_TRANSPORT`: Transport type (default: streamable-http)
  - `UNRAID_MCP_PORT`: Server port (default: 6970)
  - `UNRAID_MCP_HOST`: Server host (default: 0.0.0.0)

## Architecture

### Core Components
- **Main Server**: `unraid_mcp_server.py` - Single-file MCP server implementation
- **GraphQL Client**: Uses httpx for async HTTP requests to Unraid API
- **Transport Layer**: Supports streamable-http (recommended), SSE (deprecated), and stdio
- **Tool Framework**: FastMCP-based tool implementations

### Key Design Patterns
- **Error Handling**: Uses ToolError for user-facing errors, detailed logging for debugging
- **Timeout Management**: Custom timeout configurations for different query types
- **Data Processing**: Tools return both human-readable summaries and detailed raw data
- **Health Monitoring**: Comprehensive health check tool for system monitoring

### Tool Categories
1. **System Information**: `get_system_info()`, `get_unraid_variables()`
2. **Storage Management**: `get_array_status()`, `list_physical_disks()`, `get_disk_details()`
3. **Docker Management**: `list_docker_containers()`, `manage_docker_container()`, `get_docker_container_details()`
4. **VM Management**: `list_vms()`, `manage_vm()`, `get_vm_details()`
5. **Network & Config**: `get_network_config()`, `get_registration_info()`, `get_connect_settings()`
6. **Monitoring**: `get_notifications_overview()`, `list_notifications()`, `get_logs()`, `health_check()`
7. **File System**: `get_shares_info()`, `list_available_log_files()`

### Environment Variable Hierarchy
The server loads environment variables from multiple locations in order:
1. `/app/.env.local` (container mount)
2. `../env.local` (project root)
3. `../.env` (project root)
4. `.env` (local directory)

### Transport Configuration
- **streamable-http** (recommended): HTTP-based transport on `/mcp` endpoint
- **sse** (deprecated): Server-Sent Events transport
- **stdio**: Standard input/output for direct integration

### Error Handling Strategy
- GraphQL errors are converted to ToolError with descriptive messages
- HTTP errors include status codes and response details
- Network errors are caught and wrapped with connection context
- All errors are logged with full context for debugging

### Performance Considerations
- Increased timeouts for disk operations (90s read timeout)
- Selective queries to avoid GraphQL type overflow issues
- Optional caching controls for Docker container queries
- Rotating log files to prevent disk space issues