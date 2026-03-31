# Unraid MCP Server — Justfile
# Run `just` to list available recipes

default:
    @just --list

# ── Development ───────────────────────────────────────────────────────────────

# Start development server (hot-reload via watchfiles)
dev:
    uv run python -m unraid_mcp

# Run tests
test:
    uv run pytest tests/ -v

# Run linter (ruff)
lint:
    uv run ruff check .

# Format code (ruff)
fmt:
    uv run ruff format .

# Type-check (pyright / mypy)
typecheck:
    uv run pyright unraid_mcp/ || uv run mypy unraid_mcp/

# Validate skills SKILL.md files exist and are non-empty
validate-skills:
    @echo "=== Validating skills ==="
    @for f in skills/*/SKILL.md; do \
        if [ -f "$$f" ]; then \
            echo "  ✓ $$f"; \
        else \
            echo "  ✗ SKILL.md not found in skills/"; \
            exit 1; \
        fi; \
    done
    @echo "Skills validation passed"

# Build Docker image
build:
    docker build -t unraid-mcp .

# ── Docker Compose ────────────────────────────────────────────────────────────

# Start containers
up:
    docker compose up -d

# Stop containers
down:
    docker compose down

# Restart containers
restart:
    docker compose restart

# Tail container logs
logs:
    docker compose logs -f

# Check /health endpoint
health:
    @PORT=$$(grep -E '^UNRAID_MCP_PORT=' .env 2>/dev/null | cut -d= -f2 || echo 6970); \
    curl -sf "http://localhost:$$PORT/health" | python3 -m json.tool || echo "Health check failed"

# ── Live Testing ──────────────────────────────────────────────────────────────

# Run live integration tests against a running server
test-live:
    uv run pytest tests/ -v -m live

# ── Setup ─────────────────────────────────────────────────────────────────────

# Create .env from .env.example if missing
setup:
    @if [ ! -f .env ]; then \
        cp .env.example .env && chmod 600 .env; \
        echo "Created .env from .env.example — fill in your credentials"; \
    else \
        echo ".env already exists"; \
    fi

# Generate a secure bearer token for UNRAID_MCP_TOKEN
gen-token:
    @python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# ── Quality Gates ─────────────────────────────────────────────────────────────

# Run docker security checks
check-contract:
    bash scripts/check-docker-security.sh
    bash scripts/check-no-baked-env.sh
    bash scripts/ensure-ignore-files.sh --check

# ── Cleanup ───────────────────────────────────────────────────────────────────

# Remove build artifacts, caches, and compiled files
clean:
    rm -rf dist/ build/ .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ .coverage coverage.xml
    find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
    find . -name '*.pyc' -not -path './.venv/*' -delete 2>/dev/null || true
    @echo "Cleaned build artifacts"
