#!/usr/bin/env bash
# Validate plugin manifests, hooks, MCP config, and skills for this repo.
set -euo pipefail

plugin_root="${PLUGIN_ROOT:-}"
if [[ -z "${plugin_root}" ]]; then
  plugin_root="$(find plugins -mindepth 1 -maxdepth 1 -type d | sort | head -1)"
fi

[[ -n "${plugin_root}" ]] || { echo "MISSING: plugin root"; exit 1; }
[[ -d "${plugin_root}" ]] || { echo "MISSING: ${plugin_root}"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "MISSING: jq"; exit 1; }

claude_manifest="${plugin_root}/.claude-plugin/plugin.json"
codex_manifest="${plugin_root}/.codex-plugin/plugin.json"
mcp_json="${plugin_root}/.mcp.json"
hooks_json="${plugin_root}/hooks/hooks.json"
hook_script="${plugin_root}/hooks/plugin-setup.sh"
skills_dir="${plugin_root}/skills"

for file in "${claude_manifest}" "${codex_manifest}" "${mcp_json}" "${hooks_json}"; do
  [[ -f "${file}" ]] || { echo "MISSING: ${file}"; exit 1; }
  jq empty "${file}"
done

for file in "${claude_manifest}" "${codex_manifest}"; do
  [[ "$(jq -er 'has("version")' "${file}")" == "false" ]] || {
    echo "FORBIDDEN: ${file} contains version"
    exit 1
  }
done

jq -er '.mcpServers | type == "object" and length > 0' "${mcp_json}" >/dev/null
jq -er '.hooks.SessionStart[]?.hooks[]?.command == "${CLAUDE_PLUGIN_ROOT}/hooks/plugin-setup.sh"' "${hooks_json}" >/dev/null

[[ -f "${hook_script}" ]] || { echo "MISSING: ${hook_script}"; exit 1; }
sh -n "${hook_script}"
if grep -Eq 'cargo (build|install|run)|curl .*[|][[:space:]]*sh|docker compose|systemctl' "${hook_script}"; then
  echo "FORBIDDEN: hook performs build/install/service bootstrap: ${hook_script}"
  exit 1
fi

[[ -d "${skills_dir}" ]] || { echo "MISSING: ${skills_dir}"; exit 1; }
skill_count=0
while IFS= read -r skill_file; do
  skill_count=$((skill_count + 1))
  grep -q '^name:' "${skill_file}" || { echo "MISSING name: ${skill_file}"; exit 1; }
  grep -q '^description:' "${skill_file}" || { echo "MISSING description: ${skill_file}"; exit 1; }
done < <(find "${skills_dir}" -mindepth 2 -maxdepth 2 -name SKILL.md | sort)
(( skill_count > 0 )) || { echo "MISSING: ${skills_dir}/*/SKILL.md"; exit 1; }

echo "OK"
