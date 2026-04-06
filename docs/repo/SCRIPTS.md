# Scripts Reference -- unraid-mcp

## Quality gate scripts (`bin/`)



Audits the Dockerfile for security best practices:
- Non-root user verification
- No hardcoded secrets
- Proper permissions
- Minimal base image

```bash

```



Verifies no environment variables are baked into Docker images or committed to version control:
- Scans Dockerfile for `ENV` directives with secrets
- Checks for `.env` files in tracked directories

```bash

```



Checks for outdated Python dependencies:

```bash

```



Validates `.gitignore` and `.dockerignore` contain required patterns:
- Credential files
- Cache directories
- Build artifacts
- Log files

```bash
# Check mode (CI)


# Fix mode (development)

```

### validate-marketplace.sh

Validates marketplace JSON configuration:

```bash
bash bin/validate-marketplace.sh
```

## Utility scripts

### generate_unraid_api_reference.py

Generates the canonical Unraid API docs from GraphQL schema introspection:

```bash
python bin/generate_unraid_api_reference.py
```

Produces:
- `docs/unraid/UNRAID-API-SUMMARY.md`
- `docs/unraid/UNRAID-API-COMPLETE-REFERENCE.md`
- `docs/unraid/UNRAID-API-INTROSPECTION.json`
- `docs/unraid/UNRAID-SCHEMA.graphql`
- `docs/unraid/UNRAID-API-CHANGES.md`

## Hook scripts (`hooks/scripts/`)

| Script | Purpose |
|--------|---------|
| `fix-env-perms.sh` | Enforce 600 permissions on credential files |


| `sync-env.sh` | Environment file synchronization |

## CI usage

Scripts are called by CI workflows:

- `just check-contract` runs all three locally

## See Also

- [RECIPES.md](RECIPES.md) -- Justfile recipes that invoke scripts
- [../mcp/CICD.md](../mcp/CICD.md) -- CI workflow configuration
- [../plugin/HOOKS.md](../plugin/HOOKS.md) -- Hook scripts
