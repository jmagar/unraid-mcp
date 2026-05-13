#!/usr/bin/env bash
# reset-db.sh — WAL-safe backup + destructive SQLite reset for syslog-mcp
#
# Usage:
#   bash scripts/reset-db.sh
#   bash scripts/reset-db.sh --force
#   bash scripts/reset-db.sh --backup-dir ./backups
#   bash scripts/reset-db.sh --include-auth   # ALSO wipe auth.db + auth-jwt.pem
#
# Default backup dir: ./backups/
# Default DB path: ${SYSLOG_MCP_DB_PATH:-./data/syslog.db}
#
# By default this script ONLY touches the syslog log database. Auth state
# (auth.db + auth-jwt.pem) is NEVER deleted unless `--include-auth` is passed.
# Wiping the JWT key invalidates every issued access/refresh token — only do
# so during a deliberate credential rotation.

set -euo pipefail

DB_PATH="${SYSLOG_MCP_DB_PATH:-./data/syslog.db}"
BACKUP_DIR="./backups"
FORCE=0
INCLUDE_AUTH=0

usage() {
    cat <<'EOF'
Usage: bash scripts/reset-db.sh [--force] [--backup-dir DIR] [--include-auth] [--help]

Creates a WAL-safe SQLite backup first, then deletes the live syslog DB files:
  - <db>
  - <db>-wal
  - <db>-shm

With --include-auth, ALSO backs up and wipes the auth state:
  - <auth.db>, <auth.db>-wal, <auth.db>-shm
  - <auth-jwt.pem>

Options:
  --backup-dir DIR  Directory for the timestamped backup file (default: ./backups)
  --force           Skip the interactive confirmation prompt
  --include-auth    Also wipe lab-auth state (auth.db + auth-jwt.pem)
  --help            Show this help text

Environment:
  SYSLOG_MCP_DB_PATH   SQLite syslog database path (default: ./data/syslog.db)

Auth artifact paths (auth.db, auth-jwt.pem) come from [mcp.auth].sqlite_path and
[mcp.auth].key_path in config.toml (resolved relative to the syslog DB directory).
Defaults below match the out-of-the-box config.toml values; set AUTH_DB_PATH or
AUTH_KEY_PATH in your environment to override if you changed them in config.toml.

Important:
  Stop the syslog-mcp service before running this reset. The backup step is
  WAL-safe online, but deleting the live DB files while the service is still
  writing is unsafe. Wiping auth state invalidates every issued token.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backup-dir)
            if [[ $# -lt 2 ]]; then
                echo "ERROR: --backup-dir requires a directory path" >&2
                exit 1
            fi
            BACKUP_DIR="$2"
            shift 2
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --include-auth)
            INCLUDE_AUTH=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "ERROR: sqlite3 is required for the WAL-safe backup step" >&2
    exit 1
fi

if [[ ! -f "$DB_PATH" ]]; then
    echo "ERROR: Database not found at $DB_PATH" >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"

DB_DIR="$(dirname "$DB_PATH")"
AUTH_DB_PATH="${AUTH_DB_PATH:-${DB_DIR}/auth.db}"
AUTH_KEY_PATH="${AUTH_KEY_PATH:-${DB_DIR}/auth-jwt.pem}"

TIMESTAMP=$(date -u +%Y-%m-%d-%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/syslog-pre-reset-${TIMESTAMP}.db"
ESCAPED_BACKUP_FILE="${BACKUP_FILE//\'/\'\'}"

if [[ "$FORCE" -ne 1 ]]; then
    echo "About to create a WAL-safe backup and then permanently delete:"
    echo "  $DB_PATH"
    echo "  ${DB_PATH}-wal"
    echo "  ${DB_PATH}-shm"
    if [[ "$INCLUDE_AUTH" -eq 1 ]]; then
        echo
        echo "ALSO wiping auth state (--include-auth):"
        echo "  $AUTH_DB_PATH (+ -wal, -shm)"
        echo "  $AUTH_KEY_PATH"
        echo "  WARNING: every issued access/refresh token will be invalidated."
    else
        echo
        echo "Auth state ($AUTH_DB_PATH, $AUTH_KEY_PATH) will be left in place."
        echo "Pass --include-auth to wipe it as well (rotates the JWT key)."
    fi
    echo
    echo "Backup target: $BACKUP_FILE"
    echo "Expected follow-up: restart syslog-mcp so it recreates a fresh schema."
    echo
    read -r -p "Type RESET to continue: " CONFIRM
    if [[ "$CONFIRM" != "RESET" ]]; then
        echo "Aborted."
        exit 1
    fi
fi

sqlite3 "$DB_PATH" ".backup '${ESCAPED_BACKUP_FILE}'"

rm -f "$DB_PATH" "${DB_PATH}-wal" "${DB_PATH}-shm"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"
echo "Reset complete: removed ${DB_PATH}, ${DB_PATH}-wal, and ${DB_PATH}-shm"

if [[ "$INCLUDE_AUTH" -eq 1 ]]; then
    AUTH_FILES_WIPED=0
    if [[ -f "$AUTH_DB_PATH" ]]; then
        AUTH_BACKUP_FILE="${BACKUP_DIR}/auth-pre-reset-${TIMESTAMP}.db"
        ESCAPED_AUTH_BACKUP="${AUTH_BACKUP_FILE//\'/\'\'}"
        sqlite3 "$AUTH_DB_PATH" "PRAGMA wal_checkpoint(FULL);" >/dev/null || true
        sqlite3 "$AUTH_DB_PATH" ".backup '${ESCAPED_AUTH_BACKUP}'"
        chmod 600 "$AUTH_BACKUP_FILE" 2>/dev/null || true
        rm -f "$AUTH_DB_PATH" "${AUTH_DB_PATH}-wal" "${AUTH_DB_PATH}-shm"
        echo "Auth DB backup + reset complete: ${AUTH_BACKUP_FILE}"
        AUTH_FILES_WIPED=1
    else
        echo "Auth DB not found at ${AUTH_DB_PATH}; nothing to reset"
    fi
    if [[ -f "$AUTH_KEY_PATH" ]]; then
        AUTH_KEY_BACKUP="${BACKUP_DIR}/auth-jwt-pre-reset-${TIMESTAMP}.pem"
        cp -p "$AUTH_KEY_PATH" "$AUTH_KEY_BACKUP"
        chmod 600 "$AUTH_KEY_BACKUP" 2>/dev/null || true
        rm -f "$AUTH_KEY_PATH"
        echo "Auth JWT key backup + reset complete: ${AUTH_KEY_BACKUP}"
        AUTH_FILES_WIPED=1
    else
        echo "Auth JWT key not found at ${AUTH_KEY_PATH}; nothing to reset"
    fi
    if [[ "$AUTH_FILES_WIPED" -eq 1 ]]; then
        echo "Auth state reset: every issued access/refresh token is now invalid."
    fi
fi

echo "Next step: restart syslog-mcp to recreate the database."
