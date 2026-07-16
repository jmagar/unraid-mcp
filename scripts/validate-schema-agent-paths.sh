#!/usr/bin/env bash
set -euo pipefail

base="${1:?usage: validate-schema-agent-paths.sh BASE HEAD}"
head="${2:?usage: validate-schema-agent-paths.sh BASE HEAD}"
failed=false

while IFS= read -r path; do
  [[ -n "$path" ]] || continue
  case "$path" in
    .github/*|Dockerfile|docker-compose.yaml|entrypoint.sh|pyproject.toml|uv.lock|release-please-config.json|.release-please-manifest.json|server.json|unraid_mcp/core/auth.py|unraid_mcp/core/google_auth.py|unraid_mcp/config/*)
      echo "::error file=${path}::schema agent touched an explicitly denied path"
      failed=true
      continue
      ;;
  esac

  case "$path" in
    docs/unraid/*|README.md|CLAUDE.md|openwiki/*|unraid_mcp/tools/*|unraid_mcp/devtools/*|unraid_mcp/subscriptions/queries.py|unraid_mcp/subscriptions/diagnostics.py|tests/schema/*|tests/contract/*|tests/mock/*|tests/test_schema_diff_summary.py|tests/test_docs_match_code.py)
      ;;
    *)
      echo "::error file=${path}::schema agent path is outside the allowlist"
      failed=true
      ;;
  esac
done < <(git diff --name-only "$base...$head")

if [[ "$failed" == true ]]; then
  exit 1
fi
