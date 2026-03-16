#!/usr/bin/env bash
# =============================================================================
# test-tools.sh — Integration smoke-test for unraid-mcp MCP server tools
#
# Exercises every non-destructive action using the consolidated `unraid` tool
# (action + subaction pattern). The server is launched ad-hoc via mcporter's
# --stdio flag so no persistent process or registered server entry is required.
#
# Usage:
#   ./tests/mcporter/test-tools.sh [--timeout-ms N] [--parallel] [--verbose]
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

set -uo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/../.." && pwd -P)"
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
#   Launches the stdio server and calls unraid action=health subaction=check.
#   Returns 0 if the server responds, non-zero on import failure.
# ---------------------------------------------------------------------------
smoke_test_server() {
  log_info "Smoke-testing server startup..."

  local output
  output="$(
    mcporter call \
      --stdio "uv run unraid-mcp-server" \
      --cwd "${PROJECT_DIR}" \
      --name "unraid-smoke" \
      --tool unraid \
      --args '{"action":"health","subaction":"check"}' \
      --timeout 30000 \
      --output json \
      2>&1
  )" || true

  if printf '%s' "${output}" | grep -q '"kind": "offline"'; then
    log_error "Server failed to start. Output:"
    printf '%s\n' "${output}" >&2
    log_error "Common causes:"
    log_error "  • Missing module: check 'uv run unraid-mcp-server' locally"
    log_error "  • server.py has an import for a file that doesn't exist yet"
    log_error "  • Environment variable UNRAID_API_URL or UNRAID_API_KEY missing"
    return 2
  fi

  local key_check
  key_check="$(
    printf '%s' "${output}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if 'status' in d or 'success' in d or 'error' in d:
        print('ok')
    else:
        print('missing: no status/success/error key in response')
except Exception as e:
    print('parse_error: ' + str(e))
" 2>/dev/null
  )" || key_check="parse_error"

  if [[ "${key_check}" != "ok" ]]; then
    log_error "Smoke test: unexpected response shape — ${key_check}"
    printf '%s\n' "${output}" >&2
    return 2
  fi

  log_info "Server started successfully (health response received)."
  return 0
}

# ---------------------------------------------------------------------------
# mcporter call wrapper
#   Usage: mcporter_call <args_json>
#   All calls go to the single `unraid` tool.
# ---------------------------------------------------------------------------
mcporter_call() {
  local args_json="${1:?args_json required}"

  mcporter call \
    --stdio "uv run unraid-mcp-server" \
    --cwd "${PROJECT_DIR}" \
    --name "unraid" \
    --tool unraid \
    --args "${args_json}" \
    --timeout "${CALL_TIMEOUT_MS}" \
    --output json \
    2>&1
}

# ---------------------------------------------------------------------------
# Test runner
#   Usage: run_test <label> <args_json> [expected_key]
# ---------------------------------------------------------------------------
run_test() {
  local label="${1:?label required}"
  local args="${2:?args required}"
  local expected_key="${3:-}"

  local t0
  t0="$(date +%s%N)"

  local output
  output="$(mcporter_call "${args}" 2>&1)" || true

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
# Skip helper
# ---------------------------------------------------------------------------
skip_test() {
  local label="${1:?label required}"
  local reason="${2:-prerequisite returned empty}"
  printf "${C_YELLOW}[SKIP]${C_RESET} %-55s %s\n" "${label}" "${reason}" | tee -a "${LOG_FILE}"
  SKIP_COUNT=$(( SKIP_COUNT + 1 ))
}

# ---------------------------------------------------------------------------
# ID extractors
# ---------------------------------------------------------------------------

get_docker_id() {
  local raw
  raw="$(mcporter_call '{"action":"docker","subaction":"list"}' 2>/dev/null)" || return 0
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

get_network_id() {
  local raw
  raw="$(mcporter_call '{"action":"docker","subaction":"networks"}' 2>/dev/null)" || return 0
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

get_vm_id() {
  local raw
  raw="$(mcporter_call '{"action":"vm","subaction":"list"}' 2>/dev/null)" || return 0
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

get_key_id() {
  local raw
  raw="$(mcporter_call '{"action":"key","subaction":"list"}' 2>/dev/null)" || return 0
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

get_disk_id() {
  local raw
  raw="$(mcporter_call '{"action":"disk","subaction":"disks"}' 2>/dev/null)" || return 0
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

get_log_path() {
  local raw
  raw="$(mcporter_call '{"action":"disk","subaction":"log_files"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    files = d.get('log_files', [])
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

get_ups_id() {
  local raw
  raw="$(mcporter_call '{"action":"system","subaction":"ups_devices"}' 2>/dev/null)" || return 0
  printf '%s' "${raw}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    devs = d.get('ups_devices', d.get('upsDevices', []))
    if devs:
        print(devs[0].get('id', devs[0].get('name', '')))
except Exception:
    pass
" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Grouped test suites
# ---------------------------------------------------------------------------

suite_system() {
  printf '\n%b== system (info/metrics/UPS) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "system: overview"     '{"action":"system","subaction":"overview"}'
  run_test "system: array"        '{"action":"system","subaction":"array"}'
  run_test "system: network"      '{"action":"system","subaction":"network"}'
  run_test "system: registration" '{"action":"system","subaction":"registration"}'
  run_test "system: variables"    '{"action":"system","subaction":"variables"}'
  run_test "system: metrics"      '{"action":"system","subaction":"metrics"}'
  run_test "system: services"     '{"action":"system","subaction":"services"}'
  run_test "system: display"      '{"action":"system","subaction":"display"}'
  run_test "system: config"       '{"action":"system","subaction":"config"}'
  run_test "system: online"       '{"action":"system","subaction":"online"}'
  run_test "system: owner"        '{"action":"system","subaction":"owner"}'
  run_test "system: settings"     '{"action":"system","subaction":"settings"}'
  run_test "system: server"       '{"action":"system","subaction":"server"}'
  run_test "system: servers"      '{"action":"system","subaction":"servers"}'
  run_test "system: flash"        '{"action":"system","subaction":"flash"}'
  run_test "system: ups_devices"  '{"action":"system","subaction":"ups_devices"}'

  local ups_id
  ups_id="$(get_ups_id)" || ups_id=''
  if [[ -n "${ups_id}" ]]; then
    run_test "system: ups_device" \
      "$(printf '{"action":"system","subaction":"ups_device","device_id":"%s"}' "${ups_id}")"
    run_test "system: ups_config" \
      "$(printf '{"action":"system","subaction":"ups_config","device_id":"%s"}' "${ups_id}")"
  else
    skip_test "system: ups_device" "no UPS devices found"
    skip_test "system: ups_config" "no UPS devices found"
  fi
}

suite_array() {
  printf '\n%b== array (read-only) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"
  run_test "array: parity_status"  '{"action":"array","subaction":"parity_status"}'
  run_test "array: parity_history" '{"action":"array","subaction":"parity_history"}'
  # Destructive: parity_start/pause/resume/cancel, start_array, stop_array,
  #              add_disk, remove_disk, mount_disk, unmount_disk, clear_disk_stats — skipped
}

suite_disk() {
  printf '\n%b== disk (storage/shares/logs) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "disk: shares"    '{"action":"disk","subaction":"shares"}'
  run_test "disk: disks"     '{"action":"disk","subaction":"disks"}'
  run_test "disk: log_files" '{"action":"disk","subaction":"log_files"}'

  local disk_id
  disk_id="$(get_disk_id)" || disk_id=''
  if [[ -n "${disk_id}" ]]; then
    run_test "disk: disk_details" \
      "$(printf '{"action":"disk","subaction":"disk_details","disk_id":"%s"}' "${disk_id}")"
  else
    skip_test "disk: disk_details" "no disks found"
  fi

  local log_path
  log_path="$(get_log_path)" || log_path=''
  if [[ -n "${log_path}" ]]; then
    run_test "disk: logs" \
      "$(printf '{"action":"disk","subaction":"logs","log_path":"%s","tail_lines":20}' "${log_path}")"
  else
    skip_test "disk: logs" "no log files found"
  fi
  # Destructive: flash_backup — skipped
}

suite_docker() {
  printf '\n%b== docker ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "docker: list"     '{"action":"docker","subaction":"list"}'
  run_test "docker: networks" '{"action":"docker","subaction":"networks"}'

  local container_id
  container_id="$(get_docker_id)" || container_id=''
  if [[ -n "${container_id}" ]]; then
    run_test "docker: details" \
      "$(printf '{"action":"docker","subaction":"details","container_id":"%s"}' "${container_id}")"
  else
    skip_test "docker: details" "no containers found"
  fi

  local network_id
  network_id="$(get_network_id)" || network_id=''
  if [[ -n "${network_id}" ]]; then
    run_test "docker: network_details" \
      "$(printf '{"action":"docker","subaction":"network_details","network_id":"%s"}' "${network_id}")"
  else
    skip_test "docker: network_details" "no networks found"
  fi
  # Destructive/mutating: start/stop/restart — skipped
}

suite_vm() {
  printf '\n%b== vm ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "vm: list" '{"action":"vm","subaction":"list"}'

  local vm_id
  vm_id="$(get_vm_id)" || vm_id=''
  if [[ -n "${vm_id}" ]]; then
    run_test "vm: details" \
      "$(printf '{"action":"vm","subaction":"details","vm_id":"%s"}' "${vm_id}")"
  else
    skip_test "vm: details" "no VMs found (or VM service unavailable)"
  fi
  # Destructive: start/stop/pause/resume/force_stop/reboot/reset — skipped
}

suite_notification() {
  printf '\n%b== notification ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "notification: overview" '{"action":"notification","subaction":"overview"}'
  run_test "notification: list"     '{"action":"notification","subaction":"list"}'
  run_test "notification: recalculate" '{"action":"notification","subaction":"recalculate"}'
  # Mutating: create/archive/mark_unread/delete/delete_archived/archive_all/etc. — skipped
}

suite_rclone() {
  printf '\n%b== rclone ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "rclone: list_remotes" '{"action":"rclone","subaction":"list_remotes"}'
  run_test "rclone: config_form"  '{"action":"rclone","subaction":"config_form","provider_type":"s3"}'
  # Destructive: create_remote/delete_remote — skipped
}

suite_user() {
  printf '\n%b== user ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"
  run_test "user: me" '{"action":"user","subaction":"me"}'
}

suite_key() {
  printf '\n%b== key (API keys) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "key: list" '{"action":"key","subaction":"list"}'

  local key_id
  key_id="$(get_key_id)" || key_id=''
  if [[ -n "${key_id}" ]]; then
    run_test "key: get" \
      "$(printf '{"action":"key","subaction":"get","key_id":"%s"}' "${key_id}")"
  else
    skip_test "key: get" "no API keys found"
  fi
  # Destructive: create/update/delete/add_role/remove_role — skipped
}

suite_health() {
  printf '\n%b== health ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "health: check"           '{"action":"health","subaction":"check"}'
  run_test "health: test_connection" '{"action":"health","subaction":"test_connection"}'
  run_test "health: diagnose"        '{"action":"health","subaction":"diagnose"}'
  # setup triggers elicitation — skipped
}

suite_customization() {
  printf '\n%b== customization ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "customization: theme"        '{"action":"customization","subaction":"theme"}'
  run_test "customization: public_theme" '{"action":"customization","subaction":"public_theme"}'
  run_test "customization: sso_enabled"  '{"action":"customization","subaction":"sso_enabled"}'
  run_test "customization: is_initial_setup" '{"action":"customization","subaction":"is_initial_setup"}'
  # Mutating: set_theme — skipped
}

suite_plugin() {
  printf '\n%b== plugin ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "plugin: list" '{"action":"plugin","subaction":"list"}'
  # Destructive: add/remove — skipped
}

suite_oidc() {
  printf '\n%b== oidc ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"

  run_test "oidc: providers"        '{"action":"oidc","subaction":"providers"}'
  run_test "oidc: public_providers" '{"action":"oidc","subaction":"public_providers"}'
  run_test "oidc: configuration"    '{"action":"oidc","subaction":"configuration"}'
  # provider and validate_session require IDs — skipped
}

suite_live() {
  printf '\n%b== live (snapshot subscriptions) ==%b\n' "${C_BOLD}" "${C_RESET}" | tee -a "${LOG_FILE}"
  # Note: these subactions open a transient WebSocket and wait for the first event.
  # Event-driven actions (parity_progress, ups_status, notifications_overview,
  # owner, server_status) return status=no_recent_events when no events arrive.
  run_test "live: cpu"                   '{"action":"live","subaction":"cpu"}'
  run_test "live: memory"                '{"action":"live","subaction":"memory"}'
  run_test "live: cpu_telemetry"         '{"action":"live","subaction":"cpu_telemetry"}'
  run_test "live: notifications_overview" '{"action":"live","subaction":"notifications_overview"}'
  run_test "live: log_tail"              '{"action":"live","subaction":"log_tail"}'
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
# Parallel runner
# ---------------------------------------------------------------------------
run_parallel() {
  log_warn "--parallel mode: per-suite counters aggregated via temp files."

  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf -- "${tmp_dir}"' RETURN

  local suites=(
    suite_system
    suite_array
    suite_disk
    suite_docker
    suite_vm
    suite_notification
    suite_rclone
    suite_user
    suite_key
    suite_health
    suite_customization
    suite_plugin
    suite_oidc
    suite_live
  )

  local pids=()
  local suite
  for suite in "${suites[@]}"; do
    (
      PASS_COUNT=0; FAIL_COUNT=0; SKIP_COUNT=0; FAIL_NAMES=()
      "${suite}"
      printf '%d %d %d\n' "${PASS_COUNT}" "${FAIL_COUNT}" "${SKIP_COUNT}" \
        > "${tmp_dir}/${suite}.counts"
      printf '%s\n' "${FAIL_NAMES[@]:-}" > "${tmp_dir}/${suite}.fails"
    ) &
    pids+=($!)
  done

  local pid
  for pid in "${pids[@]}"; do
    wait "${pid}" || true
  done

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
  suite_system
  suite_array
  suite_disk
  suite_docker
  suite_vm
  suite_notification
  suite_rclone
  suite_user
  suite_key
  suite_health
  suite_customization
  suite_plugin
  suite_oidc
  suite_live
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_args "$@"

  printf '%b%s%b\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"
  printf '%b  unraid-mcp integration smoke-test (single unraid tool)%b\n' "${C_BOLD}" "${C_RESET}"
  printf '%b  Project: %s%b\n' "${C_BOLD}" "${PROJECT_DIR}" "${C_RESET}"
  printf '%b  Timeout: %dms/call | Parallel: %s%b\n' \
    "${C_BOLD}" "${CALL_TIMEOUT_MS}" "${USE_PARALLEL}" "${C_RESET}"
  printf '%b  Log: %s%b\n' "${C_BOLD}" "${LOG_FILE}" "${C_RESET}"
  printf '%b%s%b\n\n' "${C_BOLD}" "$(printf '=%.0s' {1..65})" "${C_RESET}"

  check_prerequisites || exit 2

  smoke_test_server || {
    log_error ""
    log_error "Server startup failed. Aborting — no tests will run."
    log_error ""
    log_error "To diagnose, run:"
    log_error "  cd ${PROJECT_DIR} && uv run unraid-mcp-server"
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
