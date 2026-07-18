#!/bin/bash
# Rebuild by carrying forward the complete prior binary payload and overlaying
# tracked source. This prevents the historical destructive source-only rebuild.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
build="${1:?usage: $0 NEW_BUILD_NUMBER [previous.txz]}"
previous="${2:-$(find "$ROOT/packages" -maxdepth 1 -type f -name 'incus-unraid-*.txz' -print | sort -V | tail -1)}"
version="7.0.0-${build}-x86_64-1"
output="$ROOT/packages/incus-unraid-${version}.txz"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

tar -xJf "$previous" -C "$stage"
cp -a "$ROOT/source/." "$stage/"
# Avoid a circular self-hash: the embedded copy names the package but points to
# the external signed/checksummed release metadata for final archive hashes.
sed \
  -e "s|^- File: .*|- File: \`packages/incus-unraid-${version}.txz\`|" \
  -e 's|^- Size: .*|- Size: see external release-manifest.json|' \
  -e 's|^- Entries: .*|- Entries: see external release-manifest.json|' \
  -e 's|^- MD5 .*|- MD5: see external release-manifest.json (legacy only)|' \
  -e 's|^- SHA-256: .*|- SHA-256: see external release-manifest.json|' \
  "$ROOT/MANIFEST.md" >"$stage/usr/local/incus/MANIFEST.md"
chmod 0644 "$stage/usr/local/incus/MANIFEST.md"

# A release can carry the backend in the same versioned payload, eliminating
# frontend/backend skew. CI builds dist first; local classic-only builds omit it.
if [ -d "$ROOT/unraid-api-plugin-incus/dist" ]; then
  api="$stage/usr/local/emhttp/plugins/incus/api-plugin"
  mkdir -p "$api"
  # Worktree setup may provide dist as a warm-cache symlink. Dereference it so
  # the release contains compiled files, never a machine-local absolute link.
  cp -aL "$ROOT/unraid-api-plugin-incus/dist" "$api/"
  cp -a "$ROOT/unraid-api-plugin-incus/package.json" \
    "$ROOT/unraid-api-plugin-incus/package-lock.json" "$api/"
  # Install only locked runtime dependencies. Host-provided Nest/GraphQL peers
  # remain peers; --legacy-peer-deps prevents npm from materializing them here.
  (cd "$api" && npm ci --omit=dev --ignore-scripts --legacy-peer-deps)
fi

tar -C "$stage" --owner=0 --group=0 --numeric-owner \
  --transform='s|^\./||' -cJf "$output" .
echo "built $output"
echo "md5=$(md5sum "$output" | awk '{print $1}')"
echo "sha256=$(sha256sum "$output" | awk '{print $1}')"
echo "entries=$(tar -tJf "$output" | wc -l)"
echo "Update incus.plg entities and MANIFEST.md, then run scripts/verify-classic-package.sh."
