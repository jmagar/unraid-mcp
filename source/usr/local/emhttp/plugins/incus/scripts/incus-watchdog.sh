#!/bin/bash
# Lightweight Unraid-compatible supervision. It avoids systemd assumptions,
# retries boundedly, and records health beside persistent Incus state.
set -uo pipefail

PREFIX="/usr/local/incus"
EMHTTP="/usr/local/emhttp/plugins/incus"
CFG="/boot/config/plugins/incus/incus.cfg"
export INCUS_WATCHDOG=1

failures=0
while [ -f "$CFG" ]; do
  . "$CFG"
  [ "${SERVICE:-disabled}" = "enabled" ] || exit 0
  if "${PREFIX}/bin/incus" info </dev/null >/dev/null 2>&1; then
    failures=0
  else
    failures=$((failures + 1))
    logger -t incus-watchdog "incusd unhealthy; restart attempt ${failures}/3"
    if [ "$failures" -le 3 ]; then
      /etc/rc.d/rc.incus start && "${EMHTTP}/scripts/incus-init.sh" || true
    else
      printf 'status=failed\ntime=%s\nbuild=2026.07.18\nmessage=watchdog restart limit reached\n' "$(date -Is)" >"${INCUS_DIR}/plugin-health.tmp" 2>/dev/null &&
        mv -f "${INCUS_DIR}/plugin-health.tmp" "${INCUS_DIR}/plugin-health" 2>/dev/null || true
      logger -t incus-watchdog "restart limit reached; manual intervention required"
      exit 1
    fi
  fi
  sleep 30
done
