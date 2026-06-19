# Scripts Reference -- unraid-mcp

## Hook scripts (`hooks/scripts/`)

No hook scripts remain — the hooks directory only contains `hooks.json` registering `bin/sync-uv.sh` at SessionStart.

## bin/ scripts

### `bin/validate-marketplace.sh`

Validates the Claude Code marketplace and plugin structure. Checks JSON manifests, required files, plugin listing, marketplace metadata, and version sync between `pyproject.toml` and `.claude-plugin/plugin.json`.

**Usage:**
```bash
bash bin/validate-marketplace.sh [repo-root]
```

Run from the repo root (no arguments needed in that case). Exits 0 if all checks pass, 1 on any failure. Prints a summary of passed/failed checks.

**What it validates:**
- `.claude-plugin/marketplace.json` exists and is valid JSON with required fields
- `.claude-plugin/plugin.json` exists and is valid JSON with required fields
- Required skill files (`skills/unraid/SKILL.md`, `README.md`, `scripts/`, `examples/`, `references/`)
- Plugin is listed in the marketplace manifest
- Version in `pyproject.toml` matches version in `.claude-plugin/plugin.json`

### `bin/generate_unraid_api_reference.py`

Generates canonical Unraid GraphQL documentation from API introspection. Connects to the Unraid GraphQL endpoint, runs a full introspection query, and writes several output files under `docs/unraid/`:

- `UNRAID-API-COMPLETE-REFERENCE.md` — Full type/field reference, rendered by [graphql-markdown](https://github.com/exogen/graphql-markdown)
- `UNRAID-API-SUMMARY.md` — Condensed root operations summary with tables (curated)
- `UNRAID-API-INTROSPECTION.json` — Raw introspection JSON snapshot
- `UNRAID-SCHEMA.graphql` — SDL schema output
- `UNRAID-API-CHANGES.md` — Schema diff vs. the previous snapshot, produced by [GraphQL Inspector](https://the-guild.dev/graphql/inspector)

The reference and change report are rendered by official GraphQL tooling invoked via `npx` on demand, so **Node.js 18+ is required** when generating docs (no JS dependencies are committed). The condensed summary is generated in pure Python.

**Usage:**
```bash
# From a live API (default)
uv run python bin/generate_unraid_api_reference.py

# Offline, from a saved introspection payload (reproducible; used by tests)
uv run python bin/generate_unraid_api_reference.py \
  --from-introspection docs/unraid/UNRAID-API-INTROSPECTION.json
```

Live mode requires `UNRAID_API_URL` and `UNRAID_API_KEY` environment variables (or `--api-url` / `--api-key` flags). SSL verification is disabled by default for self-signed certificates; pass `--verify-ssl` to enable.

**Key flags:**
```
--api-url URL          GraphQL endpoint (default: $UNRAID_API_URL)
--api-key KEY          API key (default: $UNRAID_API_KEY)
--from-introspection P Read introspection from a saved JSON payload (offline)
--verify-ssl           Enable SSL cert verification
--include-introspection-types  Include __Schema/__Type etc. in summary
--timeout-seconds N    HTTP timeout (default: 90)
```

## CI usage

Scripts are called by CI workflows:
- `ci.yml` runs lint, typecheck, test, version-sync, mcp-integration, audit, and gitleaks jobs

## See Also

- [RECIPES.md](RECIPES.md) -- Justfile recipes that invoke scripts
- [../mcp/CICD.md](../mcp/CICD.md) -- CI workflow configuration
- [../plugin/HOOKS.md](../plugin/HOOKS.md) -- Hook scripts
