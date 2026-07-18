#!/bin/bash
set -euo pipefail

[ "${INCUS_LIVE_TEST:-0}" = "1" ] || { echo "set INCUS_LIVE_TEST=1 on a disposable host" >&2; exit 2; }
INCUS="${INCUS_BIN:-/usr/local/incus/bin/incus}"
name="incus-isolation-test-$$"
listener_pid=""
cleanup() {
  [ -z "$listener_pid" ] || kill "$listener_pid" 2>/dev/null || true
  "$INCUS" delete "$name" --force </dev/null >/dev/null 2>&1 || true
}
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

# Prove the bridge gateway itself is filtered by opening a known host listener;
# testing an arbitrary closed port would produce the same result without ACLs.
bridge="${INCUS_TEST_BRIDGE:-agentbr0}"
gateway_cidr="$($INCUS network get "$bridge" ipv4.address </dev/null)"
gateway="${gateway_cidr%/*}"
host_port="${INCUS_HOST_TEST_PORT:-45678}"
busybox nc -l -p "$host_port" -s "$gateway" >/dev/null 2>&1 &
listener_pid=$!
sleep 1
kill -0 "$listener_pid" 2>/dev/null || { echo "failed to start host bridge test listener" >&2; exit 1; }
if "$INCUS" exec "$name" -- nc -z -w3 "$gateway" "$host_port"; then
  echo "containment failure: reached host bridge gateway $gateway:$host_port" >&2
  exit 1
fi
if "$INCUS" exec "$name" -- ip -6 route | grep -q '^default'; then
  echo "containment failure: container has an IPv6 default route" >&2
  exit 1
fi
echo "live isolation checks passed"
