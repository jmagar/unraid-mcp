#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${CLAUDE_PLUGIN_ROOT}/.env"
BACKUP_DIR="${CLAUDE_PLUGIN_ROOT}/backups"
LOCK_FILE="${CLAUDE_PLUGIN_ROOT}/.sync-env.lock"
mkdir -p "$BACKUP_DIR"

# Serialize concurrent sessions (two tabs starting at the same time)
exec 9>"$LOCK_FILE"
flock -w 10 9 || { echo "sync-env: failed to acquire lock after 10s" >&2; exit 1; }

declare -A MANAGED=(
  [UNRAID_API_URL]="${CLAUDE_PLUGIN_OPTION_UNRAID_API_URL:-}"
  [UNRAID_API_KEY]="${CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY:-}"
  [UNRAID_MCP_URL]="${CLAUDE_PLUGIN_OPTION_UNRAID_MCP_URL:-}"
  [UNRAID_MCP_BEARER_TOKEN]="${CLAUDE_PLUGIN_OPTION_UNRAID_MCP_TOKEN:-}"
)

touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Backup before writing (max 3 retained)
if [ -s "$ENV_FILE" ]; then
  cp "$ENV_FILE" "${BACKUP_DIR}/.env.bak.$(date +%s)"
fi

# Write managed keys — awk handles arbitrary values safely (no delimiter injection)
for key in "${!MANAGED[@]}"; do
  value="${MANAGED[$key]}"
  [ -z "$value" ] && continue
  if [[ "$value" == *$'\n'* || "$value" == *$'\r'* || "$value" == *$'\t'* ]]; then
    echo "sync-env: refusing ${key} with control characters" >&2
    exit 1
  fi
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    awk -v k="$key" -v v="$value" '$0 ~ "^"k"=" { print k"="v; next } { print }' \
      "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
done

# Fail if bearer token is not set — do NOT auto-generate.
# Auto-generated tokens cause a mismatch: the server reads the generated token
# but Claude Code sends the (empty) userConfig value. Every MCP call returns 401.
if ! grep -q "^UNRAID_MCP_BEARER_TOKEN=.\+" "$ENV_FILE" 2>/dev/null; then
  echo "sync-env: ERROR — UNRAID_MCP_BEARER_TOKEN is not set." >&2
  echo "  Generate one:  openssl rand -hex 32" >&2
  echo "  Then paste it into the plugin's userConfig MCP token field." >&2
  exit 1
fi

chmod 600 "$ENV_FILE"

mapfile -t baks < <(ls -t "${BACKUP_DIR}"/.env.bak.* 2>/dev/null)
for bak in "${baks[@]}"; do chmod 600 "$bak"; done
for bak in "${baks[@]:3}"; do rm -f "$bak"; done
