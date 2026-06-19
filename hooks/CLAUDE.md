# `hooks/`

> **Authoritative hooks live in `.claude-plugin/plugin.json`.** Claude Code loads both
> the inline `plugin.json` hooks and `hooks/hooks.json` and merges them, so this file
> mirrors the same wiring. All hook wrappers are idempotent (`bin/sync-uv.sh`,
> `bin/plugin-setup.sh`), so a double-run from both sources is harmless. Keep the two in sync.

Use this subtree only for hook entrypoints that are called from `hooks/hooks.json`.

- Put hook-specific wrappers here when Claude Code needs to run them automatically
- Use `bin/` for reusable executables and helpers you may run manually or from hooks
- If logic is useful outside the hook lifecycle, keep the implementation in `bin/` and make the hook call it
