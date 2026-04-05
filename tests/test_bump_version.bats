#!/usr/bin/env bats
# Tests for bin/bump-version.sh
#
# CLAUDE_PLUGIN_ROOT is used as the repo root override (same variable the
# plugin runtime exports to hook processes), so tests just point it at a
# temp copy of the relevant files.

SCRIPT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)/bin/bump-version.sh"
REAL_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"

setup() {
    TMPDIR="$(mktemp -d)"

    # Copy only the version-bearing files into the temp tree
    mkdir -p "${TMPDIR}/.claude-plugin" "${TMPDIR}/.codex-plugin"
    cp "${REAL_ROOT}/.claude-plugin/plugin.json"  "${TMPDIR}/.claude-plugin/"
    cp "${REAL_ROOT}/.codex-plugin/plugin.json"   "${TMPDIR}/.codex-plugin/"
    cp "${REAL_ROOT}/gemini-extension.json"        "${TMPDIR}/"
    cp "${REAL_ROOT}/pyproject.toml"               "${TMPDIR}/"

    # Pin all files to a known starting version
    sed -i 's/"version": "[^"]*"/"version": "9.8.7"/g' \
        "${TMPDIR}/.claude-plugin/plugin.json" \
        "${TMPDIR}/.codex-plugin/plugin.json" \
        "${TMPDIR}/gemini-extension.json"
    sed -i 's/^version = ".*"/version = "9.8.7"/' "${TMPDIR}/pyproject.toml"

    # Point the script at the temp tree via the standard plugin env var
    export CLAUDE_PLUGIN_ROOT="${TMPDIR}"
}

teardown() {
    unset CLAUDE_PLUGIN_ROOT
    rm -rf "${TMPDIR}"
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
    [ "$(version_in "${TMPDIR}/.claude-plugin/plugin.json")" = "1.2.3" ]
    [ "$(version_in "${TMPDIR}/.codex-plugin/plugin.json")"  = "1.2.3" ]
    [ "$(version_in "${TMPDIR}/gemini-extension.json")"       = "1.2.3" ]
    [ "$(version_in "${TMPDIR}/pyproject.toml")"              = "1.2.3" ]
}

@test "patch keyword increments patch component" {
    run bash "${SCRIPT}" patch
    [ "$status" -eq 0 ]
    [ "$(version_in "${TMPDIR}/.claude-plugin/plugin.json")" = "9.8.8" ]
    [ "$(version_in "${TMPDIR}/pyproject.toml")"              = "9.8.8" ]
}

@test "minor keyword increments minor and resets patch to zero" {
    run bash "${SCRIPT}" minor
    [ "$status" -eq 0 ]
    [ "$(version_in "${TMPDIR}/.claude-plugin/plugin.json")" = "9.9.0" ]
    [ "$(version_in "${TMPDIR}/pyproject.toml")"              = "9.9.0" ]
}

@test "major keyword increments major and resets minor and patch" {
    run bash "${SCRIPT}" major
    [ "$status" -eq 0 ]
    [ "$(version_in "${TMPDIR}/.claude-plugin/plugin.json")" = "10.0.0" ]
    [ "$(version_in "${TMPDIR}/pyproject.toml")"              = "10.0.0" ]
}

@test "all four files are updated in sync" {
    run bash "${SCRIPT}" 2.0.0
    [ "$status" -eq 0 ]
    local claude codex gemini pyproject
    claude="$(version_in "${TMPDIR}/.claude-plugin/plugin.json")"
    codex="$(version_in "${TMPDIR}/.codex-plugin/plugin.json")"
    gemini="$(version_in "${TMPDIR}/gemini-extension.json")"
    pyproject="$(version_in "${TMPDIR}/pyproject.toml")"
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
    # Running against the real repo root — just verify it exits 0 with patch
    # and produces the expected output format without corrupting anything
    CURRENT="$(grep -m1 '"version"' "${REAL_ROOT}/.claude-plugin/plugin.json" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')"
    run bash "${SCRIPT}" "${CURRENT}"  # bump to same version = no-op change
    [ "$status" -eq 0 ]
    [[ "$output" == *"${CURRENT}"* ]]
}
