#!/usr/bin/env bash
# Persist the plugin's userConfig credentials to ~/.unraid-mcp/.env.
# Runs `unraid-mcp setup plugin-hook` via uvx (the published PyPI package).
# Idempotent: writing identical credentials is a no-op-equivalent rewrite.
set -euo pipefail

# Make a hook failure greppable: under `set -euo pipefail` any errexit failure
# (a failed `uvx` from a missing uv binary / no network, or an unexpected setup
# error) prints this marker. Note: run_plugin_hook itself exits 0 even when the
# .env write fails (advisory, by design), so this trap is mainly the uvx safety net.
trap 'echo "plugin-setup.sh: credential setup hook failed (exit $?)" >&2' ERR

uvx unraid-mcp setup plugin-hook
