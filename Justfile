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

# Run HTTP end-to-end smoke-test against the local server (auto-reads token from ~/.unraid-mcp/.env)
test-http:
    bash tests/mcporter/test-http.sh

# Run HTTP e2e test with auth disabled (for gateway-protected deployments)
test-http-no-auth:
    bash tests/mcporter/test-http.sh --skip-auth

# Run HTTP e2e test against a remote URL
# Usage: just test-http-remote https://unraid.tootie.tv/mcp
test-http-remote url:
    bash tests/mcporter/test-http.sh --url {{url}} --skip-auth

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

# ── CLI Generation ────────────────────────────────────────────────────────────

# Generate a standalone CLI for this server (requires running server)
generate-cli:
    #!/usr/bin/env bash
    set -euo pipefail
    PORT="${UNRAID_MCP_PORT:-6970}"
    echo "⚠  Server must be running on port ${PORT} (run 'just dev' first)"
    echo "⚠  Generated CLI embeds your OAuth token — do not commit or share"
    mkdir -p dist dist/.cache
    current_hash=$(timeout 10 curl -sf \
      -H "Authorization: Bearer $MCP_TOKEN" \
      -H "Accept: application/json, text/event-stream" \
      "http://localhost:${PORT}/mcp/tools/list" 2>/dev/null | sha256sum | cut -d' ' -f1 || echo "nohash")
    cache_file="dist/.cache/unraid-mcp-cli.schema_hash"
    if [[ -f "$cache_file" ]] && [[ "$(cat "$cache_file")" == "$current_hash" ]] && [[ -f "dist/unraid-mcp-cli" ]]; then
      echo "SKIP: unraid-mcp tool schema unchanged — use existing dist/unraid-mcp-cli"
      exit 0
    fi
    timeout 30 mcporter generate-cli \
      --command "http://localhost:${PORT}/mcp" \
      --header "Authorization: Bearer $MCP_TOKEN" \
      --name unraid-mcp-cli \
      --output dist/unraid-mcp-cli
    printf '%s' "$current_hash" > "$cache_file"
    echo "✓ Generated dist/unraid-mcp-cli (requires bun at runtime)"

# ── Cleanup ───────────────────────────────────────────────────────────────────

# Remove build artifacts, caches, and compiled files
clean:
    rm -rf dist/ build/ .pytest_cache/ .ruff_cache/ .mypy_cache/ htmlcov/ .coverage coverage.xml
    find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
    find . -name '*.pyc' -not -path './.venv/*' -delete 2>/dev/null || true
    @echo "Cleaned build artifacts"

# Publish: bump version, tag, push (triggers PyPI + Docker publish)
publish bump="patch":
    #!/usr/bin/env bash
    set -euo pipefail
    [ "$(git branch --show-current)" = "main" ] || { echo "Switch to main first"; exit 1; }
    [ -z "$(git status --porcelain)" ] || { echo "Commit or stash changes first"; exit 1; }
    git pull origin main
    CURRENT=$(grep -m1 "^version" pyproject.toml | sed "s/.*\"\(.*\)\".*/\1/")
    IFS="." read -r major minor patch <<< "$CURRENT"
    case "{{bump}}" in
      major) major=$((major+1)); minor=0; patch=0 ;;
      minor) minor=$((minor+1)); patch=0 ;;
      patch) patch=$((patch+1)) ;;
      *) echo "Usage: just publish [major|minor|patch]"; exit 1 ;;
    esac
    NEW="${major}.${minor}.${patch}"
    echo "Version: ${CURRENT} → ${NEW}"
    sed -i "s/^version = \"${CURRENT}\"/version = \"${NEW}\"/" pyproject.toml
    for f in .claude-plugin/plugin.json .codex-plugin/plugin.json gemini-extension.json; do
      [ -f "$f" ] && python3 -c "import json; d=json.load(open(\"$f\")); d[\"version\"]=\"${NEW}\"; json.dump(d,open(\"$f\",\"w\"),indent=2); open(\"$f\",\"a\").write(\"
\")"
    done
    git add -A && git commit -m "release: v${NEW}" && git tag "v${NEW}" && git push origin main --tags
    echo "Tagged v${NEW} — publish workflow will run automatically"

