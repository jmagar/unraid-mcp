#!/usr/bin/env bash
# Validate Claude Code marketplace and plugin structure

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Counters
CHECKS=0
PASSED=0
FAILED=0

check() {
    local test_name="$1"
    local test_cmd="$2"

    CHECKS=$((CHECKS + 1))
    echo -n "Checking: $test_name... "

    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "=== Validating Claude Code Marketplace Structure ==="
echo ""

# Check marketplace manifest
check "Marketplace manifest exists" "test -f .claude-plugin/marketplace.json"
check "Marketplace manifest is valid JSON" "jq empty .claude-plugin/marketplace.json"
check "Marketplace has name" "jq -e '.name' .claude-plugin/marketplace.json"
check "Marketplace has plugins array" "jq -e '.plugins | type == \"array\"' .claude-plugin/marketplace.json"

# Check plugin manifest
check "Plugin manifest exists" "test -f .claude-plugin/plugin.json"
check "Plugin manifest is valid JSON" "jq empty .claude-plugin/plugin.json"
check "Plugin has name" "jq -e '.name' .claude-plugin/plugin.json"
check "Plugin has version" "jq -e '.version' .claude-plugin/plugin.json"

# Check plugin structure
check "Plugin has SKILL.md" "test -f skills/unraid/SKILL.md"
check "Plugin has README.md" "test -f skills/unraid/README.md"
check "Plugin has scripts directory" "test -d skills/unraid/scripts"
check "Plugin has examples directory" "test -d skills/unraid/examples"
check "Plugin has references directory" "test -d skills/unraid/references"

# Validate plugin is listed in marketplace
check "Plugin listed in marketplace" "jq -e '.plugins[] | select(.name == \"unraid\")' .claude-plugin/marketplace.json"

# Check marketplace metadata
check "Marketplace has repository" "jq -e '.repository' .claude-plugin/marketplace.json"
check "Marketplace has owner" "jq -e '.owner' .claude-plugin/marketplace.json"

# Verify source path
PLUGIN_SOURCE=$(jq -r '.plugins[]? | select(.name == "unraid") | .source // empty' .claude-plugin/marketplace.json 2>/dev/null || true)
if [ -n "$PLUGIN_SOURCE" ]; then
    check "Plugin source path is valid" "test -d \"$PLUGIN_SOURCE\""
else
    CHECKS=$((CHECKS + 1))
    FAILED=$((FAILED + 1))
    echo -e "Checking: Plugin source path is valid... ${RED}✗${NC} (plugin not found in marketplace)"
fi

echo ""
echo "=== Results ==="
echo -e "Total checks: $CHECKS"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All checks passed!${NC}"
    echo ""
    echo "Marketplace is ready for distribution at:"
    echo "  $(jq -r '.repository' .claude-plugin/marketplace.json)"
fi
