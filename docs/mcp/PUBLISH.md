# Publishing Strategy

Versioning and release workflow for unraid-mcp.

## Versioning

Semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (X.0.0): Breaking changes to the MCP tool interface
- **MINOR** (1.X.0): New actions, subactions, or features (backward compatible)
- **PATCH** (1.0.X): Bug fixes, documentation updates

## Version files

All must contain the same version string:

| File | Format |
|------|--------|
| `pyproject.toml` | `version = "X.Y.Z"` in `[project]` |
| `.claude-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `.codex-plugin/plugin.json` | `"version": "X.Y.Z"` |
| `gemini-extension.json` | `"version": "X.Y.Z"` |
| `server.json` | Updated by publish workflow at release time |
| `CHANGELOG.md` | Entry under the new version header |

CI enforces version sync across the first four files.

## Release workflow

### Automated (Justfile)

```bash
# Patch release (1.2.2 -> 1.2.3)
just publish patch

# Minor release (1.2.3 -> 1.3.0)
just publish minor

# Major release (1.3.0 -> 2.0.0)
just publish major
```

The `just publish` recipe:
1. Verifies you are on `main` with a clean working tree
2. Pulls latest from origin
3. Bumps version in `pyproject.toml` and all plugin manifests
4. Commits as `release: vX.Y.Z`
5. Tags as `vX.Y.Z`
6. Pushes to origin with tags

### What happens after push

The tag push triggers two workflows:

**`publish-pypi.yml`**:
1. Verifies tag version matches `pyproject.toml`
2. Builds sdist and wheel with `uv build`
3. Publishes to PyPI with trusted publisher attestations
4. Creates GitHub Release with auto-generated notes and dist artifacts
5. Updates `server.json` version and publishes to MCP Registry via `mcp-publisher`

**`docker-publish.yml`**:
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
