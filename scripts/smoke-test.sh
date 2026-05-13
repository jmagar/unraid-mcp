#!/usr/bin/env bash
# smoke-test.sh — Live end-to-end smoke test for syslog-mcp
# Tests all MCP actions via mcporter with strict PASS/FAIL validation.
# Exit code 0 = all passed. Exit code 1 = one or more failures.
#
# Usage:
#   bash scripts/smoke-test.sh [--url http://host:3100/mcp]
#   bash scripts/smoke-test.sh --skip-seed   # if data already exists
#
# Requirements: mcporter, nc, curl, python3
#
# Action inventory reference:
#   mcp_call search, mcp_call tail, mcp_call errors, mcp_call hosts,
#   mcp_call sessions, mcp_call search_sessions, mcp_call usage_blocks,
#   mcp_call project_context, mcp_call list_ai_tools, mcp_call list_ai_projects,
#   mcp_call correlate, mcp_call stats, mcp_call status, mcp_call apps,
#   mcp_call source_ips, mcp_call timeline, mcp_call patterns, mcp_call context,
#   mcp_call get, mcp_call ingest_rate, mcp_call silent_hosts,
#   mcp_call clock_skew, mcp_call anomalies, mcp_call compare,
#   mcp_call compose_status, mcp_call compose_doctor, mcp_call help

set -euo pipefail

# ─── Config ──────────────────────────────────────────────────────────────────
MCP_URL="${SYSLOG_MCP_URL:-http://localhost:3100/mcp}"
HEALTH_URL="${MCP_URL%/mcp}/health"
SYSLOG_HOST="${SYSLOG_HOST:-127.0.0.1}"
SYSLOG_PORT="${SYSLOG_PORT:-1514}"
SKIP_SEED=0
MCPORTER_CONFIG="config/mcporter.json"
_MCPORTER_CONFIG_TMPFILE=""
SEED_HOST="smoke-test-host"
GHOST_HOST="nonexistent-host-xyz-404"
RUN_ID="${SYSLOG_SMOKE_RUN_ID:-$(date -u +%Y%m%d%H%M%S)}"
TCP_MARKER="smoketcp${RUN_ID}"

trap '[[ -n "$_MCPORTER_CONFIG_TMPFILE" ]] && rm -f "$_MCPORTER_CONFIG_TMPFILE"' EXIT

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            [[ -z "${2:-}" ]] && { echo "Error: --url requires a value"; exit 1; }
            MCP_URL="$2"; HEALTH_URL="${MCP_URL%/mcp}/health"; shift 2
            _MCPORTER_CONFIG_TMPFILE=$(mktemp /tmp/mcporter-XXXXXX.json)
            printf '{"mcpServers":{"syslog":{"url":"%s","transport":"http"}}}' "$MCP_URL" > "$_MCPORTER_CONFIG_TMPFILE"
            MCPORTER_CONFIG="$_MCPORTER_CONFIG_TMPFILE"
            ;;
        --skip-seed) SKIP_SEED=1; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# ─── Helpers ─────────────────────────────────────────────────────────────────
PASS=0
FAIL=0
SKIP=0
ERRORS=()

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'

pass() { echo -e "${COLOR_GREEN}PASS${COLOR_RESET}  $1"; (( PASS++ )) || true; }
fail() { echo -e "${COLOR_RED}FAIL${COLOR_RESET}  $1"; ERRORS+=("$1"); (( FAIL++ )) || true; }
skip() { echo "SKIP  $1"; (( SKIP++ )) || true; }

mcp_call() {
    local action="$1"; shift
    mcporter call --config "$MCPORTER_CONFIG" "syslog.syslog" "action=${action}" "$@" 2>&1
}

json_get() {
    local json="$1" field="$2"
    echo "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d$field)" 2>/dev/null
}

assert_eq() {
    local label="$1" actual="$2" expected="$3"
    if [[ "$actual" == "$expected" ]]; then
        pass "$label"
    else
        fail "$label (expected '$expected', got '$actual')"
    fi
}

assert_gte() {
    local label="$1" actual="$2" min="$3"
    if python3 -c "exit(0 if int('$actual') >= $min else 1)" 2>/dev/null; then
        pass "$label"
    else
        fail "$label (expected >= $min, got '$actual')"
    fi
}

assert_no_error() {
    local label="$1" output="$2"
    if echo "$output" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    sys.exit(1 if d.get('isError') else 0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        pass "$label"
    else
        local detail
        detail=$(echo "$output" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    content = d.get('content', [])
    print(content[0].get('text','')[:120] if content else '')
except Exception:
    print(sys.stdin.read()[:120])
" 2>/dev/null)
        fail "$label (isError=true: $detail)"
    fi
}

assert_is_error() {
    local label="$1" output="$2"
    if echo "$output" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    sys.exit(0 if d.get('isError') else 1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        pass "$label"
    elif echo "$output" | grep -q "^\[mcporter\] MCP error -32602:"; then
        pass "$label"
    else
        fail "$label (expected tool isError=true or MCP invalid-params error)"
    fi
}

send_tcp_seed() {
    local message="$1"
    if printf '%s\n' "$message" | nc -w2 -N "$SYSLOG_HOST" "$SYSLOG_PORT" >/dev/null 2>&1; then
        return 0
    fi
    printf '%s\n' "$message" | nc -w2 "$SYSLOG_HOST" "$SYSLOG_PORT" >/dev/null
}

# ─── Phase 1: Pre-flight ─────────────────────────────────────────────────────
echo ""
echo -e "${COLOR_BOLD}=== syslog-mcp smoke test ===${COLOR_RESET}"
echo "MCP URL: $MCP_URL"
echo ""

echo -e "${COLOR_BOLD}[1/4] Pre-flight checks${COLOR_RESET}"

HEALTH=$(curl -sf "$HEALTH_URL" 2>&1) || { echo -e "${COLOR_RED}ABORT${COLOR_RESET}  Health endpoint unreachable: $HEALTH_URL"; exit 1; }
HEALTH_STATUS=$(json_get "$HEALTH" "['status']")
assert_eq "Health endpoint responds with ok" "$HEALTH_STATUS" "ok"

TOOL_LIST=$(mcporter list syslog --config "$MCPORTER_CONFIG" 2>&1)
TOOL_COUNT=$(echo "$TOOL_LIST" | grep -c "^  function " || true)
assert_eq "mcporter lists exactly 1 tool (syslog)" "$TOOL_COUNT" "1"

# ─── Phase 2: Seed test data ─────────────────────────────────────────────────
echo ""
echo -e "${COLOR_BOLD}[2/4] Seeding test data${COLOR_RESET}"

if [[ "$SKIP_SEED" -eq 0 ]]; then
    printf '<14>%s %s sshd[42]: smoke-test: info message\n'           "$(date '+%b %e %H:%M:%S')" "$SEED_HOST" | nc -u -w1 "$SYSLOG_HOST" "$SYSLOG_PORT"
    printf '<11>%s %s sshd[42]: smoke-test: error authentication failure\n' "$(date '+%b %e %H:%M:%S')" "$SEED_HOST" | nc -u -w1 "$SYSLOG_HOST" "$SYSLOG_PORT"
    printf '<2>%s %s kernel: smoke-test: crit memory allocation failed\n'    "$(date '+%b %e %H:%M:%S')" "$SEED_HOST" | nc -u -w1 "$SYSLOG_HOST" "$SYSLOG_PORT"
    printf '<12>%s %s dockerd[99]: smoke-test: warning container restart\n'  "$(date '+%b %e %H:%M:%S')" "$SEED_HOST" | nc -u -w1 "$SYSLOG_HOST" "$SYSLOG_PORT"
    send_tcp_seed "<14>$(date '+%b %e %H:%M:%S') ${SEED_HOST} tcpsmoke[77]: smoke-test tcp seed ${TCP_MARKER} bounded frame ok"
    sleep 2
    echo "Seeded 5 messages (4 UDP, 1 TCP) from $SEED_HOST; TCP marker=$TCP_MARKER"
else
    echo "Skipping seed (--skip-seed)"
fi

STATS_PREFLIGHT=$(mcp_call stats 2>&1)
TOTAL_PREFLIGHT=$(json_get "$STATS_PREFLIGHT" "['total_logs']")
if python3 -c "exit(0 if int('${TOTAL_PREFLIGHT:-0}') >= 1 else 1)" 2>/dev/null; then
    echo "DB has $TOTAL_PREFLIGHT logs — proceeding"
else
    echo -e "${COLOR_RED}ABORT${COLOR_RESET}  No logs in DB. Seed failed or server just started."
    exit 1
fi

# ─── Phase 3: Action tests ───────────────────────────────────────────────────
echo ""
echo -e "${COLOR_BOLD}[3/4] Action tests${COLOR_RESET}"

# ── status ────────────────────────────────────────────────────────────────────
echo ""
echo "Action: status"
STATUS=$(mcp_call status 2>&1)
assert_no_error "status: no error" "$STATUS"

STATUS_VALUE=$(json_get "$STATUS" "['status']")
STATUS_DB_OK=$(json_get "$STATUS" "['db_ok']")
STATUS_OBS=$(json_get "$STATUS" "['runtime_observability']['ingest_queue_depth']")
STATUS_OTLP=$(json_get "$STATUS" "['otlp']['logs_received']")
assert_eq "status: status is ok" "$STATUS_VALUE" "ok"
assert_eq "status: db_ok is true" "$STATUS_DB_OK" "True"
[[ -n "$STATUS_OBS" ]] \
    && pass "status: runtime_observability present" \
    || fail "status: runtime_observability missing"
[[ -n "$STATUS_OTLP" ]] \
    && pass "status: otlp counters present" \
    || fail "status: otlp counters missing"

# ── stats ─────────────────────────────────────────────────────────────────────
echo ""
echo "Action: stats"
STATS=$(mcp_call stats 2>&1)
assert_no_error "stats: no error" "$STATS"

STATS_TOTAL=$(json_get "$STATS" "['total_logs']")
STATS_HOSTS=$(json_get "$STATS" "['total_hosts']")
STATS_SIZE=$(json_get "$STATS" "['logical_db_size_mb']")
STATS_BLOCKED=$(json_get "$STATS" "['write_blocked']")
assert_gte  "stats: total_logs >= 1" "$STATS_TOTAL" 1
assert_gte  "stats: total_hosts >= 1" "$STATS_HOSTS" 1
[[ -n "$STATS_SIZE" ]] \
    && pass "stats: logical_db_size_mb present ('$STATS_SIZE')" \
    || fail "stats: logical_db_size_mb missing"
assert_eq   "stats: write_blocked is false (DB healthy)" "$STATS_BLOCKED" "False"

# ── hosts ─────────────────────────────────────────────────────────────────────
echo ""
echo "Action: hosts"
HOSTS=$(mcp_call hosts 2>&1)
assert_no_error "hosts: no error" "$HOSTS"

HOSTS_COUNT=$(echo "$HOSTS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['hosts']))" 2>/dev/null || echo "0")
assert_gte "hosts: at least 1 host" "$HOSTS_COUNT" 1

# All records have required fields and non-zero log counts
HOSTS_VALID=$(echo "$HOSTS" | python3 -c "
import sys, json
for h in json.load(sys.stdin)['hosts']:
    assert h.get('hostname'), 'hostname missing or empty'
    assert 'log_count' in h, 'log_count missing'
    assert h['log_count'] > 0, f'log_count=0 for {h[\"hostname\"]}'
    assert 'first_seen' in h, 'first_seen missing'
    assert 'last_seen' in h, 'last_seen missing'
print('ok')
" 2>&1)
assert_eq "hosts: all records have required fields and log_count > 0" "$HOSTS_VALID" "ok"

if [[ "$SKIP_SEED" -eq 0 ]]; then
    # Verify the seeded host actually appears by name
    SEED_HOST_FOUND=$(echo "$HOSTS" | python3 -c "
import sys, json
hosts = [h['hostname'] for h in json.load(sys.stdin)['hosts']]
print('ok' if '${SEED_HOST}' in hosts else f'missing: {hosts}')
" 2>/dev/null || echo "error")
    assert_eq "hosts: seeded host '$SEED_HOST' appears in list" "$SEED_HOST_FOUND" "ok"
fi

# ── sessions ──────────────────────────────────────────────────────────────────
echo ""
echo "Action: sessions"
SESSIONS=$(mcp_call sessions "limit=10" 2>&1)
assert_no_error "sessions: no error" "$SESSIONS"

SESSIONS_VALID=$(echo "$SESSIONS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'count' in d, 'count missing'
assert isinstance(d['sessions'], list), 'sessions not a list'
for s in d['sessions']:
    assert s.get('project'), 'project missing'
    assert s.get('tool'), 'tool missing'
    assert s.get('session_id'), 'session_id missing'
    assert s.get('hostname'), 'hostname missing'
    assert 'first_seen' in s, 'first_seen missing'
    assert 'last_seen' in s, 'last_seen missing'
    assert s.get('event_count', 0) >= 1, 'event_count < 1'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "sessions: response structure valid" "$SESSIONS_VALID" "ok"

echo ""
echo "Action: AI session analytics"
SEARCH_SESSIONS=$(mcp_call search_sessions "query=authentication" "limit=10" 2>&1)
assert_no_error "search_sessions: no error" "$SEARCH_SESSIONS"
SEARCH_SESSIONS_VALID=$(echo "$SEARCH_SESSIONS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'total_candidates' in d, 'total_candidates missing'
assert isinstance(d.get('sessions'), list), 'sessions not a list'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "search_sessions: response structure valid" "$SEARCH_SESSIONS_VALID" "ok"

USAGE_BLOCKS=$(mcp_call usage_blocks 2>&1)
assert_no_error "usage_blocks: no error" "$USAGE_BLOCKS"
USAGE_BLOCKS_VALID=$(echo "$USAGE_BLOCKS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert isinstance(d.get('blocks'), list), 'blocks not a list'
assert 'truncated' in d, 'truncated missing'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "usage_blocks: response structure valid" "$USAGE_BLOCKS_VALID" "ok"

PROJECT_CONTEXT=$(mcp_call project_context "project=/tmp" "limit=5" 2>&1)
assert_no_error "project_context: no error" "$PROJECT_CONTEXT"
PROJECT_CONTEXT_VALID=$(echo "$PROJECT_CONTEXT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('project') == '/tmp', 'project mismatch'
assert isinstance(d.get('recent_entries'), list), 'recent_entries not a list'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "project_context: response structure valid" "$PROJECT_CONTEXT_VALID" "ok"

AI_TOOLS=$(mcp_call list_ai_tools 2>&1)
assert_no_error "list_ai_tools: no error" "$AI_TOOLS"
AI_TOOLS_VALID=$(echo "$AI_TOOLS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert isinstance(d.get('tools'), list), 'tools not a list'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "list_ai_tools: response structure valid" "$AI_TOOLS_VALID" "ok"

AI_PROJECTS=$(mcp_call list_ai_projects 2>&1)
assert_no_error "list_ai_projects: no error" "$AI_PROJECTS"
AI_PROJECTS_VALID=$(echo "$AI_PROJECTS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert isinstance(d.get('projects'), list), 'projects not a list'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "list_ai_projects: response structure valid" "$AI_PROJECTS_VALID" "ok"

# ── tail ──────────────────────────────────────────────────────────────────────
echo ""
echo "Action: tail"
TAIL=$(mcp_call tail "n=10" 2>&1)
assert_no_error "tail: no error" "$TAIL"

TAIL_COUNT=$(echo "$TAIL" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
assert_gte "tail: returns >= 1 log" "$TAIL_COUNT" 1

TAIL_VALID=$(echo "$TAIL" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'no logs'
for l in logs:
    assert l.get('id'), 'id missing'
    assert l.get('hostname'), 'hostname missing'
    assert l.get('severity'), 'severity missing'
    assert 'message' in l, 'message missing'
    assert l.get('timestamp'), 'timestamp missing'
print('ok')
" 2>&1)
assert_eq "tail: log entries have required fields" "$TAIL_VALID" "ok"

# Results must be in non-increasing timestamp order (most recent first)
TAIL_ORDER=$(echo "$TAIL" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
for i in range(1, len(logs)):
    if logs[i]['timestamp'] > logs[i-1]['timestamp']:
        print(f'not_descending at index {i}'); sys.exit(0)
print('ok')
" 2>/dev/null || echo "error")
assert_eq "tail: results in non-increasing timestamp order" "$TAIL_ORDER" "ok"

if [[ "$SKIP_SEED" -eq 0 ]]; then
    # hostname= filter must only return logs for that host
    TAIL_FILTERED=$(mcp_call tail "hostname=${SEED_HOST}" "n=50" 2>&1)
    assert_no_error "tail(hostname filter): no error" "$TAIL_FILTERED"
    TAIL_FILTER_VALID=$(echo "$TAIL_FILTERED" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'no logs returned for seeded host'
wrong = [l['hostname'] for l in logs if l['hostname'] != '${SEED_HOST}']
assert not wrong, f'hostname filter leaked other hosts: {wrong}'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "tail(hostname filter): only returns logs for '$SEED_HOST'" "$TAIL_FILTER_VALID" "ok"

    TAIL_TCP_MARKER=$(echo "$TAIL_FILTERED" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
matches = [l for l in logs if '${TCP_MARKER}' in (l.get('message') or '')]
assert matches, 'TCP seed marker not present in tail(hostname filter)'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "tail(hostname filter): TCP seed marker appears" "$TAIL_TCP_MARKER" "ok"
fi

# ── search ────────────────────────────────────────────────────────────────────
echo ""
echo "Action: search"

# FTS5 keyword search — results must actually contain the query term
SEARCH=$(mcp_call search "query=authentication" "limit=50" 2>&1)
assert_no_error "search(query=authentication): no error" "$SEARCH"
SEARCH_COUNT=$(echo "$SEARCH" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
assert_gte "search(query=authentication): returns >= 1 result" "$SEARCH_COUNT" 1
SEARCH_MATCH=$(echo "$SEARCH" | python3 -c "
import sys, json
for l in json.load(sys.stdin)['logs']:
    if 'authentication' not in (l.get('message') or '').lower():
        print(f'result missing query term: {l[\"message\"][:80]}'); sys.exit(0)
print('ok')
" 2>/dev/null || echo "error")
assert_eq "search(query=authentication): all results contain query term" "$SEARCH_MATCH" "ok"

# Phrase search
SEARCH_PHRASE=$(mcp_call search 'query="authentication failure"' "limit=10" 2>&1)
assert_no_error "search(phrase): no error" "$SEARCH_PHRASE"
PHRASE_MATCH=$(echo "$SEARCH_PHRASE" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'phrase search returned no results'
for l in logs:
    if 'authentication failure' not in (l.get('message') or '').lower():
        print(f'phrase not found in: {l[\"message\"][:80]}'); sys.exit(0)
print('ok')
" 2>/dev/null || echo "error")
assert_eq "search(phrase): results contain exact phrase" "$PHRASE_MATCH" "ok"

if [[ "$SKIP_SEED" -eq 0 ]]; then
    # hostname= filter: should return only that host's logs
    SEARCH_HOST=$(mcp_call search "hostname=${SEED_HOST}" "limit=50" 2>&1)
    assert_no_error "search(hostname filter): no error" "$SEARCH_HOST"
    SEARCH_HOST_VALID=$(echo "$SEARCH_HOST" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'hostname filter returned no logs for seeded host'
wrong = [l['hostname'] for l in logs if l['hostname'] != '${SEED_HOST}']
assert not wrong, f'hostname filter leaked other hosts: {wrong}'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "search(hostname filter): only returns logs for '$SEED_HOST'" "$SEARCH_HOST_VALID" "ok"

    # severity= filter: warning should only return warning-level logs
    SEARCH_SEV=$(mcp_call search "hostname=${SEED_HOST}" "severity=warning" "limit=50" 2>&1)
    assert_no_error "search(severity filter): no error" "$SEARCH_SEV"
    SEARCH_SEV_VALID=$(echo "$SEARCH_SEV" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'severity filter returned no warning logs'
wrong = [l['severity'] for l in logs if l['severity'] != 'warning']
assert not wrong, f'severity filter leaked wrong levels: {set(wrong)}'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "search(severity filter): only returns warning-level logs" "$SEARCH_SEV_VALID" "ok"

    SEARCH_TCP=$(mcp_call search "query=${TCP_MARKER}" "hostname=${SEED_HOST}" "limit=10" 2>&1)
    assert_no_error "search(TCP seed marker): no error" "$SEARCH_TCP"
    SEARCH_TCP_VALID=$(echo "$SEARCH_TCP" | python3 -c "
import sys, json
logs = json.load(sys.stdin)['logs']
assert logs, 'TCP seed marker search returned no logs'
for l in logs:
    assert l['hostname'] == '${SEED_HOST}', f'wrong hostname: {l[\"hostname\"]}'
    assert '${TCP_MARKER}' in (l.get('message') or ''), 'marker missing from result'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "search(TCP seed marker): returns TCP-ingested message" "$SEARCH_TCP_VALID" "ok"
fi

# Nonexistent hostname must return 0 results (filter is not ignored)
SEARCH_GHOST=$(mcp_call search "hostname=${GHOST_HOST}" "limit=10" 2>&1)
assert_no_error "search(nonexistent hostname): no error" "$SEARCH_GHOST"
GHOST_COUNT=$(echo "$SEARCH_GHOST" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "-1")
assert_eq "search(nonexistent hostname): returns 0 results" "$GHOST_COUNT" "0"

# limit=0 edge case
SEARCH_ZERO=$(mcp_call search "limit=0" 2>&1)
assert_no_error "search(limit=0): no error" "$SEARCH_ZERO"
ZERO_COUNT=$(echo "$SEARCH_ZERO" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "-1")
assert_eq "search(limit=0): returns 0 results" "$ZERO_COUNT" "0"

# ── errors ────────────────────────────────────────────────────────────────────
echo ""
echo "Action: errors"
ERRORS_OUT=$(mcp_call errors 2>&1)
assert_no_error "errors: no error" "$ERRORS_OUT"

# Structure + severity values are valid
ERRORS_VALID=$(echo "$ERRORS_OUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'summary' in d and isinstance(d['summary'], list), 'summary missing or not a list'
valid_severities = {'emerg', 'alert', 'crit', 'err', 'warning'}
for item in d['summary']:
    assert item.get('hostname'), 'hostname missing'
    assert item.get('severity') in valid_severities, f'unexpected severity: {item.get(\"severity\")}'
    assert item.get('count', 0) >= 1, 'count must be >= 1'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "errors: summary structure and severity values valid" "$ERRORS_VALID" "ok"

# Info-level logs must NOT appear in error summary
INFO_IN_ERRORS=$(echo "$ERRORS_OUT" | python3 -c "
import sys, json
info_rows = [i for i in json.load(sys.stdin)['summary'] if i['severity'] in ('info','debug','notice')]
print('ok' if not info_rows else f'info/debug/notice leaked: {info_rows}')
" 2>/dev/null || echo "error")
assert_eq "errors: info/debug/notice levels absent from summary" "$INFO_IN_ERRORS" "ok"

ERRORS_COUNT=$(echo "$ERRORS_OUT" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['summary']))" 2>/dev/null || echo "0")
assert_gte "errors: at least 1 error group" "$ERRORS_COUNT" 1

if [[ "$SKIP_SEED" -eq 0 ]]; then
    # Seeded host must appear with err, crit, and warning entries
    SEED_IN_ERRORS=$(echo "$ERRORS_OUT" | python3 -c "
import sys, json
rows = json.load(sys.stdin)['summary']
host_rows = [r for r in rows if r['hostname'] == '${SEED_HOST}']
assert host_rows, 'seeded host not found in errors summary'
severities = {r['severity'] for r in host_rows}
for expected in ('err', 'crit', 'warning'):
    assert expected in severities, f'{expected} missing from seeded host rows (got {severities})'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "errors: seeded host present with err/crit/warning entries" "$SEED_IN_ERRORS" "ok"
fi

# ── correlate ─────────────────────────────────────────────────────────────────
echo ""
echo "Action: correlate"
REF_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CORRELATE=$(mcp_call correlate "reference_time=$REF_TIME" "window_minutes=30" 2>&1)
assert_no_error "correlate: no error" "$CORRELATE"

CORRELATE_VALID=$(echo "$CORRELATE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for field in ('reference_time', 'window_minutes', 'total_events', 'hosts', 'window_from', 'window_to', 'truncated'):
    assert field in d, f'{field} missing'
assert isinstance(d['hosts'], list), 'hosts not a list'
for h in d['hosts']:
    assert h.get('hostname'), 'hostname missing'
    assert 'event_count' in h, 'event_count missing'
    assert h['event_count'] > 0, 'event_count=0'
    assert isinstance(h.get('events'), list), 'events not a list'
    for e in h['events']:
        assert e.get('id'), 'event id missing'
        assert e.get('severity'), 'event severity missing'
        assert e.get('timestamp'), 'event timestamp missing'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "correlate: response structure valid" "$CORRELATE_VALID" "ok"

# window_minutes must be echoed back correctly
CORRELATE_WINDOW=$(json_get "$CORRELATE" "['window_minutes']")
assert_eq "correlate: window_minutes echoed back as 30" "$CORRELATE_WINDOW" "30"

CORRELATE_EVENTS=$(echo "$CORRELATE" | python3 -c "import sys,json; print(json.load(sys.stdin)['total_events'])" 2>/dev/null || echo "0")
assert_gte "correlate: found events in 30-minute window" "$CORRELATE_EVENTS" 1

if [[ "$SKIP_SEED" -eq 0 ]]; then
    SEED_IN_CORRELATE=$(echo "$CORRELATE" | python3 -c "
import sys, json
hosts = [h['hostname'] for h in json.load(sys.stdin)['hosts']]
print('ok' if '${SEED_HOST}' in hosts else f'missing (got {hosts})')
" 2>/dev/null || echo "error")
    assert_eq "correlate: seeded host '$SEED_HOST' appears in window" "$SEED_IN_CORRELATE" "ok"
fi

# Missing required arg must return an error
CORRELATE_NO_REF=$(mcp_call correlate 2>&1 || true)
assert_is_error "correlate(missing reference_time): returns error" "$CORRELATE_NO_REF"

# ── compose diagnostics ───────────────────────────────────────────────────────
echo ""
echo "Action: compose_status"
COMPOSE_STATUS=$(mcp_call compose_status 2>&1)
assert_no_error "compose_status: no error" "$COMPOSE_STATUS"
COMPOSE_STATUS_VALID=$(echo "$COMPOSE_STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for key in ('container_name', 'ownership', 'runtime_state', 'published_ports', 'diagnostics'):
    assert key in d, f'{key} missing'
text = json.dumps(d)
assert 'compose_working_dir' not in text, 'host working dir leaked'
assert 'image_id' not in text, 'image id leaked'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "compose_status: redacted safe response valid" "$COMPOSE_STATUS_VALID" "ok"
COMPOSE_STATUS_DOCTORABLE=$(echo "$COMPOSE_STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('yes' if d.get('runtime_state') != 'docker_unavailable' and d.get('ownership') == 'compose_owned' else 'no')
" 2>/dev/null || echo "no")

echo ""
echo "Action: compose_doctor"
if [[ "$COMPOSE_STATUS_DOCTORABLE" == "yes" ]]; then
    COMPOSE_DOCTOR=$(mcp_call compose_doctor 2>&1)
    assert_no_error "compose_doctor: no error" "$COMPOSE_DOCTOR"
    COMPOSE_DOCTOR_VALID=$(echo "$COMPOSE_DOCTOR" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for key in ('container_name', 'ownership', 'runtime_state'):
    assert key in d, f'{key} missing'
print('ok')
" 2>/dev/null || echo "error")
    assert_eq "compose_doctor: safe response valid" "$COMPOSE_DOCTOR_VALID" "ok"
else
    skip "compose_doctor: deployment is not doctorable from compose_status"
fi

# ── help ──────────────────────────────────────────────────────────────────────
echo ""
echo "Action: help"
HELP=$(mcp_call help 2>&1)
assert_no_error "help: no error" "$HELP"
HELP_VALID=$(echo "$HELP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'help' in d, 'help key missing'
text = d['help']
assert len(text) > 100, 'help text suspiciously short'
for section in ('search', 'tail', 'errors', 'hosts', 'sessions', 'correlate', 'stats', 'status'):
    assert section in text.lower(), f'help text missing section: {section}'
print('ok')
" 2>/dev/null || echo "error")
assert_eq "help: contains all action sections" "$HELP_VALID" "ok"

# ── invalid action (negative test) ───────────────────────────────────────────
echo ""
echo "Negative tests"
INVALID=$(mcp_call notanaction 2>&1 || true)
assert_is_error "invalid action: returns error" "$INVALID"

# ─── OAuth discovery endpoints (unconditional — no Google creds needed) ─────
echo ""
echo "OAuth discovery endpoints"
OAUTH_BASE="${MCP_URL%/mcp}"
DISCOVERY=$(curl -s -o /dev/null -w "%{http_code}" "$OAUTH_BASE/.well-known/oauth-authorization-server")
if [ "$DISCOVERY" = "200" ]; then
    echo "PASS: OAuth discovery endpoint reachable (/.well-known/oauth-authorization-server)"
    PASS=$((PASS + 1))
    JWKS=$(curl -s -o /dev/null -w "%{http_code}" "$OAUTH_BASE/jwks")
    if [ "$JWKS" = "200" ]; then
        echo "PASS: /jwks reachable"
        PASS=$((PASS + 1))
    else
        echo "WARN: /jwks returned $JWKS (expected 200 when OAuth mounted)"
        FAIL=$((FAIL + 1))
        ERRORS+=("/jwks returned $JWKS")
    fi
else
    echo "INFO: OAuth not enabled (/.well-known returned $DISCOVERY) — skipping OAuth endpoint checks"
fi

# ─── Phase 4: Summary ────────────────────────────────────────────────────────
echo ""
echo -e "${COLOR_BOLD}[4/4] Results${COLOR_RESET}"
echo "─────────────────────────────────────"
TOTAL=$((PASS + FAIL))
echo -e "  Passed:  ${COLOR_GREEN}${PASS}${COLOR_RESET} / ${TOTAL}"
echo -e "  Failed:  ${COLOR_RED}${FAIL}${COLOR_RESET} / ${TOTAL}"
echo "  Skipped: ${SKIP}"

if [[ ${#ERRORS[@]} -gt 0 ]]; then
    echo ""
    echo -e "${COLOR_RED}Failures:${COLOR_RESET}"
    for e in "${ERRORS[@]}"; do
        echo "  - $e"
    done
fi

echo ""
if [[ $FAIL -eq 0 ]]; then
    echo -e "${COLOR_GREEN}${COLOR_BOLD}ALL TESTS PASSED${COLOR_RESET}"
    exit 0
else
    echo -e "${COLOR_RED}${COLOR_BOLD}SMOKE TEST FAILED — $FAIL test(s) failed${COLOR_RESET}"
    exit 1
fi
