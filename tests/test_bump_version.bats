#!/usr/bin/env bats
# Tests for bin/bump-version.sh
#
# CLAUDE_PLUGIN_ROOT is used as the repo root override (same variable the
# plugin runtime exports to hook processes), so tests just point it at a
# temp copy of the relevant files.

SCRIPT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)/bin/bump-version.sh"
REAL_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"

setup() {
    TEST_DIR="$(mktemp -d)"

    # Copy only the version-bearing files into the temp tree
    mkdir -p "${TEST_DIR}/.claude-plugin" "${TEST_DIR}/.codex-plugin"
    cp "${REAL_ROOT}/.claude-plugin/plugin.json"  "${TEST_DIR}/.claude-plugin/"
    cp "${REAL_ROOT}/.codex-plugin/plugin.json"   "${TEST_DIR}/.codex-plugin/"
    cp "${REAL_ROOT}/gemini-extension.json"        "${TEST_DIR}/"
    cp "${REAL_ROOT}/pyproject.toml"               "${TEST_DIR}/"

    # Pin all files to a known starting version
    sed -i 's/"version": "[^"]*"/"version": "9.8.7"/g' \
        "${TEST_DIR}/.claude-plugin/plugin.json" \
        "${TEST_DIR}/.codex-plugin/plugin.json" \
        "${TEST_DIR}/gemini-extension.json"
    sed -i 's/^version = ".*"/version = "9.8.7"/' "${TEST_DIR}/pyproject.toml"

    # Point the script at the temp tree via the standard plugin env var
    export CLAUDE_PLUGIN_ROOT="${TEST_DIR}"
}

teardown() {
    unset CLAUDE_PLUGIN_ROOT
    rm -rf "${TEST_DIR}"
}

version_in() {
    grep -m1 '"version"\|^version' "$1" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+'
}

@test "no argument prints usage and exits non-zero" {
    run bash "${SCRIPT}"
    [ "$status" -ne 0 ]
    [[ "$output" == *"Usage"* ]]
}

@test "explicit version updates all four files" {
    run bash "${SCRIPT}" 1.2.3
    [ "$status" -eq 0 ]
    [ "$(version_in "${TEST_DIR}/.claude-plugin/plugin.json")" = "1.2.3" ]
    [ "$(version_in "${TEST_DIR}/.codex-plugin/plugin.json")"  = "1.2.3" ]
    [ "$(version_in "${TEST_DIR}/gemini-extension.json")"       = "1.2.3" ]
    [ "$(version_in "${TEST_DIR}/pyproject.toml")"              = "1.2.3" ]
}

@test "patch keyword increments patch component" {
    run bash "${SCRIPT}" patch
    [ "$status" -eq 0 ]
    [ "$(version_in "${TEST_DIR}/.claude-plugin/plugin.json")" = "9.8.8" ]
    [ "$(version_in "${TEST_DIR}/pyproject.toml")"              = "9.8.8" ]
}

@test "minor keyword increments minor and resets patch to zero" {
    run bash "${SCRIPT}" minor
    [ "$status" -eq 0 ]
    [ "$(version_in "${TEST_DIR}/.claude-plugin/plugin.json")" = "9.9.0" ]
    [ "$(version_in "${TEST_DIR}/pyproject.toml")"              = "9.9.0" ]
}

@test "major keyword increments major and resets minor and patch" {
    run bash "${SCRIPT}" major
    [ "$status" -eq 0 ]
    [ "$(version_in "${TEST_DIR}/.claude-plugin/plugin.json")" = "10.0.0" ]
    [ "$(version_in "${TEST_DIR}/pyproject.toml")"              = "10.0.0" ]
}

@test "all four files are updated in sync" {
    run bash "${SCRIPT}" 2.0.0
    [ "$status" -eq 0 ]
    local claude codex gemini pyproject
    claude="$(version_in "${TEST_DIR}/.claude-plugin/plugin.json")"
    codex="$(version_in "${TEST_DIR}/.codex-plugin/plugin.json")"
    gemini="$(version_in "${TEST_DIR}/gemini-extension.json")"
    pyproject="$(version_in "${TEST_DIR}/pyproject.toml")"
    [ "$claude" = "2.0.0" ]
    [ "$codex"  = "2.0.0" ]
    [ "$gemini" = "2.0.0" ]
    [ "$pyproject" = "2.0.0" ]
}

@test "output reports old and new version" {
    run bash "${SCRIPT}" 1.0.0
    [ "$status" -eq 0 ]
    [[ "$output" == *"9.8.7"* ]]
    [[ "$output" == *"1.0.0"* ]]
}

@test "output reminds about CHANGELOG" {
    run bash "${SCRIPT}" 1.0.0
    [ "$status" -eq 0 ]
    [[ "$output" == *"CHANGELOG"* ]]
}

@test "falls back to dirname resolution when CLAUDE_PLUGIN_ROOT is unset" {
    unset CLAUDE_PLUGIN_ROOT

    # Use an isolated temp copy — never touch real repo files
    local FALLBACK_DIR
    FALLBACK_DIR="$(mktemp -d)"
    mkdir -p "${FALLBACK_DIR}/.claude-plugin" "${FALLBACK_DIR}/.codex-plugin"
    cp "${REAL_ROOT}/.claude-plugin/plugin.json"  "${FALLBACK_DIR}/.claude-plugin/"
    cp "${REAL_ROOT}/.codex-plugin/plugin.json"   "${FALLBACK_DIR}/.codex-plugin/"
    cp "${REAL_ROOT}/gemini-extension.json"        "${FALLBACK_DIR}/"
    cp "${REAL_ROOT}/pyproject.toml"               "${FALLBACK_DIR}/"

    # Pin to known version and run without CLAUDE_PLUGIN_ROOT — script must
    # discover the repo root via dirname of its own path. We symlink the script
    # into bin/ inside FALLBACK_DIR so dirname resolution points there.
    mkdir -p "${FALLBACK_DIR}/bin"
    ln -s "${SCRIPT}" "${FALLBACK_DIR}/bin/bump-version.sh"

    sed -i 's/"version": "[^"]*"/"version": "9.8.7"/g' \
        "${FALLBACK_DIR}/.claude-plugin/plugin.json" \
        "${FALLBACK_DIR}/.codex-plugin/plugin.json" \
        "${FALLBACK_DIR}/gemini-extension.json"
    sed -i 's/^version = ".*"/version = "9.8.7"/' "${FALLBACK_DIR}/pyproject.toml"

    run bash "${FALLBACK_DIR}/bin/bump-version.sh" patch
    rm -rf "${FALLBACK_DIR}"

    [ "$status" -eq 0 ]
    [[ "$output" == *"9.8.7"* ]]
    [[ "$output" == *"9.8.8"* ]]
}
