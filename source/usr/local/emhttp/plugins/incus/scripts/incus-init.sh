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
STORAGE_DRIVER="${STORAGE_DRIVER:-dir}"
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

# ---------- 0. subordinate uid/gid range for root (unprivileged containers) ----------
# Real Debian/Ubuntu Incus packages populate /etc/subuid and /etc/subgid for
# root via a postinst hook; since we install by unpacking a repackaged
# binary rather than through apt, that never runs, so unprivileged (non-
# security.privileged) containers fail with "System doesn't have a
# functional idmap setup". These files are shared, system-wide, and may
# already have entries from other tools (Docker rootless, Podman, etc.) —
# only add a root: line if none exists at all; never touch existing entries.
for f in /etc/subuid /etc/subgid; do
  [ -f "$f" ] || : > "$f"
  grep -q '^root:' "$f" || echo "root:1000000:1000000000" >> "$f"
done

# liblxc hardcodes this exact path as a private mount-namespace target for
# pivoting a container's rootfs — it must exist (can be empty) or every
# container start fails with "Failed to prepare rootfs storage". Real
# Debian/Ubuntu lxc packages ship it via liblxc-common; we don't package
# liblxc through apt, so it never gets created otherwise.
mkdir -p /usr/lib/x86_64-linux-gnu/lxc/rootfs

# ---------- 1. daemon first-run init (storage pool + core), guarded ----------
# Gate on the storage pool actually existing, not on database/global/db.bin —
# incusd creates db.bin during its own normal startup bootstrap regardless of
# whether admin init ever runs or succeeds, so db.bin's presence says nothing
# about whether our storage pool was actually created. If a prior admin init
# attempt failed partway (e.g. source dir missing), db.bin would already
# exist and this gate must still retry, or the pool never gets created.
if ! "$INCUS" storage show "$STORAGE_POOL_NAME" </dev/null >/dev/null 2>&1; then
  log "first-run: incus admin init (storage=${STORAGE_DRIVER})"
  if [ "$STORAGE_DRIVER" = "zfs" ]; then
    POOL_NAME="${STORAGE_SOURCE%%/*}"
    if ! command -v zfs >/dev/null; then
      log "FATAL: STORAGE_DRIVER=zfs but no zfs command found on this host"; exit 1
    fi
    if ! zpool list "$POOL_NAME" >/dev/null 2>&1; then
      log "FATAL: zfs pool '${POOL_NAME}' (from STORAGE_SOURCE=${STORAGE_SOURCE}) does not exist."
      AVAILABLE="$(zpool list -H -o name 2>/dev/null | tr '\n' ' ')"
      log "Available zfs pools on this host: ${AVAILABLE:-none}"
      log "Set STORAGE_SOURCE to an existing pool/dataset, or switch STORAGE_DRIVER=dir."
      exit 1
    fi
    # Create the dataset if the pool exists but dataset doesn't. Won't touch existing data.
    if ! zfs list "$STORAGE_SOURCE" >/dev/null 2>&1; then
      log "creating zfs dataset ${STORAGE_SOURCE}"
      zfs create -p "$STORAGE_SOURCE" || { log "FATAL: could not create ${STORAGE_SOURCE}"; exit 1; }
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
    # Incus refuses a dir-driver source nested inside INCUS_DIR itself, so
    # this lives in a sibling directory, not underneath it.
    DIR_STORAGE_SOURCE="$(dirname "$INCUS_DIR")/incus-storage-${STORAGE_POOL_NAME}"
    mkdir -p "$DIR_STORAGE_SOURCE"
    cat <<EOF | "$INCUS" admin init --preseed
config: {}
storage_pools:
  - name: ${STORAGE_POOL_NAME}
    driver: dir
    config:
      source: ${DIR_STORAGE_SOURCE}
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

# NOTE: every un-piped `$INCUS` call below is explicitly given `</dev/null`.
# Some subcommands (confirmed: `profile create`) block waiting for stdin
# input whenever stdin isn't a closed/empty fd, instead of assuming an empty
# body — that includes a plain terminal session as well as a script invoked
# with an inherited, never-EOF'd pipe (e.g. from a process manager). Without
# this, `incus-init.sh` can hang indefinitely with zero error output.

# ---------- 2. LAN-ban ACL (deny-list egress; Internet allowed) ----------
if [ -z "${ACL_BLOCK// /}" ]; then
  log "FATAL: ACL_BLOCK is empty — refusing to start with the LAN-ban egress filter disabled"
  exit 1
fi

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
if ! "$INCUS" network acl show "$ACL_NAME" </dev/null >/dev/null 2>&1; then
  log "creating ACL ${ACL_NAME}"
  "$INCUS" network acl create "$ACL_NAME" </dev/null
fi
# Always re-apply the rule body so config edits take effect on restart.
acl_yaml | "$INCUS" network acl edit "$ACL_NAME"

# ---------- 3. jail bridge ----------
# `network show` succeeds even for a host interface Incus doesn't manage
# (e.g. a same-named bridge left over from a prior daemon incarnation
# pointed at a different INCUS_DIR) — only "managed: true" means it's
# actually ours. An unmanaged same-named interface can't be reconfigured
# (network set fails with "Only managed networks can be modified"), so
# tear it down at the OS level and recreate it properly managed.
if "$INCUS" network show "$JAIL_BRIDGE" </dev/null 2>/dev/null | grep -q '^managed: true'; then
  : # already a properly managed bridge
else
  if ip link show "$JAIL_BRIDGE" >/dev/null 2>&1; then
    log "removing stale unmanaged interface ${JAIL_BRIDGE} before recreating it as managed"
    ip link delete "$JAIL_BRIDGE" 2>/dev/null || true
  fi
  log "creating bridge ${JAIL_BRIDGE} (${JAIL_SUBNET})"
  "$INCUS" network create "$JAIL_BRIDGE" --type=bridge \
    ipv4.address="$JAIL_SUBNET" ipv4.nat="$JAIL_NAT" \
    ipv6.address="$JAIL_IPV6" ipv6.nat=false </dev/null
fi
"$INCUS" network set "$JAIL_BRIDGE" security.acls="$ACL_NAME" </dev/null
"$INCUS" network set "$JAIL_BRIDGE" security.acls.default.egress.action="$ACL_DEFAULT_EGRESS" </dev/null
"$INCUS" network set "$JAIL_BRIDGE" security.acls.default.ingress.action="$ACL_DEFAULT_INGRESS" </dev/null

# ---------- 4. agent-jail profile (from template) ----------
mkdir -p "${JAIL_WORKSPACE_ROOT}/default-workspace"
# JAIL_WORKSPACE_ROOT gets bind-mounted with idmap shifting (shift: "true")
# into every jail — it MUST be real persistent storage. tmpfs (Unraid's
# RAM-based root fs) would silently discard all workspace data on every
# reboot, which is a much worse failure mode than refusing to start.
WS_FSTYPE="$(stat -f -c '%T' "${JAIL_WORKSPACE_ROOT}" 2>/dev/null || echo unknown)"
if [ "$WS_FSTYPE" = "tmpfs" ] || [ "$WS_FSTYPE" = "ramfs" ]; then
  log "FATAL: JAIL_WORKSPACE_ROOT (${JAIL_WORKSPACE_ROOT}) is on ${WS_FSTYPE} — not persistent."
  log "Point it at a real array/cache path, e.g. /mnt/cache/appdata/agent-jails."
  exit 1
fi
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
if ! "$INCUS" profile show "$JAIL_PROFILE" </dev/null >/dev/null 2>&1; then
  log "creating profile ${JAIL_PROFILE}"
  "$INCUS" profile create "$JAIL_PROFILE" </dev/null
fi
render | "$INCUS" profile edit "$JAIL_PROFILE"

log "environment ready (bridge=${JAIL_BRIDGE} acl=${ACL_NAME} pool=${STORAGE_POOL_NAME})"
