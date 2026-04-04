# Unraid MCP

GraphQL-backed MCP server for Unraid. This repo exposes a unified `unraid` tool for system inspection, management operations, live telemetry, and selected destructive actions guarded by explicit confirmation.

## What this repository ships

- `unraid_mcp/`: server, GraphQL client, subscriptions, config, and tool handlers
- `skills/unraid/`: client-facing skill docs
- `docs/`: authentication, destructive-action, and publishing references
- `.claude-plugin/`, `.codex-plugin/`, `gemini-extension.json`: client manifests
- `docker-compose.yaml`, `Dockerfile`, `entrypoint.sh`: container deployment
- `tests/`: unit, safety, schema, HTTP-layer, and live coverage

## MCP surface

### Main tools

| Tool | Purpose |
| --- | --- |
| `unraid` | Unified action/subaction router for nearly all operations |
| `unraid_help` | Markdown help for actions and parameters |
| `diagnose_subscriptions` | Inspect the subscription system and failure state |
| `test_subscription_query` | Probe a GraphQL subscription directly for schema/debug work |

### `unraid` action groups

| Action | Representative subactions |
| --- | --- |
| `system` | `overview`, `array`, `network`, `registration`, `variables`, `metrics`, `services`, `display`, `config`, `online`, `owner`, `settings`, `server`, `servers`, `flash`, `ups_devices`, `ups_device`, `ups_config` |
| `health` | `check`, `test_connection`, `diagnose`, `setup` |
| `array` | `parity_status`, `parity_history`, `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`, `start_array`, `stop_array`, `add_disk`, `remove_disk`, `mount_disk`, `unmount_disk`, `clear_disk_stats` |
| `disk` | `shares`, `disks`, `disk_details`, `log_files`, `logs`, `flash_backup` |
| `docker` | `list`, `details`, `start`, `stop`, `restart`, `networks`, `network_details` |
| `vm` | `list`, `details`, `start`, `stop`, `pause`, `resume`, `force_stop`, `reboot`, `reset` |
| `notification` | `overview`, `list`, `create`, `archive`, `mark_unread`, `recalculate`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`, `delete_archived` |
| `key` | `list`, `get`, `create`, `update`, `delete`, `add_role`, `remove_role` |
| `plugin` | `list`, `add`, `remove` |
| `rclone` | `list_remotes`, `config_form`, `create_remote`, `delete_remote` |
| `setting` | `update`, `configure_ups` |
| `customization` | `theme`, `public_theme`, `is_initial_setup`, `sso_enabled`, `set_theme` |
| `oidc` | `providers`, `provider`, `configuration`, `public_providers`, `validate_session` |
| `user` | `me` |
| `live` | `cpu`, `memory`, `cpu_telemetry`, `array_state`, `parity_progress`, `ups_status`, `notifications_overview`, `owner`, `server_status`, `log_tail`, `notification_feed` |

Destructive subactions require `confirm=true`.

## Installation

### Marketplace

```bash
/plugin marketplace add jmagar/claude-homelab
/plugin install unraid-mcp @jmagar-claude-homelab
```

### Local development

```bash
uv sync --dev
uv run unraid-mcp-server
```

Equivalent entrypoints:

```bash
uv run unraid-mcp
uv run python -m unraid_mcp
```

## Configuration

Create `.env` from `.env.example` and set, at minimum:

```bash
UNRAID_API_URL=https://tower.local/graphql
UNRAID_API_KEY=your_api_key
UNRAID_MCP_TRANSPORT=streamable-http
UNRAID_MCP_HOST=0.0.0.0
UNRAID_MCP_PORT=6970
UNRAID_MCP_BEARER_TOKEN=...
UNRAID_MCP_DISABLE_HTTP_AUTH=false
UNRAID_MCP_ALLOW_DESTRUCTIVE=false
UNRAID_MCP_ALLOW_YOLO=false
```

Authentication rules:

- `stdio` does not need a Bearer token.
- `streamable-http` and `sse` expect `UNRAID_MCP_BEARER_TOKEN` unless auth is explicitly disabled.
- `streamable-http` is the current default transport.

Credential locations:

- repo-local: `.env`
- supported shared location: `~/.unraid-mcp/.env`

## Development commands

```bash
just dev
just lint
just fmt
just typecheck
just test
just test-live
just up
just health
```

Notable recipes:

- `just dev`: `uv run python -m unraid_mcp`
- `just check-contract`: Docker/env/ignore-file checks
- `just gen-token`: create a secure token

## Verification

Recommended:

```bash
just lint
just typecheck
just test
```

For a stdio MCP smoke test, start:

```bash
uv run unraid-mcp-server
```

Or use the bundled mcporter harness under `tests/mcporter/`.

## Related files

- `unraid_mcp/server.py`: server bootstrap and transport/auth handling
- `unraid_mcp/main.py`: CLI entrypoint
- `docs/AUTHENTICATION.md`: HTTP auth details
- `docs/DESTRUCTIVE_ACTIONS.md`: manual verification strategy for dangerous operations
- `skills/unraid/`: user-facing operational guidance

## License

MIT
