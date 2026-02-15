# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an MCP (Model Context Protocol) server that provides tools to interact with an Unraid server's GraphQL API. The server is built using FastMCP with a **modular architecture** consisting of separate packages for configuration, core functionality, subscriptions, and tools.

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
# Local development with uv (recommended)
uv run unraid-mcp-server

# Using development script with hot reload
./dev.sh

# Direct module execution
uv run -m unraid_mcp.main
```

### Code Quality
```bash
# Format code with black
uv run black unraid_mcp/

# Lint with ruff
uv run ruff check unraid_mcp/

# Type checking with mypy
uv run mypy unraid_mcp/

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
- **Main Server**: `unraid_mcp/server.py` - Modular MCP server with FastMCP integration
- **Entry Point**: `unraid_mcp/main.py` - Application entry point and startup logic
- **Configuration**: `unraid_mcp/config/` - Settings management and logging configuration
- **Core Infrastructure**: `unraid_mcp/core/` - GraphQL client, exceptions, and shared types
- **Subscriptions**: `unraid_mcp/subscriptions/` - Real-time WebSocket subscriptions and diagnostics
- **Tools**: `unraid_mcp/tools/` - Domain-specific tool implementations
- **GraphQL Client**: Uses httpx for async HTTP requests to Unraid API
- **Transport Layer**: Supports streamable-http (recommended), SSE (deprecated), and stdio

### Key Design Patterns
- **Consolidated Action Pattern**: Each tool uses `action: Literal[...]` parameter to expose multiple operations via a single MCP tool, reducing context window usage
- **Pre-built Query Dicts**: `QUERIES` and `MUTATIONS` dicts prevent GraphQL injection and organize operations
- **Destructive Action Safety**: `DESTRUCTIVE_ACTIONS` sets require `confirm=True` for dangerous operations
- **Modular Architecture**: Clean separation of concerns across focused modules
- **Error Handling**: Uses ToolError for user-facing errors, detailed logging for debugging
- **Timeout Management**: Custom timeout configurations for different query types (90s for disk ops)
- **Data Processing**: Tools return both human-readable summaries and detailed raw data
- **Health Monitoring**: Comprehensive health check tool for system monitoring
- **Real-time Subscriptions**: WebSocket-based live data streaming

### Tool Categories (10 Tools, 90 Actions)
1. **`unraid_info`** (19 actions): overview, array, network, registration, connect, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config
2. **`unraid_array`** (12 actions): start, stop, parity_start/pause/resume/cancel/history, mount_disk, unmount_disk, clear_stats, shutdown, reboot
3. **`unraid_storage`** (6 actions): shares, disks, disk_details, unassigned, log_files, logs
4. **`unraid_docker`** (15 actions): list, details, start, stop, restart, pause, unpause, remove, update, update_all, logs, networks, network_details, port_conflicts, check_updates
5. **`unraid_vm`** (9 actions): list, details, start, stop, pause, resume, force_stop, reboot, reset
6. **`unraid_notifications`** (9 actions): overview, list, warnings, create, archive, unread, delete, delete_archived, archive_all
7. **`unraid_rclone`** (4 actions): list_remotes, config_form, create_remote, delete_remote
8. **`unraid_users`** (8 actions): me, list, get, add, delete, cloud, remote_access, origins
9. **`unraid_keys`** (5 actions): list, get, create, update, delete
10. **`unraid_health`** (3 actions): check, test_connection, diagnose

### Environment Variable Hierarchy
The server loads environment variables from multiple locations in order:
1. `/app/.env.local` (container mount)
2. `../.env.local` (project root)
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
- Log file overwrite at 10MB cap to prevent disk space issues