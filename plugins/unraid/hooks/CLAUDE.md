# `hooks/`

This directory holds the plugin's hook configuration. `hooks.json` is the
**single source of truth** — the Claude plugin manifest
(`../.claude-plugin/plugin.json`) references it via `"hooks": "./hooks/hooks.json"`
rather than inlining hook commands.

Current wiring (both run the same idempotent credential-setup script):

- **SessionStart** → `${CLAUDE_PLUGIN_ROOT}/scripts/plugin-setup.sh`
- **ConfigChange** (`user_settings`) → `${CLAUDE_PLUGIN_ROOT}/scripts/plugin-setup.sh`

`plugin-setup.sh` lives in `../scripts/` and runs `uvx unraid-mcp setup
plugin-hook` to persist the plugin's userConfig credentials to
`~/.unraid-mcp/.env`. Because the server is launched with `uvx unraid-mcp`
(published PyPI package), there is no bundled uv project to sync — the old
`sync-uv.sh` hook was removed.

**Advisory contract — these hooks must never block the session.** Credential
persistence is a convenience; the server also receives credentials directly via the
plugin's `.mcp.json` env. So `plugin-setup.sh` is idempotent (rewriting identical
creds is a no-op) and **always exits 0** — a missing `uvx`, no network, or a setup
error warns to stderr (greppable `plugin-setup.sh:` prefix) and continues.

`ConfigChange` uses a `user_settings` matcher so it re-runs only when plugin settings
change, propagating updated credentials without a restart.

When changing hook wiring, edit `hooks.json` only; the manifest picks it up.
