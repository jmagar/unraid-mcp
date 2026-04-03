# Unraid MCP Server

> **Powerful, real-time management for Unraid servers via the Model Context Protocol.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Python Version](https://img.shields.io/badge/python-3.12+-green.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Enabled-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

---

## ✨ Overview
Unraid MCP provides a comprehensive GraphQL-backed interface for monitoring and managing Unraid servers. It enables AI assistants to control array states, manage Docker/VM lifecycles, and monitor system health in real-time.

### 🎯 Key Features
| Feature | Description |
|---------|-------------|
| **107 Subactions** | Granular control over array, disks, docker, VMs, and settings |
| **Live Metrics** | Persistent WebSocket subscriptions for CPU, memory, and status |
| **Safety Guards** | Mandatory `confirm=True` flag for all destructive operations |
| **Interactive Setup** | Built-in credential elicitation and health validation |

---

## 🎯 Claude Code Integration
The easiest way to use this plugin is through the Claude Code marketplace:

```bash
# Add the marketplace
/plugin marketplace add jmagar/claude-homelab

# Install the plugin
/plugin install unraid-mcp @jmagar-claude-homelab
```

---

## ⚙️ Configuration & Credentials
Credentials follow the standardized `homelab-core` pattern.

**Location:** `~/.unraid-mcp/.env` (also supports shared `~/.claude-homelab/.env`)

### Required Variables
```bash
UNRAID_API_URL="https://10-1-0-2.xxx.myunraid.net:31337"
UNRAID_API_KEY="your-api-key-from-unraid-settings"
UNRAID_MCP_LOG_LEVEL="INFO"
```

> **Security Note:** Never commit `.env` files. Ensure permissions are set to `chmod 600`.

---

## 🔐 Authentication

HTTP transports (`streamable-http`, `sse`) require a Bearer token.
`stdio` (Claude Code plugin default) does **not** require a token.

### Generate a token

```bash
openssl rand -hex 32
```

### Server config (`~/.unraid-mcp/.env`)

```env
UNRAID_MCP_BEARER_TOKEN=<your-token>
```

### Claude Code client config

```json
{
  "mcpServers": {
    "unraid": {
      "type": "http",
      "url": "http://your-server:6970/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```

> The `Bearer ` prefix and space are required — omitting them causes a 401.

See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for full details and troubleshooting.

---

## 🛠️ Available Tools & Resources

### 🔧 Primary Tools
| Tool | Parameters | Description |
|------|------------|-------------|
| **`unraid`** | `action`, `subaction`, `confirm` | Unified tool for 107+ management actions |
| **`diagnose_subscriptions`** | `none` | Status report for real-time WebSocket connections |
| **`test_subscription_query`**| `subscription_query`| Debug tool for testing GraphQL subscriptions |

### 📊 Resources (`unraid://`)
| URI | Description | Output Format |
|-----|-------------|---------------|
| `unraid://live/cpu` | Real-time CPU utilization | Live Snapshot |
| `unraid://live/array_state` | Array and parity progress | Status Update |
| `unraid://logs/stream` | Streaming tail for `/var/log/syslog` | Raw Stream |

---

## 🏗️ Architecture & Design
Built on a modular, async-first Python architecture:
- **GraphQL Engine:** Concurrent-safe client with optimized timeouts.
- **Subscription Manager:** Persistent WebSocket manager for real-time resources.
- **Destructive Guards:** Network-layer isolation and action-specific confirmation requirements.

---

## 🔧 Development
### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup
```bash
uv sync
uv run unraid-mcp-server
```

### Quality Assurance
```bash
uv run ruff check .        # Linting
uv run ty check .          # Type Checking
uv run pytest              # Comprehensive test suite
```

---

## 🐛 Troubleshooting
| Issue | Cause | Solution |
|-------|-------|----------|
| **Connection Refused** | API Down / Wrong URL | Verify `UNRAID_API_URL` connectivity |
| **Subscription Pending**| Initializing state | Wait 2-3 seconds for WebSocket startup |
| **Permission Denied** | Key Invalidation | Regenerate API Key in Unraid settings |

---

## 📄 License
MIT © jmagar
