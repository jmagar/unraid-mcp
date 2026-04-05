# Plugin Checklist -- unraid-mcp

Pre-release and quality checklist. Complete all items before tagging a release.

## Version and metadata

- [ ] `pyproject.toml` version bumped
- [ ] `.claude-plugin/plugin.json` version matches
- [ ] `.codex-plugin/plugin.json` version matches
- [ ] `gemini-extension.json` version matches
- [ ] `server.json` version matches (updated by publish workflow)
- [ ] `CHANGELOG.md` has entry for the new version
- [ ] All four version files show the same version string

## Code quality

- [ ] `uv run ruff check unraid_mcp/` passes (no lint errors)
- [ ] `uv run ruff format --check unraid_mcp/` passes (no format drift)
- [ ] `uv run ty check unraid_mcp/` passes (no type errors)
- [ ] `uv run pytest -m "not slow and not integration"` passes (all unit tests green)
- [ ] `uv run pytest tests/safety/` passes (destructive action guards verified)
- [ ] `uv run pytest tests/schema/` passes (GraphQL query validation)

## Security

- [ ] No credentials in code, docs, or commit history
- [ ] `~/.unraid-mcp/.env` has `chmod 600` permissions
- [ ] `~/.unraid-mcp/` directory has `chmod 700` permissions
- [ ] `bin/check-docker-security.sh` passes
- [ ] `bin/check-no-baked-env.sh` passes
- [ ] `bin/ensure-ignore-files.sh --check` passes
- [ ] Bearer token uses constant-time comparison (`hmac.compare_digest`)
- [ ] No sensitive values logged (even at DEBUG level)
- [ ] `UNRAID_MCP_BEARER_TOKEN` removed from `os.environ` after startup

## Plugin manifests

- [ ] `.claude-plugin/plugin.json` has correct `mcpServers` config
- [ ] `.codex-plugin/plugin.json` has correct interface metadata
- [ ] `gemini-extension.json` has correct `mcpServers` and `settings`
- [ ] `server.json` has correct MCP registry schema and PyPI package info
- [ ] `skills/unraid/SKILL.md` is up to date with all actions and subactions

## Docker

- [ ] `Dockerfile` uses multi-stage build (builder + runtime)
- [ ] Runtime image runs as non-root user (`mcp:1000`)
- [ ] `HEALTHCHECK` configured in Dockerfile
- [ ] `docker-compose.yaml` healthcheck works for both HTTP and stdio transports
- [ ] Resource limits set (1024M memory, 1.0 CPU)
- [ ] Credentials volume mount is named volume (not bind mount)

## CI/CD

- [ ] `ci.yml` lint, typecheck, test, version-sync, audit, docker-security jobs pass
- [ ] `docker-publish.yml` builds multi-arch (amd64, arm64) images
- [ ] `publish-pypi.yml` tag-version check, PyPI publish, GitHub release, MCP registry publish all configured
- [ ] Trivy vulnerability scan runs on published images

## Hooks

- [ ] `hooks/hooks.json` registers PostToolUse hooks
- [ ] `fix-env-perms.sh` enforces 600 on credential files
- [ ] `ensure-ignore-files.sh` keeps `.gitignore` and `.dockerignore` aligned

## Documentation

- [ ] `CLAUDE.md` reflects current architecture and tool counts
- [ ] `README.md` has correct tool table and quick start examples
- [ ] `skills/unraid/SKILL.md` documents all 15 action domains
- [ ] `docs/` directory is complete and has no template placeholders
