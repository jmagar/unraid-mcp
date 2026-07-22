#!/usr/bin/env bash
# Build the unraid-mcp Slackware package (.txz).
#
# Stages:
#   1. Build the settings web bundle (vite) into source/.../web/.
#   2. Vendor a relocatable CPython (python-build-standalone — the same
#      distribution uv uses) under usr/local/unraid-mcp/python/.
#   3. Install the unraid-mcp wheel + deps into that interpreter's
#      site-packages so `python3 -m unraid_mcp.main` just works.
#   4. Assemble a deterministic root-owned .txz and print its hashes.
#
# Usage: build-txz.sh <plugin-version> [wheel-path]
#   <plugin-version>  e.g. 2.5.0 — used in the package filename.
#   [wheel-path]      optional local wheel; defaults to pulling
#                     unraid-mcp==<plugin-version> from PyPI.

set -euo pipefail

VERSION="${1:?usage: build-txz.sh <version> [wheel-path]}"
WHEEL="${2:-}"

PYTHON_VERSION="3.12.12"
PBS_RELEASE="20260710"
PBS_TARBALL="cpython-${PYTHON_VERSION}+${PBS_RELEASE}-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"
PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PBS_RELEASE}/${PBS_TARBALL}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="$(mktemp -d)"
CACHE="${ROOT}/.cache"
OUT_DIR="${ROOT}/packages"
PKG_NAME="unraid-mcp-${VERSION}-x86_64-1.txz"

trap 'rm -rf "${STAGE}"' EXIT
mkdir -p "${CACHE}" "${OUT_DIR}"

echo "==> [1/4] building web bundle"
(cd "${ROOT}/web" && npm ci --no-audit --no-fund && npm run build)

echo "==> [2/4] vendoring python ${PYTHON_VERSION} (${PBS_RELEASE})"
if [ ! -f "${CACHE}/${PBS_TARBALL}" ]; then
    curl -fsSL -o "${CACHE}/${PBS_TARBALL}" "${PBS_URL}"
fi
mkdir -p "${STAGE}/usr/local/unraid-mcp/python"
tar -xzf "${CACHE}/${PBS_TARBALL}" --strip-components=1 \
    -C "${STAGE}/usr/local/unraid-mcp/python"

echo "==> [3/4] installing unraid-mcp into the bundled interpreter"
PY="${STAGE}/usr/local/unraid-mcp/python/bin/python3"
"${PY}" -m pip install --quiet --no-cache-dir --upgrade pip
if [ -n "${WHEEL}" ]; then
    "${PY}" -m pip install --quiet --no-cache-dir "${WHEEL}"
else
    "${PY}" -m pip install --quiet --no-cache-dir "unraid-mcp==${VERSION}"
fi
"${PY}" -m pip uninstall --quiet -y pip setuptools 2>/dev/null || true
# Sanity: the module must import with the bundled interpreter alone.
"${PY}" -c "import unraid_mcp; import importlib.metadata as m; print('unraid-mcp', m.version('unraid-mcp'))"

echo "==> [4/4] assembling ${PKG_NAME}"
cp -a "${ROOT}/source/." "${STAGE}/"
# Slackware package description (install/slack-desc is conventional).
mkdir -p "${STAGE}/install"
cat > "${STAGE}/install/slack-desc" <<EOF
unraid-mcp: unraid-mcp (MCP server for the Unraid GraphQL API)
unraid-mcp:
unraid-mcp: Exposes Unraid system control to MCP clients (Claude et al.)
unraid-mcp: with bearer-token auth and a webGUI settings page.
unraid-mcp:
unraid-mcp: https://github.com/dinglebear-ai/unraid-mcp
EOF

find "${STAGE}" -type d -exec chmod 755 {} +
chmod +x "${STAGE}/usr/local/emhttp/plugins/unraid-mcp/scripts/"* \
         "${STAGE}/usr/local/emhttp/plugins/unraid-mcp/event/"* \
         "${STAGE}/usr/local/unraid-mcp/python/bin/"*

tar -C "${STAGE}" --owner=0 --group=0 --numeric-owner \
    --transform='s|^\./||' -cJf "${OUT_DIR}/${PKG_NAME}" .

MD5="$(md5sum "${OUT_DIR}/${PKG_NAME}" | awk '{print $1}')"
SHA256="$(sha256sum "${OUT_DIR}/${PKG_NAME}" | awk '{print $1}')"
SIZE="$(stat -c%s "${OUT_DIR}/${PKG_NAME}")"

echo ""
echo "package: ${OUT_DIR}/${PKG_NAME}"
echo "size:    ${SIZE} bytes"
echo "md5:     ${MD5}"
echo "sha256:  ${SHA256}"
echo ""
echo "==> writing ${OUT_DIR}/unraid-mcp.plg"
sed -e "s/VERSION_PLACEHOLDER/${VERSION}/g" \
    -e "s/MD5_PLACEHOLDER/${MD5}/g" \
    -e "s/SHA256_PLACEHOLDER/${SHA256}/g" \
    "${ROOT}/unraid-mcp.plg" > "${OUT_DIR}/unraid-mcp.plg"
echo "done — upload both files to the GitHub release for v${VERSION}"
