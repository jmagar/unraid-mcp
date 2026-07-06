#!/bin/bash
# incus-init.sh — idempotently apply the jail environment from incus.cfg.
# Runs on every array start (after incusd is up). Safe to re-run: every step is
# check-then-create. Nothing here is destructive.
set -euo pipefail

CFG="/boot/config/plugins/incus/incus.cfg"
PREFIX="/usr/local/incus"
EMHTTP="/usr/local/emhttp/plugins/incus"
if [ ! -f "${EMHTTP}/scripts/incus-env.sh" ]; then
  echo "incus-init: FATAL — ${EMHTTP}/scripts/incus-env.sh not found" >&2; exit 1
fi
. "${EMHTTP}/scripts/incus-env.sh"   # exports PATH/LD_LIBRARY_PATH/INCUS_DIR
if [ ! -f "$CFG" ]; then
  echo "incus-init: FATAL — $CFG not found" >&2; exit 1
fi
. "$CFG"
INCUS="${PREFIX}/bin/incus"
log() { logger -t incus-init "$*"; echo "incus-init: $*"; }

# ---------- L6: Prevent concurrent execution ----------
LOCKFILE="/var/run/incus-init.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { log "Another instance is already running. Exiting."; exit 0; }

# ---------- H1: Ensure default values for all config variables ----------
STORAGE_DRIVER="${STORAGE_DRIVER:-zfs}"
STORAGE_SOURCE="${STORAGE_SOURCE:-nvme/incus}"
STORAGE_POOL_NAME="${STORAGE_POOL_NAME:-default}"
JAIL_BRIDGE="${JAIL_BRIDGE:-agentbr0}"
JAIL_SUBNET="${JAIL_SUBNET:-198.18.0.1/24}"
JAIL_NAT="${JAIL_NAT:-true}"
JAIL_IPV6="${JAIL_IPV6:-none}"
ACL_NAME="${ACL_NAME:-agent-block-lan}"
ACL_BLOCK="${ACL_BLOCK:-10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16}"
ACL_ALLOW="${ACL_ALLOW:-}"
ACL_DEFAULT_EGRESS="${ACL_DEFAULT_EGRESS:-allow}"
ACL_DEFAULT_INGRESS="${ACL_DEFAULT_INGRESS:-drop}"
JAIL_PROFILE="${JAIL_PROFILE:-agent-jail}"
JAIL_IMAGE="${JAIL_IMAGE:-images:debian/trixie/cloud}"
JAIL_NESTING="${JAIL_NESTING:-false}"
JAIL_CPU="${JAIL_CPU:-2}"
JAIL_MEMORY="${JAIL_MEMORY:-4GiB}"
JAIL_WORKSPACE_ROOT="${JAIL_WORKSPACE_ROOT:-/srv/agent-jails}"
JAIL_AGENT_UID="${JAIL_AGENT_UID:-1000}"
JAIL_AGENT_GID="${JAIL_AGENT_GID:-1000}"

# ---------- 1. daemon first-run init (storage pool + core), guarded ----------
if [ ! -e "${INCUS_DIR}/database/global/db.bin" ]; then
  log "first-run: incus admin init (storage=${STORAGE_DRIVER})"
  if [ "$STORAGE_DRIVER" = "zfs" ]; then
    # Create the dataset if the pool exists but dataset doesn't. Won't touch existing data.
    if command -v zfs >/dev/null && ! zfs list "$STORAGE_SOURCE" >/dev/null 2>&1; then
      log "creating zfs dataset ${STORAGE_SOURCE}"
      zfs create -p "$STORAGE_SOURCE" || log "WARN: could not create ${STORAGE_SOURCE}"
    fi
    cat <<EOF | "$INCUS" admin init --preseed
config: {}
storage_pools:
  - name: ${STORAGE_POOL_NAME}
    driver: zfs
    config:
      source: ${STORAGE_SOURCE}
networks: []
profiles:
  - name: default
    devices:
      root:
        type: disk
        path: /
        pool: ${STORAGE_POOL_NAME}
EOF
  else
    mkdir -p "${INCUS_DIR}/storage-${STORAGE_POOL_NAME}"
    cat <<EOF | "$INCUS" admin init --preseed
config: {}
storage_pools:
  - name: ${STORAGE_POOL_NAME}
    driver: dir
    config:
      source: ${INCUS_DIR}/storage-${STORAGE_POOL_NAME}
networks: []
profiles:
  - name: default
    devices:
      root:
        type: disk
        path: /
        pool: ${STORAGE_POOL_NAME}
EOF
  fi
fi

# ---------- 2. LAN-ban ACL (deny-list egress; Internet allowed) ----------
# Build egress rules: optional allow-holes FIRST, then the block list.
acl_yaml() {
  echo "name: ${ACL_NAME}"
  echo "description: \"Deny agent egress to LAN ranges; allow Internet.\""
  echo "egress:"
  if [ -n "${ACL_ALLOW:-}" ]; then
    echo "  - action: allow"
    echo "    state: enabled"
    echo "    description: \"Allowlisted destinations\""
    echo "    destination: ${ACL_ALLOW}"
  fi
  echo "  - action: reject"
  echo "    state: enabled"
  echo "    description: \"Blocked LAN ranges\""
  echo "    destination: ${ACL_BLOCK}"
  echo "ingress: []"
  echo "config: {}"
}
if ! "$INCUS" network acl show "$ACL_NAME" >/dev/null 2>&1; then
  log "creating ACL ${ACL_NAME}"
  "$INCUS" network acl create "$ACL_NAME"
fi
# Always re-apply the rule body so config edits take effect on restart.
acl_yaml | "$INCUS" network acl edit "$ACL_NAME"

# ---------- 3. jail bridge ----------
if ! "$INCUS" network show "$JAIL_BRIDGE" >/dev/null 2>&1; then
  log "creating bridge ${JAIL_BRIDGE} (${JAIL_SUBNET})"
  "$INCUS" network create "$JAIL_BRIDGE" --type=bridge \
    ipv4.address="$JAIL_SUBNET" ipv4.nat="$JAIL_NAT" \
    ipv6.address="$JAIL_IPV6" ipv6.nat=false
fi
"$INCUS" network set "$JAIL_BRIDGE" security.acls="$ACL_NAME"
"$INCUS" network set "$JAIL_BRIDGE" security.acls.default.egress.action="$ACL_DEFAULT_EGRESS"
"$INCUS" network set "$JAIL_BRIDGE" security.acls.default.ingress.action="$ACL_DEFAULT_INGRESS"

# ---------- 4. agent-jail profile (from template) ----------
mkdir -p "${JAIL_WORKSPACE_ROOT}/default-workspace"
TMPL="/usr/local/emhttp/plugins/incus/templates/agent-jail-profile.yaml.tmpl"
if [ ! -f "$TMPL" ]; then
  log "ERROR: profile template not found at ${TMPL}"
  exit 1
fi
render() {
  local out
  out=$(sed -e "s|@PROFILE@|${JAIL_PROFILE}|g" \
            -e "s|@BRIDGE@|${JAIL_BRIDGE}|g" \
            -e "s|@NESTING@|${JAIL_NESTING}|g" \
            -e "s|@UID@|${JAIL_AGENT_UID}|g" \
            -e "s|@GID@|${JAIL_AGENT_GID}|g" \
            -e "s|@WSROOT@|${JAIL_WORKSPACE_ROOT}|g" "$TMPL")
  # Handle empty CPU/MEMORY (= no cap): remove the limits line entirely
  if [ -n "${JAIL_CPU}" ]; then
    out=$(echo "$out" | sed "s|@CPU@|${JAIL_CPU}|g")
  else
    out=$(echo "$out" | grep -v '@CPU@')
  fi
  if [ -n "${JAIL_MEMORY}" ]; then
    out=$(echo "$out" | sed "s|@MEMORY@|${JAIL_MEMORY}|g")
  else
    out=$(echo "$out" | grep -v '@MEMORY@')
  fi
  echo "$out"
}
if ! "$INCUS" profile show "$JAIL_PROFILE" >/dev/null 2>&1; then
  log "creating profile ${JAIL_PROFILE}"
  "$INCUS" profile create "$JAIL_PROFILE"
fi
render | "$INCUS" profile edit "$JAIL_PROFILE"

log "environment ready (bridge=${JAIL_BRIDGE} acl=${ACL_NAME} pool=${STORAGE_POOL_NAME})"
