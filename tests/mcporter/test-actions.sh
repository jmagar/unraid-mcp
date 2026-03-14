#!/usr/bin/env bash
# test-actions.sh — Test all non-destructive Unraid MCP actions via mcporter
#
# Usage:
#   ./scripts/test-actions.sh [MCP_URL]
#
# Default MCP_URL: http://localhost:6970/mcp
# Skips: destructive (confirm=True required), state-changing mutations,
#        and actions requiring IDs not yet discovered.
#
# Phase 1: param-free reads
# Phase 2: ID-discovered reads (container, network, disk, vm, key, log)

set -euo pipefail

MCP_URL="${1:-${UNRAID_MCP_URL:-http://localhost:6970/mcp}}"

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

PASS=0; FAIL=0; SKIP=0
declare -a FAILED_TESTS=()

# ── helpers ───────────────────────────────────────────────────────────────────

mcall() {
    # mcall <tool> <json-args>
    local tool="$1" args="$2"
    mcporter call \
        --http-url "$MCP_URL" \
        --allow-http \
        --tool "$tool" \
        --args "$args" \
        --output json \
        2>&1
}

_check_output() {
    # Returns 0 if output looks like a successful JSON response, 1 otherwise.
    local output="$1" exit_code="$2"
    [[ $exit_code -ne 0 ]] && return 1
    echo "$output" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if isinstance(d, dict) and (d.get('isError') or d.get('error') or 'ToolError' in str(d)):
        sys.exit(1)
except Exception:
    pass
sys.exit(0)
" 2>/dev/null
}

run_test() {
    # Print result; do NOT echo the JSON body (kept quiet for readability).
    local label="$1" tool="$2" args="$3"
    printf "  %-60s" "$label"
    local output exit_code=0
    output=$(mcall "$tool" "$args" 2>&1) || exit_code=$?
    if _check_output "$output" "$exit_code"; then
        echo -e "${GREEN}PASS${NC}"
        ((PASS++)) || true
    else
        echo -e "${RED}FAIL${NC}"
        ((FAIL++)) || true
        FAILED_TESTS+=("$label")
        # Show first 3 lines of error detail, indented
        echo "$output" | head -3 | sed 's/^/      /'
    fi
}

run_test_capture() {
    # Like run_test but echoes raw JSON to stdout for ID extraction by caller.
    # Status lines go to stderr so the caller's $() captures only clean JSON.
    local label="$1" tool="$2" args="$3"
    local output exit_code=0
    printf "  %-60s" "$label" >&2
    output=$(mcall "$tool" "$args" 2>&1) || exit_code=$?
    if _check_output "$output" "$exit_code"; then
        echo -e "${GREEN}PASS${NC}" >&2
        ((PASS++)) || true
    else
        echo -e "${RED}FAIL${NC}" >&2
        ((FAIL++)) || true
        FAILED_TESTS+=("$label")
        echo "$output" | head -3 | sed 's/^/      /' >&2
    fi
    echo "$output"   # pure JSON → captured by caller's $()
}

extract_id() {
    # Extract an ID from JSON output using a Python snippet.
    # Usage: ID=$(extract_id "$JSON_OUTPUT" "$LABEL" 'python expression')
    # If JSON parsing fails (malformed mcporter output), record a FAIL.
    # If parsing succeeds but finds no items, return empty (caller skips).
    local json_input="$1" label="$2" py_code="$3"
    local result="" py_exit=0 parse_err=""
    # Capture stdout (the extracted ID) and stderr (any parse errors) separately.
    # A temp file is needed because $() can only capture one stream.
    local errfile
    errfile=$(mktemp)
    result=$(echo "$json_input" | python3 -c "$py_code" 2>"$errfile") || py_exit=$?
    parse_err=$(<"$errfile")
    rm -f "$errfile"
    if [[ $py_exit -ne 0 ]]; then
        printf "  %-60s${RED}FAIL${NC} (JSON parse error)\n" "$label" >&2
        [[ -n "$parse_err" ]] && echo "$parse_err" | head -2 | sed 's/^/      /' >&2
        ((FAIL++)) || true
        FAILED_TESTS+=("$label (JSON parse)")
        echo ""
        return 1
    fi
    echo "$result"
}

skip_test() {
    local label="$1" reason="$2"
    printf "  %-60s${YELLOW}SKIP${NC} (%s)\n" "$label" "$reason"
    ((SKIP++)) || true
}

section() {
    echo ""
    echo -e "${CYAN}${BOLD}━━━ $1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ── connectivity check ────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Unraid MCP Non-Destructive Action Test Suite${NC}"
echo -e "Server: ${CYAN}$MCP_URL${NC}"
echo ""
printf "Checking connectivity... "
# Use -s (silent) without -f: a 4xx/406 means the MCP server is up and
# responding correctly to a plain GET — only "connection refused" is fatal.
# Capture curl's exit code directly — don't mask failures with a fallback.
HTTP_CODE=""
curl_exit=0
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$MCP_URL" 2>/dev/null) || curl_exit=$?
if [[ $curl_exit -ne 0 ]]; then
    echo -e "${RED}UNREACHABLE${NC} (curl exit code: $curl_exit)"
    echo "Start the server first: docker compose up -d  OR  uv run unraid-mcp-server"
    exit 1
fi
echo -e "${GREEN}OK${NC} (HTTP $HTTP_CODE)"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — Param-free read actions
# ═══════════════════════════════════════════════════════════════════════════════

section "unraid_info (19 query actions)"
run_test "info: overview"      unraid_info '{"action":"overview"}'
run_test "info: array"         unraid_info '{"action":"array"}'
run_test "info: network"       unraid_info '{"action":"network"}'
run_test "info: registration"  unraid_info '{"action":"registration"}'
run_test "info: connect"       unraid_info '{"action":"connect"}'
run_test "info: variables"     unraid_info '{"action":"variables"}'
run_test "info: metrics"       unraid_info '{"action":"metrics"}'
run_test "info: services"      unraid_info '{"action":"services"}'
run_test "info: display"       unraid_info '{"action":"display"}'
run_test "info: config"        unraid_info '{"action":"config"}'
run_test "info: online"        unraid_info '{"action":"online"}'
run_test "info: owner"         unraid_info '{"action":"owner"}'
run_test "info: settings"      unraid_info '{"action":"settings"}'
run_test "info: server"        unraid_info '{"action":"server"}'
run_test "info: servers"       unraid_info '{"action":"servers"}'
run_test "info: flash"         unraid_info '{"action":"flash"}'
run_test "info: ups_devices"   unraid_info '{"action":"ups_devices"}'
run_test "info: ups_device"    unraid_info '{"action":"ups_device"}'
run_test "info: ups_config"    unraid_info '{"action":"ups_config"}'
skip_test "info: update_server" "mutation — state-changing"
skip_test "info: update_ssh"    "mutation — state-changing"

section "unraid_array"
run_test "array: parity_status" unraid_array '{"action":"parity_status"}'
skip_test "array: parity_start"  "mutation — starts parity check"
skip_test "array: parity_pause"  "mutation — pauses parity check"
skip_test "array: parity_resume" "mutation — resumes parity check"
skip_test "array: parity_cancel" "mutation — cancels parity check"

section "unraid_storage (param-free reads)"
STORAGE_DISKS=$(run_test_capture "storage: disks" unraid_storage '{"action":"disks"}')
run_test "storage: shares"       unraid_storage '{"action":"shares"}'
run_test "storage: unassigned"   unraid_storage '{"action":"unassigned"}'
LOG_FILES=$(run_test_capture "storage: log_files" unraid_storage '{"action":"log_files"}')
skip_test "storage: flash_backup" "destructive (confirm=True required)"

section "unraid_docker (param-free reads)"
DOCKER_LIST=$(run_test_capture "docker: list" unraid_docker '{"action":"list"}')
DOCKER_NETS=$(run_test_capture "docker: networks" unraid_docker '{"action":"networks"}')
run_test "docker: port_conflicts" unraid_docker '{"action":"port_conflicts"}'
run_test "docker: check_updates"  unraid_docker '{"action":"check_updates"}'
run_test "docker: sync_templates" unraid_docker '{"action":"sync_templates"}'
run_test "docker: refresh_digests" unraid_docker '{"action":"refresh_digests"}'
skip_test "docker: start"                   "mutation — changes container state"
skip_test "docker: stop"                    "mutation — changes container state"
skip_test "docker: restart"                 "mutation — changes container state"
skip_test "docker: pause"                   "mutation — changes container state"
skip_test "docker: unpause"                 "mutation — changes container state"
skip_test "docker: update"                  "mutation — updates container image"
skip_test "docker: remove"                  "destructive (confirm=True required)"
skip_test "docker: update_all"              "destructive (confirm=True required)"
skip_test "docker: create_folder"           "mutation — changes organizer state"
skip_test "docker: set_folder_children"     "mutation — changes organizer state"
skip_test "docker: delete_entries"          "destructive (confirm=True required)"
skip_test "docker: move_to_folder"          "mutation — changes organizer state"
skip_test "docker: move_to_position"        "mutation — changes organizer state"
skip_test "docker: rename_folder"           "mutation — changes organizer state"
skip_test "docker: create_folder_with_items" "mutation — changes organizer state"
skip_test "docker: update_view_prefs"       "mutation — changes organizer state"
skip_test "docker: reset_template_mappings" "destructive (confirm=True required)"

section "unraid_vm (param-free reads)"
VM_LIST=$(run_test_capture "vm: list" unraid_vm '{"action":"list"}')
skip_test "vm: start"      "mutation — changes VM state"
skip_test "vm: stop"       "mutation — changes VM state"
skip_test "vm: pause"      "mutation — changes VM state"
skip_test "vm: resume"     "mutation — changes VM state"
skip_test "vm: reboot"     "mutation — changes VM state"
skip_test "vm: force_stop" "destructive (confirm=True required)"
skip_test "vm: reset"      "destructive (confirm=True required)"

section "unraid_notifications"
run_test "notifications: overview"    unraid_notifications '{"action":"overview"}'
run_test "notifications: list"        unraid_notifications '{"action":"list"}'
run_test "notifications: warnings"    unraid_notifications '{"action":"warnings"}'
run_test "notifications: recalculate" unraid_notifications '{"action":"recalculate"}'
skip_test "notifications: create"          "mutation — creates notification"
skip_test "notifications: create_unique"   "mutation — creates notification"
skip_test "notifications: archive"         "mutation — changes notification state"
skip_test "notifications: unread"          "mutation — changes notification state"
skip_test "notifications: archive_all"     "mutation — changes notification state"
skip_test "notifications: archive_many"    "mutation — changes notification state"
skip_test "notifications: unarchive_many"  "mutation — changes notification state"
skip_test "notifications: unarchive_all"   "mutation — changes notification state"
skip_test "notifications: delete"          "destructive (confirm=True required)"
skip_test "notifications: delete_archived" "destructive (confirm=True required)"

section "unraid_rclone"
run_test "rclone: list_remotes" unraid_rclone '{"action":"list_remotes"}'
run_test "rclone: config_form"  unraid_rclone '{"action":"config_form"}'
skip_test "rclone: create_remote" "mutation — creates remote"
skip_test "rclone: delete_remote" "destructive (confirm=True required)"

section "unraid_users"
run_test "users: me" unraid_users '{"action":"me"}'

section "unraid_keys"
KEYS_LIST=$(run_test_capture "keys: list" unraid_keys '{"action":"list"}')
skip_test "keys: create" "mutation — creates API key"
skip_test "keys: update" "mutation — modifies API key"
skip_test "keys: delete" "destructive (confirm=True required)"

section "unraid_health"
run_test "health: check"           unraid_health '{"action":"check"}'
run_test "health: test_connection" unraid_health '{"action":"test_connection"}'
run_test "health: diagnose"        unraid_health '{"action":"diagnose"}'

section "unraid_settings (all mutations — skipped)"
skip_test "settings: update"                    "mutation — modifies settings"
skip_test "settings: update_temperature"        "mutation — modifies settings"
skip_test "settings: update_time"               "mutation — modifies settings"
skip_test "settings: configure_ups"             "destructive (confirm=True required)"
skip_test "settings: update_api"                "mutation — modifies settings"
skip_test "settings: connect_sign_in"           "mutation — authentication action"
skip_test "settings: connect_sign_out"          "mutation — authentication action"
skip_test "settings: setup_remote_access"       "destructive (confirm=True required)"
skip_test "settings: enable_dynamic_remote_access" "destructive (confirm=True required)"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — ID-discovered read actions
# ═══════════════════════════════════════════════════════════════════════════════

section "Phase 2: ID-discovered reads"

# ── docker container ID ───────────────────────────────────────────────────────
CONTAINER_ID=$(extract_id "$DOCKER_LIST" "docker: extract container ID" "
import json, sys
d = json.load(sys.stdin)
containers = d.get('containers') or d.get('data', {}).get('containers') or []
if isinstance(containers, list) and containers:
    c = containers[0]
    cid = c.get('id') or c.get('names', [''])[0].lstrip('/')
    if cid:
        print(cid)
")

if [[ -n "$CONTAINER_ID" ]]; then
    run_test "docker: details (id=$CONTAINER_ID)" \
        unraid_docker "{\"action\":\"details\",\"container_id\":\"$CONTAINER_ID\"}"
    run_test "docker: logs (id=$CONTAINER_ID)" \
        unraid_docker "{\"action\":\"logs\",\"container_id\":\"$CONTAINER_ID\",\"tail_lines\":20}"
else
    skip_test "docker: details" "no containers found to discover ID"
    skip_test "docker: logs"    "no containers found to discover ID"
fi

# ── docker network ID ─────────────────────────────────────────────────────────
NETWORK_ID=$(extract_id "$DOCKER_NETS" "docker: extract network ID" "
import json, sys
d = json.load(sys.stdin)
nets = d.get('networks') or d.get('data', {}).get('networks') or []
if isinstance(nets, list) and nets:
    nid = nets[0].get('id') or nets[0].get('Id')
    if nid:
        print(nid)
")

if [[ -n "$NETWORK_ID" ]]; then
    run_test "docker: network_details (id=$NETWORK_ID)" \
        unraid_docker "{\"action\":\"network_details\",\"network_id\":\"$NETWORK_ID\"}"
else
    skip_test "docker: network_details" "no networks found to discover ID"
fi

# ── disk ID ───────────────────────────────────────────────────────────────────
DISK_ID=$(extract_id "$STORAGE_DISKS" "storage: extract disk ID" "
import json, sys
d = json.load(sys.stdin)
disks = d.get('disks') or d.get('data', {}).get('disks') or []
if isinstance(disks, list) and disks:
    did = disks[0].get('id') or disks[0].get('device')
    if did:
        print(did)
")

if [[ -n "$DISK_ID" ]]; then
    run_test "storage: disk_details (id=$DISK_ID)" \
        unraid_storage "{\"action\":\"disk_details\",\"disk_id\":\"$DISK_ID\"}"
else
    skip_test "storage: disk_details" "no disks found to discover ID"
fi

# ── log path ──────────────────────────────────────────────────────────────────
LOG_PATH=$(extract_id "$LOG_FILES" "storage: extract log path" "
import json, sys
d = json.load(sys.stdin)
files = d.get('log_files') or d.get('files') or d.get('data', {}).get('log_files') or []
if isinstance(files, list) and files:
    p = files[0].get('path') or (files[0] if isinstance(files[0], str) else None)
    if p:
        print(p)
")

if [[ -n "$LOG_PATH" ]]; then
    run_test "storage: logs (path=$LOG_PATH)" \
        unraid_storage "{\"action\":\"logs\",\"log_path\":\"$LOG_PATH\",\"tail_lines\":20}"
else
    skip_test "storage: logs" "no log files found to discover path"
fi

# ── VM ID ─────────────────────────────────────────────────────────────────────
VM_ID=$(extract_id "$VM_LIST" "vm: extract VM ID" "
import json, sys
d = json.load(sys.stdin)
vms = d.get('vms') or d.get('data', {}).get('vms') or []
if isinstance(vms, list) and vms:
    vid = vms[0].get('uuid') or vms[0].get('id') or vms[0].get('name')
    if vid:
        print(vid)
")

if [[ -n "$VM_ID" ]]; then
    run_test "vm: details (id=$VM_ID)" \
        unraid_vm "{\"action\":\"details\",\"vm_id\":\"$VM_ID\"}"
else
    skip_test "vm: details" "no VMs found to discover ID"
fi

# ── API key ID ────────────────────────────────────────────────────────────────
KEY_ID=$(extract_id "$KEYS_LIST" "keys: extract key ID" "
import json, sys
d = json.load(sys.stdin)
keys = d.get('keys') or d.get('apiKeys') or d.get('data', {}).get('keys') or []
if isinstance(keys, list) and keys:
    kid = keys[0].get('id')
    if kid:
        print(kid)
")

if [[ -n "$KEY_ID" ]]; then
    run_test "keys: get (id=$KEY_ID)" \
        unraid_keys "{\"action\":\"get\",\"key_id\":\"$KEY_ID\"}"
else
    skip_test "keys: get" "no API keys found to discover ID"
fi

# ═══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

TOTAL=$((PASS + FAIL + SKIP))
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}Results: ${GREEN}${PASS} passed${NC}  ${RED}${FAIL} failed${NC}  ${YELLOW}${SKIP} skipped${NC}  (${TOTAL} total)"

if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
    echo ""
    echo -e "${RED}${BOLD}Failed tests:${NC}"
    for t in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $t"
    done
fi

echo ""
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
