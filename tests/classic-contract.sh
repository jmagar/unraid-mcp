#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/source/usr/local/emhttp/plugins/incus/incus.cfg"
INIT="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/incus-init.sh"
MIGRATE="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/migrate-config.sh"

grep -Eq 'ACL_BLOCK=.*100\.64\.0\.0/10' "$CFG"
grep -Fq 'Block host bridge and peer containers' "$INIT"
grep -Fq 'destination_port: \"53\"' "$INIT"
grep -Fq 'JAIL_IPV6 must remain' "$INIT"
grep -Fq 'render_bind_mounts' "$INIT"
# Literal implementation contract, not a shell expression in this test.
# shellcheck disable=SC2016
grep -Fq 'mode="${mode:-ro}"' "$INIT"
grep -Fq 'config bind mounts must be read-only' "$INIT"
grep -Fq 'readonly: "true"' "$INIT"
for script in "$ROOT"/source/usr/local/emhttp/plugins/incus/scripts/*.sh "$ROOT"/source/usr/local/emhttp/plugins/incus/event/*; do
  bash -n "$script"
done

# A preserved pre-hardening config and its rollback copy must both gain the
# CGNAT block exactly once; a second run is a no-op via the version marker.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat >"$tmp/incus.cfg" <<'EOF'
SERVICE="disabled"
ACL_BLOCK="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16"
EOF
cp "$tmp/incus.cfg" "$tmp/incus.cfg.known-good"
INCUS_CFG_PATH="$tmp/incus.cfg" "$MIGRATE"
INCUS_CFG_PATH="$tmp/incus.cfg" "$MIGRATE"
for migrated in "$tmp/incus.cfg" "$tmp/incus.cfg.known-good"; do
  [ "$(grep -o '100\.64\.0\.0/10' "$migrated" | wc -l)" -eq 1 ]
done

# The live boundary suite is deliberately opt-in because it needs Incus and
# network privileges on a disposable Unraid host.
if [ "${INCUS_LIVE_TEST:-0}" = "1" ]; then
  "$ROOT/tests/live-isolation.sh"
fi

echo "classic contract checks passed"
