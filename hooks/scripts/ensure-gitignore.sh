#!/usr/bin/env bash
set -euo pipefail

GITIGNORE="${CLAUDE_PLUGIN_ROOT}/.gitignore"

REQUIRED=(
  ".env"
  ".env.*"
  "!.env.example"
  "backups/*"
  "!backups/.gitkeep"
  "logs/*"
  "!logs/.gitkeep"
  "__pycache__/"
)

touch "$GITIGNORE"

for pattern in "${REQUIRED[@]}"; do
  if ! grep -qxF "$pattern" "$GITIGNORE" 2>/dev/null; then
    echo "$pattern" >> "$GITIGNORE"
  fi
done
