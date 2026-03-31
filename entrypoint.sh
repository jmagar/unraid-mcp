#!/usr/bin/env bash
set -euo pipefail

# Validate required environment variables before starting the server
required_vars=(
  UNRAID_API_URL
  UNRAID_API_KEY
  UNRAID_MCP_BEARER_TOKEN
)

missing=()
for var in "${required_vars[@]}"; do
  if [ -z "${!var:-}" ]; then
    missing+=("$var")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  echo "entrypoint: ERROR — required environment variables not set:" >&2
  for v in "${missing[@]}"; do
    echo "  $v" >&2
  done
  exit 1
fi

# Hand off to server — exec replaces this process so signals are forwarded correctly
exec unraid-mcp-server "$@"
