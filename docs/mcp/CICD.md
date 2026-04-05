# CI/CD Workflows

GitHub Actions configuration for unraid-mcp.

## Workflows

### `ci.yml` -- Continuous Integration

**Triggers**: Push to `main`, `feat/**`, `fix/**`; PRs to `main`.

| Job | Purpose | Tools |
|-----|---------|-------|
| `lint` | Ruff check and format verification | `ruff check`, `ruff format --check` |
| `typecheck` | Static type analysis | `ty check` |
| `test` | Unit tests with coverage | `pytest -m "not slow and not integration" --cov` |
| `version-sync` | Verify all version files match | Shell script comparing pyproject.toml, plugin.json (x3), gemini-extension.json |
| `mcp-integration` | Live MCP integration tests | `test_live.sh` with secrets (push/same-repo PRs only) |
| `audit` | Dependency security audit | `uv audit` |
| `docker-security` | Docker security checks | `check-docker-security.sh`, `check-no-baked-env.sh`, `ensure-ignore-files.sh` |

### `docker-publish.yml` -- Docker Image Build

**Triggers**: Push to `main`, tags `v*`, PRs to `main`, manual dispatch.

| Step | Purpose |
|------|---------|
| Docker Buildx setup | Multi-platform build support |
| GHCR login | Authenticate to GitHub Container Registry |
| Metadata extraction | Generate image tags (semver, branch, SHA, latest) |
| Build and push | Multi-arch (amd64, arm64), layer caching (GHA), SBOM, provenance |
| Trivy scan | Vulnerability scan for CRITICAL and HIGH severity |

**Image tags**: `latest` (main branch), `v1.2.3`, `v1.2`, `v1`, `main`, `pr-N`, `sha-<hex>`.

**Registry**: `ghcr.io/jmagar/unraid-mcp`.

### `publish-pypi.yml` -- PyPI and Registry Release

**Triggers**: Tags matching `v*.*.*`.

| Step | Purpose |
|------|---------|
| Version verification | Tag must match `pyproject.toml` version |
| Build | `uv build` produces sdist and wheel |
| PyPI publish | Trusted publisher with attestations |
| GitHub Release | Auto-generated release notes with dist artifacts |
| MCP Registry publish | DNS-authenticated publish to `tv.tootie/unraid-mcp` via `mcp-publisher` |

## Version sync enforcement

The `version-sync` job ensures these files all contain the same version string:
- `pyproject.toml`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `gemini-extension.json`

Failure blocks the CI pipeline.

## Secrets required

| Secret | Used by | Purpose |
|--------|---------|---------|
| `GITHUB_TOKEN` | All workflows | GHCR login, release creation |
| `UNRAID_API_URL` | `mcp-integration` | Live test target |
| `UNRAID_API_KEY` | `mcp-integration` | Live test auth |
| `MCP_PRIVATE_KEY` | `publish-pypi` | DNS-authenticated MCP registry publish |

## Local equivalents

| CI Job | Local command |
|--------|--------------|
| lint | `just lint` or `uv run ruff check .` |
| format | `just fmt` or `uv run ruff format .` |
| typecheck | `just typecheck` or `uv run ty check unraid_mcp/` |
| test | `just test` or `uv run pytest` |
| docker-security | `just check-contract` |
| build | `just build` or `docker build -t unraid-mcp .` |

## See Also

- [TESTS.md](TESTS.md) -- Test suite details
- [PUBLISH.md](PUBLISH.md) -- Versioning and release strategy
- [PRE-COMMIT.md](PRE-COMMIT.md) -- Local pre-commit checks
