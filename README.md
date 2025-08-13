# 🚀 Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A powerful MCP (Model Context Protocol) server that provides comprehensive tools to interact with an Unraid server's GraphQL API.**

## ✨ Features

- 🔧 **26 Tools**: Complete Unraid management through MCP protocol
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible codebase  
- ⚡ **High Performance**: Async/concurrent operations with optimized timeouts
- 🔄 **Real-time Data**: WebSocket subscriptions for live log streaming
- 📊 **Health Monitoring**: Comprehensive system diagnostics and status
- 🐳 **Docker Ready**: Full containerization support with Docker Compose
- 🔒 **Secure**: Proper SSL/TLS configuration and API key management
- 📝 **Rich Logging**: Structured logging with rotation and multiple levels

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Available Tools & Resources](#-available-tools--resources)
- [Development](#-development)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- OR Python 3.10+ with [uv](https://github.com/astral-sh/uv) for development
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
./dev.sh
```

---

## 📦 Installation

### 🐳 Docker Deployment (Recommended)

The easiest way to run the Unraid MCP Server is with Docker:

```bash
# Clone and configure
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp
cp .env.example .env
# Edit .env with your Unraid API details

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
  --env-file .env \
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
./dev.sh
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

### System Information & Status
- `get_system_info()` - Comprehensive system, OS, CPU, memory, hardware info
- `get_array_status()` - Storage array status, capacity, and disk details  
- `get_unraid_variables()` - System variables and settings
- `get_network_config()` - Network configuration and access URLs
- `get_registration_info()` - Unraid registration details
- `get_connect_settings()` - Unraid Connect configuration

### Docker Container Management  
- `list_docker_containers()` - List all containers with caching options
- `manage_docker_container(id, action)` - Start/stop containers (idempotent)
- `get_docker_container_details(identifier)` - Detailed container information

### Virtual Machine Management
- `list_vms()` - List all VMs and their states  
- `manage_vm(id, action)` - VM lifecycle (start/stop/pause/resume/reboot)
- `get_vm_details(identifier)` - Detailed VM information

### Storage & File Systems
- `get_shares_info()` - User shares information
- `list_physical_disks()` - Physical disk discovery
- `get_disk_details(disk_id)` - SMART data and detailed disk info

### Monitoring & Diagnostics
- `health_check()` - Comprehensive system health assessment
- `get_notifications_overview()` - Notification counts by severity
- `list_notifications(type, offset, limit)` - Filtered notification listing
- `list_available_log_files()` - Available system logs
- `get_logs(path, tail_lines)` - Log file content retrieval

### Cloud Storage (RClone)
- `list_rclone_remotes()` - List configured remotes
- `get_rclone_config_form(provider)` - Configuration schemas
- `create_rclone_remote(name, type, config)` - Create new remote
- `delete_rclone_remote(name)` - Remove existing remote

### Real-time Subscriptions & Resources
- `test_subscription_query(query)` - Test GraphQL subscriptions
- `diagnose_subscriptions()` - Subscription system diagnostics

### MCP Resources (Real-time Data)
- `unraid://logs/stream` - Live log streaming from `/var/log/syslog` with WebSocket subscriptions

> **Note**: MCP Resources provide real-time data streams that can be accessed via MCP clients. The log stream resource automatically connects to your Unraid system logs and provides live updates.

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
│   ├── tools/                # MCP tool categories
│   │   ├── docker.py         # Container management
│   │   ├── system.py         # System information
│   │   ├── storage.py        # Storage & monitoring
│   │   ├── health.py         # Health checks
│   │   ├── virtualization.py # VM management
│   │   └── rclone.py         # Cloud storage
│   └── server.py             # FastMCP server setup
├── logs/                     # Log files (auto-created)
├── dev.sh                    # Development script  
└── docker-compose.yml        # Docker Compose deployment
```

### Code Quality Commands
```bash
# Format code
uv run black unraid_mcp/

# Lint code  
uv run ruff check unraid_mcp/

# Type checking
uv run mypy unraid_mcp/

# Run tests
uv run pytest
```

### Development Workflow
```bash
# Start development server (kills existing processes safely)
./dev.sh

# Stop server only
./dev.sh --kill
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
./dev.sh  # Automatically kills existing processes
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