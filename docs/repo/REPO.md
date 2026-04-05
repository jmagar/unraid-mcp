# Repository Structure -- unraid-mcp

## Directory layout

```
unraid-mcp/
+-- CLAUDE.md                          # Development instructions for AI coding assistants
+-- AGENTS.md -> CLAUDE.md             # Codex compatibility symlink
+-- GEMINI.md -> CLAUDE.md             # Gemini compatibility symlink
+-- CHANGELOG.md                       # Version history
+-- README.md                          # User-facing documentation
+-- LICENSE                            # MIT license
+-- pyproject.toml                     # Python project metadata, dependencies, tool config
+-- uv.lock                            # Locked dependency versions
+-- Justfile                           # Task runner recipes
+-- Dockerfile                         # Multi-stage Docker build
+-- docker-compose.yaml                # Container orchestration
+-- entrypoint.sh                      # Docker entrypoint with env validation
+-- server.json                        # MCP Registry manifest (tv.tootie/unraid-mcp)
+-- gemini-extension.json              # Gemini CLI manifest
+-- .env.example                       # Environment variable template
|
+-- .claude-plugin/
|   +-- plugin.json                    # Claude Code plugin manifest
|   +-- marketplace.json               # Marketplace catalog entry
|   +-- README.md                      # Plugin marketplace description
|
+-- .codex-plugin/
|   +-- plugin.json                    # Codex CLI plugin manifest
|
+-- unraid_mcp/                        # Python source package
|   +-- __init__.py
|   +-- main.py                        # Entry point and shutdown cleanup
|   +-- server.py                      # FastMCP server, middleware chain, ASGI auth
|   +-- version.py                     # Version from package metadata
|   +-- config/
|   |   +-- __init__.py
|   |   +-- settings.py                # Environment loading, configuration constants
|   |   +-- logging.py                 # Structured logging setup
|   +-- core/
|   |   +-- __init__.py
|   |   +-- auth.py                    # BearerAuthMiddleware, HealthMiddleware, WellKnownMiddleware
|   |   +-- client.py                  # Async GraphQL HTTP client
|   |   +-- exceptions.py              # ToolError, CredentialsNotConfiguredError
|   |   +-- guards.py                  # Destructive action gating via elicitation
|   |   +-- middleware_refs.py         # Circular import breaker for error middleware
|   |   +-- setup.py                   # Elicitation-based credential setup
|   |   +-- types.py                   # Shared type definitions
|   |   +-- utils.py                   # safe_get, safe_display_url, path validation
|   |   +-- validation.py             # Input validation helpers
|   +-- subscriptions/
|   |   +-- __init__.py
|   |   +-- diagnostics.py            # Diagnostic tools for subscription debugging
|   |   +-- manager.py                # WebSocket subscription manager singleton
|   |   +-- queries.py                # GraphQL subscription query strings
|   |   +-- resources.py              # MCP resource registration
|   |   +-- snapshot.py               # One-shot subscribe_once fallback
|   |   +-- utils.py                  # WebSocket URL building, SSL context, status analysis
|   +-- tools/
|       +-- __init__.py
|       +-- unraid.py                  # Consolidated action router (15 domains)
|       +-- _array.py                  # Array and parity operations
|       +-- _customization.py          # Theme and UI customization
|       +-- _disk.py                   # Shares, disks, logs, flash backup
|       +-- _docker.py                # Container lifecycle and networks
|       +-- _health.py                 # Health check, connection test
|       +-- _key.py                    # API key management
|       +-- _live.py                   # Live subscription snapshots
|       +-- _notification.py           # Notification CRUD
|       +-- _oidc.py                   # OIDC/SSO providers
|       +-- _plugin.py                 # Plugin management
|       +-- _rclone.py                 # Cloud storage remotes
|       +-- _setting.py                # System settings and UPS
|       +-- _system.py                 # Server info, metrics, network
|       +-- _user.py                   # Current user
|       +-- _vm.py                     # Virtual machine lifecycle
|
+-- skills/
|   +-- unraid/
|       +-- SKILL.md                   # Client-facing skill documentation
|
+-- hooks/
|   +-- hooks.json                     # PostToolUse hook definitions
|   +-- scripts/
|       +-- fix-env-perms.sh           # Credential permission enforcement
|       +-- ensure-ignore-files.sh     # Gitignore/dockerignore alignment
|       +-- ensure-gitignore.sh        # Gitignore-specific checks
|       +-- sync-env.sh               # Environment file synchronization
|
+-- scripts/
|   +-- check-docker-security.sh       # Dockerfile security audit
|   +-- check-no-baked-env.sh          # No baked environment variables
|   +-- check-outdated-deps.sh         # Dependency freshness
|   +-- ensure-ignore-files.sh         # Ignore file validation
|   +-- generate_unraid_api_reference.py  # GraphQL schema to docs
|   +-- lint-plugin.sh                 # Plugin manifest validation
|   +-- validate-marketplace.sh        # Marketplace JSON validation
|
+-- tests/                             # Test suite (see mcp/TESTS.md)
|   +-- conftest.py
|   +-- test_*.py                      # 28 unit test files
|   +-- contract/                      # Response shape tests
|   +-- http_layer/                    # httpx layer tests
|   +-- integration/                   # WebSocket lifecycle tests
|   +-- mcporter/                      # End-to-end smoke tests
|   +-- property/                      # Hypothesis property tests
|   +-- safety/                        # Destructive guard tests
|   +-- schema/                        # GraphQL validation tests
|
+-- docs/                              # Documentation (this directory)
|   +-- plans/                         # Development plans
|   +-- reports/                       # Audit reports
|   +-- sessions/                      # Session logs
|   +-- superpowers/                   # Capability docs
|   +-- AUTHENTICATION.md              # Auth reference
|   +-- DESTRUCTIVE_ACTIONS.md         # Destructive action reference
|   +-- MARKETPLACE.md                 # Marketplace guide
|   +-- PUBLISHING.md                  # Publishing guide
|   +-- UNRAID_API_*.md                # Unraid API documentation
|   +-- unraid-schema.graphql          # Full GraphQL schema
|   +-- unraid-api-introspection.json  # Schema introspection data
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml                     # CI pipeline
|       +-- docker-publish.yml         # Docker image publishing
|       +-- publish-pypi.yml           # PyPI and MCP registry publishing
|
+-- assets/                            # Icons and logos
+-- backups/                           # Flash backup storage
+-- logs/                              # Application logs
```

## Key conventions

- **Single source package**: `unraid_mcp/` contains all server code
- **Domain modules**: Private `_<domain>.py` files in `tools/`, imported by `unraid.py`
- **Config module**: `config/settings.py` loads all env vars at import time
- **Symlinks**: `AGENTS.md` and `GEMINI.md` symlink to `CLAUDE.md`
- **Credentials**: Never stored in repo; live at `~/.unraid-mcp/.env`
