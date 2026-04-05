# MCP Elicitation

Interactive credential and configuration entry via the MCP elicitation protocol.

## What is elicitation

Elicitation is an MCP protocol capability that allows servers to request information from users interactively through the client. Instead of requiring pre-configured environment variables, the server can prompt the user for missing values at runtime.

## When elicitation is used

- **First-run setup**: Server detects missing `UNRAID_API_URL` or `UNRAID_API_KEY` and prompts the user via `health/setup`.
- **Credential rotation**: User triggers `health/setup` to reconfigure credentials, even when existing credentials are working.
- **Destructive operation confirmation**: All 12 destructive subactions gate execution behind explicit user acknowledgment.

## Credential setup flow

### Implementation (`core/setup.py`)

The `elicit_and_configure()` function handles first-run and reconfiguration:

1. Client calls `unraid(action="health", subaction="setup")`
2. If credentials exist:
   - Server tests the connection (GraphQL query for `online` status)
   - Reports whether connection is working, failing, or uncertain
   - Asks via `elicit_reset_confirmation()` whether to overwrite (uses `bool` response type)
   - If user declines, returns current status without changes
3. Server sends elicitation request with `_UnraidCredentials` schema:
   ```
   Fields:
     api_url: str  -- Unraid GraphQL endpoint (e.g. https://10-1-0-2.xxx.myunraid.net:31337)
     api_key: str  -- API key from Unraid Settings > Management Access > API Keys
   ```
4. Client renders an interactive form
5. User fills in values and submits
6. Server writes to `~/.unraid-mcp/.env` (atomic: tmp file + `os.replace`)
7. Sets directory to mode 700, file to mode 600
8. Applies credentials to running process via `apply_runtime_config()`
9. Returns success message

### Connection probe behavior

The setup wizard always prompts for confirmation before overwriting, even if the current connection is failing. This prevents a transient outage from silently triggering a credential reset.

Status messages:
- "Credentials already configured (and working)" -- connection test passed
- "Credentials already configured (but the connection test failed -- may be a transient outage)" -- connection test failed
- "Credentials not configured" -- no `.env` file found

## Destructive operation confirmation

### Implementation (`core/guards.py`)

The `gate_destructive_action()` function provides two-tier confirmation:

1. **Check**: Is the subaction in the domain's `_*_DESTRUCTIVE` set?
   - No: proceed immediately (non-destructive)
   - Yes: continue to confirmation

2. **Bypass check**: Is `confirm=True`?
   - Yes: proceed (logged as "bypassed via confirm=True")
   - No: continue to elicitation

3. **Elicitation**: Send `_ConfirmAction` form to client:
   ```
   Fields:
     confirmed: bool (default: False)  -- "Check the box to confirm and proceed"
   ```

4. **User response**:
   - Accepted + confirmed: proceed with operation
   - Accepted but not confirmed: `ToolError("Action was not confirmed")`
   - Cancelled/declined: `ToolError("Action was not confirmed")`

### Per-domain descriptions

Each domain provides human-readable descriptions for its destructive actions:

```python
# Example from _array.py
_ARRAY_DESTRUCTIVE = {"stop_array", "remove_disk", "clear_disk_stats"}
# Each has a description dict explaining the impact
```

## Client support

| Client | Elicitation support | Behavior |
|--------|-------------------|----------|
| Claude Code | Full | Interactive form rendering with checkboxes |
| Codex CLI | Partial | Text-based prompts |
| Gemini CLI | Partial | Text-based prompts |
| MCP Inspector | Full | Form rendering in web UI |
| Non-interactive | None | Falls back to `ToolError` with instructions |

## Fallback for unsupported clients

When the client does not support elicitation (`NotImplementedError`):

**Credential setup**: Returns a `ToolError` with manual instructions:
```
Missing required configuration. Create ~/.unraid-mcp/.env with:
  UNRAID_API_URL=https://your-unraid-server:port
  UNRAID_API_KEY=your-api-key
```

**Destructive actions**: Returns a `ToolError` instructing:
```
Action 'stop_array' was not confirmed. Re-run with confirm=True to bypass elicitation.
```

**Reset confirmation**: Silently declines the reset (returns False). Overwriting working credentials on a non-interactive client could be destructive.

## See Also

- [AUTH.md](AUTH.md) -- How credentials are used after setup
- [ENV.md](ENV.md) -- Environment variables set by elicitation
- [TOOLS.md](TOOLS.md) -- Destructive action list
- [../GUARDRAILS.md](../GUARDRAILS.md) -- Security patterns
