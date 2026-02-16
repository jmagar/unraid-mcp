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
- 10 tools with 76 actions (queries and mutations)
- Real-time system metrics
- Disk health and temperature monitoring
- Docker container management
- VM status and control
- Log file access
- Network share information
- Notification management

**Version:** 0.2.0
**Category:** Infrastructure
**Tags:** unraid, monitoring, homelab, graphql, docker, virtualization

## Configuration

After installation, configure your Unraid server credentials:

```bash
export UNRAID_API_URL="https://your-unraid-server/graphql"
export UNRAID_API_KEY="your-api-key"
```

**Getting an API Key:**
1. Open Unraid WebUI
2. Go to Settings → Management Access → API Keys
3. Click "Create" and select "Viewer" role
4. Copy the generated API key

## Documentation

- **Plugin Documentation:** See `skills/unraid/README.md`
- **MCP Server Documentation:** See root `README.md`
- **API Reference:** See `skills/unraid/references/`

## Support

- **Issues:** https://github.com/jmagar/unraid-mcp/issues
- **Repository:** https://github.com/jmagar/unraid-mcp
