# Claude Code Marketplace Setup

This document explains the Claude Code marketplace and plugin structure for the Unraid MCP project.

## What Was Created

### 1. Marketplace Manifest (`.claude-plugin/marketplace.json`)
The marketplace catalog that lists all available plugins in this repository.

**Location:** `.claude-plugin/marketplace.json`

**Contents:**
- Marketplace metadata (name, version, owner, repository)
- Plugin catalog with the "unraid" skill
- Categories and tags for discoverability

### 2. Plugin Manifest (`skills/unraid/.claude-plugin/plugin.json`)
The individual plugin configuration for the Unraid skill.

**Location:** `skills/unraid/.claude-plugin/plugin.json`

**Contents:**
- Plugin name, version, author
- Repository and homepage links
- Plugin-specific metadata

### 3. Documentation
- `.claude-plugin/README.md` - Marketplace installation guide
- Updated root `README.md` with plugin installation section

### 4. Validation Script
- `scripts/validate-marketplace.sh` - Automated validation of marketplace structure

## Installation Methods

### Method 1: GitHub Distribution (Recommended for Users)

Once you push this to GitHub, users can install via:

```bash
# Add your marketplace
/plugin marketplace add jmagar/unraid-mcp

# Install the Unraid skill
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

Users can also install from a specific commit or branch:

```bash
# From specific branch
/plugin marketplace add jmagar/unraid-mcp#main

# From specific commit
/plugin marketplace add jmagar/unraid-mcp#abc123
```

## Plugin Structure

```
unraid-mcp/
├── .claude-plugin/          # Marketplace manifest
│   ├── marketplace.json
│   └── README.md
├── skills/unraid/           # Plugin directory
│   ├── .claude-plugin/      # Plugin manifest
│   │   └── plugin.json
│   ├── SKILL.md             # Skill documentation
│   ├── README.md            # Plugin documentation
│   ├── examples/            # Example scripts
│   ├── scripts/             # Helper scripts
│   └── references/          # API reference docs
└── scripts/
    └── validate-marketplace.sh  # Validation tool
```

## Marketplace Metadata

### Categories
- `infrastructure` - Server management and monitoring tools

### Tags
- `unraid` - Unraid-specific functionality
- `monitoring` - System monitoring capabilities
- `homelab` - Homelab automation
- `graphql` - GraphQL API integration
- `docker` - Docker container management
- `virtualization` - VM management

## Publishing Checklist

Before publishing to GitHub:

1. **Validate Structure**
   ```bash
   ./scripts/validate-marketplace.sh
   ```

2. **Update Version Numbers**
   - Bump version in `.claude-plugin/marketplace.json`
   - Bump version in `skills/unraid/.claude-plugin/plugin.json`
   - Update version in `README.md` if needed

3. **Test Locally**
   ```bash
   /plugin marketplace add .
   /plugin install unraid @unraid-mcp
   ```

4. **Commit and Push**
   ```bash
   git add .claude-plugin/ skills/unraid/.claude-plugin/
   git commit -m "feat: add Claude Code marketplace configuration"
   git push origin main
   ```

5. **Create Release Tag** (Optional)
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

## User Experience

After installation, users will:

1. **See the skill in their skill list**
   ```bash
   /skill list
   ```

2. **Access Unraid functionality directly**
   - Claude Code will automatically detect when to invoke the skill
   - Users can explicitly invoke with `/unraid`

3. **Have access to all helper scripts**
   - Example scripts in `examples/`
   - Utility scripts in `scripts/`
   - API reference in `references/`

## Maintenance

### Updating the Plugin

To release a new version:

1. Make changes to the plugin
2. Update version in `skills/unraid/.claude-plugin/plugin.json`
3. Update marketplace catalog in `.claude-plugin/marketplace.json`
4. Run validation: `./scripts/validate-marketplace.sh`
5. Commit and push

Users with the plugin installed will see the update available and can upgrade with:
```bash
/plugin update unraid
```

### Adding More Plugins

To add additional plugins to this marketplace:

1. Create new plugin directory: `skills/new-plugin/`
2. Add plugin manifest: `skills/new-plugin/.claude-plugin/plugin.json`
3. Update marketplace catalog: add entry to `.plugins[]` array in `.claude-plugin/marketplace.json`
4. Validate: `./scripts/validate-marketplace.sh`

## Support

- **Repository:** https://github.com/jmagar/unraid-mcp
- **Issues:** https://github.com/jmagar/unraid-mcp/issues
- **Documentation:** See `.claude-plugin/README.md` and `skills/unraid/README.md`

## Validation

Run the validation script anytime to ensure marketplace integrity:

```bash
./scripts/validate-marketplace.sh
```

This checks:
- Manifest file existence and validity
- JSON syntax
- Required fields
- Plugin structure
- Source path accuracy
- Documentation completeness

All 17 checks must pass before publishing.
