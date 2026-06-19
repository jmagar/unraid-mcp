#!/bin/bash
# Environment Loading Library for the Unraid skill.
#
# Sources the credentials file that the plugin's setup hook materializes from the
# userConfig form. Claude Code injects CLAUDE_PLUGIN_OPTION_* only into plugin
# subprocesses (hooks/MCP/LSP), NOT into the Bash tool that runs skill scripts —
# so the hook reads those vars and writes ~/.unraid-mcp/.env, and the skill
# sources that file.
#
# In skill scripts, source as:
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "$SCRIPT_DIR/../load-env.sh"

# Prevent direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This library must be sourced, not executed directly" >&2
    exit 1
fi

# Load ~/.unraid-mcp/.env (honoring UNRAID_CREDENTIALS_DIR), with a legacy
# ~/.lab/.env fallback. Usage: load_env_file [/optional/override/path]
load_env_file() {
    local creds_dir="${UNRAID_CREDENTIALS_DIR:-$HOME/.unraid-mcp}"
    local default_file="$creds_dir/.env"
    local env_file="${1:-${UNRAID_ENV_FILE:-$default_file}}"

    if [[ ! -f "$env_file" && "$env_file" == "$default_file" && -f "$HOME/.lab/.env" ]]; then
        env_file="$HOME/.lab/.env"
    fi
    if [[ ! -f "$env_file" ]]; then
        echo "ERROR: $env_file not found" >&2
        echo "Set the plugin's Unraid GraphQL API URL / API Key in the config form" >&2
        echo "(the setup hook writes ~/.unraid-mcp/.env), or create the file manually." >&2
        return 1
    fi

    set -a
    # shellcheck source=/dev/null
    source "$env_file"
    set +a
}

# Validate that required environment variables are set and non-empty.
# Usage: validate_env_vars "VAR1" "VAR2" ...
validate_env_vars() {
    local missing=()
    for var in "$@"; do
        [[ -z "${!var:-}" ]] && missing+=("$var")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: Missing required variables: ${missing[*]}" >&2
        return 1
    fi
}

# Load and validate the default-server Unraid credentials in one call.
# Populates UNRAID_API_URL and UNRAID_API_KEY. Usage: load_unraid_credentials
load_unraid_credentials() {
    if [[ -z "${UNRAID_API_URL:-}" || -z "${UNRAID_API_KEY:-}" ]]; then
        load_env_file || return 1
    fi
    validate_env_vars UNRAID_API_URL UNRAID_API_KEY
}
