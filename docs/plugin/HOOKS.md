# Hook Configuration -- unraid-mcp

## Overview

unraid-mcp registers PostToolUse hooks that run after Write, Edit, MultiEdit, or Bash operations to enforce security invariants.

## Hook definition

**File**: `hooks/hooks.json`

The hooks configuration registers a single `SessionStart` hook:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/sync-uv.sh"
          }
        ]
      }
    ]
  }
}
```

## Hook scripts

### bin/sync-uv.sh

**Purpose**: Ensures the uv environment is up to date at the start of each session.

- Runs `uv sync` to install/update dependencies
- Runs silently on success

## Trigger

The hook fires once at `SessionStart` to synchronize the Python environment.

## See Also

- [../GUARDRAILS.md](../GUARDRAILS.md) -- Security patterns enforced by hooks
- [PLUGINS.md](PLUGINS.md) -- Plugin manifest that registers hooks
