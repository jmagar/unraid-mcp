# 🚀 Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.2+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A powerful MCP (Model Context Protocol) server that provides comprehensive tools to interact with an Unraid server's GraphQL API.**

## ✨ Features

- 🔧 **1 Tool, ~108 Actions**: Complete Unraid management through a single consolidated MCP tool
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible codebase
- ⚡ **High Performance**: Async/concurrent operations with optimized timeouts
- 🔄 **Real-time Data**: WebSocket subscriptions for live metrics, logs, array state, and more
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
- **1 MCP tool** (`unraid`) exposing **~108 actions** via `action` + `subaction` routing
- **11 slash commands** for quick CLI-style access (`commands/`)
- Real-time system metrics and health monitoring
- Docker container and VM lifecycle management
- Disk health monitoring and storage management

**See [.claude-plugin/README.md](.claude-plugin/README.md) for detailed plugin documentation.**

### ⚙️ Credential Setup

Credentials are stored in `~/.unraid-mcp/.env` — one location that works for the
Claude Code plugin, direct `uv run` invocations, and Docker.

**Option 1 — Interactive (Claude Code plugin, elicitation-supported clients):**
```
unraid(action="health", subaction="setup")
```
The server prompts for your API URL and key, writes `~/.unraid-mcp/.env` automatically
(created with mode 700/600), and activates credentials without restart.

**Option 2 — Manual:**
```bash
mkdir -p ~/.unraid-mcp && chmod 700 ~/.unraid-mcp
cp .env.example ~/.unraid-mcp/.env && chmod 600 ~/.unraid-mcp/.env
# Edit ~/.unraid-mcp/.env with your values:
#   UNRAID_API_URL=https://10-1-0-2.xxx.myunraid.net:31337
#   UNRAID_API_KEY=your-key-from-unraid-settings
```

**Docker:** `~/.unraid-mcp/.env` is loaded via `env_file` in `docker-compose.yml` —
same file, no duplication needed.

> **Finding your API key:** Unraid → Settings → Management Access → API Keys

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

- **MCP Server**: 1 `unraid` tool with ~108 actions via GraphQL API
- **Slash Commands**: 11 commands in `commands/` for quick CLI-style access
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

The single `unraid` tool uses `action` (domain) + `subaction` (operation) routing to expose all operations via one MCP tool, minimizing context window usage. Destructive actions require `confirm=True`.

### Single Tool, 15 Domains, ~108 Actions

Call pattern: `unraid(action="<domain>", subaction="<operation>")`

| action= | Subactions | Description |
|---------|-----------|-------------|
| **`system`** | overview, array, network, registration, connect, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config | Server info, metrics, network, UPS (19 subactions) |
| **`health`** | check, test_connection, diagnose, setup | Health checks, connection test, diagnostics, interactive setup (4 subactions) |
| **`array`** | parity_status, parity_history, parity_start, parity_pause, parity_resume, parity_cancel, start_array, stop_array, add_disk, remove_disk, mount_disk, unmount_disk, clear_disk_stats | Parity checks, array state, disk operations (13 subactions) |
| **`disk`** | shares, disks, disk_details, log_files, logs, flash_backup | Shares, physical disks, log files (6 subactions) |
| **`docker`** | list, details, start, stop, restart, networks, network_details | Container lifecycle and network inspection (7 subactions) |
| **`vm`** | list, details, start, stop, pause, resume, force_stop, reboot, reset | Virtual machine lifecycle (9 subactions) |
| **`notification`** | overview, list, create, archive, unread, delete, delete_archived, archive_all, archive_many, unarchive_many, unarchive_all, recalculate | System notifications CRUD (12 subactions) |
| **`key`** | list, get, create, update, delete, add_role, remove_role | API key management (7 subactions) |
| **`plugin`** | list, add, remove | Plugin management (3 subactions) |
| **`rclone`** | list_remotes, config_form, create_remote, delete_remote | Cloud storage remote management (4 subactions) |
| **`setting`** | update, configure_ups | System settings and UPS config (2 subactions) |
| **`customization`** | theme, public_theme, is_initial_setup, sso_enabled, set_theme | Theme and UI customization (5 subactions) |
| **`oidc`** | providers, provider, configuration, public_providers, validate_session | OIDC/SSO provider management (5 subactions) |
| **`user`** | me | Current authenticated user (1 subaction) |
| **`live`** | cpu, memory, cpu_telemetry, array_state, parity_progress, ups_status, notifications_overview, owner, server_status, log_tail, notification_feed | Real-time WebSocket subscription snapshots (11 subactions) |

### Destructive Actions (require `confirm=True`)
- **array**: `stop_array`, `remove_disk`, `clear_disk_stats`
- **vm**: `force_stop`, `reset`
- **notification**: `delete`, `delete_archived`
- **rclone**: `delete_remote`
- **key**: `delete`
- **disk**: `flash_backup`
- **setting**: `configure_ups`
- **plugin**: `remove`

### MCP Resources (Real-time Cached Data)

The `unraid://live/*` resources expose cached subscription data from persistent WebSocket connections:

- `unraid://live/cpu` — CPU utilization
- `unraid://live/memory` — Memory usage
- `unraid://live/cpu_telemetry` — Detailed CPU telemetry
- `unraid://live/array_state` — Array state changes
- `unraid://live/parity_progress` — Parity check progress
- `unraid://live/ups_status` — UPS status
- `unraid://live/notifications_overview` — Notification counts
- `unraid://live/owner` — Owner info changes
- `unraid://live/server_status` — Server status changes
- `unraid://live/log_tail` — Live syslog tail
- `unraid://live/notification_feed` — Real-time notification events

> **Note**: Resources return cached data from persistent WebSocket subscriptions. A `{"status": "connecting"}` placeholder is returned while the subscription initializes — retry in a moment.

---

## 💬 Custom Slash Commands

The project includes **11 custom slash commands** in `commands/` for quick access to Unraid operations. Each command maps to a domain of the `unraid` tool.

### Available Commands

| Command | Domain (`action=`) | Quick Access |
|---------|-------------------|--------------|
| `/info` | `system` | System information, metrics, UPS, network |
| `/array` | `array` | Parity checks, array state, disk operations |
| `/storage` | `disk` | Shares, disks, log files |
| `/docker` | `docker` | Container lifecycle and network inspection |
| `/vm` | `vm` | Virtual machine lifecycle |
| `/notifications` | `notification` | Alert management |
| `/rclone` | `rclone` | Cloud storage remotes |
| `/users` | `user` | Current user query |
| `/keys` | `key` | API key management |
| `/health` | `health` | System health checks and setup |
| `/settings` | `setting` | System settings configuration |

### Example Usage

```bash
# System monitoring
/info overview
/health check
/storage shares

# Container management
/docker list
/docker start plex

# VM operations
/vm list
/vm start windows-10

# Notifications
/notifications list
/notifications archive_all

# API key management
/keys list
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
│   │   ├── guards.py         # Destructive action guards
│   │   └── types.py          # Shared data types
│   ├── subscriptions/        # Real-time subscriptions
│   │   ├── manager.py        # Persistent WebSocket manager
│   │   ├── resources.py      # MCP resources (unraid://live/*)
│   │   ├── snapshot.py       # Transient subscribe_once helpers
│   │   └── diagnostics.py    # Diagnostic tools
│   ├── tools/                # Single consolidated tool (~108 actions)
│   │   └── unraid.py         # All 15 domains in one file
│   └── server.py             # FastMCP server setup
├── commands/                 # 11 custom slash commands
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

### Integration Smoke-Tests (mcporter)

Live integration tests that exercise all non-destructive actions via [mcporter](https://github.com/mcporter/mcporter). Two scripts cover two transport modes:

```bash
# stdio — no running server needed (good for CI)
./tests/mcporter/test-tools.sh [--parallel] [--timeout-ms N] [--verbose]

# HTTP — connects to a live server (most up-to-date coverage)
./tests/mcporter/test-actions.sh [MCP_URL]   # default: http://localhost:6970/mcp
```

Destructive actions are always skipped in both scripts. For safe testing strategies and exact mcporter commands per destructive action, see [`docs/DESTRUCTIVE_ACTIONS.md`](docs/DESTRUCTIVE_ACTIONS.md).

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
