# Claude Code Marketplace Setup

This document explains the Claude Code marketplace and plugin structure for the Unraid MCP project.

## What Was Created

### 1. Marketplace Manifest (`.claude-plugin/marketplace.json`)
The marketplace catalog that lists all available plugins in this repository.

**Location:** `.claude-plugin/marketplace.json`

**Contents:**
- Marketplace metadata (name, version, owner, repository)
- Plugin catalog with the "unraid" plugin
- Categories and tags for discoverability

### 2. Plugin Manifest (`.claude-plugin/plugin.json`)
The individual plugin configuration for the Unraid MCP server.

**Location:** `.claude-plugin/plugin.json`

**Contents:**
- Plugin name (`unraid`), version (`1.1.2`), author
- Repository and homepage links
- `mcpServers` block that configures the server to run via `uv run unraid-mcp-server` in stdio mode

### 3. Validation Script
- `bin/validate-marketplace.sh` — Automated validation of marketplace structure

## MCP Tools Exposed

The plugin registers **3 MCP tools**:

| Tool | Purpose |
|------|---------|
| `unraid` | Primary tool — `action` (domain) + `subaction` (operation) routing, ~107 subactions across 15 domains |
| `diagnose_subscriptions` | Inspect WebSocket subscription connection states and errors |
| `test_subscription_query` | Test a specific GraphQL subscription query (allowlisted fields only) |

### Calling Convention

All Unraid operations go through the single `unraid` tool:

```
unraid(action="docker", subaction="list")
unraid(action="system", subaction="overview")
unraid(action="array", subaction="parity_status")
unraid(action="vm", subaction="list")
unraid(action="live", subaction="cpu")
```

### Domains (action=)

| action | example subactions |
|--------|--------------------|
| `system` | overview, array, network, metrics, services, ups_devices |
| `health` | check, test_connection, diagnose, setup |
| `array` | parity_status, parity_start, start_array, add_disk |
| `disk` | shares, disks, disk_details, logs |
| `docker` | list, details, start, stop, restart |
| `vm` | list, details, start, stop, pause, resume |
| `notification` | overview, list, create, archive, archive_all |
| `key` | list, get, create, update, delete |
| `plugin` | list, add, remove |
| `rclone` | list_remotes, config_form, create_remote |
| `setting` | update, configure_ups |
| `customization` | theme, set_theme, sso_enabled |
| `oidc` | providers, configuration, validate_session |
| `user` | me |
| `live` | cpu, memory, array_state, log_tail, notification_feed |

Destructive subactions (e.g. `stop_array`, `force_stop`, `delete`) require `confirm=True`.

## Installation Methods

### Method 1: GitHub Distribution (Recommended for Users)

Once pushed to GitHub, users install via:

```bash
# Add the marketplace
/plugin marketplace add jmagar/unraid-mcp

# Install the Unraid plugin
/plugin install unraid @unraid-mcp
```

### Method 2: Local Installation (Development)

For testing locally before publishing:

```bash
# Add local marketplace
/plugin marketplace add /home/jmagar/workspace/unraid-mcp

# Install the plugin
/plugin install unraid @unraid-mcp
```

### Method 3: Direct URL

Install from a specific branch or commit:

```bash
# From specific branch
/plugin marketplace add jmagar/unraid-mcp#main

# From specific commit
/plugin marketplace add jmagar/unraid-mcp#abc123
```

## Plugin Structure

```text
unraid-mcp/
├── .claude-plugin/          # Plugin manifest + marketplace manifest
│   ├── plugin.json          # Plugin configuration (name, version, mcpServers)
│   └── marketplace.json     # Marketplace catalog
├── unraid_mcp/              # Python package (the actual MCP server)
│   ├── main.py              # Entry point
│   ├── server.py            # FastMCP server registration
│   ├── tools/unraid.py      # Consolidated tool (all 3 tools registered here)
│   ├── config/              # Settings management
│   ├── core/                # GraphQL client, exceptions, shared types
│   └── subscriptions/       # Real-time WebSocket subscription manager
└── bin/
    └── validate-marketplace.sh  # Validation tool
```

## Marketplace Metadata

### Categories
- `infrastructure` — Server management and monitoring tools

### Tags
- `unraid` — Unraid-specific functionality
- `monitoring` — System monitoring capabilities
- `homelab` — Homelab automation
- `graphql` — GraphQL API integration
- `docker` — Docker container management
- `virtualization` — VM management

## Publishing Checklist

Before publishing to GitHub:

1. **Validate Structure**
   ```bash
   ./bin/validate-marketplace.sh
   ```

2. **Update Version Numbers** (must be in sync)
   - `pyproject.toml` → `version = "X.Y.Z"` under `[project]`
   - `.claude-plugin/plugin.json` → `"version": "X.Y.Z"`
   - `.claude-plugin/marketplace.json` → `"version"` in both `metadata` and `plugins[]`

3. **Test Locally**
   ```bash
   /plugin marketplace add .
   /plugin install unraid @unraid-mcp
   ```

4. **Commit and Push**
   ```bash
   git add .claude-plugin/
   git commit -m "chore: bump marketplace to vX.Y.Z"
   git push origin main
   ```

5. **Create Release Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

## User Experience

After installation, users can:

1. **Invoke Unraid operations directly in Claude Code**
   ```
   unraid(action="system", subaction="overview")
   unraid(action="docker", subaction="list")
   unraid(action="health", subaction="check")
   ```

2. **Use the credential setup tool on first run**
   ```
   unraid(action="health", subaction="setup")
   ```
   This triggers elicitation to collect and persist credentials to `~/.unraid-mcp/.env`.

3. **Monitor live data via subscriptions**
   ```
   unraid(action="live", subaction="cpu")
   unraid(action="live", subaction="log_tail")
   ```

## Maintenance

### Updating the Plugin

To release a new version:

1. Make changes to the plugin code
2. Update version in `pyproject.toml`, `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json`
3. Run validation: `./bin/validate-marketplace.sh`
4. Commit and push

Users with the plugin installed will see the update available and can upgrade:
```bash
/plugin update unraid
```

## Support

- **Repository:** https://github.com/jmagar/unraid-mcp
- **Issues:** https://github.com/jmagar/unraid-mcp/issues
- **Destructive Actions:** `docs/DESTRUCTIVE_ACTIONS.md`

## Validation

Run the validation script anytime to ensure marketplace integrity:

```bash
./bin/validate-marketplace.sh
```

This checks:
- Manifest file existence and validity
- JSON syntax
- Required fields
- Plugin structure
- Source path accuracy
- Documentation completeness
