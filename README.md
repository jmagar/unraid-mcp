# 🚀 Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A powerful MCP (Model Context Protocol) server that provides comprehensive tools to interact with an Unraid server's GraphQL API.**

## ✨ Features

- 🔧 **10 Tools, 90 Actions**: Complete Unraid management through MCP protocol
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible codebase  
- ⚡ **High Performance**: Async/concurrent operations with optimized timeouts
- 🔄 **Real-time Data**: WebSocket subscriptions for live log streaming
- 📊 **Health Monitoring**: Comprehensive system diagnostics and status
- 🐳 **Docker Ready**: Full containerization support with Docker Compose
- 🔒 **Secure**: Proper SSL/TLS configuration and API key management
- 📝 **Rich Logging**: Structured logging with rotation and multiple levels

---

## 📋 Table of Contents

- [Claude Code Plugin](#-claude-code-plugin)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Available Tools & Resources](#-available-tools--resources)
- [Custom Slash Commands](#-custom-slash-commands)
- [Development](#-development)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Claude Code Plugin

**The easiest way to use Unraid MCP is through the Claude Code marketplace:**

```bash
# Add the marketplace
/plugin marketplace add jmagar/unraid-mcp

# Install the Unraid skill
/plugin install unraid @unraid-mcp
```

This provides instant access to Unraid monitoring and management through Claude Code with:
- **10 MCP tools** exposing **83 actions** via the consolidated action pattern
- **10 slash commands** for quick CLI-style access (`commands/`)
- Real-time system metrics and health monitoring
- Docker container and VM lifecycle management
- Disk health monitoring and storage management

**See [.claude-plugin/README.md](.claude-plugin/README.md) for detailed plugin documentation.**

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- OR Python 3.12+ with [uv](https://github.com/astral-sh/uv) for development
- Unraid server with GraphQL API enabled

### 1. Clone Repository
```bash
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Unraid API details
```

### 3. Deploy with Docker (Recommended)
```bash
# Start with Docker Compose
docker compose up -d

# View logs
docker compose logs -f unraid-mcp
```

### OR 3. Run for Development
```bash
# Install dependencies
uv sync

# Run development server
uv run unraid-mcp-server
```

---

## 📂 Plugin Structure

This repository is a Claude Code plugin. Key components:

```
unraid-mcp/                      # ${CLAUDE_PLUGIN_ROOT}
├── .claude-plugin/
│   ├── marketplace.json         # Marketplace catalog
│   └── plugin.json              # Plugin manifest
├── commands/                    # 10 custom slash commands
├── unraid_mcp/                  # MCP server Python package
├── skills/unraid/               # Skill and documentation
├── pyproject.toml               # Dependencies and entry points
└── scripts/                     # Validation and helper scripts
```

- **MCP Server**: 10 tools with 76 actions via GraphQL API
- **Slash Commands**: 10 commands in `commands/` for quick CLI-style access
- **Skill**: `/unraid` skill for monitoring and queries
- **Entry Point**: `unraid-mcp-server` defined in pyproject.toml

---

## 📦 Installation

### 🐳 Docker Deployment (Recommended)

The easiest way to run the Unraid MCP Server is with Docker:

```bash
# Clone repository
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp

# Set required environment variables
export UNRAID_API_URL="http://your-unraid-server/graphql"
export UNRAID_API_KEY="your_api_key_here"

# Deploy with Docker Compose
docker compose up -d

# View logs
docker compose logs -f unraid-mcp
```

#### Manual Docker Build
```bash
# Build and run manually
docker build -t unraid-mcp-server .
docker run -d --name unraid-mcp \
  --restart unless-stopped \
  -p 6970:6970 \
  -e UNRAID_API_URL="http://your-unraid-server/graphql" \
  -e UNRAID_API_KEY="your_api_key_here" \
  unraid-mcp-server
```

### 🔧 Development Installation

For development and testing:

```bash
# Clone repository
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp

# Install dependencies with uv
uv sync

# Install development dependencies  
uv sync --group dev

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server
uv run unraid-mcp-server
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the project root:

```bash
# Core API Configuration (Required)
UNRAID_API_URL=https://your-unraid-server-url/graphql
UNRAID_API_KEY=your_unraid_api_key

# MCP Server Settings
UNRAID_MCP_TRANSPORT=streamable-http  # streamable-http (recommended), sse (deprecated), stdio
UNRAID_MCP_HOST=0.0.0.0
UNRAID_MCP_PORT=6970

# Logging Configuration
UNRAID_MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
UNRAID_MCP_LOG_FILE=unraid-mcp.log

# SSL/TLS Configuration  
UNRAID_VERIFY_SSL=true  # true, false, or path to CA bundle

# Optional: Log Stream Configuration
# UNRAID_AUTOSTART_LOG_PATH=/var/log/syslog  # Path for log streaming resource
```

### Transport Options

| Transport | Description | Use Case |
|-----------|-------------|----------|
| `streamable-http` | HTTP-based (recommended) | Most compatible, best performance |
| `sse` | Server-Sent Events (deprecated) | Legacy support only |
| `stdio` | Standard I/O | Direct integration scenarios |

---

## 🛠️ Available Tools & Resources

Each tool uses a consolidated `action` parameter to expose multiple operations, reducing context window usage. Destructive actions require `confirm=True`.

### Tool Categories (10 Tools, 76 Actions)

| Tool | Actions | Description |
|------|---------|-------------|
| **`unraid_info`** | 19 | overview, array, network, registration, connect, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config |
| **`unraid_array`** | 5 | parity_start, parity_pause, parity_resume, parity_cancel, parity_status |
| **`unraid_storage`** | 6 | shares, disks, disk_details, unassigned, log_files, logs |
| **`unraid_docker`** | 15 | list, details, start, stop, restart, pause, unpause, remove, update, update_all, logs, networks, network_details, port_conflicts, check_updates |
| **`unraid_vm`** | 9 | list, details, start, stop, pause, resume, force_stop, reboot, reset |
| **`unraid_notifications`** | 9 | overview, list, warnings, create, archive, unread, delete, delete_archived, archive_all |
| **`unraid_rclone`** | 4 | list_remotes, config_form, create_remote, delete_remote |
| **`unraid_users`** | 1 | me |
| **`unraid_keys`** | 5 | list, get, create, update, delete |
| **`unraid_health`** | 3 | check, test_connection, diagnose |

### MCP Resources (Real-time Data)
- `unraid://logs/stream` - Live log streaming from `/var/log/syslog` with WebSocket subscriptions

> **Note**: MCP Resources provide real-time data streams that can be accessed via MCP clients. The log stream resource automatically connects to your Unraid system logs and provides live updates.

---

## 💬 Custom Slash Commands

The project includes **10 custom slash commands** in `commands/` for quick access to Unraid operations:

### Available Commands

| Command | Actions | Quick Access |
|---------|---------|--------------|
| `/info` | 19 | System information, metrics, configuration |
| `/array` | 5 | Parity check management |
| `/storage` | 6 | Shares, disks, logs |
| `/docker` | 15 | Container management and monitoring |
| `/vm` | 9 | Virtual machine lifecycle |
| `/notifications` | 9 | Alert management |
| `/rclone` | 4 | Cloud storage remotes |
| `/users` | 1 | Current user query |
| `/keys` | 5 | API key management |
| `/health` | 3 | System health checks |

### Example Usage

```bash
# System monitoring
/info overview
/health check
/storage shares

# Container management
/docker list
/docker start plex
/docker logs nginx

# VM operations
/vm list
/vm start windows-10

# Notifications
/notifications warnings
/notifications archive_all

# User management
/users list
/keys create "Automation Key" "For CI/CD"
```

### Command Features

Each slash command provides:
- **Comprehensive documentation** of all available actions
- **Argument hints** for required parameters
- **Safety warnings** for destructive operations (⚠️)
- **Usage examples** for common scenarios
- **Action categorization** (Query, Lifecycle, Management, Destructive)

Run any command without arguments to see full documentation, or type `/help` to list all available commands.

---


## 🔧 Development

### Project Structure
```
unraid-mcp/
├── unraid_mcp/               # Main package
│   ├── main.py               # Entry point
│   ├── config/               # Configuration management
│   │   ├── settings.py       # Environment & settings
│   │   └── logging.py        # Logging setup
│   ├── core/                 # Core infrastructure  
│   │   ├── client.py         # GraphQL client
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── types.py          # Shared data types
│   ├── subscriptions/        # Real-time subscriptions
│   │   ├── manager.py        # WebSocket management
│   │   ├── resources.py      # MCP resources
│   │   └── diagnostics.py    # Diagnostic tools
│   ├── tools/                # MCP tool categories (10 tools, 76 actions)
│   │   ├── info.py           # System information (19 actions)
│   │   ├── array.py          # Parity checks (5 actions)
│   │   ├── storage.py        # Storage & monitoring (6 actions)
│   │   ├── docker.py         # Container management (15 actions)
│   │   ├── virtualization.py # VM management (9 actions)
│   │   ├── notifications.py  # Notification management (9 actions)
│   │   ├── rclone.py         # Cloud storage (4 actions)
│   │   ├── users.py          # Current user query (1 action)
│   │   ├── keys.py           # API key management (5 actions)
│   │   └── health.py         # Health checks (3 actions)
│   └── server.py             # FastMCP server setup
├── logs/                     # Log files (auto-created)
└── docker-compose.yml        # Docker Compose deployment
```

### Code Quality Commands
```bash
# Lint and format code
uv run ruff check unraid_mcp/
uv run ruff format unraid_mcp/

# Type checking
uv run ty check unraid_mcp/

# Run tests
uv run pytest
```

### API Schema Docs Automation
```bash
# Regenerate complete GraphQL schema reference from live introspection
set -a; source .env; set +a
uv run python scripts/generate_unraid_api_reference.py
```

This updates `docs/UNRAID_API_COMPLETE_REFERENCE.md` with all operations, directives, and types visible to your API key.

Optional cron example (daily at 03:15):
```bash
15 3 * * * cd /path/to/unraid-mcp && /usr/bin/env bash -lc 'set -a; source .env; set +a; uv run python scripts/generate_unraid_api_reference.py && git add docs/UNRAID_API_COMPLETE_REFERENCE.md && git commit -m "docs: refresh unraid graphql schema"'
```

### Development Workflow
```bash
# Start development server
uv run unraid-mcp-server

# Or run via module directly
uv run -m unraid_mcp.main
```

---

## 🏗️ Architecture

### Core Principles
- **Modular Design**: Separate concerns across focused modules
- **Async First**: All operations are non-blocking and concurrent-safe  
- **Error Resilience**: Comprehensive error handling with graceful degradation
- **Configuration Driven**: Environment-based configuration with validation
- **Observability**: Structured logging and health monitoring

### Key Components

| Component | Purpose |
|-----------|---------|
| **FastMCP Server** | MCP protocol implementation and tool registration |
| **GraphQL Client** | Async HTTP client with timeout management |
| **Subscription Manager** | WebSocket connections for real-time data |
| **Tool Modules** | Domain-specific business logic (Docker, VMs, etc.) |
| **Configuration System** | Environment loading and validation |
| **Logging Framework** | Structured logging with file rotation |

---

## 🐛 Troubleshooting

### Common Issues

**🔥 Port Already in Use**
```bash
# Kill existing process on port 6970, then restart
lsof -ti :6970 | xargs kill -9 2>/dev/null; uv run unraid-mcp-server
```

**🔧 Connection Refused**
```bash
# Check Unraid API configuration
curl -k "${UNRAID_API_URL}" -H "X-API-Key: ${UNRAID_API_KEY}"
```

**📝 Import Errors**  
```bash
# Reinstall dependencies
uv sync --reinstall
```

**🔍 Debug Mode**
```bash
# Enable debug logging
export UNRAID_MCP_LOG_LEVEL=DEBUG
uv run unraid-mcp-server
```

### Health Check
```bash
# Use the built-in health check tool via MCP client
# or check logs at: logs/unraid-mcp.log
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`  
3. Run tests: `uv run pytest`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

---

## 📞 Support

- 📚 Documentation: Check inline code documentation
- 🐛 Issues: [GitHub Issues](https://github.com/jmagar/unraid-mcp/issues)
- 💬 Discussions: Use GitHub Discussions for questions

---

*Built with ❤️ for the Unraid community*
