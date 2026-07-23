#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/source/usr/local/emhttp/plugins/incus/incus.cfg"
INIT="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/incus-init.sh"
MIGRATE="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/migrate-config.sh"
VALIDATE="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/config-validation.sh"
APPLY="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/apply-settings.sh"
API_REGISTRATION="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/api-plugin-registration.sh"
INSTALL_API="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/install-api-plugin.sh"
UNINSTALL_API="$ROOT/source/usr/local/emhttp/plugins/incus/scripts/uninstall-api-plugin.sh"
PLG="$ROOT/incus.plg"

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
grep -Fq 'validate_containment_config' "$APPLY"
# Fresh installs must create the persistent config before API activation. The
# backend chooses its config path once in its constructor during that restart.
config_bootstrap_line="$(grep -n 'cp "&emhttp;/incus.cfg" "&plugin;/incus.cfg" || exit 1' "$PLG" | cut -d: -f1)"
api_activation_line="$(grep -n 'if ! &emhttp;/scripts/install-api-plugin.sh' "$PLG" | cut -d: -f1)"
[ -n "$config_bootstrap_line" ]
[ -n "$api_activation_line" ]
[ "$config_bootstrap_line" -lt "$api_activation_line" ]
grep -Fq '"$REGISTRATION" register' "$INSTALL_API"
grep -Fq '"$REGISTRATION" unregister' "$UNINSTALL_API"
grep -Fq 'removepkg &txz;' "$PLG"
# Literal workflow contract, not a shell expression in this test.
# shellcheck disable=SC2016
grep -Fq 'diff -qr dist "$payload/dist"' "$ROOT/.github/workflows/api-plugin-ci.yml"
[ "$(grep -Fc '      - "packages/**"' "$ROOT/.github/workflows/api-plugin-ci.yml")" -eq 2 ]
[ "$(grep -Fc '      - "incus.plg"' "$ROOT/.github/workflows/api-plugin-ci.yml")" -eq 2 ]
grep -Fq 'archive entry count differs from release manifest' "$ROOT/scripts/verify-classic-package.sh"
for script in "$ROOT"/source/usr/local/emhttp/plugins/incus/scripts/*.sh "$ROOT"/source/usr/local/emhttp/plugins/incus/event/*; do
  bash -n "$script"
done

# Disabled candidates are validated before apply-settings can promote them to
# known-good. Exercise the shared side-effect-free validator directly so this
# safety boundary remains testable without an Incus daemon.
validate_config() (
  export JAIL_WORKSPACE_ROOT="$1"
  export JAIL_BIND_MOUNTS="$2"
  # shellcheck source=/dev/null
  . "$VALIDATE"
  validate_containment_config
)
validate_config "/srv/agent-jails" ""
if validate_config "/etc" ""; then
  echo "unsafe workspace root unexpectedly passed validation" >&2
  exit 1
fi
if validate_config "/srv/agent-jails" "/etc:/host:rw"; then
  echo "unsafe bind source unexpectedly passed validation" >&2
  exit 1
fi

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

# Current unraid-api releases discover third-party modules only when the
# package is present in node_modules, named in api.json, and declared in the
# API root package.json. Registration must be idempotent and preserve other
# plugins and package metadata.
cat >"$tmp/package.json" <<'EOF'
{"name":"@unraid/api","dependencies":{"unraid-api-plugin-connect":"file:connect.tgz"},"private":true}
EOF
cat >"$tmp/api.json" <<'EOF'
{"version":"test","sandbox":true,"plugins":["unraid-api-plugin-connect"]}
EOF
API_PACKAGE_JSON="$tmp/package.json" API_CONFIG_JSON="$tmp/api.json" "$API_REGISTRATION" register
API_PACKAGE_JSON="$tmp/package.json" API_CONFIG_JSON="$tmp/api.json" "$API_REGISTRATION" register
[ "$(jq -r '.peerDependencies["unraid-api-plugin-incus"]' "$tmp/package.json")" = "*" ]
[ "$(jq '[.plugins[] | select(. == "unraid-api-plugin-incus")] | length' "$tmp/api.json")" -eq 1 ]
[ "$(jq -r '.dependencies["unraid-api-plugin-connect"]' "$tmp/package.json")" = "file:connect.tgz" ]
[ "$(jq -r '.sandbox' "$tmp/api.json")" = "true" ]
API_PACKAGE_JSON="$tmp/package.json" API_CONFIG_JSON="$tmp/api.json" "$API_REGISTRATION" unregister
[ "$(jq -r '.peerDependencies["unraid-api-plugin-incus"] // "missing"' "$tmp/package.json")" = "missing" ]
[ "$(jq '[.plugins[] | select(. == "unraid-api-plugin-incus")] | length' "$tmp/api.json")" -eq 0 ]
[ "$(jq -r '.dependencies["unraid-api-plugin-connect"]' "$tmp/package.json")" = "file:connect.tgz" ]

# The live boundary suite is deliberately opt-in because it needs Incus and
# network privileges on a disposable Unraid host.
if [ "${INCUS_LIVE_TEST:-0}" = "1" ]; then
  "$ROOT/tests/live-isolation.sh"
fi

echo "classic contract checks passed"
