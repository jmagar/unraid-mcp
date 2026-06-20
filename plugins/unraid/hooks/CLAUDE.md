# `hooks/`

> **Authoritative hooks live in `.claude-plugin/plugin.json`** (declared inline). This
> `hooks/hooks.json` is kept as a mirror for environments/tooling that read the default
> `hooks/` location. The two are not byte-identical — `plugin.json` inlines the uv-sync
> command while this file calls `bin/sync-uv.sh` — but both end SessionStart by running
> `bin/plugin-setup.sh` and define the same `ConfigChange` hook. Every wrapper is
> idempotent, so if both sources are loaded a double-run is harmless. When changing the
> setup/ConfigChange wiring, update both files.

Use this subtree only for hook entrypoints that are called from `hooks/hooks.json`.

- Put hook-specific wrappers here when Claude Code needs to run them automatically
- Use `bin/` for reusable executables and helpers you may run manually or from hooks
- If logic is useful outside the hook lifecycle, keep the implementation in `bin/` and make the hook call it
