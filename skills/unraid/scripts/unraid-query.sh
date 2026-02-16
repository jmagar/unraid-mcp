#!/bin/bash
# Unraid GraphQL API Query Helper
# Makes it easy to query the Unraid API from the command line

set -e

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Query the Unraid GraphQL API

OPTIONS:
    -u, --url URL          Unraid server URL (required)
    -k, --key KEY          API key (required)
    -q, --query QUERY      GraphQL query (required)
    -f, --format FORMAT    Output format: json (default), raw, pretty
    --ignore-errors        Continue if GraphQL returns data alongside errors
    --insecure             Disable TLS certificate verification
    -h, --help             Show this help message

ENVIRONMENT VARIABLES:
    UNRAID_URL             Default Unraid server URL
    UNRAID_API_KEY         Default API key

EXAMPLES:
    # Get system status
    $0 -u https://unraid.local/graphql -k YOUR_KEY -q "{ online }"

    # Use environment variables
    export UNRAID_URL="https://unraid.local/graphql"
    export UNRAID_API_KEY="your-api-key"
    $0 -q "{ metrics { cpu { percentTotal } } }"

    # Pretty print output
    $0 -q "{ array { state } }" -f pretty

EOF
    exit 1
}

# Default values
URL="${UNRAID_URL:-}"
API_KEY="${UNRAID_API_KEY:-}"
QUERY=""
FORMAT="json"
IGNORE_ERRORS="${IGNORE_ERRORS:-false}"
INSECURE="false"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -k|--key)
            API_KEY="$2"
            shift 2
            ;;
        -q|--query)
            QUERY="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        --ignore-errors)
            IGNORE_ERRORS="true"
            shift
            ;;
        --insecure)
            INSECURE="true"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$URL" ]]; then
    echo "Error: Unraid URL is required (use -u or set UNRAID_URL)"
    exit 1
fi

if [[ -z "$API_KEY" ]]; then
    echo "Error: API key is required (use -k or set UNRAID_API_KEY)"
    exit 1
fi

if [[ -z "$QUERY" ]]; then
    echo "Error: GraphQL query is required (use -q)"
    exit 1
fi

# Build JSON payload with proper escaping
PAYLOAD=$(jq -n --arg q "$QUERY" '{"query": $q}')

# Build curl flags
CURL_FLAGS=("-sL" "-X" "POST")
[[ "$INSECURE" == "true" ]] && CURL_FLAGS+=("-k")

# Make the request
RESPONSE=$(curl "${CURL_FLAGS[@]}" "$URL" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $API_KEY" \
    -d "$PAYLOAD") || {
    echo "Error: curl request failed (exit code $?). Check URL and network connectivity." >&2
    exit 1
}

if [[ -z "$RESPONSE" ]]; then
    echo "Error: Empty response from server." >&2
    exit 1
fi

if ! echo "$RESPONSE" | jq -e . > /dev/null 2>&1; then
    echo "Error: Server returned invalid JSON. Response:" >&2
    echo "$RESPONSE" | head -c 500 >&2
    exit 1
fi

# Check for errors
if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    # If we have data despite errors and --ignore-errors was passed, continue
    if [[ "$IGNORE_ERRORS" == "true" ]] && echo "$RESPONSE" | jq -e '.data' > /dev/null 2>&1; then
        echo "GraphQL Warning:" >&2
        echo "$RESPONSE" | jq -r '.errors[0].message' >&2
    else
        echo "GraphQL Error:" >&2
        echo "$RESPONSE" | jq -r '.errors[0].message' >&2
        exit 1
    fi
fi

# Output based on format
case "$FORMAT" in
    json)
        echo "$RESPONSE"
        ;;
    raw)
        echo "$RESPONSE" | jq -r '.data'
        ;;
    pretty)
        echo "$RESPONSE" | jq '.'
        ;;
    *)
        echo "Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac
