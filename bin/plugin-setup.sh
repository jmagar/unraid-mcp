#!/usr/bin/env bash
# Persist the plugin's userConfig credentials to ~/.unraid-mcp/.env.
# Runs `unraid-mcp setup plugin-hook` inside the plugin's uv-managed venv.
# Idempotent: writing identical credentials is a no-op-equivalent rewrite.
set -euo pipefail

# Make a hook failure greppable: under `set -euo pipefail` any errexit failure
# (a failed `uv run` from missing uv / broken venv, or an unexpected setup error)
# prints this marker. Note: run_plugin_hook itself exits 0 even when the .env
# write fails (advisory, by design), so this trap is mainly the uv/env safety net.
trap 'echo "plugin-setup.sh: credential setup hook failed (exit $?)" >&2' ERR

REPO_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DATA_ROOT="${CLAUDE_PLUGIN_DATA:-${REPO_ROOT}}"
VENV_DIR="${DATA_ROOT}/.venv"

UV_PROJECT_ENVIRONMENT="${VENV_DIR}" uv run --project "${REPO_ROOT}" \
  unraid-mcp setup plugin-hook
