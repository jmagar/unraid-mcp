#!/bin/sh
# install-deps.sh — language-agnostic dependency installer for Claude Code plugins.
#
# Detects the package manager from lock files and installs deps into
# CLAUDE_PLUGIN_DATA on first run and whenever the lock file changes.
# Follows the same diff-copy-install-or-rollback pattern as the npm example
# in the Claude Code plugin docs.
#
# Supported: uv (Python), cargo (Rust), npm/yarn/pnpm (TypeScript/JavaScript)

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
DATA_DIR="${CLAUDE_PLUGIN_DATA}"

# sync_if_changed <lockfile> <install-command>
# Skips install when the stored lockfile matches the bundled one.
# On install failure, removes the stored lockfile so the next session retries.
sync_if_changed() {
    lockfile="$1"
    install_cmd="$2"

    if diff -q "${PLUGIN_ROOT}/${lockfile}" "${DATA_DIR}/${lockfile}" >/dev/null 2>&1; then
        return 0
    fi

    cp "${PLUGIN_ROOT}/${lockfile}" "${DATA_DIR}/${lockfile}" \
        && eval "${install_cmd}" \
        || rm -f "${DATA_DIR}/${lockfile}"
}

if [ -f "${PLUGIN_ROOT}/uv.lock" ]; then
    sync_if_changed "uv.lock" \
        "UV_PROJECT_ENVIRONMENT=\"${DATA_DIR}/.venv\" uv sync --project \"${PLUGIN_ROOT}\""

elif [ -f "${PLUGIN_ROOT}/package-lock.json" ]; then
    sync_if_changed "package-lock.json" \
        "npm ci --prefix \"${DATA_DIR}\""

elif [ -f "${PLUGIN_ROOT}/yarn.lock" ]; then
    sync_if_changed "yarn.lock" \
        "yarn install --cwd \"${PLUGIN_ROOT}\" --modules-folder \"${DATA_DIR}/node_modules\""

elif [ -f "${PLUGIN_ROOT}/pnpm-lock.yaml" ]; then
    sync_if_changed "pnpm-lock.yaml" \
        "pnpm install --dir \"${PLUGIN_ROOT}\" --virtual-store-dir \"${DATA_DIR}/pnpm-store\""

elif [ -f "${PLUGIN_ROOT}/Cargo.lock" ]; then
    sync_if_changed "Cargo.lock" \
        "cargo build --release --manifest-path \"${PLUGIN_ROOT}/Cargo.toml\" --target-dir \"${DATA_DIR}/target\""
fi
