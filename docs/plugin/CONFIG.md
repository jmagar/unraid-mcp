# Plugin Settings -- unraid-mcp

## userConfig (Claude Code)

The `.claude-plugin/plugin.json` defines four user-configurable settings:

| Key | Type | Sensitive | Default | Description |
|-----|------|-----------|---------|-------------|
| `unraid_mcp_url` | string | no | `https://unraid.tootie.tv/mcp` | URL of the MCP server |
| `unraid_mcp_token` | string | yes | -- | Bearer token for MCP auth |
| `unraid_api_url` | string | yes | -- | Unraid GraphQL API URL |
| `unraid_api_key` | string | yes | -- | Unraid API key |

### How settings are used

- **Non-sensitive**: Available as literal values in skill templates (`${user_config.unraid_mcp_url}`)
- **Sensitive**: Available ONLY as `$CLAUDE_PLUGIN_OPTION_*` environment variables in Bash subprocesses
  - `$CLAUDE_PLUGIN_OPTION_UNRAID_MCP_TOKEN`
  - `$CLAUDE_PLUGIN_OPTION_UNRAID_API_URL`
  - `$CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY`

Attempting `${user_config.unraid_api_key}` in a template will not work for sensitive values.

## Settings (Gemini CLI)

The `gemini-extension.json` defines two settings:

| Name | envVar | Sensitive |
|------|--------|-----------|
| Unraid API URL | `UNRAID_API_URL` | no |
| Unraid API Key | `UNRAID_API_KEY` | yes |

Gemini sets these as environment variables before launching the MCP server.

## Codex CLI

The `.codex-plugin/plugin.json` does not define explicit settings. Codex reads credentials from `~/.unraid-mcp/.env` via the standard loading chain.

## See Also

- [PLUGINS.md](PLUGINS.md) -- Full plugin manifest reference
- [SKILLS.md](SKILLS.md) -- How skills reference userConfig
- [../mcp/ENV.md](../mcp/ENV.md) -- Server-side environment variables
