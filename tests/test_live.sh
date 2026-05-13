#!/usr/bin/env bash
# =============================================================================
# tests/test_live.sh — Canonical integration test for syslog-mcp
#
# Modes:
#   --mode docker  Build image, start container, run all test phases, teardown
#   --mode http    Test against an already-running server (requires --url)
#   --mode all     Alias for docker (default)
#
# Flags:
#   --url URL        Base URL of the MCP server (default: http://localhost:3100)
#   --token TOKEN    Bearer token (also read from SYSLOG_MCP_TOKEN env var)
#   --verbose        Print raw JSON responses for every call
#   --help           Show this help
#
# Environment variables:
#   SYSLOG_MCP_TOKEN       Bearer token for auth (optional — server may run without it)
#   PORT                   Override server port (default: 3100)
#
# Action inventory reference (not every action is exercised by this live test):
#   syslog search, syslog tail, syslog errors, syslog hosts, syslog sessions,
#   syslog search_sessions, syslog usage_blocks, syslog project_context,
#   syslog list_ai_tools, syslog list_ai_projects, syslog correlate, syslog stats, syslog status, syslog apps,
#   syslog source_ips, syslog timeline, syslog patterns, syslog context,
#   syslog get, syslog ingest_rate, syslog silent_hosts, syslog clock_skew,
#   syslog anomalies, syslog compare, syslog compose_status,
#   syslog compose_doctor, syslog help
#
# Exit codes:
#   0 — all tests passed (SKIPs do not count as failures)
#   1 — one or more tests failed
#   2 — prerequisite check failed or docker build/start failed
#
# Examples:
#   # Docker mode (default — builds image, runs tests, tears down)
#   SYSLOG_MCP_TOKEN=ci-integration-token bash tests/test_live.sh
#
#   # HTTP mode — test an already-running server
#   bash tests/test_live.sh --mode http --url http://192.168.1.10:3100
# =============================================================================

set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
MODE="all"          # all | docker | http
BASE_URL=""         # populated after arg parsing
TOKEN=""            # populated from args or env
VERBOSE=false
PORT="${PORT:-3100}"
CONTAINER_NAME="syslog-mcp-test-$$"
IMAGE_NAME="syslog-mcp-test"

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
declare -a FAIL_NAMES=()

# ---------------------------------------------------------------------------
# Colours (disabled when stdout is not a terminal or NO_COLOR is set)
# ---------------------------------------------------------------------------
if [[ -t 1 && "${NO_COLOR:-}" == "" ]]; then
  C_RESET='\033[0m'
  C_BOLD='\033[1m'
  C_GREEN='\033[0;32m'
  C_RED='\033[0;31m'
  C_YELLOW='\033[0;33m'
  C_CYAN='\033[0;36m'
  C_DIM='\033[2m'
else
  C_RESET='' C_BOLD='' C_GREEN='' C_RED='' C_YELLOW='' C_CYAN='' C_DIM=''
fi

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log_info()  { printf "${C_CYAN}[INFO]${C_RESET}  %s\n" "$*"; }
log_warn()  { printf "${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*"; }
log_error() { printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" >&2; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --mode)
        MODE="${2:?--mode requires a value: docker|http|all}"
        shift 2
        ;;
      --url)
        BASE_URL="${2:?--url requires a value}"
        shift 2
        ;;
      --token)
        TOKEN="${2:?--token requires a value}"
        shift 2
        ;;
      --verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        sed -n '2,30p' "$0" | sed 's/^# \?//'
        exit 0
        ;;
      *)
        log_error "Unknown argument: $1"
        exit 2
        ;;
    esac
  done

  # Normalise "all" → "docker"
  if [[ "${MODE}" == "all" ]]; then
    MODE="docker"
  fi

  # Env var fallback for token
  if [[ -z "${TOKEN}" ]]; then
    TOKEN="${SYSLOG_MCP_TOKEN:-${SYSLOG_MCP_API_TOKEN:-}}"
  fi

  # Default BASE_URL
  if [[ -z "${BASE_URL}" ]]; then
    BASE_URL="http://localhost:${PORT}"
  fi
}

# ---------------------------------------------------------------------------
# Test result helpers
# ---------------------------------------------------------------------------
_pass() {
  local label="$1"
  printf "${C_GREEN}[PASS]${C_RESET} %s\n" "${label}"
  PASS_COUNT=$(( PASS_COUNT + 1 ))
}

_fail() {
  local label="$1"
  local reason="${2:-}"
  printf "${C_RED}[FAIL]${C_RESET} %s\n" "${label}"
  if [[ -n "${reason}" ]]; then
    printf "       %s\n" "${reason}"
  fi
  FAIL_COUNT=$(( FAIL_COUNT + 1 ))
  FAIL_NAMES+=("${label}")
}

_skip() {
  local label="$1"
  local reason="${2:-}"
  printf "${C_YELLOW}[SKIP]${C_RESET} %s" "${label}"
  if [[ -n "${reason}" ]]; then
    printf " — %s" "${reason}"
  fi
  printf '\n'
  SKIP_COUNT=$(( SKIP_COUNT + 1 ))
}

section() {
  printf '\n%b=== %s ===%b\n' "${C_BOLD}" "$*" "${C_RESET}"
}

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
check_prerequisites() {
  local missing=false

  if ! command -v curl &>/dev/null; then
    log_error "curl not found in PATH"
    missing=true
  fi

  if ! command -v jq &>/dev/null; then
    log_error "jq not found in PATH"
    missing=true
  fi

  if [[ "${MODE}" == "docker" ]]; then
    if ! command -v docker &>/dev/null; then
      log_error "docker not found in PATH (required for --mode docker)"
      missing=true
    fi
  fi

  if [[ "${missing}" == "true" ]]; then
    return 2
  fi
}

# ---------------------------------------------------------------------------
# Build auth header array for curl
# Usage: build_auth_args
# Sets AUTH_ARGS global array
# ---------------------------------------------------------------------------
AUTH_ARGS=()
build_auth_args() {
  AUTH_ARGS=()
  if [[ -n "${TOKEN}" ]]; then
    AUTH_ARGS=(-H "Authorization: Bearer ${TOKEN}")
  fi
}

# ---------------------------------------------------------------------------
# Raw MCP JSON-RPC POST
# Usage: mcp_post <json-body>
# Returns raw JSON response on stdout; returns non-zero on curl failure
# ---------------------------------------------------------------------------
mcp_post() {
  local body="$1"
  curl -sf --max-time 15 \
    -X POST "${BASE_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    "${AUTH_ARGS[@]+"${AUTH_ARGS[@]}"}" \
    -d "${body}"
}

# ---------------------------------------------------------------------------
# assert_jq — validate a jq expression on a JSON value
# Usage: assert_jq <label> <json> <jq-expr> [expected-value]
#
# If expected-value is omitted, just checks the expression is not null/false/empty.
# If expected-value is provided, checks the expression equals that string.
# ---------------------------------------------------------------------------
assert_jq() {
  local label="$1"
  local json="$2"
  local expr="$3"
  local expected="${4:-}"

  local actual
  actual="$(printf '%s' "${json}" | jq -r "${expr}" 2>/dev/null)" || actual=""

  if [[ -n "${expected}" ]]; then
    if [[ "${actual}" == "${expected}" ]]; then
      _pass "${label}"
      return 0
    else
      _fail "${label}" "expected '${expected}', got '${actual}'"
      return 1
    fi
  else
    # No expected — just verify not null / not empty string / not "false"
    if [[ -n "${actual}" && "${actual}" != "null" && "${actual}" != "false" ]]; then
      _pass "${label}"
      return 0
    else
      _fail "${label}" "expression '${expr}' returned '${actual}' (null/false/empty)"
      return 1
    fi
  fi
}

# ---------------------------------------------------------------------------
# call_tool — call a tool via MCP JSON-RPC and return the result JSON
# Usage: result=$(call_tool <tool_name> <args_json>)
# The returned JSON is the value of .result.content[0].text (parsed from JSON-in-JSON)
# ---------------------------------------------------------------------------
_req_id=0
call_tool() {
  local tool="$1"
  local args="${2:-{\}}"
  _req_id=$(( _req_id + 1 ))

  local body
  body="$(jq -nc \
    --arg tool "${tool}" \
    --argjson args "${args}" \
    --argjson id "${_req_id}" \
    '{"jsonrpc":"2.0","id":$id,"method":"tools/call","params":{"name":$tool,"arguments":$args}}')"

  local raw
  raw="$(mcp_post "${body}")" || { log_error "curl failed for tool ${tool}"; return 1; }

  if [[ "${VERBOSE}" == "true" ]]; then
    printf '%b[VERBOSE] %s response:%b\n%s\n' "${C_DIM}" "${tool}" "${C_RESET}" "${raw}"
  fi

  # Extract text content (tools return content[0].text as a JSON string)
  local text
  text="$(printf '%s' "${raw}" | jq -r '.result.content[0].text // empty' 2>/dev/null)" || text=""

  if [[ -z "${text}" ]]; then
    # Check if it's an error response
    local err
    err="$(printf '%s' "${raw}" | jq -r '.error.message // .result.content[0].text // "unknown"' 2>/dev/null)"
    log_error "call_tool ${tool}: no text content in response (error: ${err})"
    printf '%s' "${raw}"
    return 1
  fi

  # text itself is a JSON string — parse it
  printf '%s' "${text}"
}

# ---------------------------------------------------------------------------
# Phase 1 — Health check
# ---------------------------------------------------------------------------
phase_health() {
  section "Phase 1 — Health"

  local response
  response="$(curl -sf --max-time 10 \
    -H "Accept: application/json, text/event-stream" \
    "${BASE_URL}/health" 2>/dev/null)" || response=""

  if [[ -z "${response}" ]]; then
    _fail "GET /health returns 200" "curl failed or no response"
    return 1
  fi

  assert_jq "GET /health — status is ok" "${response}" '.status' "ok"
}

# ---------------------------------------------------------------------------
# Phase 2 — Auth enforcement
# ---------------------------------------------------------------------------
phase_auth() {
  section "Phase 2 — Auth"

  if [[ -z "${TOKEN}" ]]; then
    _skip "auth: unauthenticated /mcp returns 401" "SYSLOG_MCP_TOKEN not set — auth assumed disabled"
    _skip "auth: bad token returns 401"             "SYSLOG_MCP_TOKEN not set — auth assumed disabled"
    return 0
  fi

  local status

  # Test: no token → 401
  status="$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" \
    -X POST "${BASE_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' 2>/dev/null)" || status=0

  if [[ "${status}" == "401" ]]; then
    _pass "auth: unauthenticated /mcp returns 401"
  else
    _fail "auth: unauthenticated /mcp returns 401" "got HTTP ${status}"
  fi

  # Test: wrong token → 401
  status="$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" \
    -X POST "${BASE_URL}/mcp" \
    -H "Authorization: Bearer intentionally-wrong-token-for-testing" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' 2>/dev/null)" || status=0

  if [[ "${status}" == "401" ]]; then
    _pass "auth: bad token returns 401"
  else
    _fail "auth: bad token returns 401" "got HTTP ${status}"
  fi
}

# ---------------------------------------------------------------------------
# Phase 3 — Protocol (initialize + tools/list)
# ---------------------------------------------------------------------------
phase_protocol() {
  section "Phase 3 — Protocol"

  local expected_tools=("syslog")

  # initialize
  local init_resp
  init_resp="$(mcp_post '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test_live.sh","version":"1.0.0"}}}')" || init_resp=""

  assert_jq "initialize — protocolVersion present"    "${init_resp}" '.result.protocolVersion'
  assert_jq "initialize — serverInfo.name present"    "${init_resp}" '.result.serverInfo.name'
  assert_jq "initialize — capabilities.tools present" "${init_resp}" '.result.capabilities.tools'

  # tools/list
  local list_resp
  list_resp="$(mcp_post '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}')" || list_resp=""

  local tool_count
  tool_count="$(printf '%s' "${list_resp}" | jq '.result.tools | length' 2>/dev/null)" || tool_count=0

  if [[ "${tool_count}" -eq 1 ]]; then
    _pass "tools/list — returns ${tool_count} tool (expected 1)"
  else
    _fail "tools/list — returns ${tool_count} tools (expected 1)"
  fi

  # Verify each expected tool is present by name
  local tool
  for tool in "${expected_tools[@]}"; do
    local found
    found="$(printf '%s' "${list_resp}" | jq -r --arg name "${tool}" '.result.tools[] | select(.name == $name) | .name' 2>/dev/null)" || found=""
    if [[ "${found}" == "${tool}" ]]; then
      _pass "tools/list — tool '${tool}' present"
    else
      _fail "tools/list — tool '${tool}' present" "not found in tools list"
    fi
  done
}

# ---------------------------------------------------------------------------
# Phase 4 — Tool calls
# ---------------------------------------------------------------------------
phase_tools() {
  section "Phase 4 — Tool calls"

  # --- syslog help ---
  section "  syslog help"
  local help_result
  help_result="$(call_tool syslog '{"action":"help"}')" || help_result=""

  assert_jq "syslog help — help field present"          "${help_result}" '.help'
  assert_jq "syslog help — help text is non-empty"      "${help_result}" '.help | length > 0'
  assert_jq "syslog help — help text contains 'syslog'" "${help_result}" '.help | ascii_downcase | contains("syslog")'

  # --- syslog status ---
  section "  syslog status"
  local status_result
  status_result="$(call_tool syslog '{"action":"status"}')" || status_result=""

  assert_jq "syslog status — status is ok"                    "${status_result}" '.status' "ok"
  assert_jq "syslog status — db_ok field present"             "${status_result}" '.db_ok != null'
  assert_jq "syslog status — runtime_observability present"   "${status_result}" '.runtime_observability'
  assert_jq "syslog status — otlp counters present"           "${status_result}" '.otlp'

  # --- syslog stats ---
  section "  syslog stats"
  local stats_result
  stats_result="$(call_tool syslog '{"action":"stats"}')" || stats_result=""

  assert_jq "syslog stats — total_logs field present"         "${stats_result}" '.total_logs != null'
  assert_jq "syslog stats — total_hosts field present"        "${stats_result}" '.total_hosts != null'
  assert_jq "syslog stats — logical_db_size_mb present"       "${stats_result}" '.logical_db_size_mb'
  assert_jq "syslog stats — physical_db_size_mb present"      "${stats_result}" '.physical_db_size_mb'
  assert_jq "syslog stats — write_blocked field present"      "${stats_result}" '.write_blocked != null'
  assert_jq "syslog stats — total_logs is a number >= 0"      "${stats_result}" '.total_logs >= 0'
  assert_jq "syslog stats — total_hosts is a number >= 0"     "${stats_result}" '.total_hosts >= 0'

  # --- compose diagnostics ---
  section "  syslog compose diagnostics"
  local compose_status_result
  compose_status_result="$(call_tool syslog '{"action":"compose_status"}')" || compose_status_result=""
  assert_jq "syslog compose_status — runtime_state present" "${compose_status_result}" '.runtime_state'
  assert_jq "syslog compose_status — no host working dir leaks" "${compose_status_result}" 'has("compose_working_dir") | not'
  assert_jq "syslog compose_status — no image id leaks" "${compose_status_result}" 'has("image_id") | not'
  local compose_runtime compose_ownership
  compose_runtime="$(printf '%s' "${compose_status_result}" | jq -r '.runtime_state // "unknown"' 2>/dev/null)" || compose_runtime="unknown"
  compose_ownership="$(printf '%s' "${compose_status_result}" | jq -r '.ownership // "unknown"' 2>/dev/null)" || compose_ownership="unknown"
  if [[ "${compose_runtime}" != "docker_unavailable" && "${compose_ownership}" == "compose_owned" ]]; then
    assert_jq "syslog compose_status — ownership known" "${compose_status_result}" '.ownership != "unknown"'
    assert_jq "syslog compose_status — no unsafe diagnostics" "${compose_status_result}" '[.diagnostics[]?.severity] | all(. != "error" and . != "unsafe")'

    local compose_doctor_result
    compose_doctor_result="$(call_tool syslog '{"action":"compose_doctor"}')" || compose_doctor_result=""
    assert_jq "syslog compose_doctor — ownership present" "${compose_doctor_result}" '.ownership'
    assert_jq "syslog compose_doctor — runtime_state present" "${compose_doctor_result}" '.runtime_state'
    assert_jq "syslog compose_doctor — no unsafe diagnostics" "${compose_doctor_result}" '[.diagnostics[]?.severity] | all(. != "error" and . != "unsafe")'
  else
    _skip "syslog compose_status strict diagnostics" "runtime=${compose_runtime}, ownership=${compose_ownership}"
    _skip "syslog compose_doctor strict diagnostics" "runtime=${compose_runtime}, ownership=${compose_ownership}"
  fi

  # --- syslog hosts ---
  section "  syslog hosts"
  local hosts_result
  hosts_result="$(call_tool syslog '{"action":"hosts"}')" || hosts_result=""

  assert_jq "syslog hosts — hosts field is an array"       "${hosts_result}" '.hosts | type' "array"

  # Structure check (only if hosts are present — may be empty in CI with no syslog data)
  local host_count
  host_count="$(printf '%s' "${hosts_result}" | jq '.hosts | length' 2>/dev/null)" || host_count=0

  if [[ "${host_count}" -gt 0 ]]; then
    assert_jq "syslog hosts — entry has hostname field"  "${hosts_result}" '.hosts[0].hostname'
    assert_jq "syslog hosts — entry has log_count field" "${hosts_result}" '.hosts[0].log_count != null'
    assert_jq "syslog hosts — entry has first_seen field" "${hosts_result}" '.hosts[0].first_seen'
    assert_jq "syslog hosts — entry has last_seen field"  "${hosts_result}" '.hosts[0].last_seen'
  else
    _skip "syslog hosts — entry field validation" "no hosts in DB (no syslog data ingested)"
  fi

  # --- syslog sessions ---
  section "  syslog sessions"
  local sessions_result
  sessions_result="$(call_tool syslog '{"action":"sessions","limit":10}')" || sessions_result=""

  assert_jq "syslog sessions — count field present" "${sessions_result}" '.count != null'
  assert_jq "syslog sessions — sessions field is array" "${sessions_result}" '.sessions | type' "array"

  local search_sessions_result
  search_sessions_result="$(call_tool syslog '{"action":"search_sessions","query":"error","limit":10}')" || search_sessions_result=""
  assert_jq "syslog search_sessions — total_candidates present" "${search_sessions_result}" '.total_candidates != null'
  assert_jq "syslog search_sessions — sessions field is array" "${search_sessions_result}" '.sessions | type' "array"

  local usage_blocks_result
  usage_blocks_result="$(call_tool syslog '{"action":"usage_blocks"}')" || usage_blocks_result=""
  assert_jq "syslog usage_blocks — blocks field is array" "${usage_blocks_result}" '.blocks | type' "array"
  assert_jq "syslog usage_blocks — truncated field present" "${usage_blocks_result}" '.truncated != null'

  local project_context_result
  project_context_result="$(call_tool syslog '{"action":"project_context","project":"/tmp","limit":5}')" || project_context_result=""
  assert_jq "syslog project_context — project field present" "${project_context_result}" '.project' "/tmp"
  assert_jq "syslog project_context — recent_entries field is array" "${project_context_result}" '.recent_entries | type' "array"

  local ai_tools_result
  ai_tools_result="$(call_tool syslog '{"action":"list_ai_tools"}')" || ai_tools_result=""
  assert_jq "syslog list_ai_tools — tools field is array" "${ai_tools_result}" '.tools | type' "array"

  local ai_projects_result
  ai_projects_result="$(call_tool syslog '{"action":"list_ai_projects"}')" || ai_projects_result=""
  assert_jq "syslog list_ai_projects — projects field is array" "${ai_projects_result}" '.projects | type' "array"

  # --- syslog search ---
  section "  syslog search"
  local search_result
  search_result="$(call_tool syslog '{"action":"search","query":"error","limit":10}')" || search_result=""

  assert_jq "syslog search — count field present"   "${search_result}" '.count != null'
  assert_jq "syslog search — logs field is array"   "${search_result}" '.logs | type' "array"
  assert_jq "syslog search — count is number >= 0"  "${search_result}" '.count >= 0'

  local log_count
  log_count="$(printf '%s' "${search_result}" | jq '.logs | length' 2>/dev/null)" || log_count=0
  if [[ "${log_count}" -gt 0 ]]; then
    assert_jq "syslog search — log entry has message field"   "${search_result}" '.logs[0].message'
    assert_jq "syslog search — log entry has hostname field"  "${search_result}" '.logs[0].hostname'
    assert_jq "syslog search — log entry has severity field"  "${search_result}" '.logs[0].severity'
    assert_jq "syslog search — log entry has timestamp field" "${search_result}" '.logs[0].timestamp'
  else
    _skip "syslog search — log entry field validation" "no matching logs (empty DB)"
  fi

  # syslog search with no query (list recent)
  local search_noq
  search_noq="$(call_tool syslog '{"action":"search","limit":5}')" || search_noq=""
  assert_jq "syslog search (no query) — count field present" "${search_noq}" '.count != null'
  assert_jq "syslog search (no query) — logs field is array" "${search_noq}" '.logs | type' "array"

  # --- syslog errors ---
  section "  syslog errors"
  local errors_result
  errors_result="$(call_tool syslog '{"action":"errors"}')" || errors_result=""

  assert_jq "syslog errors — summary field is array" "${errors_result}" '.summary | type' "array"

  local err_count
  err_count="$(printf '%s' "${errors_result}" | jq '.summary | length' 2>/dev/null)" || err_count=0
  if [[ "${err_count}" -gt 0 ]]; then
    assert_jq "syslog errors — entry has hostname field" "${errors_result}" '.summary[0].hostname'
    assert_jq "syslog errors — entry has severity field" "${errors_result}" '.summary[0].severity'
    assert_jq "syslog errors — entry has count field"    "${errors_result}" '.summary[0].count != null'
  else
    _skip "syslog errors — entry field validation" "no error-level logs in DB"
  fi

  # --- syslog tail ---
  section "  syslog tail"
  local tail_result
  tail_result="$(call_tool syslog '{"action":"tail","n":10}')" || tail_result=""

  assert_jq "syslog tail — count field present"   "${tail_result}" '.count != null'
  assert_jq "syslog tail — logs field is array"   "${tail_result}" '.logs | type' "array"
  assert_jq "syslog tail — count is number >= 0"  "${tail_result}" '.count >= 0'

  local tail_count
  tail_count="$(printf '%s' "${tail_result}" | jq '.logs | length' 2>/dev/null)" || tail_count=0
  if [[ "${tail_count}" -gt 0 ]]; then
    assert_jq "syslog tail — entry has message field"   "${tail_result}" '.logs[0].message'
    assert_jq "syslog tail — entry has hostname field"  "${tail_result}" '.logs[0].hostname'
    assert_jq "syslog tail — entry has severity field"  "${tail_result}" '.logs[0].severity'
    assert_jq "syslog tail — entry has timestamp field" "${tail_result}" '.logs[0].timestamp'
  else
    _skip "syslog tail — entry field validation" "no logs in DB"
  fi

  # --- syslog correlate ---
  section "  syslog correlate"
  local ref_time
  ref_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  local correlate_result
  correlate_result="$(call_tool syslog \
    "$(jq -nc --arg t "${ref_time}" '{"action":"correlate","reference_time":$t,"window_minutes":5,"severity_min":"debug","limit":50}')")" \
    || correlate_result=""

  assert_jq "syslog correlate — reference_time present"  "${correlate_result}" '.reference_time'
  assert_jq "syslog correlate — window_minutes present"  "${correlate_result}" '.window_minutes != null'
  assert_jq "syslog correlate — window_from present"     "${correlate_result}" '.window_from'
  assert_jq "syslog correlate — window_to present"       "${correlate_result}" '.window_to'
  assert_jq "syslog correlate — hosts field is array"    "${correlate_result}" '.hosts | type' "array"
  assert_jq "syslog correlate — total_events >= 0"       "${correlate_result}" '.total_events >= 0'
  assert_jq "syslog correlate — truncated field present" "${correlate_result}" '.truncated != null'
}

# ---------------------------------------------------------------------------
# Docker mode — build, start, test, teardown
# ---------------------------------------------------------------------------
docker_cleanup() {
  if docker inspect "${CONTAINER_NAME}" &>/dev/null 2>&1; then
    log_info "Removing test container ${CONTAINER_NAME}..."
    docker rm -f "${CONTAINER_NAME}" &>/dev/null || true
  fi
}

run_docker_mode() {
  local project_dir
  project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"

  log_info "Project dir: ${project_dir}"
  log_info "Image:       ${IMAGE_NAME}"
  log_info "Container:   ${CONTAINER_NAME}"

  # Register cleanup on exit
  trap docker_cleanup EXIT INT TERM

  # Build image
  section "Docker — Build"
  log_info "Building Docker image ${IMAGE_NAME}..."
  if ! docker build -f "${project_dir}/config/Dockerfile" -t "${IMAGE_NAME}" "${project_dir}"; then
    log_error "Docker build failed"
    return 2
  fi
  log_info "Docker build succeeded"

  # Start container
  section "Docker — Start"
  local docker_args=(
    "--name" "${CONTAINER_NAME}"
    "--detach"
    "--rm"
    # Expose MCP HTTP port
    "-p" "0:3100"
    # Use a tmpfs for SQLite (no volume needed for CI)
    # uid=1000,gid=1000 matches the 'syslog' user in the container image
    "--tmpfs" "/data:rw,noexec,nosuid,size=64m,uid=1000,gid=1000"
  )

  if [[ -n "${TOKEN}" ]]; then
    docker_args+=("-e" "SYSLOG_MCP_TOKEN=${TOKEN}")
  fi

  # Remove storage budget env vars that conflict with tmpfs size limits
  docker_args+=(
    "-e" "SYSLOG_MCP_MAX_DB_SIZE_MB=0"
    "-e" "SYSLOG_MCP_RECOVERY_DB_SIZE_MB=0"
    "-e" "SYSLOG_MCP_MIN_FREE_DISK_MB=0"
    "-e" "SYSLOG_MCP_RECOVERY_FREE_DISK_MB=0"
  )

  log_info "Starting container..."
  if ! docker run "${docker_args[@]}" "${IMAGE_NAME}"; then
    log_error "docker run failed"
    return 2
  fi

  # Discover the mapped port (since we used -p 0:3100)
  local mapped_port
  mapped_port="$(docker inspect "${CONTAINER_NAME}" \
    --format '{{(index (index .NetworkSettings.Ports "3100/tcp") 0).HostPort}}' 2>/dev/null)" || mapped_port=""

  if [[ -z "${mapped_port}" ]]; then
    log_warn "Could not detect mapped port — falling back to ${PORT}"
    mapped_port="${PORT}"
  fi

  BASE_URL="http://localhost:${mapped_port}"
  log_info "MCP server at ${BASE_URL}"

  # Poll /health until ready (30 attempts × 1s)
  section "Docker — Wait for health"
  local attempt=0
  local max_attempts=30
  while [[ ${attempt} -lt ${max_attempts} ]]; do
    attempt=$(( attempt + 1 ))
    local health_status
    health_status="$(curl -sf --max-time 3 \
      -H "Accept: application/json, text/event-stream" \
      "${BASE_URL}/health" 2>/dev/null | jq -r '.status' 2>/dev/null)" || health_status=""
    if [[ "${health_status}" == "ok" ]]; then
      log_info "Server healthy after ${attempt}s"
      break
    fi
    if [[ ${attempt} -eq ${max_attempts} ]]; then
      log_error "Server did not become healthy after ${max_attempts}s"
      docker logs "${CONTAINER_NAME}" 2>&1 | tail -30
      return 2
    fi
    sleep 1
  done

  # Run all test phases
  build_auth_args
  run_test_phases

  # Print summary (trap handles container cleanup)
  print_summary
}

# ---------------------------------------------------------------------------
# HTTP mode — test against already-running server
# ---------------------------------------------------------------------------
run_http_mode() {
  log_info "HTTP mode — testing against ${BASE_URL}"
  build_auth_args
  run_test_phases
  print_summary
}

# ---------------------------------------------------------------------------
# Run all four test phases
# ---------------------------------------------------------------------------
run_test_phases() {
  phase_health
  phase_auth
  phase_protocol
  phase_tools
}

# ---------------------------------------------------------------------------
# Print final summary
# ---------------------------------------------------------------------------
print_summary() {
  local total=$(( PASS_COUNT + FAIL_COUNT + SKIP_COUNT ))
  printf '\n%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "PASS"  "${C_RESET}" "${C_GREEN}"  "${PASS_COUNT}"  "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "FAIL"  "${C_RESET}" "${C_RED}"    "${FAIL_COUNT}"  "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "SKIP"  "${C_RESET}" "${C_YELLOW}" "${SKIP_COUNT}"  "${C_RESET}"
  printf '%b%-20s%b  %d\n'     "${C_BOLD}" "TOTAL" "${C_RESET}"               "${total}"
  printf '%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"

  if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    printf '\n%bFailed tests:%b\n' "${C_RED}" "${C_RESET}"
    local name
    for name in "${FAIL_NAMES[@]}"; do
      printf '  • %s\n' "${name}"
    done
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_args "$@"

  printf '%b%s%b\n'                 "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"
  printf '%b  syslog-mcp integration tests%b\n' "${C_BOLD}" "${C_RESET}"
  printf '%b  Mode:    %s%b\n'      "${C_BOLD}" "${MODE}" "${C_RESET}"
  printf '%b  URL:     %s%b\n'      "${C_BOLD}" "${BASE_URL}" "${C_RESET}"
  printf '%b  Token:   %s%b\n'      "${C_BOLD}" "${TOKEN:+(set)}" "${C_RESET}"
  printf '%b%s%b\n\n'               "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"

  check_prerequisites || exit 2

  case "${MODE}" in
    docker) run_docker_mode || exit 2 ;;
    http)   run_http_mode              ;;
    *)
      log_error "Unknown mode '${MODE}' — use docker|http|all"
      exit 2
      ;;
  esac

  if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    exit 1
  fi
  exit 0
}

main "$@"
