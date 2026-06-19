# Plugin Manifest Reference -- unraid-mcp

## Claude Code (`.claude-plugin/plugin.json`)

```json
{
  "name": "unraid-mcp",
  "displayName": "Unraid MCP",
  "version": "1.2.3",
  "description": "Query, monitor, and manage Unraid servers via GraphQL API through MCP tools.",
  "mcpServers": {
    "unraid": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}", "unraid-mcp-server"],
      "env": { "UNRAID_MCP_TRANSPORT": "stdio" }
    }
  },
  "userConfig": {
    "unraid_api_url": { "type": "string", "sensitive": true },
    "unraid_api_key": { "type": "string", "sensitive": true }
  }
}
```

### Key fields

- **mcpServers.unraid**: stdio transport via `uv run`. The `${CLAUDE_PLUGIN_ROOT}` variable resolves to the plugin installation directory.
- **userConfig**: Two settings collected at install time (`unraid_api_url`, `unraid_api_key`). Both are sensitive, stored encrypted, and exposed as `$CLAUDE_PLUGIN_OPTION_*` environment variables. `.mcp.json` wires them into the stdio server's `UNRAID_API_URL` / `UNRAID_API_KEY` env vars.

## Codex CLI (`.codex-plugin/plugin.json`)

```json
{
  "name": "unraid-mcp",
  "version": "1.2.3",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json",
  "interface": {
    "displayName": "Unraid MCP",
    "category": "Infrastructure",
    "capabilities": ["Read", "Write"],
    "brandColor": "#F59E0B"
  }
}
```

### Key fields

- **skills**: Points to `./skills/` directory containing the unraid skill
- **interface**: Rich metadata for Codex CLI display, including brand color and default prompts

## Gemini CLI (`gemini-extension.json`)

```json
{
  "name": "unraid-mcp",
  "version": "1.2.3",
  "mcpServers": {
    "unraid-mcp": {
      "command": "uv",
      "args": ["run", "unraid-mcp-server"],
      "cwd": "${extensionPath}"
    }
  },
  "settings": [
    { "name": "Unraid API URL", "envVar": "UNRAID_API_URL", "sensitive": false },
    { "name": "Unraid API Key", "envVar": "UNRAID_API_KEY", "sensitive": true }
  ]
}
```

## MCP Registry (`server.json`)

```json
{
  "name": "tv.tootie/unraid-mcp",
  "packages": [{
    "registryType": "pypi",
    "identifier": "unraid-mcp",
    "runtimeHint": "uvx",
    "transport": { "type": "stdio" },
    "environmentVariables": [
      { "name": "UNRAID_API_URL", "isRequired": true },
      { "name": "UNRAID_API_KEY", "isRequired": true, "isSecret": true }
    ]
  }]
}
```

## Versioning

The Claude/Codex plugin manifests are **not** versioned — they carry no `version`
field. The plugin is distributed from this git repo, so it is versioned by **commit
SHA** (every commit to `main` is its own version). This is enforced by:
- CI `no-plugin-version` job (`bin/check-no-plugin-version.sh`) — fails if a
  `version` field reappears in `.claude-plugin/plugin.json` or `.codex-plugin/plugin.json`
- `bin/validate-marketplace.sh` — asserts `.claude-plugin/plugin.json` has no version

`gemini-extension.json` keeps a static `version` (the Gemini CLI requires it). Only
`pyproject.toml` is actively versioned (for the Python package / Docker release),
bumped via `just publish` when cutting a tagged release.

## See Also

- [CONFIG.md](CONFIG.md) -- userConfig field details
- [MARKETPLACES.md](MARKETPLACES.md) -- Publishing to marketplaces
- [../mcp/CONNECT.md](../mcp/CONNECT.md) -- Client connection guides
