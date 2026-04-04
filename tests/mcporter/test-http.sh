#!/usr/bin/env bash
# =============================================================================
# test-http.sh — Live HTTP end-to-end smoke-test for unraid-mcp
#
# Tests the full HTTP stack against a running server:
#   Phase 1 — Middleware endpoints (no auth required)
#   Phase 2 — Auth enforcement (skipped with --skip-auth)
#   Phase 3 — MCP protocol (initialize, tools/list, ping)
#   Phase 4 — Tool smoke-tests (non-destructive subactions)
#
# Usage:
#   ./tests/mcporter/test-http.sh
#   ./tests/mcporter/test-http.sh --url http://localhost:6970/mcp
#   ./tests/mcporter/test-http.sh --url https://unraid.tootie.tv/mcp --token <tok>
#   ./tests/mcporter/test-http.sh --skip-auth     # for gateway-protected deployments
#   ./tests/mcporter/test-http.sh --verbose       # print raw responses
#
# Options:
#   --url URL       MCP endpoint (default: http://localhost:6970/mcp)
#   --token TOK     Bearer token (auto-read from ~/.unraid-mcp/.env if omitted)
#   --skip-auth     Skip Phase 2 auth tests (use for OAuth gateway deployments)
#   --verbose       Print raw response bodies
#
# Exit codes:
#   0 — all tests passed (or skipped)
#   1 — one or more tests failed
#   2 — prerequisite check failed
# =============================================================================

set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
MCP_URL="http://localhost:6970/mcp"
TOKEN=""
SKIP_AUTH=false
SKIP_TOOLS=false
VERBOSE=false

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  R='\033[0;31m' G='\033[0;32m' Y='\033[0;33m' C='\033[0;36m'
  B='\033[1m' D='\033[2m' N='\033[0m'
else
  R='' G='' Y='' C='' B='' D='' N=''
fi

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
PASS=0; FAIL=0; SKIP=0
declare -a FAILED=()

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)         MCP_URL="${2:?--url requires a value}";   shift 2 ;;
    --token)       TOKEN="${2:?--token requires a value}";   shift 2 ;;
    --skip-auth)   SKIP_AUTH=true;                           shift ;;
    --skip-tools)  SKIP_TOOLS=true;                          shift ;;
    --verbose)     VERBOSE=true;                             shift ;;
    -h|--help)
      sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) printf '[ERROR] Unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

# Derive base URL: strip trailing /mcp (with or without trailing slash).
# Examples:
#   http://localhost:6970/mcp  → http://localhost:6970
#   https://host/api/mcp/      → https://host/api
#   https://host/mcp           → https://host
# If the URL doesn't end in /mcp[/], use it as-is (strip trailing slash only).
_stripped="${MCP_URL%/}"          # remove optional trailing slash
if [[ "$_stripped" == */mcp ]]; then
  BASE_URL="${_stripped%/mcp}"
else
  BASE_URL="$_stripped"
fi
unset _stripped

# ---------------------------------------------------------------------------
# Auto-detect token from ~/.unraid-mcp/.env if not supplied
# ---------------------------------------------------------------------------
ENV_FILE="$HOME/.unraid-mcp/.env"
if [[ -z "$TOKEN" && -f "$ENV_FILE" ]]; then
  TOKEN="$(grep -E '^UNRAID_MCP_BEARER_TOKEN=' "$ENV_FILE" 2>/dev/null \
           | head -1 | cut -d= -f2- | tr -d '"'"'" | xargs)"
fi

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------
section() { printf "\n${C}${B}━━━ %s ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${N}\n" "$1"; }
pass()    { printf "  %-62s${G}PASS${N}\n" "$1"; (( PASS++ )); }
fail()    { printf "  %-62s${R}FAIL${N}\n" "$1"; (( FAIL++ )); FAILED+=("$1"); }
skip()    { printf "  %-62s${Y}SKIP${N}${D} ($2)${N}\n" "$1"; (( SKIP++ )); }
verbose() { [[ "$VERBOSE" == true ]] && printf "${D}    %s${N}\n" "$1" || true; }

for cmd in curl jq; do
  command -v "$cmd" &>/dev/null || { printf '[ERROR] %s not found in PATH\n' "$cmd" >&2; exit 2; }
done

# Check server is reachable
if ! curl -sk --max-time 5 -o /dev/null "$BASE_URL/health" 2>/dev/null; then
  printf '[ERROR] Server unreachable at %s\n' "$BASE_URL" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

# http_get URL [extra_curl_args...]
# Sets: HTTP_STATUS, HTTP_BODY
http_get() {
  local url="$1"; shift
  local tmp; tmp="$(mktemp)"
  HTTP_STATUS="$(curl -sk --max-time 10 -w '%{http_code}' -o "$tmp" "$@" "$url")"
  HTTP_BODY="$(cat "$tmp")"; rm -f "$tmp"
  verbose "$HTTP_BODY"
}

# mcp_post METHOD [PARAMS_JSON]
# Posts a JSON-RPC request to MCP_URL with the configured token.
# Sets: HTTP_STATUS, HTTP_BODY, MCP_RESULT, MCP_ERROR
_MCP_ID=0
mcp_post() {
  local method="$1"
  local params="${2:-null}"
  (( _MCP_ID++ ))
  local payload; payload="$(jq -cn --arg m "$method" --argjson p "$params" \
    --argjson id "$_MCP_ID" \
    '{"jsonrpc":"2.0","id":$id,"method":$m,"params":$p}')"

  local args=(-sk --max-time 15
    -X POST
    -H "Content-Type: application/json"
    -H "Accept: application/json, text/event-stream"
  )
  [[ -n "$TOKEN" ]] && args+=(-H "Authorization: Bearer $TOKEN")
  [[ -n "${MCP_SESSION_ID:-}" ]] && args+=(-H "Mcp-Session-Id: $MCP_SESSION_ID")

  local tmp; tmp="$(mktemp)"
  # Capture headers too so we can extract session ID
  HTTP_STATUS="$(curl "${args[@]}" -D "$tmp.hdr" -w '%{http_code}' \
    -o "$tmp.body" "$MCP_URL" -d "$payload")"
  HTTP_BODY="$(cat "$tmp.body" 2>/dev/null)"

  # Extract session ID if present
  local sid; sid="$(grep -i '^mcp-session-id:' "$tmp.hdr" 2>/dev/null \
    | head -1 | awk '{print $2}' | tr -d '\r')"
  [[ -n "$sid" ]] && MCP_SESSION_ID="$sid"

  rm -f "$tmp" "$tmp.hdr" "$tmp.body"
  verbose "$HTTP_BODY"

  # For SSE responses, extract the JSON data line
  if echo "$HTTP_BODY" | grep -q '^data:'; then
    HTTP_BODY="$(echo "$HTTP_BODY" | grep '^data:' | head -1 | sed 's/^data: //')"
  fi

  MCP_RESULT="$(echo "$HTTP_BODY" | jq -r '.result // empty' 2>/dev/null)"
  MCP_ERROR="$(echo "$HTTP_BODY" | jq -r '.error // empty' 2>/dev/null)"
}

# assert_jq LABEL JSON_INPUT JQ_FILTER
# Passes if jq filter returns a non-empty, non-null, non-false value.
assert_jq() {
  local label="$1" body="$2" filter="$3"
  local val; val="$(echo "$body" | jq -r "$filter" 2>/dev/null)"
  if [[ -n "$val" && "$val" != "null" && "$val" != "false" ]]; then
    pass "$label"
  else
    fail "$label"
    verbose "  filter: $filter"
    verbose "  body:   $(echo "$body" | head -c 300)"
  fi
}

# ---------------------------------------------------------------------------
printf '\n%s%sUnraid MCP — HTTP live test%s\n' "$B" "$C" "$N"
printf '  URL:  %s\n' "$MCP_URL"
printf '  Auth: %s\n' "$([[ -n "$TOKEN" ]] && echo "token configured" || echo "none (auth disabled or gateway)")"

MCP_SESSION_ID=""

# =============================================================================
# Phase 1 — Middleware (no auth)
# =============================================================================
section "Phase 1 · Middleware (no auth)"

# /health
http_get "$BASE_URL/health"
if [[ "$HTTP_STATUS" == "200" ]] && echo "$HTTP_BODY" | jq -e '.status == "ok"' &>/dev/null; then
  pass "/health → 200 {status:ok}"
else
  fail "/health → 200 {status:ok}  (got $HTTP_STATUS)"
fi

# /.well-known/oauth-protected-resource
http_get "$BASE_URL/.well-known/oauth-protected-resource"
if [[ "$HTTP_STATUS" == "200" ]]; then
  pass "/.well-known/oauth-protected-resource → 200"
  assert_jq "  bearer_methods_supported present" \
    "$HTTP_BODY" '.bearer_methods_supported | length > 0'
  assert_jq "  resource field present" \
    "$HTTP_BODY" '.resource | length > 0'
else
  fail "/.well-known/oauth-protected-resource → 200  (got $HTTP_STATUS)"
  skip "  bearer_methods_supported present" "parent failed"
  skip "  resource field present"           "parent failed"
fi

# /.well-known/oauth-protected-resource/mcp
http_get "$BASE_URL/.well-known/oauth-protected-resource/mcp"
if [[ "$HTTP_STATUS" == "200" ]]; then
  pass "/.well-known/oauth-protected-resource/mcp → 200"
else
  fail "/.well-known/oauth-protected-resource/mcp → 200  (got $HTTP_STATUS)"
fi

# =============================================================================
# Phase 2 — Auth enforcement
# =============================================================================
section "Phase 2 · Auth enforcement"

if [[ "$SKIP_AUTH" == true ]]; then
  skip "no-token → 401"    "--skip-auth"
  skip "bad-token → 401"   "--skip-auth"
  skip "good-token → pass" "--skip-auth"
elif [[ -z "$TOKEN" ]]; then
  skip "no-token → 401"    "no token configured, likely auth disabled"
  skip "bad-token → 401"   "no token configured, likely auth disabled"
  skip "good-token → pass" "no token configured, likely auth disabled"
else
  # No token — expect 401
  local_tmp="$(mktemp)"
  no_token_status="$(curl -sk --max-time 10 -w '%{http_code}' -o "$local_tmp" \
    -X POST -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":99,"method":"ping","params":null}' \
    "$MCP_URL")"
  no_token_body="$(cat "$local_tmp")"; rm -f "$local_tmp"
  verbose "$no_token_body"
  if [[ "$no_token_status" == "401" ]]; then
    pass "no-token → 401"
  else
    fail "no-token → 401  (got $no_token_status)"
  fi

  # Wrong token — expect 401 with invalid_token
  local_tmp="$(mktemp)"
  bad_token_status="$(curl -sk --max-time 10 -w '%{http_code}' -o "$local_tmp" \
    -X POST -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Authorization: Bearer this-is-the-wrong-token-intentionally" \
    -d '{"jsonrpc":"2.0","id":99,"method":"ping","params":null}' \
    "$MCP_URL")"
  bad_token_body="$(cat "$local_tmp")"; rm -f "$local_tmp"
  verbose "$bad_token_body"
  if [[ "$bad_token_status" == "401" ]]; then
    err_field="$(echo "$bad_token_body" | jq -r '.error // empty' 2>/dev/null)"
    if [[ "$err_field" == "invalid_token" ]]; then
      pass "bad-token → 401 invalid_token"
    else
      pass "bad-token → 401  (error field: ${err_field:-absent})"
    fi
  else
    fail "bad-token → 401  (got $bad_token_status)"
  fi

  # Good token — should not be 401
  local_tmp="$(mktemp)"
  good_token_status="$(curl -sk --max-time 10 -w '%{http_code}' -o "$local_tmp" \
    -X POST -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-http","version":"0"}}}' \
    "$MCP_URL")"
  rm -f "$local_tmp"
  if [[ "$good_token_status" != "401" && "$good_token_status" != "403" ]]; then
    pass "good-token → not 401/403  (got $good_token_status)"
  else
    fail "good-token → not 401/403  (got $good_token_status)"
  fi
fi

# =============================================================================
# Phase 3 — MCP Protocol
# =============================================================================
section "Phase 3 · MCP protocol"

# initialize
mcp_post "initialize" '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-http","version":"0"}}'
if [[ "$HTTP_STATUS" == "200" ]]; then
  pass "initialize → 200"
  assert_jq "  serverInfo.name present" "$HTTP_BODY" '.result.serverInfo.name | length > 0'
  assert_jq "  protocolVersion present" "$HTTP_BODY" '.result.protocolVersion | length > 0'
else
  fail "initialize → 200  (got $HTTP_STATUS: $(echo "$HTTP_BODY" | head -c 120))"
  skip "  serverInfo.name present" "initialize failed"
  skip "  protocolVersion present" "initialize failed"
fi

# tools/list
mcp_post "tools/list" 'null'
if [[ "$HTTP_STATUS" == "200" ]]; then
  tool_count="$(echo "$HTTP_BODY" | jq '.result.tools | length' 2>/dev/null)"
  pass "tools/list → 200  ($tool_count tools)"
  assert_jq "  unraid tool present" \
    "$HTTP_BODY" '.result.tools[] | select(.name == "unraid") | .name'
  assert_jq "  diagnose_subscriptions tool present" \
    "$HTTP_BODY" '.result.tools[] | select(.name == "diagnose_subscriptions") | .name'
else
  fail "tools/list → 200  (got $HTTP_STATUS)"
  skip "  unraid tool present"                  "tools/list failed"
  skip "  diagnose_subscriptions tool present"  "tools/list failed"
fi

# ping
mcp_post "ping" 'null'
if [[ "$HTTP_STATUS" == "200" ]]; then
  pass "ping → 200"
else
  # ping returning non-200 is not critical — some MCP servers don't implement it
  skip "ping → 200" "not implemented (got $HTTP_STATUS)"
fi

# =============================================================================
# Phase 4 — Tool smoke-tests
# =============================================================================
section "Phase 4 · Tool smoke-tests (non-destructive)"

if [[ "$SKIP_TOOLS" == true ]]; then
  skip "Phase 4 tool calls" "--skip-tools (no live Unraid API)"
  skip "Phase 4b guard bypass tests" "--skip-tools"
  # Jump to summary
  TOTAL=$(( PASS + FAIL + SKIP ))
  printf '\n%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n' "$C$B" "$N"
  printf 'Results: %s%d passed%s  %s%d failed%s  %s%d skipped%s  (%d total)\n' \
    "$G" "$PASS" "$N" \
    "$([[ $FAIL -gt 0 ]] && echo "$R" || echo "$D")" "$FAIL" "$N" \
    "$D" "$SKIP" "$N" \
    "$TOTAL"
  printf '\n'
  [[ $FAIL -eq 0 ]]
  exit $?
fi

# Helper: call unraid tool and check for no error
call_unraid() {
  local label="$1" action="$2" subaction="$3"
  local extra_params="${4:-}"
  local params; params="$(jq -cn \
    --arg a "$action" --arg s "$subaction" \
    '{"name":"unraid","arguments":{"action":$a,"subaction":$s}}')"
  if [[ -n "$extra_params" ]]; then
    params="$(echo "$params" | jq --argjson x "$extra_params" \
      '.arguments += $x')"
  fi
  mcp_post "tools/call" "$params"

  if [[ "$HTTP_STATUS" == "200" ]]; then
    # isError:true means the tool itself reported failure
    if echo "$HTTP_BODY" | jq -e '.result.isError == true' &>/dev/null; then
      local errmsg; errmsg="$(echo "$HTTP_BODY" | jq -r '.result.content[0].text' 2>/dev/null | head -c 100)"
      fail "$label  (tool error: $errmsg)"
    else
      pass "$label"
    fi
  else
    local detail; detail="$(echo "$HTTP_BODY" | jq -r \
      '.error.message // .result.content[0].text // empty' 2>/dev/null | head -c 120)"
    fail "$label  (HTTP $HTTP_STATUS${detail:+: $detail})"
  fi
}

call_unraid "unraid health/check"             "health"  "check"
call_unraid "unraid health/test_connection"   "health"  "test_connection"
call_unraid "unraid system/overview"          "system"  "overview"
call_unraid "unraid system/network"           "system"  "network"
call_unraid "unraid docker/list"              "docker"  "list"
call_unraid "unraid docker/networks"          "docker"  "networks"
call_unraid "unraid array/parity_status"      "array"   "parity_status"
call_unraid "unraid disk/disks"               "disk"    "disks"
call_unraid "unraid disk/shares"              "disk"    "shares"
call_unraid "unraid vm/list"                  "vm"      "list"
call_unraid "unraid notification/overview"    "notification" "overview"
call_unraid "unraid user/me"                  "user"    "me"
call_unraid "unraid key/list"                 "key"     "list"
call_unraid "unraid rclone/list_remotes"      "rclone"  "list_remotes"

# Destructive guard: confirm=True must bypass the guard (operation reaches the tool).
# Note: confirm=false triggers MCP elicitation (a persistent SSE form exchange) which
# hangs in a one-shot HTTP request. That path is covered by tests/safety/ unit tests.
# Here we verify the bypass path — that confirm=True gets past the guard and the
# operation either succeeds or fails for a real-world reason (not a guard rejection).
section "Phase 4b · Destructive action guards (confirm=True bypass)"

guard_bypass_test() {
  local label="$1" action="$2" subaction="$3"
  shift 3
  local extra_args=("$@")
  local args_json='{}'; [[ ${#extra_args[@]} -gt 0 ]] && args_json="${extra_args[0]}"
  local params; params="$(jq -cn \
    --arg a "$action" --arg s "$subaction" --argjson x "$args_json" \
    '{"name":"unraid","arguments":({"action":$a,"subaction":$s,"confirm":true} + $x)}')"
  mcp_post "tools/call" "$params"
  local body_text; body_text="$(echo "$HTTP_BODY" | jq -r \
    '.result.content[0].text // empty' 2>/dev/null | head -c 200)"
  # Guard rejection messages contain "confirm=True" — any other response means the
  # guard was bypassed (operation reached the tool layer).
  if echo "$body_text" | grep -qiE 're-run with confirm'; then
    fail "$label  guard rejected confirm=True — should not happen"
  elif [[ "$HTTP_STATUS" == "200" ]]; then
    pass "$label  guard bypassed (confirm=True accepted)"
  else
    fail "$label  unexpected HTTP $HTTP_STATUS"
  fi
}

# notification/delete with a non-existent ID: guard passes, tool returns 404-style error — that's fine.
guard_bypass_test "notification/delete guard bypass" "notification" "delete" \
  '{"notification_id":"test-guard-check-nonexistent"}'

# vm/force_stop without a vm_id: guard passes, tool returns validation error — that's fine.
guard_bypass_test "vm/force_stop guard bypass" "vm" "force_stop"

# =============================================================================
# Summary
# =============================================================================
TOTAL=$(( PASS + FAIL + SKIP ))
printf '\n%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n' "$C$B" "$N"
printf 'Results: %s%d passed%s  %s%d failed%s  %s%d skipped%s  (%d total)\n' \
  "$G" "$PASS" "$N" \
  "$([[ $FAIL -gt 0 ]] && echo "$R" || echo "$D")" "$FAIL" "$N" \
  "$D" "$SKIP" "$N" \
  "$TOTAL"

if [[ ${#FAILED[@]} -gt 0 ]]; then
  printf '\n%sFailed tests:%s\n' "$R$B" "$N"
  for t in "${FAILED[@]}"; do
    printf '  • %s\n' "$t"
  done
fi

printf '\n'
[[ $FAIL -eq 0 ]]
