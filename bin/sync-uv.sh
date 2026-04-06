#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DATA_ROOT="${CLAUDE_PLUGIN_DATA:-${REPO_ROOT}}"
VENV_DIR="${DATA_ROOT}/.venv"

if [[ ! -f "${REPO_ROOT}/uv.lock" ]]; then
  echo "sync-uv.sh: missing lockfile at ${REPO_ROOT}/uv.lock" >&2
  exit 1
fi

mkdir -p "${DATA_ROOT}"
UV_PROJECT_ENVIRONMENT="${VENV_DIR}" uv sync --project "${REPO_ROOT}"
