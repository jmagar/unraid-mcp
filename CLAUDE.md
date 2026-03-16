# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an MCP (Model Context Protocol) server that provides tools to interact with an Unraid server's GraphQL API. The server is built using FastMCP with a **modular architecture** consisting of separate packages for configuration, core functionality, subscriptions, and tools.

## Development Commands

### Setup
```bash
# Initialize uv virtual environment and install dependencies
uv sync

# Install dev dependencies
uv sync --group dev
```

### Running the Server
```bash
# Local development with uv (recommended)
uv run unraid-mcp-server

# Direct module execution
uv run -m unraid_mcp.main
```

### Code Quality
```bash
# Lint and format with ruff
uv run ruff check unraid_mcp/
uv run ruff format unraid_mcp/

# Type checking with ty (Astral's fast type checker)
uv run ty check unraid_mcp/

# Run tests
uv run pytest
```

### Docker Development
```bash
# Build the Docker image
docker build -t unraid-mcp-server .

# Run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f unraid-mcp

# Stop service
docker compose down
```

### Environment Setup
- Copy `.env.example` to `.env` and configure:
  - `UNRAID_API_URL`: Unraid GraphQL endpoint (required)
  - `UNRAID_API_KEY`: Unraid API key (required)
  - `UNRAID_MCP_TRANSPORT`: Transport type (default: streamable-http)
  - `UNRAID_MCP_PORT`: Server port (default: 6970)
  - `UNRAID_MCP_HOST`: Server host (default: 0.0.0.0)

## Architecture

### Core Components
- **Main Server**: `unraid_mcp/server.py` - Modular MCP server with FastMCP integration
- **Entry Point**: `unraid_mcp/main.py` - Application entry point and startup logic
- **Configuration**: `unraid_mcp/config/` - Settings management and logging configuration
- **Core Infrastructure**: `unraid_mcp/core/` - GraphQL client, exceptions, and shared types
- **Subscriptions**: `unraid_mcp/subscriptions/` - Real-time WebSocket subscriptions and diagnostics
- **Tools**: `unraid_mcp/tools/` - Domain-specific tool implementations
- **GraphQL Client**: Uses httpx for async HTTP requests to Unraid API
- **Transport Layer**: Supports streamable-http (recommended), SSE (deprecated), and stdio

### Key Design Patterns
- **Consolidated Action Pattern**: Each tool uses `action: Literal[...]` parameter to expose multiple operations via a single MCP tool, reducing context window usage
- **Pre-built Query Dicts**: `QUERIES` and `MUTATIONS` dicts prevent GraphQL injection and organize operations
- **Destructive Action Safety**: `DESTRUCTIVE_ACTIONS` sets require `confirm=True` for dangerous operations
- **Modular Architecture**: Clean separation of concerns across focused modules
- **Error Handling**: Uses ToolError for user-facing errors, detailed logging for debugging
- **Timeout Management**: Custom timeout configurations for different query types (90s for disk ops)
- **Data Processing**: Tools return both human-readable summaries and detailed raw data
- **Health Monitoring**: Comprehensive health check tool for system monitoring
- **Real-time Subscriptions**: WebSocket-based live data streaming
- **Persistent Subscription Manager**: `unraid_live` actions use a shared `SubscriptionManager`
  that maintains persistent WebSocket connections. Resources serve cached data via
  `subscription_manager.get_resource_data(action)`. A "connecting" placeholder is returned
  while the subscription starts — callers should retry in a moment.

### Tool Categories (15 Tools, ~108 Actions)
1. **`unraid_info`** (19 actions): overview, array, network, registration, connect, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config
2. **`unraid_array`** (13 actions): parity_start, parity_pause, parity_resume, parity_cancel, parity_status, parity_history, start_array, stop_array, add_disk, remove_disk, mount_disk, unmount_disk, clear_disk_stats
3. **`unraid_storage`** (6 actions): shares, disks, disk_details, log_files, logs, flash_backup
4. **`unraid_docker`** (7 actions): list, details, start, stop, restart, networks, network_details
5. **`unraid_vm`** (9 actions): list, details, start, stop, pause, resume, force_stop, reboot, reset
6. **`unraid_notifications`** (12 actions): overview, list, create, archive, unread, delete, delete_archived, archive_all, archive_many, unarchive_many, unarchive_all, recalculate
7. **`unraid_rclone`** (4 actions): list_remotes, config_form, create_remote, delete_remote
8. **`unraid_users`** (1 action): me
9. **`unraid_keys`** (7 actions): list, get, create, update, delete, add_role, remove_role
10. **`unraid_health`** (4 actions): check, test_connection, diagnose, setup
11. **`unraid_settings`** (2 actions): update, configure_ups
12. **`unraid_customization`** (5 actions): theme, public_theme, is_initial_setup, sso_enabled, set_theme
13. **`unraid_plugins`** (3 actions): list, add, remove
14. **`unraid_oidc`** (5 actions): providers, provider, configuration, public_providers, validate_session
15. **`unraid_live`** (11 actions): cpu, memory, cpu_telemetry, array_state, parity_progress, ups_status, notifications_overview, notification_feed, log_tail, owner, server_status

### Destructive Actions (require `confirm=True`)
- **array**: stop_array, remove_disk, clear_disk_stats
- **vm**: force_stop, reset
- **notifications**: delete, delete_archived
- **rclone**: delete_remote
- **keys**: delete
- **storage**: flash_backup
- **settings**: configure_ups
- **plugins**: remove

### Environment Variable Hierarchy
The server loads environment variables from multiple locations in order:
1. `~/.unraid-mcp/.env` (primary — canonical credentials dir, all runtimes)
2. `~/.unraid-mcp/.env.local` (local overrides, only used if primary is absent)
3. `/app/.env.local` (Docker container mount)
4. `../.env.local` (project root local overrides)
5. `../.env` (project root fallback)
6. `unraid_mcp/.env` (last resort)

### Transport Configuration
- **streamable-http** (recommended): HTTP-based transport on `/mcp` endpoint
- **sse** (deprecated): Server-Sent Events transport
- **stdio**: Standard input/output for direct integration

### Error Handling Strategy
- GraphQL errors are converted to ToolError with descriptive messages
- HTTP errors include status codes and response details
- Network errors are caught and wrapped with connection context
- All errors are logged with full context for debugging

### Performance Considerations
- Increased timeouts for disk operations (90s read timeout)
- Selective queries to avoid GraphQL type overflow issues
- Optional caching controls for Docker container queries
- Log file overwrite at 10MB cap to prevent disk space issues

## Critical Gotchas

### Mutation Handler Ordering
**Mutation handlers MUST return before the `QUERIES[action]` lookup.** Mutations are not in the `QUERIES` dict — reaching that line for a mutation action causes a `KeyError`. Always add early-return `if action == "mutation_name": ... return` blocks BEFORE the `QUERIES` lookup.

### Test Patching
- Patch at the **tool module level**: `unraid_mcp.tools.info.make_graphql_request` (not core)
- `conftest.py`'s `mock_graphql_request` patches the core module — wrong for tool-level tests
- Use `conftest.py`'s `make_tool_fn()` helper or local `_make_tool()` pattern

### Test Suite Structure
```
tests/
├── conftest.py           # Shared fixtures + make_tool_fn() helper
├── test_*.py             # Unit tests (mock at tool module level)
├── http_layer/           # httpx-level request/response tests (respx)
├── integration/          # WebSocket subscription lifecycle tests (slow)
├── safety/               # Destructive action guard tests
└── schema/               # GraphQL query validation (99 tests, all passing)
```

### Running Targeted Tests
```bash
uv run pytest tests/safety/          # Destructive action guards only
uv run pytest tests/schema/          # GraphQL query validation only
uv run pytest tests/http_layer/      # HTTP/httpx layer only
uv run pytest tests/test_docker.py   # Single tool only
uv run pytest -x                     # Fail fast on first error
```

### Scripts
```bash
# HTTP smoke-test against a live server (11 tools, all non-destructive actions)
./tests/mcporter/test-actions.sh [MCP_URL]  # default: http://localhost:6970/mcp

# stdio smoke-test, no running server needed (good for CI)
./tests/mcporter/test-tools.sh [--parallel] [--timeout-ms N] [--verbose]
```
See `tests/mcporter/README.md` for transport differences and `docs/DESTRUCTIVE_ACTIONS.md` for exact destructive-action test commands.

### API Reference Docs
- `docs/UNRAID_API_COMPLETE_REFERENCE.md` — Full GraphQL schema reference
- `docs/UNRAID_API_OPERATIONS.md` — All supported operations with examples

Use these when adding new queries/mutations.

### Version Bumps
When bumping the version, **always update both files** — they must stay in sync:
- `pyproject.toml` → `version = "X.Y.Z"` under `[project]`
- `.claude-plugin/plugin.json` → `"version": "X.Y.Z"`

### Credential Storage (`~/.unraid-mcp/.env`)
All runtimes (plugin, direct, Docker) load credentials from `~/.unraid-mcp/.env`.
- **Plugin/direct:** `unraid_health action=setup` writes this file automatically via elicitation,
  **Safe to re-run**: if credentials exist and are working, it asks before overwriting.
  If credentials exist but connection fails, it silently re-configures without prompting.
  or manual: `mkdir -p ~/.unraid-mcp && cp .env.example ~/.unraid-mcp/.env` then edit.
- **Docker:** `docker-compose.yml` loads it via `env_file` before container start.
- **No symlinks needed.** Version bumps do not affect this path.
- **Permissions:** dir=700, file=600 (set automatically by elicitation; set manually if
  using `cp`: `chmod 700 ~/.unraid-mcp && chmod 600 ~/.unraid-mcp/.env`).

### Symlinks
`AGENTS.md` and `GEMINI.md` are symlinks to `CLAUDE.md` for Codex/Gemini compatibility:
```bash
ln -sf CLAUDE.md AGENTS.md && ln -sf CLAUDE.md GEMINI.md
```
