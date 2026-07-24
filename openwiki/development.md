# Development

Local development workflow for unraid-mcp, including setup, testing, code quality, and versioning.

## Prerequisites

- **Python 3.12+** (required)
- **uv** - Fast Python package manager (`pip install uv` or from [docs.astral.sh](https://docs.astral.sh/uv/))
- **Unraid server** with GraphQL API (for live testing)
- **API key** from Unraid Settings > Management Access > API Keys

## Initial Setup

```bash
# Clone the repository
git clone https://github.com/jmagar/unraid-mcp
cd unraid-mcp

# Install dependencies and create virtual environment
uv sync --dev

# Create .env from example
cp .env.example .env
chmod 600 .env

# Edit .env with your credentials
nano .env  # Add UNRAID_API_URL and UNRAID_API_KEY
```

## Development Commands

### Running the Server

```bash
# Local development (recommended)
uv run unraid-mcp-server

# Direct module execution
uv run -m unraid_mcp

# Hot-reload development server (via Justfile)
just dev
```

The server starts on `http://127.0.0.1:6970/mcp` by default (streamable-http transport).

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test module
uv run pytest tests/test_client.py

# Run with coverage
uv run pytest --cov=unraid_mcp

# Run live integration tests (requires running Unraid)
uv run pytest -m live

# Run live HTTP smoke test
just test-http

# Run specific test categories
uv run pytest tests/schema/        # Schema validation
uv run pytest tests/safety/        # Destructive action guards
uv run pytest tests/property/      # Property-based tests
uv run pytest tests/contract/      # Response contracts
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check unraid_mcp/

# Format code with ruff
uv run ruff format unraid_mcp/

# Type-check with ty (Astral's fast type checker)
uv run ty check unraid_mcp/

# Run all quality checks (via Justfile)
just lint      # Lint only
just fmt       # Format only
just typecheck # Type-check only

# Run validations
just validate-skills      # Validate SKILL.md files
just validate-marketplace # Validate plugin manifests
```

### Justfile Recipes

The [`/Justfile`](Justfile) provides convenient commands:

```bash
just           # List all recipes
just dev       # Start development server
just test      # Run tests
just lint      # Lint code
just fmt       # Format code
just typecheck # Type-check
just up        # Start Docker containers
just down      # Stop Docker containers
just logs      # Tail container logs
just health    # Check /health endpoint
```

## Project Structure

```
unraid-mcp/
├── unraid_mcp/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── server.py            # FastMCP server with middleware
│   ├── version.py           # Version helper
│   ├── config/              # Settings and logging
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging.py
│   ├── core/                # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── client.py        # GraphQL client
│   │   ├── auth.py          # ASGI auth middleware
│   │   ├── guards.py        # Destructive action gates
│   │   ├── pagination.py    # List capping
│   │   ├── response_limit.py
│   │   ├── setup.py         # Credential setup
│   │   ├── utils.py
│   │   ├── validation.py
│   │   └── types.py
│   ├── subscriptions/       # WebSocket subscriptions
│   │   ├── __init__.py
│   │   ├── manager.py       # SubscriptionManager
│   │   ├── resources.py     # MCP resource URIs
│   │   ├── protocol.py
│   │   ├── queries.py
│   │   ├── state.py
│   │   ├── snapshot.py
│   │   ├── utils.py
│   │   └── diagnostics.py
│   └── tools/               # Domain tools (17 modules)
│       ├── __init__.py
│       ├── unraid.py        # Consolidated router
│       ├── _system.py
│       ├── _health.py
│       ├── _array.py
│       ├── _disk.py
│       ├── _docker.py
│       ├── _vm.py
│       ├── _notification.py
│       ├── _key.py
│       ├── _plugin.py
│       ├── _rclone.py
│       ├── _setting.py
│       ├── _connect.py
│       ├── _customization.py
│       ├── _oidc.py
│       ├── _onboarding.py
│       ├── _user.py
│       └── _live.py
├── tests/                   # Test suites
├── docs/                    # Extensive documentation
├── plugins/                 # Claude Code / Codex plugin
├── scripts/                 # Utility scripts
├── pyproject.toml
├── uv.lock
├── Justfile
├── Dockerfile
├── docker-compose.yaml
└── .github/                 # CI/CD workflows
```

## Adding a New Tool Subaction

When adding a new subaction to a domain tool:

1. **Add GraphQL query to the domain dict** (`/unraid_mcp/tools/_<domain>.py`):

```python
_DOCKER_QUERIES = {
    "new_subaction": """
        query NewSubaction($id: ID!) {
            docker(id: $id) {
                id
                name
            }
        }
    """,
}
```

2. **Add subaction name to handler** (if not auto-routed):

```python
def _handle_docker(
    subaction: str,
    **kwargs: Any,
) -> Any:
    if subaction == "new_subaction":
        container_id = kwargs.get("container_id")
        # ... implementation
```

3. **Mark as destructive if needed**:

```python
_DOCKER_DESTRUCTIVE = {"remove_container", "delete_entries", "new_destructive_subaction"}
```

4. **Add to tests** (`/tests/test_schema_drift_workflow.py` for schema parity):

```python
def test_new_subaction_response_contract():
    result = unraid(action="docker", subaction="new_subaction", container_id="test")
    assert result is not None
```

5. **Update documentation** (if major feature):
   - Add to [`/docs/mcp/TOOLS.md`](docs/mcp/TOOLS.md) table
   - Update action/subaction count in README
   - Add to OpenWiki [api-reference.md](openwiki/api-reference.md)

6. **Run tests and linting**:

```bash
just test
just lint
just typecheck
```

## Schema Drift Detection

The project includes automated schema drift detection to ensure the MCP tool surface matches the upstream Unraid GraphQL API.

### Testing Schema Parity

```bash
# Run schema drift tests
uv run pytest tests/schema/test_api_parity.py

# Generate API parity report
uv run python scripts/report_api_parity.py
```

See [`/tests/schema/test_api_parity.py`](tests/schema/test_api_parity.py) for the automated check and [`/docs/unraid/UNRAID-API-CHANGES.md`](docs/unraid/UNRAID-API-CHANGES.md) for recent changes.

### Updating for Schema Changes

If Unraid adds a new field or operation:

1. **Add GraphQL query to the appropriate domain dict**
2. **Update the corresponding tool handler**
3. **Run schema parity tests** to verify coverage
4. **Commit with Conventional Commit message** (e.g., `feat(docker): add container health endpoint`)
5. **release-please** will bump the version on merge

## Destructive Action Testing

Destructive actions are tested in two ways:

1. **Safety tests** (verify `confirm=True` guard):

```python
def test_array_stop_array_requires_confirm():
    """Calling stop_array without confirm=True should raise ToolError."""
    with pytest.raises(ToolError, match="confirm.*True"):
        unraid(action="array", subaction="stop_array", confirm=False)
```

2. **Live manual tests** (execute safely in dev):

```bash
# Create test VM first, then test force_stop
mcporter call --stdio-cmd "uv run unraid-mcp-server" --tool unraid \
  --args '{"action":"vm","subaction":"force_stop","vm_id":"test-vm","confirm":true}' --output json
```

See [`/docs/DESTRUCTIVE_ACTIONS.md`](docs/DESTRUCTIVE_ACTIONS.md) for testing strategies.

## Versioning

**Versioning is fully automated by release-please.** Do NOT bump versions by hand.

### Conventional Commits

Use Conventional Commit messages so release-please computes the correct bump:

- `feat!` or `BREAKING CHANGE` → **major** (X+1.0.0)
- `feat` or `feat(...)` → **minor** (X.Y+1.0)
- `fix`, `chore`, `refactor`, `test`, `docs`, etc. → **patch** (X.Y.Z+1)

Examples:
```bash
git commit -m "feat(docker): add container health endpoint"
git commit -m "fix: handle null response from Unraid API"
git commit -m "feat!: remove deprecated SSH action"
```

### What release-please Keeps in Sync

release-please automatically updates these files:
- `pyproject.toml` — `version = "X.Y.Z"`
- `plugins/unraid/.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
- `plugins/unraid/.codex-plugin/plugin.json` — `"version": "X.Y.Z"`
- `gemini-extension.json` — `"version": "X.Y.Z"`
- `CHANGELOG.md` — new entry from commit messages

`server.json` (placeholder `0.0.0` in-repo) and `unraid_mcp/version.py` (reads package metadata) are never edited.

### Release Workflow

1. Feature branch commits use Conventional Commits
2. PR merges to `main`
3. CI runs release-please action
4. release-please computes version bump from commits
5. release-please creates a release PR with version bump and CHANGELOG
6. Release PR merges → tag created → GitHub Actions publish to PyPI and Docker

See [`/AGENTS.md`](AGENTS.md) and [`/.github/workflows/release-please.yml`](.github/workflows/release-please.yml) for details.

## CI/CD

The project uses GitHub Actions for CI/CD:

- **`.github/workflows/ci.yml`** - Lint, format, type-check, tests on every push
- **`.github/workflows/claude.yml`** - Claude Code review
- **`.github/workflows/docker-publish.yml`** - Docker image builds
- **`.github/workflows/publish-pypi.yml`** - PyPI publishing
- **`.github/workflows/release-please.yml`** - Automated versioning
- **`.github/workflows/openwiki-update.yml`** - Scheduled/manual OpenWiki documentation updates (`openwiki code --update --print`) run with OpenRouter (`OPENWIKI_PROVIDER=openrouter`, `OPENWIKI_MODEL_ID=z-ai/glm-5.2`) and include tracing/metadata env vars (`LANGCHAIN_PROJECT=openwiki`, `LANGCHAIN_TRACING_V2=true`, optional `LANGSMITH_API_KEY`) while generating a PR that includes `openwiki/`, `AGENTS.md`, `CLAUDE.md`, and the workflow file itself.
- **`.github/workflows/schema-drift.yml`** - Schema drift detection

## Common Development Tasks

### Adding a New Domain Tool

1. Create `/unraid_mcp/tools/_<domain>.py`
2. Export `_*_QUERIES`, `_*_MUTATIONS`, `_DESTRUCTIVE`, and `_handle_*`
3. Register in `/unraid_mcp/tools/unraid.py` router
4. Add tests in `/tests/`
5. Update documentation

### Debugging WebSocket Subscriptions

```bash
# Enable DEBUG logging
export UNRAID_MCP_LOG_LEVEL=DEBUG

# Check subscription diagnostics
uv run unraid-mcp-server
unraid(action="subscriptions", subaction="diagnose")

# Test a specific query
unraid(action="subscriptions", subaction="test_query", subscription_query="{...}")
```

### Testing with a Mock Server

```bash
# Start the mock Unraid server (Node.js)
cd tests/mock
npm install
npm start

# Run mock integration tests
uv run pytest tests/mock/
```

See [`/tests/mock/README.md`](tests/mock/README.md) for mock server details.

### Updating Unraid API Reference

```bash
# Generate API reference from introspection
uv run python scripts/generate_unraid_api_reference.py

# Update docs/unraid/ reference files
# Commit changes
```

See [`/docs/unraid/`](docs/unraid/) for API reference documentation.

## Source References

- **Entry point**: `/unraid_mcp/main.py`
- **Server**: `/unraid_mcp/server.py`
- **Tools**: `/unraid_mcp/tools/`
- **Tests**: `/tests/`
- **Justfile**: `/Justfile`
- **Configuration**: `/pyproject.toml`
- **CI/CD**: `/.github/workflows/`
- **Development docs**: [`/docs/mcp/DEV.md`](docs/mcp/DEV.md)
- **Repository workflow**: [`/docs/repo/`](docs/repo/)
- **Testing guide**: [`/docs/mcp/TESTS.md`](docs/mcp/TESTS.md)
- **Pre-commit hooks**: [`/docs/mcp/PRE-COMMIT.md`](docs/mcp/PRE-COMMIT.md)
