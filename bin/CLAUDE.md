# `bin/`

This subtree contains plugin executables that should be added to `PATH` in generated Claude Code plugin repositories.


## Contract

- Put executable entrypoints here, not repo-maintenance scripts
- Keep the files shell-friendly and portable unless a specific runtime is required
- Make names stable and descriptive so they are safe to expose on `PATH`

## Expectations

- Each executable should have a shebang
- Executables should be safe to call without extra wrapper logic
- Commands should prefer deterministic behavior and clear exit codes
- If a script needs inputs, document them near the file that consumes them

## Notes for Claude Code Plugins

This subtree is specifically for plugin surfaces that Claude Code can invoke directly from the shell. Use it for generated plugin utilities such as:

- setup helpers
- validation helpers
- lightweight wrapper commands
- plugin-local tooling that needs to be discoverable on `PATH`
