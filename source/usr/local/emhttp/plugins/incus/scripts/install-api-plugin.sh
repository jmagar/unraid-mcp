#!/bin/bash
# Atomically install the API half when a release payload is bundled alongside
# the classic plugin. Keeps one known-good copy and rolls back a failed reload.
set -euo pipefail

PAYLOAD="/usr/local/emhttp/plugins/incus/api-plugin"
TARGET="/usr/local/unraid-api/node_modules/unraid-api-plugin-incus"
BACKUP="${TARGET}.rollback"

[ -d "$PAYLOAD/dist" ] && [ -d "$PAYLOAD/node_modules" ] && [ -f "$PAYLOAD/package.json" ] || {
  logger -t incus "API payload absent; classic runtime installed in classic-only mode"
  exit 0
}
command -v unraid-api >/dev/null || {
  logger -t incus "unraid-api unavailable; leaving API payload staged but inactive"
  exit 0
}

stage="${TARGET}.new.$$"
rm -rf "$stage"
mkdir -p "$stage"
cp -a "$PAYLOAD/." "$stage/"

rm -rf "$BACKUP"
[ ! -e "$TARGET" ] || mv "$TARGET" "$BACKUP"
mv "$stage" "$TARGET"
if unraid-api restart && grep -q 'IncusPluginModule' /var/log/graphql-api.log 2>/dev/null; then
  logger -t incus "API plugin installed and verified"
  exit 0
fi

logger -t incus "API plugin reload failed; restoring previous backend"
rm -rf "$TARGET"
[ ! -e "$BACKUP" ] || mv "$BACKUP" "$TARGET"
unraid-api restart || true
exit 1
