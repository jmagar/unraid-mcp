# Unraid MCP Marketplace

This directory contains the Claude Code marketplace configuration for the Unraid MCP server and skills.

## Installation

### From GitHub (Recommended)

```bash
# Add the marketplace
/plugin marketplace add jmagar/unraid-mcp

# Install the Unraid skill
/plugin install unraid @unraid-mcp
```

### From Local Path (Development)

```bash
# Add local marketplace
/plugin marketplace add /path/to/unraid-mcp

# Install the plugin
/plugin install unraid @unraid-mcp
```

## Available Plugins

### unraid

Query and monitor Unraid servers via GraphQL API - array status, disk health, containers, VMs, system monitoring.

**Features:**
- 1 consolidated `unraid` tool with ~108 actions across 15 domains
- Real-time live subscriptions (CPU, memory, logs, array state, UPS)
- Disk health and temperature monitoring
- Docker container management
- VM status and control
- Log file access
- Network share information
- Notification management
- Plugin, rclone, API key, and OIDC management

**Version:** 1.0.0
**Category:** Infrastructure
**Tags:** unraid, monitoring, homelab, graphql, docker, virtualization

## Configuration

After installation, run setup to configure credentials interactively:

```python
unraid(action="health", subaction="setup")
```

Credentials are stored at `~/.unraid-mcp/.env` automatically.

**Getting an API Key:**
1. Open Unraid WebUI
2. Go to Settings → Management Access → API Keys
3. Click "Create" and select "Viewer" role (or appropriate roles for mutations)
4. Copy the generated API key

## Documentation

- **Plugin Documentation:** See `skills/unraid/README.md`
- **MCP Server Documentation:** See root `README.md`
- **API Reference:** See `skills/unraid/references/`

## Support

- **Issues:** https://github.com/jmagar/unraid-mcp/issues
- **Repository:** https://github.com/jmagar/unraid-mcp
