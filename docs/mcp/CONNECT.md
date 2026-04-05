# Connect to MCP

How to connect to the unraid-mcp server from every supported client and transport.

## Claude Code (plugin -- recommended)

### Install from marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install unraid-mcp @jmagar-claude-homelab
```

Claude Code runs the server in stdio mode via `uv run --directory <plugin-root> unraid-mcp-server`.

The plugin prompts for `userConfig` values:
- **Unraid MCP Server URL**: URL of the MCP server (default: `https://unraid.tootie.tv/mcp`)
- **MCP Server Bearer Token**: For HTTP transport auth
- **Unraid GraphQL API URL**: Your Unraid server's GraphQL endpoint
- **Unraid API Key**: API key from Unraid Settings

### Connect to remote HTTP server

If running the server separately (Docker, remote host):

```json
{
  "mcpServers": {
    "unraid": {
      "type": "url",
      "url": "http://localhost:6970/mcp",
      "headers": {
        "Authorization": "Bearer <your-token>"
      }
    }
  }
}
```

## Codex CLI

The `.codex-plugin/plugin.json` provides Codex integration:

```bash
# Install plugin
codex plugin install ./
```

Codex discovers the MCP server via `.mcp.json` referenced in the manifest.

## Gemini CLI

The `gemini-extension.json` provides Gemini integration:

```json
{
  "mcpServers": {
    "unraid-mcp": {
      "command": "uv",
      "args": ["run", "unraid-mcp-server"],
      "cwd": "${extensionPath}"
    }
  }
}
```

Settings are collected via the `settings` array for `UNRAID_API_URL` and `UNRAID_API_KEY`.

## Direct HTTP (any client)

### streamable-http

```bash
# Health check (no auth)
curl http://localhost:6970/health

# Tool call (with auth)
curl -X POST http://localhost:6970/mcp \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"unraid","arguments":{"action":"system","subaction":"overview"}},"id":1}'
```

### stdio

```bash
# Spawn and interact via pipes
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | \
  UNRAID_MCP_TRANSPORT=stdio uv run unraid-mcp-server
```

## MCP Registry

The server is published to the MCP Registry as `tv.tootie/unraid-mcp`. Clients that support registry discovery can auto-install:

```bash
uvx unraid-mcp
```

Required environment variables: `UNRAID_API_URL`, `UNRAID_API_KEY`.

## MCP Inspector

For development and debugging:

```bash
# Start server
uv run unraid-mcp-server

# Open MCP Inspector in browser
# Connect to http://localhost:6970/mcp with bearer token
```

## See Also

- [TRANSPORT.md](TRANSPORT.md) -- Transport configuration details
- [AUTH.md](AUTH.md) -- Authentication setup
- [DEPLOY.md](DEPLOY.md) -- Server deployment options
