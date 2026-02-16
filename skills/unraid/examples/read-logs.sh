#!/bin/bash
# Read Unraid system logs
# Usage: ./read-logs.sh [log-name] [lines]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUERY_SCRIPT="$SCRIPT_DIR/../scripts/unraid-query.sh"

LOG_NAME="${1:-syslog}"
LINES="${2:-20}"

# Validate inputs to prevent GraphQL injection
if ! [[ "$LOG_NAME" =~ ^[a-zA-Z0-9_./-]+$ ]]; then
    echo "Error: Invalid log name. Only alphanumeric characters, dots, slashes, hyphens, and underscores are allowed." >&2
    exit 1
fi
if ! [[ "$LINES" =~ ^[0-9]+$ ]]; then
    echo "Error: Lines must be a positive integer." >&2
    exit 1
fi

echo "=== Reading $LOG_NAME (last $LINES lines) ==="
echo ""

QUERY="{ logFile(path: \"$LOG_NAME\", lines: $LINES) { path totalLines startLine content } }"

RESPONSE=$("$QUERY_SCRIPT" -q "$QUERY" -f raw)

echo "$RESPONSE" | jq -r '.logFile.content'

echo ""
echo "---"
echo "Total lines in log: $(echo "$RESPONSE" | jq -r '.logFile.totalLines')"
echo "Showing from line: $(echo "$RESPONSE" | jq -r '.logFile.startLine')"
