# Pre-commit Hook Configuration

Pre-commit checks and the SessionStart hook for unraid-mcp.

## Code Quality Tools

### Ruff (linting and formatting)

Configured in `pyproject.toml`:

```bash
# Lint
uv run ruff check unraid_mcp/

# Auto-fix
uv run ruff check --fix unraid_mcp/

# Format
uv run ruff format unraid_mcp/

# Format check (no changes)
uv run ruff format --check unraid_mcp/
```

**Configuration highlights**:
- Target: Python 3.12
- Line length: 100
- Enabled rule sets: F, E, W, I, N, D, UP, YTT, B, Q, C4, SIM, TCH, PTH, ASYNC, RET, PERF, RUF, S
- Docstring convention: Google style
- Per-file ignores: relaxed rules for `__init__.py` and `tests/`
- Cache: `.cache/.ruff_cache`

### ty (type checking)

Astral's fast type checker:

```bash
uv run ty check unraid_mcp/
```

Configured for Python 3.12 with respect for `type: ignore` comments.

## SessionStart Hook

The `hooks/hooks.json` file registers a `SessionStart` hook that delegates to `bin/sync-uv.sh`.

- `bin/sync-uv.sh` runs `UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/.venv" uv sync --project "${CLAUDE_PLUGIN_ROOT}"`
- The hook keeps the installed virtual environment in the plugin data directory

## Justfile Integration

```bash
just lint       # uv run ruff check .
just fmt        # uv run ruff format .
just typecheck  # uv run ty check unraid_mcp/
```

## CI Enforcement

The `ci.yml` workflow runs lint and format checks:
- `uv run ruff check unraid_mcp/ tests/`
- `uv run ruff format --check unraid_mcp/ tests/`
- `uv run ty check unraid_mcp/`

All three must pass for the CI pipeline to succeed.

## See Also

- [CICD.md](CICD.md) -- CI workflow details
- [DEV.md](DEV.md) -- Development workflow
- [../GUARDRAILS.md](../GUARDRAILS.md) -- Security enforcement via hooks
