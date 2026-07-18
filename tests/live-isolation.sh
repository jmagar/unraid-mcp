#!/bin/bash
set -euo pipefail

[ "${INCUS_LIVE_TEST:-0}" = "1" ] || { echo "set INCUS_LIVE_TEST=1 on a disposable host" >&2; exit 2; }
INCUS="${INCUS_BIN:-/usr/local/incus/bin/incus}"
name="incus-isolation-test-$$"
cleanup() { "$INCUS" delete "$name" --force </dev/null >/dev/null 2>&1 || true; }
trap cleanup EXIT

"$INCUS" launch images:debian/trixie/cloud "$name" --profile default --profile agent-jail </dev/null
# Expansion intentionally occurs inside the container.
# shellcheck disable=SC2016
"$INCUS" exec "$name" -- sh -c 'for i in $(seq 1 60); do command -v nc >/dev/null && exit 0; sleep 2; done; exit 1'
"$INCUS" exec "$name" -- nc -z -w5 1.1.1.1 443
for target in 10.0.0.1 172.16.0.1 192.168.1.1 169.254.169.254 100.64.0.1; do
  if "$INCUS" exec "$name" -- nc -z -w2 "$target" 443; then
    echo "containment failure: reached $target" >&2
    exit 1
  fi
done
if "$INCUS" exec "$name" -- ip -6 route | grep -q '^default'; then
  echo "containment failure: container has an IPv6 default route" >&2
  exit 1
fi
echo "live isolation checks passed"
