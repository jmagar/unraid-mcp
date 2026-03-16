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

### Google OAuth (Optional — protects the HTTP server)

When `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `UNRAID_MCP_BASE_URL` are all set,
the MCP server requires Google login before any tool call.

| Env Var | Required | Purpose |
|---------|----------|---------|
| `GOOGLE_CLIENT_ID` | For OAuth | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | For OAuth | Google OAuth 2.0 Client Secret |
| `UNRAID_MCP_BASE_URL` | For OAuth | Public URL of this server (e.g. `http://10.1.0.2:6970`) |
| `UNRAID_MCP_JWT_SIGNING_KEY` | Recommended | Stable 32+ char secret — prevents token invalidation on restart |

**Google Cloud Console setup:**
1. APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web application)
2. Authorized redirect URIs: `<UNRAID_MCP_BASE_URL>/auth/callback`
3. Copy Client ID + Secret to `~/.unraid-mcp/.env`

**Generate a stable JWT signing key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Omit `GOOGLE_CLIENT_ID` to run without auth** (default — preserves existing behaviour).

**Full guide:** [`docs/GOOGLE_OAUTH.md`](docs/GOOGLE_OAUTH.md)

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
- **Persistent Subscription Manager**: `live` action subactions use a shared `SubscriptionManager`
  that maintains persistent WebSocket connections. Resources serve cached data via
  `subscription_manager.get_resource_data(action)`. A "connecting" placeholder is returned
  while the subscription starts — callers should retry in a moment. When
  `UNRAID_AUTO_START_SUBSCRIPTIONS=false`, resources fall back to on-demand `subscribe_once`.

### Tool Categories (1 Tool, ~107 Subactions)

The server registers a **single consolidated `unraid` tool** with `action` (domain) + `subaction` (operation) routing. Call it as `unraid(action="docker", subaction="list")`.

| action | subactions |
|--------|-----------|
| **system** (19) | overview, array, network, registration, variables, metrics, services, display, config, online, owner, settings, server, servers, flash, ups_devices, ups_device, ups_config |
| **health** (4) | check, test_connection, diagnose, setup |
| **array** (13) | parity_status, parity_history, parity_start, parity_pause, parity_resume, parity_cancel, start_array, stop_array*, add_disk, remove_disk*, mount_disk, unmount_disk, clear_disk_stats* |
| **disk** (6) | shares, disks, disk_details, log_files, logs, flash_backup* |
| **docker** (7) | list, details, start, stop, restart, networks, network_details |
| **vm** (9) | list, details, start, stop, pause, resume, force_stop*, reboot, reset* |
| **notification** (12) | overview, list, create, archive, mark_unread, recalculate, archive_all, archive_many, unarchive_many, unarchive_all, delete*, delete_archived* |
| **key** (7) | list, get, create, update, delete*, add_role, remove_role |
| **plugin** (3) | list, add, remove* |
| **rclone** (4) | list_remotes, config_form, create_remote, delete_remote* |
| **setting** (2) | update, configure_ups* |
| **customization** (5) | theme, public_theme, is_initial_setup, sso_enabled, set_theme |
| **oidc** (5) | providers, provider, configuration, public_providers, validate_session |
| **user** (1) | me |
| **live** (11) | cpu, memory, cpu_telemetry, array_state, parity_progress, ups_status, notifications_overview, notification_feed, log_tail, owner, server_status |

`*` = destructive, requires `confirm=True`

### Destructive Actions (require `confirm=True`)
- **array**: stop_array, remove_disk, clear_disk_stats
- **vm**: force_stop, reset
- **notifications**: delete, delete_archived
- **rclone**: delete_remote
- **keys**: delete
- **disk**: flash_backup
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
**Mutation handlers MUST return before the domain query dict lookup.** Mutations are not in the domain `_*_QUERIES` dicts (e.g., `_DOCKER_QUERIES`, `_ARRAY_QUERIES`) — reaching that line for a mutation subaction causes a `KeyError`. Always add early-return `if subaction == "mutation_name": ... return` blocks BEFORE the queries lookup.

### Test Patching
- Patch at the **tool module level**: `unraid_mcp.tools.unraid.make_graphql_request` (not core)
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

# Destructive action smoke-test (confirms guard blocks without confirm=True)
./tests/mcporter/test-destructive.sh [MCP_URL]
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
- **Plugin/direct:** `unraid action=health subaction=setup` writes this file automatically via elicitation,
  **Safe to re-run**: always prompts for confirmation before overwriting existing credentials,
  whether the connection is working or not (failed probe may be a transient outage, not bad creds).
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
