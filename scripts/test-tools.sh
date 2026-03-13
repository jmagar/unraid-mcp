#!/usr/bin/env bash
# =============================================================================
# test-tools.sh — Integration smoke-test for unraid-mcp MCP server tools
#
# Exercises every non-destructive action across all 10 tools using mcporter.
# The server is launched ad-hoc via mcporter's --stdio flag so no persistent
# process or registered server entry is required.
#
# Usage:
#   ./scripts/test-tools.sh [--timeout-ms N] [--parallel] [--verbose]
#
# Options:
#   --timeout-ms N   Per-call timeout in milliseconds (default: 25000)
#   --parallel       Run independent test groups in parallel (default: off)
#   --verbose        Print raw mcporter output for each call
#
# Exit codes:
#   0 — all tests passed or skipped
#   1 — one or more tests failed
#   2 — prerequisite check failed (mcporter, uv, server startup)
# =============================================================================

set -Eeuo pipefail
shopt -s inherit_errexit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
readonly SCRIPT_NAME="$(basename -- "${BASH_SOURCE[0]}")"
readonly TS_START="$(date +%s%N)"                  # nanosecond epoch
readonly LOG_FILE="${TMPDIR:-/tmp}/${SCRIPT_NAME%.sh}.$(date +%Y%m%d-%H%M%S).log"

# Colours (disabled automatically when stdout is not a terminal)
if [[ -t 1 ]]; then
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
# Defaults (overridable via flags)
# ---------------------------------------------------------------------------
CALL_TIMEOUT_MS=25000
USE_PARALLEL=false
VERBOSE=false

# ---------------------------------------------------------------------------
# Counters (updated by run_test / skip_test)
# ---------------------------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
declare -a FAIL_NAMES=()

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --timeout-ms)
        CALL_TIMEOUT_MS="${2:?--timeout-ms requires a value}"
        shift 2
        ;;
      --parallel)
        USE_PARALLEL=true
        shift
        ;;
      --verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        printf 'Usage: %s [--timeout-ms N] [--parallel] [--verbose]\n' "${SCRIPT_NAME}"
        exit 0
        ;;
      *)
        printf '[ERROR] Unknown argument: %s\n' "$1" >&2
        exit 2
        ;;
    esac
  done
}

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log_info()  { printf "${C_CYAN}[INFO]${C_RESET}  %s\n" "$*" | tee -a "${LOG_FILE}"; }
log_warn()  { printf "${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*" | tee -a "${LOG_FILE}"; }
log_error() { printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" | tee -a "${LOG_FILE}" >&2; }

elapsed_ms() {
  local now
  now="$(date +%s%N)"
  printf '%d' "$(( (now - TS_START) / 1000000 ))"
}

# ---------------------------------------------------------------------------
# Cleanup trap
# ---------------------------------------------------------------------------
cleanup() {
  local rc=$?
  if [[ $rc -ne 0 ]]; then
    log_warn "Script exited with rc=${rc}. Log: ${LOG_FILE}"
  fi
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
check_prerequisites() {
  local missing=false

  if ! command -v mcporter &>/dev/null; then
    log_error "mcporter not found in PATH. Install it and re-run."
    missing=true
  fi

  if ! command -v uv &>/dev/null; then
    log_error "uv not found in PATH. Install it and re-run."
    missing=true
  fi

  if ! command -v python3 &>/dev/null; then
    log_error "python3 not found in PATH."
    missing=true
  fi

  if [[ ! -f "${PROJECT_DIR}/pyproject.toml" ]]; then
    log_error "pyproject.toml not found at ${PROJECT_DIR}. Wrong directory?"
    missing=true
  fi

  if [[ "${missing}" == true ]]; then
    return 2
  fi
}

# ---------------------------------------------------------------------------
# Server startup smoke-test
#   Launches the stdio server and calls unraid_health action=check.
#   Returns 0 if the server responds (even with an API error — that still
#   means the Python process started cleanly), non-zero on import failure.
# ---------------------------------------------------------------------------
smoke_test_server() {
  log_info "Smoke-testing server startup..."

  local output
  output="$(
    mcporter call \
      --stdio "uv run unraid-mcp-server" \
      --cwd "${PROJECT_DIR}" \
      --name "unraid-smoke" \
      --tool unraid_health \
      --args '{"action":"check"}' \
      --timeout 30000 \
      --output json \
      2>&1
  )" || true

  # If mcporter returns the offline error the server failed to import/start
  if printf '%s' "${output}" | grep -q '"kind": "offline"'; then
    log_error "Server failed to start. Output:"
    printf '%s\n' "${output}" >&2
    log_error "Common causes:"
    log_error "  • Missing module: check 'uv run unraid-mcp-server' locally"
    log_error "  • server.py has an import for a file that doesn't exist yet"
    log_error "  • Environment variable UNRAID_API_URL or UNRAID_API_KEY missing"
    return 2
  fi

  log_info "Server started successfully (health response received)."
  return 0
}

# ---------------------------------------------------------------------------
# mcporter call wrapper
#   Usage: mcporter_call <tool_name> <args_json>
#   Writes the mcporter JSON output to stdout.
#   Returns the mcporter exit code.
# ---------------------------------------------------------------------------
mcporter_call() {
  local tool_name="${1:?tool_name required}"
  local args_json="${2:?args_json required}"

  mcporter call \
    --stdio "uv run unraid-mcp-server" \
    --cwd "${PROJECT_DIR}" \
    --name "unraid" \
    --tool "${tool_name}" \
    --args "${args_json}" \
    --timeout "${CALL_TIMEOUT_MS}" \
    --output json \
    2>&1
}

# ---------------------------------------------------------------------------
# Test runner
#   Usage: run_test <label> <tool_name> <args_json> [expected_key]
#
#   expected_key — optional jq-style python key path to validate in the
#                  response (e.g. ".status" or ".containers").  If omitted,
#                  any non-offline response is a PASS (tool errors from the
#                  API — e.g. VMs disabled — are still considered PASS because
#                  the tool itself responded correctly).
# ---------------------------------------------------------------------------
run_test() {
  local label="${1:?label required}"
  local tool="${2:?tool required}"
  local args="${3:?args required}"
  local expected_key="${4:-}"

  local t0
  t0="$(date +%s%N)"

  local output
  output="$(mcporter_call "${tool}" "${args}" 2>&1)" || true

  local elapsed_ms
  elapsed_ms="$(( ( $(date +%s%N) - t0 ) / 1000000 ))"

  if [[ "${VERBOSE}" == true ]]; then
    printf '%s\n' "${output}" | tee -a "${LOG_FILE}"
  else
    printf '%s\n' "${output}" >> "${LOG_FILE}"
  fi

  # Detect server-offline (import/startup failure)
  if printf '%s' "${output}" | grep -q '"kind": "offline"'; then
    printf "${C_RED}[FAIL]${C_RESET} %-55s ${C_DIM}%dms${C_RESET}\n" \
      "${label}" "${elapsed_ms}" | tee -a "${LOG_FILE}"
    printf '       server offline — check startup errors in %s\n' "${LOG_FILE}" | tee -a "${LOG_FILE}"
    FAIL_COUNT=$(( FAIL_COUNT + 1 ))
    FAIL_NAMES+=("${label}")
    return 1
  fi

  # Validate optional key presence
  if [[ -n "${expected_key}" ]]; then
    local key_check
    key_check="$(
      printf '%s' "${output}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    keys = '${expected_key}'.split('.')
    node = d
    for k in keys:
        if k:
            node = node[k]
    print('ok')
except Exception as e:
    print('missing: ' + str(e))
" 2>/dev/null
    )" || key_check="parse_error"

    if [[ "${key_check}" != "ok" ]]; then
      printf "${C_RED}[FAIL]${C_RESET} %-55s ${C_DIM}%dms${C_RESET}\n" \
        "${label}" "${elapsed_ms}" | tee -a "${LOG_FILE}"
      printf '       expected key .%s not found: %s\n' "${expected_key}" "${key_check}" | tee -a "${LOG_FILE}"
      FAIL_COUNT=$(( FAIL_COUNT + 1 ))
      FAIL_NAMES+=("${label}")
      return 1
    fi
  fi

  printf "${C_GREEN}[PASS]${C_RESET} %-55s ${C_DIM}%dms${C_RESET}\n" \
    "${label}" "${elapsed_ms}" | tee -a "${LOG_FILE}"
  PASS_COUNT=$(( PASS_COUNT + 1 ))
  return 0
}

# ---------------------------------------------------------------------------
# Skip helper — use when a prerequisite (like a list) returned empty
# ---------------------------------------------------------------------------
skip_test() {
  local label="${1:?label required}"
  local reason="${2:-prerequisite returned empty}"
  printf "${C_YELLOW}[SKIP]${C_RESET} %-55s %s\n" "${label}" "${reason}" | tee -a "${LOG_FILE}"
  SKIP_COUNT=$(( SKIP_COUNT + 1 ))
}

# ---------------------------------------------------------------------------
# ID extractors
#   Each function calls the relevant list action and prints the first ID.
#   Prints nothing (empty string) if the list is empty or the call fails.
# ---------------------------------------------------------------------------

# Extract first docker container ID
get_docker_id() {
  local raw
  raw="$(mcporter_call unraid_docker '{"action":"list"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    containers = d.get('containers', [])
    if containers:
        print(containers[0]['id'])
except Exception:
    pass
" 2>/dev/null || true
}

# Extract first docker network ID
get_network_id() {
  local raw
  raw="$(mcporter_call unraid_docker '{"action":"networks"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    nets = d.get('networks', [])
    if nets:
        print(nets[0]['id'])
except Exception:
    pass
" 2>/dev/null || true
}

# Extract first VM ID
get_vm_id() {
  local raw
  raw="$(mcporter_call unraid_vm '{"action":"list"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    vms = d.get('vms', d.get('domains', []))
    if vms:
        print(vms[0].get('id', vms[0].get('uuid', '')))
except Exception:
    pass
" 2>/dev/null || true
}

# Extract first API key ID
get_key_id() {
  local raw
  raw="$(mcporter_call unraid_keys '{"action":"list"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    keys = d.get('keys', d.get('apiKeys', []))
    if keys:
        print(keys[0].get('id', ''))
except Exception:
    pass
" 2>/dev/null || true
}

# Extract first disk ID
get_disk_id() {
  local raw
  raw="$(mcporter_call unraid_storage '{"action":"disks"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    disks = d.get('disks', [])
    if disks:
        print(disks[0]['id'])
except Exception:
    pass
" 2>/dev/null || true
}

# Extract first log file path
get_log_path() {
  local raw
  raw="$(mcporter_call unraid_storage '{"action":"log_files"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    files = d.get('log_files', [])
    # Prefer a plain text log (not binary like btmp/lastlog)
    for f in files:
        p = f.get('path', '')
        if p.endswith('.log') or 'syslog' in p or 'messages' in p:
            print(p)
            break
    else:
        if files:
            print(files[0]['path'])
except Exception:
    pass
" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Grouped test suites
# ---------------------------------------------------------------------------

suite_unraid_info() {
  printf '\n%b== unraid_info (19 actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_info: overview"     unraid_info '{"action":"overview"}'
  run_test "unraid_info: array"        unraid_info '{"action":"array"}'
  run_test "unraid_info: network"      unraid_info '{"action":"network"}'
  run_test "unraid_info: registration" unraid_info '{"action":"registration"}'
  run_test "unraid_info: connect"      unraid_info '{"action":"connect"}'
  run_test "unraid_info: variables"    unraid_info '{"action":"variables"}'
  run_test "unraid_info: metrics"      unraid_info '{"action":"metrics"}'
  run_test "unraid_info: services"     unraid_info '{"action":"services"}'
  run_test "unraid_info: display"      unraid_info '{"action":"display"}'
  run_test "unraid_info: config"       unraid_info '{"action":"config"}'
  run_test "unraid_info: online"       unraid_info '{"action":"online"}'
  run_test "unraid_info: owner"        unraid_info '{"action":"owner"}'
  run_test "unraid_info: settings"     unraid_info '{"action":"settings"}'
  run_test "unraid_info: server"       unraid_info '{"action":"server"}'
  run_test "unraid_info: servers"      unraid_info '{"action":"servers"}'
  run_test "unraid_info: flash"        unraid_info '{"action":"flash"}'
  run_test "unraid_info: ups_devices"  unraid_info '{"action":"ups_devices"}'
  # ups_device and ups_config require a device_id — skip if no UPS devices found
  local ups_raw
  ups_raw="$(mcporter_call unraid_info '{"action":"ups_devices"}' 2>/dev/null)" || ups_raw=''
  local ups_id
  ups_id="$(printf '%s' "${ups_raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    devs = d.get('ups_devices', d.get('upsDevices', []))
    if devs:
        print(devs[0].get('id', devs[0].get('name', '')))
except Exception:
    pass
" 2>/dev/null)" || ups_id=''

  if [[ -n "${ups_id}" ]]; then
    run_test "unraid_info: ups_device" unraid_info \
      "$(printf '{"action":"ups_device","device_id":"%s"}' "${ups_id}")"
    run_test "unraid_info: ups_config" unraid_info \
      "$(printf '{"action":"ups_config","device_id":"%s"}' "${ups_id}")"
  else
    skip_test "unraid_info: ups_device" "no UPS devices found"
    skip_test "unraid_info: ups_config" "no UPS devices found"
  fi
}

suite_unraid_array() {
  printf '\n%b== unraid_array (1 read-only action) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"
  run_test "unraid_array: parity_status" unraid_array '{"action":"parity_status"}'
  # Destructive actions (parity_start/pause/resume/cancel) skipped
}

suite_unraid_storage() {
  printf '\n%b== unraid_storage (6 actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_storage: shares"   unraid_storage '{"action":"shares"}'
  run_test "unraid_storage: disks"    unraid_storage '{"action":"disks"}'
  run_test "unraid_storage: unassigned" unraid_storage '{"action":"unassigned"}'
  run_test "unraid_storage: log_files"  unraid_storage '{"action":"log_files"}'

  # disk_details needs a disk ID
  local disk_id
  disk_id="$(get_disk_id)" || disk_id=''
  if [[ -n "${disk_id}" ]]; then
    run_test "unraid_storage: disk_details" unraid_storage \
      "$(printf '{"action":"disk_details","disk_id":"%s"}' "${disk_id}")"
  else
    skip_test "unraid_storage: disk_details" "no disks found"
  fi

  # logs needs a valid log path
  local log_path
  log_path="$(get_log_path)" || log_path=''
  if [[ -n "${log_path}" ]]; then
    run_test "unraid_storage: logs" unraid_storage \
      "$(printf '{"action":"logs","log_path":"%s","tail_lines":20}' "${log_path}")"
  else
    skip_test "unraid_storage: logs" "no log files found"
  fi
}

suite_unraid_docker() {
  printf '\n%b== unraid_docker (7 read-only actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_docker: list"           unraid_docker '{"action":"list"}'
  run_test "unraid_docker: networks"       unraid_docker '{"action":"networks"}'
  run_test "unraid_docker: port_conflicts" unraid_docker '{"action":"port_conflicts"}'
  run_test "unraid_docker: check_updates"  unraid_docker '{"action":"check_updates"}'

  # details, logs, network_details need IDs
  local container_id
  container_id="$(get_docker_id)" || container_id=''
  if [[ -n "${container_id}" ]]; then
    run_test "unraid_docker: details" unraid_docker \
      "$(printf '{"action":"details","container_id":"%s"}' "${container_id}")"
    run_test "unraid_docker: logs" unraid_docker \
      "$(printf '{"action":"logs","container_id":"%s","tail_lines":20}' "${container_id}")"
  else
    skip_test "unraid_docker: details" "no containers found"
    skip_test "unraid_docker: logs"    "no containers found"
  fi

  local network_id
  network_id="$(get_network_id)" || network_id=''
  if [[ -n "${network_id}" ]]; then
    run_test "unraid_docker: network_details" unraid_docker \
      "$(printf '{"action":"network_details","network_id":"%s"}' "${network_id}")"
  else
    skip_test "unraid_docker: network_details" "no networks found"
  fi

  # Destructive actions (start/stop/restart/pause/unpause/remove/update/update_all) skipped
}

suite_unraid_vm() {
  printf '\n%b== unraid_vm (2 read-only actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_vm: list" unraid_vm '{"action":"list"}'

  local vm_id
  vm_id="$(get_vm_id)" || vm_id=''
  if [[ -n "${vm_id}" ]]; then
    run_test "unraid_vm: details" unraid_vm \
      "$(printf '{"action":"details","vm_id":"%s"}' "${vm_id}")"
  else
    skip_test "unraid_vm: details" "no VMs found (or VM service unavailable)"
  fi

  # Destructive actions (start/stop/pause/resume/force_stop/reboot/reset) skipped
}

suite_unraid_notifications() {
  printf '\n%b== unraid_notifications (4 read-only actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_notifications: overview" unraid_notifications '{"action":"overview"}'
  run_test "unraid_notifications: list"     unraid_notifications '{"action":"list"}'
  run_test "unraid_notifications: warnings" unraid_notifications '{"action":"warnings"}'
  run_test "unraid_notifications: unread"   unraid_notifications '{"action":"unread"}'

  # Destructive actions (create/archive/delete/delete_archived/archive_all/etc.) skipped
}

suite_unraid_rclone() {
  printf '\n%b== unraid_rclone (2 read-only actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_rclone: list_remotes" unraid_rclone '{"action":"list_remotes"}'
  # config_form requires a provider_type — use "s3" as a safe, always-available provider
  run_test "unraid_rclone: config_form"  unraid_rclone '{"action":"config_form","provider_type":"s3"}'

  # Destructive actions (create_remote/delete_remote) skipped
}

suite_unraid_users() {
  printf '\n%b== unraid_users (1 action) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"
  run_test "unraid_users: me" unraid_users '{"action":"me"}'
}

suite_unraid_keys() {
  printf '\n%b== unraid_keys (2 read-only actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_keys: list" unraid_keys '{"action":"list"}'

  local key_id
  key_id="$(get_key_id)" || key_id=''
  if [[ -n "${key_id}" ]]; then
    run_test "unraid_keys: get" unraid_keys \
      "$(printf '{"action":"get","key_id":"%s"}' "${key_id}")"
  else
    skip_test "unraid_keys: get" "no API keys found"
  fi

  # Destructive actions (create/update/delete) skipped
}

suite_unraid_health() {
  printf '\n%b== unraid_health (3 actions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "unraid_health: check"           unraid_health '{"action":"check"}'
  run_test "unraid_health: test_connection" unraid_health '{"action":"test_connection"}'
  run_test "unraid_health: diagnose"        unraid_health '{"action":"diagnose"}'
}

# ---------------------------------------------------------------------------
# Print final summary
# ---------------------------------------------------------------------------
print_summary() {
  local total_ms="$(( ( $(date +%s%N) - TS_START ) / 1000000 ))"
  local total=$(( PASS_COUNT + FAIL_COUNT + SKIP_COUNT ))

  printf '\n%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "PASS" "${C_RESET}" "${C_GREEN}" "${PASS_COUNT}" "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "FAIL" "${C_RESET}" "${C_RED}"   "${FAIL_COUNT}" "${C_RESET}"
  printf '%b%-20s%b  %b%d%b\n' "${C_BOLD}" "SKIP" "${C_RESET}" "${C_YELLOW}" "${SKIP_COUNT}" "${C_RESET}"
  printf '%b%-20s%b  %d\n' "${C_BOLD}" "TOTAL" "${C_RESET}" "${total}"
  printf '%b%-20s%b  %ds (%dms)\n' "${C_BOLD}" "ELAPSED" "${C_RESET}" \
    "$(( total_ms / 1000 ))" "${total_ms}"
  printf '%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"

  if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    printf '\n%bFailed tests:%b\n' "${C_RED}" "${C_RESET}"
    local name
    for name in "${FAIL_NAMES[@]}"; do
      printf '  • %s\n' "${name}"
    done
    printf '\nFull log: %s\n' "${LOG_FILE}"
  fi
}

# ---------------------------------------------------------------------------
# Parallel runner — wraps each suite in a background subshell and waits
# ---------------------------------------------------------------------------
run_parallel() {
  # Each suite is independent (only cross-suite dependency: IDs are fetched
  # fresh inside each suite function, not shared across suites).
  # Counter updates from subshells won't propagate to the parent — collect
  # results via temp files instead.
  log_warn "--parallel mode: per-suite counters aggregated via temp files."

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf -- "${tmp_dir}"' RETURN

  local suites=(
    suite_unraid_info
    suite_unraid_array
    suite_unraid_storage
    suite_unraid_docker
    suite_unraid_vm
    suite_unraid_notifications
    suite_unraid_rclone
    suite_unraid_users
    suite_unraid_keys
    suite_unraid_health
  )

  local pids=()
  local suite
  for suite in "${suites[@]}"; do
    (
      # Reset counters in subshell
      PASS_COUNT=0; FAIL_COUNT=0; SKIP_COUNT=0; FAIL_NAMES=()
      "${suite}"
      printf '%d %d %d\n' "${PASS_COUNT}" "${FAIL_COUNT}" "${SKIP_COUNT}" \
        > "${tmp_dir}/${suite}.counts"
      printf '%s\n' "${FAIL_NAMES[@]:-}" > "${tmp_dir}/${suite}.fails"
    ) &
    pids+=($!)
  done

  # Wait for all background suites
  local pid
  for pid in "${pids[@]}"; do
    wait "${pid}" || true
  done

  # Aggregate counters
  local f
  for f in "${tmp_dir}"/*.counts; do
    [[ -f "${f}" ]] || continue
    local p fl s
    read -r p fl s < "${f}"
    PASS_COUNT=$(( PASS_COUNT + p ))
    FAIL_COUNT=$(( FAIL_COUNT + fl ))
    SKIP_COUNT=$(( SKIP_COUNT + s ))
  done

  for f in "${tmp_dir}"/*.fails; do
    [[ -f "${f}" ]] || continue
    while IFS= read -r line; do
      [[ -n "${line}" ]] && FAIL_NAMES+=("${line}")
    done < "${f}"
  done
}

# ---------------------------------------------------------------------------
# Sequential runner
# ---------------------------------------------------------------------------
run_sequential() {
  suite_unraid_info
  suite_unraid_array
  suite_unraid_storage
  suite_unraid_docker
  suite_unraid_vm
  suite_unraid_notifications
  suite_unraid_rclone
  suite_unraid_users
  suite_unraid_keys
  suite_unraid_health
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_args "$@"

  printf '%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"
  printf '%b  unraid-mcp integration smoke-test%b\n' "${C_BOLD}" "${C_RESET}"
  printf '%b  Project: %s%b\n' "${C_BOLD}" "${PROJECT_DIR}" "${C_RESET}"
  printf '%b  Timeout: %dms/call | Parallel: %s%b\n' \
    "${C_BOLD}" "${CALL_TIMEOUT_MS}" "${USE_PARALLEL}" "${C_RESET}"
  printf '%b  Log: %s%b\n' "${C_BOLD}" "${LOG_FILE}" "${C_RESET}"
  printf '%b%s%b\n\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"

  # Prerequisite gate
  check_prerequisites || exit 2

  # Server startup gate — fail fast if the Python process can't start
  smoke_test_server || {
    log_error ""
    log_error "Server startup failed. Aborting — no tests will run."
    log_error ""
    log_error "To diagnose, run:"
    log_error "  cd ${PROJECT_DIR} && uv run unraid-mcp-server"
    log_error ""
    log_error "If server.py has a broken import (e.g. missing tools/settings.py),"
    log_error "stash or revert the uncommitted server.py change first:"
    log_error "  git stash -- unraid_mcp/server.py"
    log_error "  ./scripts/test-tools.sh"
    log_error "  git stash pop"
    exit 2
  }

  if [[ "${USE_PARALLEL}" == true ]]; then
    run_parallel
  else
    run_sequential
  fi

  print_summary

  if [[ "${FAIL_COUNT}" -gt 0 ]]; then
    exit 1
  fi
  exit 0
}

main "$@"
