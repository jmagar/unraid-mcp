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
| `no-plugin-version` | Verify plugin manifests declare no `version` (SHA-versioned) | `bin/check-no-plugin-version.sh` |
| `mcp-integration` | Live MCP integration tests | `test_live.sh` with secrets (push/same-repo PRs only) |
| `audit` | Dependency security audit | `uv audit` |

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

## No-plugin-version enforcement

The Claude/Codex plugin manifests are versioned by git commit SHA, so they must
**not** declare a `version` field. The `no-plugin-version` job runs
`bin/check-no-plugin-version.sh`, which fails the pipeline if a `version` key
reappears in either of:
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`

Not checked: `gemini-extension.json` keeps a static `version` (the Gemini CLI
requires the field), and `pyproject.toml` keeps its `version` (required by Python
packaging).

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
| build | `just build` or `docker build -t unraid-mcp .` |

## See Also

- [TESTS.md](TESTS.md) -- Test suite details
- [PUBLISH.md](PUBLISH.md) -- Versioning and release strategy
- [PRE-COMMIT.md](PRE-COMMIT.md) -- Local git hook checks
