#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/source/usr/local/emhttp/plugins/incus/incus.cfg"
INIT="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/incus-init.sh"

grep -Eq 'ACL_BLOCK=.*100\.64\.0\.0/10' "$CFG"
grep -Fq 'JAIL_IPV6 must remain' "$INIT"
grep -Fq 'render_bind_mounts' "$INIT"
grep -Fq 'readonly: "true"' "$INIT"
for script in "$ROOT"/source/usr/local/emhttp/plugins/incus/scripts/*.sh "$ROOT"/source/usr/local/emhttp/plugins/incus/event/*; do
  bash -n "$script"
done

# The live boundary suite is deliberately opt-in because it needs Incus and
# network privileges on a disposable Unraid host.
if [ "${INCUS_LIVE_TEST:-0}" = "1" ]; then
  "$ROOT/tests/live-isolation.sh"
fi

echo "classic contract checks passed"
