#!/usr/bin/env bash
# Lightweight checks for check-runtime-current.sh argument handling. Runtime
# systemd/docker behavior is verified live by the command itself.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="${SCRIPT_DIR}/check-runtime-current.sh"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

out="$("${CHECKER}" --help)"
[[ "${out}" == *"--mode auto|systemd|docker"* ]] || fail "help omits mode usage"
[[ "${out}" == *"local cache"* ]] || fail "help omits Docker cache semantics"

set +e
out="$("${CHECKER}" --bogus 2>&1)"
status=$?
set -e
[[ "${status}" -eq 2 ]] || fail "unknown argument exit=${status}, want 2"
[[ "${out}" == *"unknown argument: --bogus"* ]] || fail "unknown argument message missing"

set +e
out="$("${CHECKER}" --mode nope 2>&1)"
status=$?
set -e
[[ "${status}" -eq 2 ]] || fail "invalid mode exit=${status}, want 2"
[[ "${out}" == *"invalid mode: nope"* ]] || fail "invalid mode message missing"

echo "check-runtime-current.sh argument tests passed"
