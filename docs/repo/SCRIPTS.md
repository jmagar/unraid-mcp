# Scripts Reference -- unraid-mcp

## Quality gate scripts (`scripts/`)

### check-docker-security.sh

Audits the Dockerfile for security best practices:
- Non-root user verification
- No hardcoded secrets
- Proper permissions
- Minimal base image

```bash
bash scripts/check-docker-security.sh Dockerfile
```

### check-no-baked-env.sh

Verifies no environment variables are baked into Docker images or committed to version control:
- Scans Dockerfile for `ENV` directives with secrets
- Checks for `.env` files in tracked directories

```bash
bash scripts/check-no-baked-env.sh .
```

### check-outdated-deps.sh

Checks for outdated Python dependencies:

```bash
bash scripts/check-outdated-deps.sh
```

### ensure-ignore-files.sh

Validates `.gitignore` and `.dockerignore` contain required patterns:
- Credential files
- Cache directories
- Build artifacts
- Log files

```bash
# Check mode (CI)
bash scripts/ensure-ignore-files.sh --check .

# Fix mode (development)
bash scripts/ensure-ignore-files.sh .
```

### lint-plugin.sh

Validates plugin manifest files:
- JSON syntax
- Required fields
- Version consistency
- MCP server configuration

```bash
bash scripts/lint-plugin.sh
```

### validate-marketplace.sh

Validates marketplace JSON configuration:

```bash
bash scripts/validate-marketplace.sh
```

## Utility scripts

### generate_unraid_api_reference.py

Generates API reference documentation from GraphQL schema introspection:

```bash
python scripts/generate_unraid_api_reference.py
```

Produces the docs in `docs/UNRAID_API_COMPLETE_REFERENCE.md`.

## Hook scripts (`hooks/scripts/`)

| Script | Purpose |
|--------|---------|
| `fix-env-perms.sh` | Enforce 600 permissions on credential files |
| `ensure-ignore-files.sh` | Keep ignore files aligned |
| `ensure-gitignore.sh` | Gitignore-specific checks |
| `sync-env.sh` | Environment file synchronization |

## CI usage

Scripts are called by CI workflows:
- `ci.yml` runs `check-docker-security.sh`, `check-no-baked-env.sh`, `ensure-ignore-files.sh --check`
- `just check-contract` runs all three locally

## See Also

- [RECIPES.md](RECIPES.md) -- Justfile recipes that invoke scripts
- [../mcp/CICD.md](../mcp/CICD.md) -- CI workflow configuration
- [../plugin/HOOKS.md](../plugin/HOOKS.md) -- Hook scripts
