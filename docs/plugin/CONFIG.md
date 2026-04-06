# Plugin Settings -- unraid-mcp

Plugin configuration and user-facing settings for stdio deployment.

## How it works

Claude Code plugins use a two-layer config model:

1. **`plugin.json`** -- declares `userConfig` fields that Claude Code prompts for at install time
2. **`.mcp.json`** -- references those fields as `${userConfig.<key>}` in the `env` section

No `.env` file is needed for plugin deployment. Claude Code handles interpolation directly.

## userConfig fields

| Key | Title | Sensitive | Purpose |
| --- | --- | --- | --- |
| `unraid_api_url` | Unraid GraphQL API URL | yes | Your Unraid server's GraphQL endpoint |
| `unraid_api_key` | Unraid API Key | yes | API key from Settings > Management Access > API Keys |

Both fields are required. The server exits at startup if either is empty.

## Hardcoded defaults in .mcp.json

| Variable | Value | Reason |
| --- | --- | --- |
| `UNRAID_MCP_TRANSPORT` | `stdio` | Plugin always uses stdio |
| `UNRAID_MCP_DISABLE_HTTP_AUTH` | `true` | No HTTP layer in stdio mode |
| `UNRAID_AUTO_START_SUBSCRIPTIONS` | `false` | Prevents 11 concurrent WebSocket connections on session spawn |
| `UNRAID_MAX_RECONNECT_ATTEMPTS` | `3` | Fast fail (vs 50min of silent retries at default 10) |
| `UNRAID_VERIFY_SSL` | `true` | Secure by default |

## Session startup

The `sync-uv.sh` hook runs at `SessionStart` to ensure Python dependencies are in sync. The venv is stored at `${CLAUDE_PLUGIN_DATA}/.venv`.

## Security

Sensitive credentials (`UNRAID_API_KEY`) are scrubbed from `os.environ` after capture at startup, reducing the `/proc/PID/environ` exposure window.

## Other clients

### Gemini CLI

`gemini-extension.json` defines `UNRAID_API_URL` and `UNRAID_API_KEY` as environment settings.

### Codex CLI

`.codex-plugin/plugin.json` does not define explicit settings. Codex reads credentials from `~/.unraid-mcp/.env`.

## See Also

- [PLUGINS.md](PLUGINS.md) -- Full plugin manifest reference
- [../mcp/ENV.md](../mcp/ENV.md) -- Server-side environment variables
- [../CONFIG.md](../CONFIG.md) -- Full configuration reference
