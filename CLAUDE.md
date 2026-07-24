# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this is

A monorepo of Unraid tooling. It keeps the `dinglebear-ai/unraid-mcp` GitHub
identity and the `unraid-mcp` PyPI name, but internally hosts four release units
plus two agent-plugin integrations.

## Repository layout

| Path | Component | Toolchain | Build / test from repo root |
|------|-----------|-----------|------------------------------|
| `unraid-py/` | Python MCP server (**unraid-mcp** on PyPI, import `unraid_mcp`). Self-contained: its own `pyproject.toml`, `uv.lock`, `Dockerfile`, `docs/`, `openwiki/`, `scripts/`, and tests. | Python / uv / hatchling | `cd unraid-py && uv sync && uv run pytest && uv build --wheel` |
| `unraid-rs/` | Rust MCP server + CLI (crate `unraid-rmcp`, binary `runraid`) and the `unraid-rmcp` npx wrapper. | Rust / cargo | `cd unraid-rs && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test` |
| `plugins/mcp/` | Unraid OS `.plg` shipping the Python server (was `unraid/`). | shell + Python | `bash plugins/mcp/scripts/build-txz.sh <ver> <wheel>` |
| `plugins/incus/` | Unraid OS `.plg` for Incus dev-containers + nested `unraid-api-plugin-incus/` (NestJS/Vue). Build gotchas: see `plugins/incus/CLAUDE.md`. | shell + NestJS/Vue | `cd plugins/incus && ./scripts/verify-classic-package.sh && ./tests/classic-contract.sh` |
| `plugins/codex/` | Unraid OS `.plg` for the Codex chathead (was `unraid-codex/`). | shell + React | `cd plugins/codex && ./tests/contract.sh` |
| `agents/unraid-py/` | Claude/Codex plugin, `name: unraid-mcp`. | — | listed in `.claude-plugin/marketplace.json` |
| `agents/unraid-rs/` | Claude/Codex plugin, `name: runraid`. | — | listed in `.claude-plugin/marketplace.json` |
| Root | Orchestration only: `.claude-plugin/marketplace.json`, merged path-scoped `.github/workflows/`, unified `release-please-config.json` + `.release-please-manifest.json`, umbrella README/CHANGELOG. | — | — |

Per-component guidance lives in each component's own `CLAUDE.md` / `README.md`.
The Python server's detailed dev guide is `unraid-py/CLAUDE.md`.

## Conventions that span the monorepo

- **`.txz` plugin payloads are GitHub release assets, never tracked in git.** A
  `no-large-blobs.yml` CI guard blocks re-committing them; the incus history was
  scrubbed of ~746 MB of committed `.txz`.
- **Every CI action must be SHA-pinned** (`test_every_external_action_is_immutable`
  enforces it across `unraid-py/tests/`). Copy an existing pinned SHA from another
  workflow rather than using a floating `@vN` tag.
- **release-please drives versioning** for all four units. `unraid-py` is the
  primary package with an empty component (unprefixed `vX.Y.Z` tags); the others
  use `unraid-rs-v*`, `incus-v*`, `codex-v*`. The incus/codex `.plg` version
  entities are annotated `x-release-please-version` so the plugin string version
  stays in sync (Unraid does a string version compare — never let it regress).
- **Secret scanning (`secret-scan.yml`) and shared-root validation (`meta-ci.yml`)
  are unfiltered/broadly-scoped** so a path-scoped workflow can never gate them off.
- **CI workflows are path-scoped per component**; a change under one component's
  subtree only runs that component's jobs.

## Toolchain

The root `.mise.toml` is polyglot (python + rust + node) so every component's
toolchain is available from a single `mise install`.
