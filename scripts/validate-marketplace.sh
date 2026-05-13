#!/usr/bin/env bash
# Validate the Claude Code plugin artifacts shipped by this repository.

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

CHECKS=0
PASSED=0
FAILED=0

check() {
  local test_name="$1"
  local test_cmd="$2"

  CHECKS=$((CHECKS + 1))
  printf 'Checking: %s... ' "${test_name}"

  if eval "${test_cmd}" >/dev/null 2>&1; then
    printf '%b\n' "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
    return 0
  fi

  printf '%b\n' "${RED}FAIL${NC}"
  FAILED=$((FAILED + 1))
  return 1
}

check_equals() {
  local test_name="$1"
  local expected="$2"
  local actual="$3"

  CHECKS=$((CHECKS + 1))
  printf 'Checking: %s... ' "${test_name}"

  if [[ "${actual}" == "${expected}" ]]; then
    printf '%b\n' "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
    return 0
  fi

  printf '%b expected %q, got %q\n' "${RED}FAIL${NC}" "${expected}" "${actual}"
  FAILED=$((FAILED + 1))
  return 1
}

json_value() {
  local query="$1"
  local file="$2"
  jq -er "${query}" "${file}" 2>/dev/null
}

echo "=== Validating syslog-mcp Plugin Layout ==="
echo

check "jq is available" "command -v jq"

PLUGIN_JSON=".claude-plugin/plugin.json"
MCP_JSON="plugins/.mcp.json"
HOOKS_JSON="plugins/hooks/hooks.json"
SKILLS_DIR="plugins/skills"

check "plugin manifest exists" "test -f '${PLUGIN_JSON}'"
check "plugin manifest is valid JSON" "jq empty '${PLUGIN_JSON}'"
check "plugin name is syslog" "test \"\$(jq -er '.name' '${PLUGIN_JSON}')\" = 'syslog'"
check "plugin has semver version" "jq -er '.version | test(\"^[0-9]+\\\\.[0-9]+\\\\.[0-9]+$\")' '${PLUGIN_JSON}'"
check "plugin points to MCP config" "test \"\$(jq -er '.mcpServers' '${PLUGIN_JSON}')\" = './plugins/.mcp.json'"
check "plugin points to hooks config" "test \"\$(jq -er '.hooks' '${PLUGIN_JSON}')\" = './plugins/hooks/hooks.json'"
check "plugin points to skills directory" "test \"\$(jq -er '.skills' '${PLUGIN_JSON}')\" = './plugins/skills'"
check "plugin declares server_url userConfig" "jq -er '.userConfig.server_url.default == \"http://localhost:3100\"' '${PLUGIN_JSON}'"
check "plugin declares syslog_port userConfig" "jq -er '.userConfig.syslog_port.default == 1514' '${PLUGIN_JSON}'"
check "plugin declares syslog_host_port userConfig" "jq -er '.userConfig.syslog_host_port.default == 1514' '${PLUGIN_JSON}'"
check "plugin declares mcp_port userConfig" "jq -er '.userConfig.mcp_port.default == 3100' '${PLUGIN_JSON}'"
check "plugin declares api_token as sensitive" "jq -er '.userConfig.api_token.sensitive == true' '${PLUGIN_JSON}'"

if [[ -f "${PLUGIN_JSON}" && -f Cargo.toml ]]; then
  plugin_version="$(json_value '.version' "${PLUGIN_JSON}" || true)"
  cargo_version="$(awk '
    /^\[/ { section = $0 }
    section == "[package]" && /^version *= *"[^"]+"/ {
      line = $0
      sub(/^[^"]*"/, "", line)
      sub(/".*/, "", line)
      print line
      exit
    }
  ' Cargo.toml)"
  check_equals "plugin version matches Cargo.toml" "${cargo_version}" "${plugin_version}"
else
  check "plugin version matches Cargo.toml" "false"
fi

check "MCP config exists" "test -f '${MCP_JSON}'"
check "MCP config is valid JSON" "jq empty '${MCP_JSON}'"
check "MCP server is named syslog" "jq -er '.mcpServers.syslog' '${MCP_JSON}'"
check "MCP transport is HTTP" "jq -er '.mcpServers.syslog.type == \"http\"' '${MCP_JSON}'"
check "MCP URL uses server_url and /mcp path" "jq -er '.mcpServers.syslog.url == \"\${user_config.server_url}/mcp\"' '${MCP_JSON}'"
check "MCP Authorization header uses api_token" "jq -er '.mcpServers.syslog.headers.Authorization == \"Bearer \${user_config.api_token}\"' '${MCP_JSON}'"

check "hooks config exists" "test -f '${HOOKS_JSON}'"
check "hooks config is valid JSON" "jq empty '${HOOKS_JSON}'"
check "SessionStart runs plugin setup" "jq -er '.hooks.SessionStart[]?.hooks[]?.command == \"\${CLAUDE_PLUGIN_ROOT}/scripts/plugin-setup.sh\"' '${HOOKS_JSON}'"
check "ConfigChange runs plugin setup" "jq -er '.hooks.ConfigChange[]? | select(.matcher == \"user_settings\") | .hooks[]?.command == \"\${CLAUDE_PLUGIN_ROOT}/scripts/plugin-setup.sh\"' '${HOOKS_JSON}'"

check "skills directory exists" "test -d '${SKILLS_DIR}'"

skill_count=0
if [[ -d "${SKILLS_DIR}" ]]; then
  while IFS= read -r skill_file; do
    skill_count=$((skill_count + 1))
    skill_dir="$(basename "$(dirname "${skill_file}")")"
    check "skill ${skill_dir} has front matter name" "awk 'BEGIN {found=0} /^name:[[:space:]]*${skill_dir}[[:space:]]*$/ {found=1} END {exit found ? 0 : 1}' '${skill_file}'"
    check "skill ${skill_dir} has description" "awk 'BEGIN {found=0} /^description:[[:space:]]*[^[:space:]]/ {found=1} END {exit found ? 0 : 1}' '${skill_file}'"
  done < <(find "${SKILLS_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md | sort)
fi

CHECKS=$((CHECKS + 1))
printf 'Checking: at least one plugin skill exists... '
if (( skill_count > 0 )); then
  printf '%b\n' "${GREEN}PASS${NC}"
  PASSED=$((PASSED + 1))
else
  printf '%b\n' "${RED}FAIL${NC}"
  FAILED=$((FAILED + 1))
fi

echo
echo "=== Results ==="
echo "Total checks: ${CHECKS}"
printf '%b\n' "${GREEN}Passed: ${PASSED}${NC}"
if (( FAILED > 0 )); then
  printf '%b\n' "${RED}Failed: ${FAILED}${NC}"
  exit 1
fi

printf '%b\n' "${GREEN}All checks passed.${NC}"
