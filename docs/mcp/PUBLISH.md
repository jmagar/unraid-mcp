# Publishing Strategy

Versioning and release workflow for unraid-mcp.

## Versioning

Semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (X.0.0): Breaking changes to the MCP tool interface
- **MINOR** (1.X.0): New actions, subactions, or features (backward compatible)
- **PATCH** (1.0.X): Bug fixes, documentation updates

## Version files

**Do not edit version strings by hand** — release-please keeps these in sync from
Conventional Commits (configured in `release-please-config.json`):

| File | Format | Managed by |
|------|--------|------------|
| `pyproject.toml` | `version = "X.Y.Z"` in `[project]` | release-please |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` | release-please (`extra-files`) |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` | release-please (`extra-files`) |
| `gemini-extension.json` | `"version": "X.Y.Z"` | release-please (`extra-files`) |
| `CHANGELOG.md` | Entry generated from commits | release-please |
| `server.json` | `0.0.0` placeholder in-repo; set from the tag at publish time | `publish-pypi.yml` |
| `unraid_mcp/version.py` | reads `importlib.metadata` at runtime | not a file (auto) |

`.release-please-manifest.json` tracks the last released version. The CI `version-sync`
job is a safety net asserting the first four files agree.

## Release workflow

Releases are driven by **release-please** + Conventional Commits — there is no manual
`just publish`. Bump type is inferred from commit messages: `fix:` → patch, `feat:` →
minor, `feat!:` / `BREAKING CHANGE` → major.

1. Land changes on `main` with Conventional Commit messages.
2. `release-please.yml` opens/updates a `chore(main): release X.Y.Z` PR that bumps every
   version file and updates `CHANGELOG.md`.
3. **Merge the release PR.** release-please creates the `vX.Y.Z` tag and GitHub Release.

> The release-please action authenticates with the `RELEASE_PLEASE_TOKEN` secret (a PAT or
> GitHub App token). The default `GITHUB_TOKEN` cannot trigger the downstream publish
> workflows, so this token is required for PyPI/Docker/registry publishing to fire.

### What happens after the release PR merges

The new tag + Release trigger two workflows:

**`publish-pypi.yml`** (on `release: published`):
1. Verifies the tag version matches `pyproject.toml`
2. Builds sdist and wheel with `uv build`
3. Publishes to PyPI with trusted publisher attestations
4. Attaches the dist artifacts to the release created by release-please
5. Sets `server.json` version from the tag and publishes to the MCP Registry via `mcp-publisher`

**`docker-publish.yml`** (on tag `v*`):
1. Builds multi-arch Docker image (amd64, arm64)
2. Tags with semver variants (`v1.2.3`, `v1.2`, `v1`, `latest`)
3. Pushes to `ghcr.io/jmagar/unraid-mcp`
4. Runs Trivy vulnerability scan

## Distribution channels

| Channel | Package | Install command |
|---------|---------|----------------|
| PyPI | `unraid-mcp` | `pip install unraid-mcp` or `uvx unraid-mcp` |
| GHCR | `ghcr.io/jmagar/unraid-mcp` | `docker pull ghcr.io/jmagar/unraid-mcp:latest` |
| MCP Registry | `tv.tootie/unraid-mcp` | MCP client auto-discovery |
| Claude Plugin | `jmagar/unraid-mcp` | `/plugin install unraid-mcp` |
| GitHub Release | Source + wheel | Download from releases page |

## MCP Registry

Published as `tv.tootie/unraid-mcp` using DNS authentication via `tootie.tv`.

The `server.json` defines the registry entry:
- Package type: `pypi`
- Runtime hint: `uvx`
- Transport: `stdio`
- Required env vars: `UNRAID_API_URL`, `UNRAID_API_KEY`

## See Also

- [CICD.md](CICD.md) -- Workflow configuration details
- [../CHECKLIST.md](../CHECKLIST.md) -- Pre-release checklist
