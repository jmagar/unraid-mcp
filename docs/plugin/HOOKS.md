# Hook Configuration -- unraid-mcp

## Overview

unraid-mcp registers a `SessionStart` hook in `hooks/hooks.json` to keep the Python environment in sync with `uv.lock`.

## Hook definition

**File**: `hooks/hooks.json`

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

## Behavior

- The hook runs at session start before normal work begins.
- `bin/sync-uv.sh` runs `uv sync` against the repo root.
- The resulting virtual environment lives under `${CLAUDE_PLUGIN_DATA}/.venv`.
- The hook entrypoint is `bin/sync-uv.sh`.

## See Also

- [../GUARDRAILS.md](../GUARDRAILS.md) -- Security patterns enforced by hooks
- [PLUGINS.md](PLUGINS.md) -- Plugin manifest that uses the repo-level hooks file
