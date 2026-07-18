#!/bin/bash
# Atomically install the API half when a release payload is bundled alongside
# the classic plugin. Keeps one known-good copy and rolls back a failed reload.
set -euo pipefail

PAYLOAD="/usr/local/emhttp/plugins/incus/api-plugin"
TARGET="/usr/local/unraid-api/node_modules/unraid-api-plugin-incus"
BACKUP="${TARGET}.rollback"

if [ ! -d "$PAYLOAD/dist" ] || [ ! -d "$PAYLOAD/node_modules" ] || [ ! -f "$PAYLOAD/package.json" ]; then
  logger -t incus "API payload absent; classic runtime installed in classic-only mode"
  exit 0
fi
if ! command -v unraid-api >/dev/null; then
  logger -t incus "unraid-api unavailable; leaving API payload staged but inactive"
  exit 0
fi

stage="${TARGET}.new.$$"
rm -rf "$stage"
mkdir -p "$stage"
cp -a "$PAYLOAD/." "$stage/"

rm -rf "$BACKUP"
[ ! -e "$TARGET" ] || mv "$TARGET" "$BACKUP"
mv "$stage" "$TARGET"
api_log="/var/log/graphql-api.log"
before_inode="$(stat -c %i "$api_log" 2>/dev/null || echo missing)"
before_size="$(stat -c %s "$api_log" 2>/dev/null || echo 0)"
verified=0
if unraid-api restart; then
  for _ in $(seq 1 30); do
    current_inode="$(stat -c %i "$api_log" 2>/dev/null || echo missing)"
    current_size="$(stat -c %s "$api_log" 2>/dev/null || echo 0)"
    offset=1
    if [ "$current_inode" = "$before_inode" ] && [ "$current_size" -ge "$before_size" ]; then
      offset=$((before_size + 1))
    fi
    if tail -c "+${offset}" "$api_log" 2>/dev/null | grep -q 'IncusPluginModule'; then
      verified=1
      break
    fi
    sleep 1
  done
fi
if [ "$verified" -eq 1 ]; then
  logger -t incus "API plugin installed and verified"
  exit 0
fi

logger -t incus "API plugin reload failed; restoring previous backend"
rm -rf "$TARGET"
[ ! -e "$BACKUP" ] || mv "$BACKUP" "$TARGET"
unraid-api restart || true
exit 1
