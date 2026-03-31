#!/usr/bin/env bash
# tests/test_live.sh — Full live integration test for unraid-mcp
# Requires: mcporter, jq, running server at $MCP_URL with $UNRAID_MCP_BEARER_TOKEN
set -euo pipefail

MCP_URL="${UNRAID_MCP_URL:-http://localhost:6970}"
TOKEN="${UNRAID_MCP_BEARER_TOKEN:?UNRAID_MCP_BEARER_TOKEN must be set}"
SERVER_NAME="unraid-mcp"
AUTH_HEADER="Authorization: Bearer $TOKEN"
PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS: $1"; ((++PASS)); }
fail() { echo "  FAIL: $1 — $2"; ((++FAIL)); }
skip() { echo "  SKIP: $1 — $2"; ((++SKIP)); }

header() { echo; echo "=== $1 ==="; }

# ── Schema comparison ──────────────────────────────────────────────────────────
header "Schema: external vs internal"

EXTERNAL_SCHEMA=$(npx mcporter list "$SERVER_NAME" --http-url "$MCP_URL" \
  --header "$AUTH_HEADER" --json 2>/dev/null) || fail "schema/list" "mcporter list failed"

TOOL_COUNT=$(echo "$EXTERNAL_SCHEMA" | jq '.tools | length' 2>/dev/null || echo 0)
echo "  Tools exposed: $TOOL_COUNT"

# Verify expected tool exists
if echo "$EXTERNAL_SCHEMA" | jq -e '.tools[] | select(.name == "unraid")' > /dev/null 2>&1; then
  pass "schema/tool-exists: unraid"
else
  fail "schema/tool-exists" "unraid tool not found in external schema"
fi

# ── Health check ───────────────────────────────────────────────────────────────
header "Health"

health=$(curl -sf "${MCP_URL}/health" 2>/dev/null) && pass "health/endpoint" || fail "health/endpoint" "HTTP error"

# ── Tool: unraid — read-only actions ─────────────────────────────────────────
header "Tool: unraid — action=health, subaction=check"

result=$(npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=health subaction=check 2>/dev/null) \
  && pass "action/health/check" || fail "action/health/check" "call failed"

header "Tool: unraid — action=health, subaction=test_connection"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=health subaction=test_connection > /dev/null 2>&1 \
  && pass "action/health/test_connection" || fail "action/health/test_connection" "call failed"

header "Tool: unraid — action=system, subaction=overview"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=system subaction=overview > /dev/null 2>&1 \
  && pass "action/system/overview" || fail "action/system/overview" "call failed"

header "Tool: unraid — action=docker, subaction=list"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=docker subaction=list > /dev/null 2>&1 \
  && pass "action/docker/list" || fail "action/docker/list" "call failed"

header "Tool: unraid — action=vm, subaction=list"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=vm subaction=list > /dev/null 2>&1 \
  && pass "action/vm/list" || fail "action/vm/list" "call failed"

header "Tool: unraid — action=disk, subaction=disks"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=disk subaction=disks > /dev/null 2>&1 \
  && pass "action/disk/disks" || fail "action/disk/disks" "call failed"

header "Tool: unraid — action=array, subaction=parity_status"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=array subaction=parity_status > /dev/null 2>&1 \
  && pass "action/array/parity_status" || fail "action/array/parity_status" "call failed"

header "Tool: unraid — action=notification, subaction=overview"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=notification subaction=overview > /dev/null 2>&1 \
  && pass "action/notification/overview" || fail "action/notification/overview" "call failed"

header "Tool: unraid — action=live, subaction=cpu"

npx mcporter call "${SERVER_NAME}.unraid" \
  --http-url "$MCP_URL" --header "$AUTH_HEADER" \
  action=live subaction=cpu > /dev/null 2>&1 \
  && pass "action/live/cpu" || fail "action/live/cpu" "call failed"

# ── Resources (server-level, no tool name needed) ────────────────────────────
header "Resources"

resources_output="$(
  npx mcporter call "${SERVER_NAME}" --http-url "$MCP_URL" --header "$AUTH_HEADER" \
    --list-resources 2>&1
)" && pass "resources/list" || {
  if printf '%s' "$resources_output" | grep -qi "no resources defined"; then
    skip "resources/list" "no resources defined"
  else
    fail "resources/list" "$resources_output"
  fi
}

# ── Bearer token enforcement ─────────────────────────────────────────────────
header "Bearer token enforcement"

UNAUTH=$(curl -s -o /dev/null -w "%{http_code}" "${MCP_URL}/mcp" \
  -X POST -H "Content-Type: application/json" -d '{}')
[ "$UNAUTH" = "401" ] \
  && pass "auth/unauthenticated-rejected" \
  || fail "auth/unauthenticated-rejected" "expected 401, got $UNAUTH"

BAD_TOKEN=$(curl -s -o /dev/null -w "%{http_code}" "${MCP_URL}/mcp" \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid-token-here" -d '{}')
[ "$BAD_TOKEN" = "401" ] \
  && pass "auth/bad-token-rejected" \
  || fail "auth/bad-token-rejected" "expected 401, got $BAD_TOKEN"

# ── Summary ────────────────────────────────────────────────────────────────────
echo
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
[ "$FAIL" -eq 0 ] && echo "ALL TESTS PASSED" && exit 0
echo "FAILURES DETECTED" && exit 1
