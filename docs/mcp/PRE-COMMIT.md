# Pre-commit Hook Configuration

Pre-commit checks and PostToolUse hooks for unraid-mcp.

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

## PostToolUse Hooks

The `.claude-plugin/hooks/hooks.json` registers hooks that run after Write, Edit, MultiEdit, or Bash operations:

### fix-env-perms.sh

Ensures credential files maintain secure permissions:
- `~/.unraid-mcp/.env` stays at mode 600
- `~/.unraid-mcp/` directory stays at mode 700

### ensure-ignore-files.sh

Keeps `.gitignore` and `.dockerignore` aligned:
- Ensures sensitive patterns are never committed
- Prevents credential files from being included in Docker images
- Runs in check mode (no modifications) during CI

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
