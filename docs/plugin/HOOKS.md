# Hook Configuration -- unraid-mcp

## Overview

unraid-mcp registers PostToolUse hooks that run after Write, Edit, MultiEdit, or Bash operations to enforce security invariants.

## Hook definition

**File**: `hooks/hooks.json`

```json
{
  "description": "Enforce 600 permissions and keep gitignore aligned",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fix-env-perms.sh",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ensure-ignore-files.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Hook scripts

### fix-env-perms.sh

**Purpose**: Ensures credential files maintain secure permissions after any file operation.

- Sets `~/.unraid-mcp/.env` to mode 600
- Sets `~/.unraid-mcp/` directory to mode 700
- Runs silently (no output on success)
- Timeout: 5 seconds

### ensure-ignore-files.sh

**Purpose**: Keeps `.gitignore` and `.dockerignore` aligned with security requirements.

- Verifies sensitive patterns are present in ignore files
- Prevents credential files from being committed or included in Docker images
- Can run in check mode (`--check`) for CI validation
- Timeout: 5 seconds

### Other hook scripts

| Script | Purpose |
|--------|---------|
| `ensure-gitignore.sh` | Gitignore-specific enforcement |
| `sync-env.sh` | Environment file synchronization |

## Trigger

Hooks fire after every:
- `Write` -- new file creation
- `Edit` -- file modification
- `MultiEdit` -- batch file modification
- `Bash` -- shell command execution

The 5-second timeout ensures hooks never block the development workflow.

## See Also

- [../GUARDRAILS.md](../GUARDRAILS.md) -- Security patterns enforced by hooks
- [PLUGINS.md](PLUGINS.md) -- Plugin manifest that registers hooks
