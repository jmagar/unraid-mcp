# 🚀 Unraid MCP Server

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.x-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A powerful MCP (Model Context Protocol) server that provides comprehensive tools to interact with an Unraid server's GraphQL API.**

## ✨ Features

- 🔧 **1 primary tool + 2 diagnostic tools, 107 subactions**: Complete Unraid management through a consolidated MCP tool
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible codebase
- ⚡ **High Performance**: Async/concurrent operations with optimized timeouts
- 🔄 **Real-time Data**: WebSocket subscriptions for live metrics, logs, array state, and more
- 📊 **Health Monitoring**: Comprehensive system diagnostics and status
- 🔒 **Secure**: Network-layer isolation
- 📝 **Rich Logging**: Structured logging with rotation and multiple levels

---

## 📋 Table of Contents

- [Claude Code Plugin](#-claude-code-plugin)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Authentication](#-authentication)
- [Available Tools & Resources](#-available-tools--resources)
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
- **1 primary MCP tool** (`unraid`) exposing **107 subactions** via `action` + `subaction` routing, plus `diagnose_subscriptions` and `test_subscription_query` diagnostic tools
- Real-time system metrics and health monitoring
- Docker container and VM lifecycle management
- Disk health monitoring and storage management

**See [.claude-plugin/README.md](.claude-plugin/README.md) for detailed plugin documentation.**

### ⚙️ Credential Setup

Credentials are stored in `~/.unraid-mcp/.env` — one location that works for the
Claude Code plugin and direct `uv run` invocations.

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

> **Finding your API key:** Unraid → Settings → Management Access → API Keys

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ with [uv](https://github.com/astral-sh/uv) for development
- Unraid server with GraphQL API enabled

### 1. Clone Repository
```bash
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp
```

### 2. Configure Environment
```bash
# Canonical credential location (all runtimes)
mkdir -p ~/.unraid-mcp && chmod 700 ~/.unraid-mcp
cp .env.example ~/.unraid-mcp/.env && chmod 600 ~/.unraid-mcp/.env
# Edit ~/.unraid-mcp/.env with your values

# For local development only
cp .env.example .env
```

### 3. Run for Development
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
├── unraid_mcp/                  # MCP server Python package
├── skills/unraid/               # Skill and documentation
├── pyproject.toml               # Dependencies and entry points
└── scripts/                     # Validation and helper scripts
```

- **MCP Server**: 3 tools — `unraid` (107 subactions) + `diagnose_subscriptions` + `test_subscription_query`
- **Skill**: `/unraid` skill for monitoring and queries
- **Entry Point**: `unraid-mcp-server` defined in pyproject.toml

---

## 📦 Installation

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

Credentials and settings go in `~/.unraid-mcp/.env` (the canonical location loaded by all runtimes — plugin and direct `uv run`). See the [Credential Setup](#%EF%B8%8F-credential-setup) section above for how to create it.

```bash
# Core API Configuration (Required)
UNRAID_API_URL=https://your-unraid-server-url/graphql
UNRAID_API_KEY=your_unraid_api_key

# MCP Server Settings
UNRAID_MCP_TRANSPORT=stdio  # stdio (default)
UNRAID_MCP_HOST=0.0.0.0
UNRAID_MCP_PORT=6970

# Logging Configuration
UNRAID_MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
UNRAID_MCP_LOG_FILE=unraid-mcp.log

# SSL/TLS Configuration
UNRAID_VERIFY_SSL=true  # true, false, or path to CA bundle

# Subscription Configuration
UNRAID_AUTO_START_SUBSCRIPTIONS=true  # Auto-start WebSocket subscriptions on startup (default: true)
UNRAID_MAX_RECONNECT_ATTEMPTS=10      # Max WebSocket reconnection attempts (default: 10)

# Optional: Auto-start log file subscription path
# Defaults to /var/log/syslog if it exists and this is unset
# UNRAID_AUTOSTART_LOG_PATH=/var/log/syslog

# Optional: Credentials directory override (default: ~/.unraid-mcp/)
# Useful for containers or non-standard home directory layouts
# UNRAID_CREDENTIALS_DIR=/custom/path/to/credentials
```

---

## 🛠️ Available Tools & Resources

The single `unraid` tool uses `action` (domain) + `subaction` (operation) routing to expose all operations via one MCP tool, minimizing context window usage. Destructive actions require `confirm=True`.

### Primary Tool: 15 Domains, 107 Subactions

Call pattern: `unraid(action="<domain>", subaction="<operation>")`

| action= | Subactions | Description |
|---------|-----------|-------------|
| **`system`** | overview, array, network, registration, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config | Server info, metrics, network, UPS (18 subactions) |
| **`health`** | check, test_connection, diagnose, setup | Health checks, connection test, diagnostics, interactive setup (4 subactions) |
| **`array`** | parity_status, parity_history, parity_start, parity_pause, parity_resume, parity_cancel, start_array, stop_array, add_disk, remove_disk, mount_disk, unmount_disk, clear_disk_stats | Parity checks, array state, disk operations (13 subactions) |
| **`disk`** | shares, disks, disk_details, log_files, logs, flash_backup | Shares, physical disks, log files (6 subactions) |
| **`docker`** | list, details, start, stop, restart, networks, network_details | Container lifecycle and network inspection (7 subactions) |
| **`vm`** | list, details, start, stop, pause, resume, force_stop, reboot, reset | Virtual machine lifecycle (9 subactions) |
| **`notification`** | overview, list, create, archive, mark_unread, delete, delete_archived, archive_all, archive_many, unarchive_many, unarchive_all, recalculate | System notifications CRUD (12 subactions) |
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

The server exposes two classes of MCP resources backed by persistent WebSocket connections:

**`unraid://live/*` — 9 snapshot resources** (auto-started, always-cached):
- `unraid://live/cpu` — CPU utilization
- `unraid://live/memory` — Memory usage
- `unraid://live/cpu_telemetry` — Detailed CPU telemetry
- `unraid://live/array_state` — Array state changes
- `unraid://live/parity_progress` — Parity check progress
- `unraid://live/ups_status` — UPS status
- `unraid://live/notifications_overview` — Notification counts
- `unraid://live/owner` — Owner info changes
- `unraid://live/server_status` — Server status changes

**`unraid://logs/stream`** — Live log file tail (path controlled by `UNRAID_AUTOSTART_LOG_PATH`)

> **Note**: Resources return cached data from persistent WebSocket subscriptions. A `{"status": "connecting"}` placeholder is returned while the subscription initializes — retry in a moment.
>
> **`log_tail`** is accessible as a tool subaction (`unraid(action="live", subaction="log_tail", path="/var/log/syslog")`) and requires a `path`; **`notification_feed`** is also available as a tool subaction but uses a transient one-shot subscription and accepts optional parameters. Neither is registered as an MCP resource.

> **Security note**: The `disk/logs` and `live/log_tail` subactions allow reading files under `/var/log/` and `/boot/logs/` on the Unraid server. Authenticated MCP clients can stream any log file within these directories.

---


## 🔧 Development

### Project Structure
```
unraid-mcp/
├── unraid_mcp/               # Main package
│   ├── main.py               # Entry point
│   ├── server.py             # FastMCP server setup
│   ├── version.py            # Version management (importlib.metadata)
│   ├── config/               # Configuration management
│   │   ├── settings.py       # Environment & settings
│   │   └── logging.py        # Logging setup
│   ├── core/                 # Core infrastructure
│   │   ├── client.py         # GraphQL client
│   │   ├── exceptions.py     # Custom exceptions
│   │   ├── guards.py         # Destructive action guards
│   │   ├── setup.py          # Interactive credential setup
│   │   ├── types.py          # Shared data types
│   │   └── utils.py          # Utility functions
│   ├── subscriptions/        # Real-time subscriptions
│   │   ├── manager.py        # Persistent WebSocket manager
│   │   ├── resources.py      # MCP resources (unraid://live/*)
│   │   ├── snapshot.py       # Transient subscribe_once helpers
│   │   ├── queries.py        # Subscription query constants
│   │   ├── diagnostics.py    # Diagnostic tools
│   │   └── utils.py          # Subscription utility functions
│   └── tools/                # Consolidated tools (unraid: 107 subactions + 2 diagnostic tools)
│       └── unraid.py         # All 15 domains in one file
├── tests/                    # Test suite
│   ├── conftest.py           # Shared fixtures
│   ├── test_*.py             # Unit tests (per domain)
│   ├── http_layer/           # httpx-level request tests
│   ├── integration/          # WebSocket lifecycle tests
│   ├── safety/               # Destructive action guard tests
│   └── schema/               # GraphQL query validation
├── docs/                     # Documentation & API references
├── scripts/                  # Build and utility scripts
├── skills/unraid/            # Claude skill assets
├── .claude-plugin/           # Plugin manifest & marketplace config
├── .env.example              # Environment template
├── pyproject.toml            # Project config & dependencies
└── logs/                     # Log files (auto-created, gitignored)
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

Live integration tests that exercise all non-destructive actions via [mcporter](https://github.com/mcporter/mcporter).

```bash
# stdio — no running server needed (good for CI)
./tests/mcporter/test-tools.sh [--parallel] [--timeout-ms N] [--verbose]
```

Destructive actions are always skipped. For safe testing strategies and exact mcporter commands per destructive action, see [`docs/DESTRUCTIVE_ACTIONS.md`](docs/DESTRUCTIVE_ACTIONS.md).

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

# Run via named config files
fastmcp run fastmcp.stdio.json  # stdio transport
```

### Ad-hoc Tool Testing (fastmcp CLI)
```bash
# Call without a running server (stdio config)
fastmcp list fastmcp.stdio.json
fastmcp call fastmcp.stdio.json unraid action=health subaction=check
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
