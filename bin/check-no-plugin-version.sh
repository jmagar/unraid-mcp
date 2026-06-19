#!/usr/bin/env bash
# check-no-plugin-version.sh — guard that the Claude/Codex plugin manifests carry
# NO `version` field.
#
# Rationale: this plugin is distributed from a git repo, so Claude Code (and the
# Codex surface) version it by commit SHA — every commit to main is its own
# version. Manually maintaining a synced semver across manifests was pure churn
# (and a frequent source of merge conflicts), so the `version` field was removed.
# This check fails if a `version` field reappears, to stop the manual-bump habit
# from creeping back.
#
# Exceptions (NOT checked here):
#   - gemini-extension.json — the Gemini CLI requires a `version` field, so it
#     keeps a static one (not SHA-versioned).
#   - pyproject.toml — keeps its `version` (required by Python packaging and read
#     at runtime via importlib metadata); bumped only for tagged releases.
set -euo pipefail

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

MANIFESTS=(
  ".claude-plugin/plugin.json"
  ".codex-plugin/plugin.json"
)

fail=0
for manifest in "${MANIFESTS[@]}"; do
  [ -f "$manifest" ] || continue
  has_version=$(python3 -c "import json,sys; print('1' if 'version' in json.load(open('$manifest')) else '0')" 2>/dev/null || echo "0")
  if [ "$has_version" = "1" ]; then
    echo "[no-plugin-version] FAIL — $manifest has a 'version' field; remove it."
    fail=1
  fi
done

if [ "$fail" = "1" ]; then
  echo ""
  echo "Plugin manifests are versioned by git commit SHA — do not add a 'version' field."
  echo "See bin/check-no-plugin-version.sh and CLAUDE.md for the reasoning."
  exit 1
fi

echo "[no-plugin-version] OK — no plugin manifest declares a version field."
exit 0
