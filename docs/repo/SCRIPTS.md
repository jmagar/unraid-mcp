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
- Plugin manifest has **no** `version` field (plugins are versioned by git commit SHA)

### `bin/generate_unraid_api_reference.py`

Generates canonical Unraid GraphQL documentation from live API introspection. Connects to the Unraid GraphQL endpoint, runs a full introspection query, and writes several output files under `docs/unraid/`:

- `UNRAID-API-COMPLETE-REFERENCE.md` — Full human-readable type/field reference
- `UNRAID-API-SUMMARY.md` — Condensed root operations summary with tables
- `UNRAID-API-INTROSPECTION.json` — Raw introspection JSON snapshot
- `UNRAID-SCHEMA.graphql` — SDL schema output
- `UNRAID-API-CHANGES.md` — Diff of type/field changes vs. the previous snapshot

**Usage:**
```bash
uv run python bin/generate_unraid_api_reference.py
```

Requires `UNRAID_API_URL` and `UNRAID_API_KEY` environment variables (or `--api-url` / `--api-key` flags). SSL verification is disabled by default for self-signed certificates; pass `--verify-ssl` to enable.

**Key flags:**
```
--api-url URL          GraphQL endpoint (default: $UNRAID_API_URL)
--api-key KEY          API key (default: $UNRAID_API_KEY)
--verify-ssl           Enable SSL cert verification
--include-introspection-types  Include __Schema/__Type etc. in output
--timeout-seconds N    HTTP timeout (default: 90)
```

## CI usage

Scripts are called by CI workflows:
- `ci.yml` runs lint, typecheck, test, no-plugin-version, mcp-integration, audit, and gitleaks jobs

## See Also

- [RECIPES.md](RECIPES.md) -- Justfile recipes that invoke scripts
- [../mcp/CICD.md](../mcp/CICD.md) -- CI workflow configuration
- [../plugin/HOOKS.md](../plugin/HOOKS.md) -- Hook scripts
