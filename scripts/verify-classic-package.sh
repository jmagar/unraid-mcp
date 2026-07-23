#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

plugin_name="$(sed -n 's/.*<!ENTITY name[[:space:]]*"\([^"]*\)".*/\1/p' incus.plg)"
txz="$(sed -n 's/.*<!ENTITY txz[[:space:]]*"\([^"]*\)".*/\1/p' incus.plg)"
txz="${txz//&name;/$plugin_name}"
md5="$(sed -n 's/.*<!ENTITY md5[[:space:]]*"\([^"]*\)".*/\1/p' incus.plg)"
sha256="$(sed -n 's/.*<!ENTITY sha256[[:space:]]*"\([^"]*\)".*/\1/p' incus.plg)"
archive="packages/$txz"
[ -f "$archive" ] || { echo "missing $archive" >&2; exit 1; }
archive_list="$(mktemp)"
archive_tree="$(mktemp -d)"
trap 'rm -f "$archive_list"; rm -rf "$archive_tree"' EXIT
tar -tJf "$archive" >"$archive_list"
tar -xJf "$archive" -C "$archive_tree"
echo "$md5  $archive" | md5sum -c -
echo "$sha256  $archive" | sha256sum -c -

if awk '$0 == "./" { found=1 } END { exit !found }' "$archive_list"; then
  echo "archive must not contain a root directory entry" >&2
  exit 1
fi
bad_directory_mode="$(
  find "$archive_tree" -mindepth 1 -type d ! -perm 0755 -print -quit
)"
[ -z "$bad_directory_mode" ] || {
  echo "archive contains non-0755 directory: ${bad_directory_mode#"$archive_tree"/}" >&2
  exit 1
}

xmllint --noout incus.plg
find source/usr/local/emhttp/plugins/incus -type f \( -name '*.sh' -o -path '*/event/*' \) -print0 |
  xargs -0 -r -n1 bash -n
shellcheck -x -e SC1090,SC1091,SC2001 source/usr/local/emhttp/plugins/incus/scripts/*.sh source/usr/local/emhttp/plugins/incus/event/*

entries="$(wc -l <"$archive_list")"
expected_entries="$(sed -n 's/^- Entries: \([0-9][0-9]*\)$/\1/p' MANIFEST.md)"
[ -n "$expected_entries" ] || { echo "MANIFEST.md has no numeric package entry count" >&2; exit 1; }
[ "$entries" -eq "$expected_entries" ] || {
  echo "archive entry count differs from release manifest: $entries != $expected_entries" >&2
  exit 1
}
for path in \
  usr/local/incus/libexec/incus/incusd \
  usr/local/incus/bin/incus \
  usr/local/incus/bin/nft \
  usr/local/incus/bin/unsquashfs \
  usr/local/emhttp/plugins/incus/api-plugin/dist/index.js \
  usr/local/emhttp/plugins/incus/api-plugin/node_modules/ws/package.json \
  usr/local/emhttp/plugins/incus/api-plugin/node_modules/graphql-subscriptions/package.json \
  usr/local/emhttp/plugins/incus/scripts/rc.incus \
  usr/local/emhttp/plugins/incus/build-id \
  usr/local/emhttp/plugins/incus/web/incus-settings.js \
  usr/local/emhttp/plugins/incus/web/incus-dashboard.js; do
  grep -Fxq "$path" "$archive_list" || { echo "archive missing $path" >&2; exit 1; }
done

release="$(jq -er '.release' release-manifest.json)"
package_build="$(sed -n 's/.*<!ENTITY txz[[:space:]]*"&name;-unraid-7\.0\.0-\([0-9][0-9]*\)-x86_64-1\.txz".*/\1/p' incus.plg)"
[ "$(cat "$archive_tree/usr/local/emhttp/plugins/incus/build-id")" = "${release}+${package_build}" ] || {
  echo "embedded build-id differs from coordinated release metadata" >&2
  exit 1
}

if tar -tvJf "$archive" usr/local/emhttp/plugins/incus/api-plugin/dist | grep -q '^l'; then
  echo "API dist must contain files, not symlinks" >&2
  exit 1
fi

# Every tracked classic source must be present in the release payload.
while IFS= read -r path; do
  member="${path#source/}"
  grep -Fxq "$member" "$archive_list" || { echo "archive/source drift: $member missing" >&2; exit 1; }
  cmp -s "$path" "$archive_tree/$member" || { echo "archive/source drift: $member content differs" >&2; exit 1; }
done < <(git ls-files source)

bad_owner="$(tar --numeric-owner -tvJf "$archive" | awk '$2 != "0/0" && bad == "" { bad=$2 } END { print bad }')"
[ -z "$bad_owner" ] || { echo "archive contains non-root ownership: $bad_owner" >&2; exit 1; }

embedded_manifest="$(tar -xOJf "$archive" usr/local/incus/MANIFEST.md)"
grep -Fq "$txz" <<<"$embedded_manifest" || { echo "embedded manifest build drift" >&2; exit 1; }

echo "classic/package verification passed ($entries entries)"
