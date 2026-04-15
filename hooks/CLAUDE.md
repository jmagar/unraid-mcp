# `hooks/`

Use this subtree only for hook entrypoints that are called from `hooks/hooks.json`.

- Put hook-specific wrappers here when Claude Code needs to run them automatically
- Use `bin/` for reusable executables and helpers you may run manually or from hooks
- If logic is useful outside the hook lifecycle, keep the implementation in `bin/` and make the hook call it
