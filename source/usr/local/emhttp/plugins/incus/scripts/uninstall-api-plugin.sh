#!/bin/bash
set -euo pipefail

TARGET="/usr/local/unraid-api/node_modules/unraid-api-plugin-incus"
rm -rf "$TARGET" "${TARGET}.rollback" "${TARGET}.new."*
if command -v unraid-api >/dev/null; then
  unraid-api restart || {
    logger -t incus "API backend removed but unraid-api reload failed"
    exit 1
  }
fi
logger -t incus "API backend removed"
