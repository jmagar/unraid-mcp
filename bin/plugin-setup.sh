#!/usr/bin/env bash
# Persist the plugin's userConfig credentials to ~/.unraid-mcp/.env.
# Runs `unraid-mcp setup plugin-hook` inside the plugin's uv-managed venv.
# Idempotent: writing identical credentials is a no-op-equivalent rewrite.
set -euo pipefail

# Make a hook failure greppable: `set -e` exits non-zero on a failed `uv run`
# (missing uv, broken venv), but the raw error gives no hint that *credential
# setup* is what failed. Note: run_plugin_hook itself exits 0 even when the .env
# write fails (advisory, by design), so this trap only catches uv/env failures.
trap 'echo "plugin-setup.sh: credential setup hook failed (exit $?)" >&2' ERR

REPO_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DATA_ROOT="${CLAUDE_PLUGIN_DATA:-${REPO_ROOT}}"
VENV_DIR="${DATA_ROOT}/.venv"

UV_PROJECT_ENVIRONMENT="${VENV_DIR}" uv run --project "${REPO_ROOT}" \
  unraid-mcp setup plugin-hook
