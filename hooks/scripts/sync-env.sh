#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"
BACKUP_DIR="${CLAUDE_PLUGIN_ROOT}/backups"
mkdir -p "$BACKUP_DIR"

declare -A MANAGED=(
  [UNRAID_API_URL]="${CLAUDE_PLUGIN_OPTION_UNRAID_API_URL:-}"
  [UNRAID_API_KEY]="${CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY:-}"
  [UNRAID_MCP_URL]="${CLAUDE_PLUGIN_OPTION_UNRAID_MCP_URL:-}"
  [UNRAID_MCP_BEARER_TOKEN]="${CLAUDE_PLUGIN_OPTION_UNRAID_MCP_TOKEN:-}"
)

touch "$ENV_FILE"

if [ -s "$ENV_FILE" ]; then
  cp "$ENV_FILE" "${BACKUP_DIR}/.env.bak.$(date +%s)"
fi

for key in "${!MANAGED[@]}"; do
  value="${MANAGED[$key]}"
  [ -z "$value" ] && continue
  escaped_value=$(printf '%s\n' "$value" | sed 's/[&/\|]/\\&/g')
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=${escaped_value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
done

# Auto-generate UNRAID_MCP_BEARER_TOKEN if not yet set
if ! grep -q "^UNRAID_MCP_BEARER_TOKEN=" "$ENV_FILE" 2>/dev/null; then
  generated=$(openssl rand -hex 32)
  echo "UNRAID_MCP_BEARER_TOKEN=${generated}" >> "$ENV_FILE"
  echo "sync-env: generated UNRAID_MCP_BEARER_TOKEN (update plugin userConfig to match)" >&2
fi

chmod 600 "$ENV_FILE"

mapfile -t baks < <(ls -t "${BACKUP_DIR}"/.env.bak.* 2>/dev/null)
for bak in "${baks[@]}"; do chmod 600 "$bak"; done
for bak in "${baks[@]:3}"; do rm -f "$bak"; done
