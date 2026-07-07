#!/bin/bash
# apply-settings.sh — invoked by the Settings page's Apply button after
# incus.cfg has been rewritten. A plain `rc.incus restart` alone is not
# enough: it only brings the raw daemon up, it does not re-apply the
# storage pool/ACL/bridge/profile environment for the (possibly new)
# INCUS_DIR/config — that's incus-init.sh's job. Mirrors the same
# start-then-init sequence the array-start event script uses.
set -uo pipefail

CFG="/boot/config/plugins/incus/incus.cfg"
[ -f "$CFG" ] || exit 0
. "$CFG"

if [ "${SERVICE:-disabled}" != "enabled" ]; then
  /etc/rc.d/rc.incus stop
  exit 0
fi

/etc/rc.d/rc.incus restart || { logger -t incus "incusd failed to start"; exit 1; }
/usr/local/emhttp/plugins/incus/scripts/incus-init.sh
