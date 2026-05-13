#!/usr/bin/env bash
# SessionStart / ConfigChange hook — deploys or connects unraid-mcp based on userConfig
set -euo pipefail

# When invoked directly (e.g. for repair), the plugin runtime vars are absent.
# Derive CLAUDE_PLUGIN_ROOT from the script's own location and default
# CLAUDE_PLUGIN_DATA to the well-known plugin data directory.
: "${CLAUDE_PLUGIN_ROOT:=$(cd "$(dirname "$0")/.." && pwd)}"
: "${CLAUDE_PLUGIN_DATA:=${HOME}/.claude/plugins/data/unraid-jmagar-lab}"

# ── Helpers ───────────────────────────────────────────────────────────────────

existing_env_value() {
  local key="$1"
  local file value
  for file in "${CLAUDE_PLUGIN_DATA}/.env" "${CLAUDE_PLUGIN_DATA}/unraid-mcp.env"; do
    [[ -f "${file}" ]] || continue
    value="$(awk -F= -v key="${key}" '$1 == key {print substr($0, index($0, "=") + 1); exit}' "${file}")"
    if [[ -n "${value}" ]]; then
      printf '%s\n' "${value}"
      return 0
    fi
  done
  return 0
}

validate_port_value() {
  local name="$1" value="$2"
  if ! [[ "${value}" =~ ^[0-9]+$ ]] || (( value < 1 || value > 65535 )); then
    echo "ERROR: ${name} must be a TCP/UDP port number (1-65535), got: ${value}" >&2
    exit 1
  fi
}

mcp_host_is_loopback() {
  case "$1" in
    127.*|::1) return 0 ;;
    *) return 1 ;;
  esac
}

strip_trailing_mcp_path() {
  local url="${1%/}"
  if [[ "${url}" == */mcp ]]; then
    url="${url%/mcp}"
  fi
  printf '%s\n' "${url}"
}

derive_public_url() {
  if [[ -n "${PUBLIC_URL}" ]]; then
    strip_trailing_mcp_path "${PUBLIC_URL}"
    return
  fi
  if [[ "${SERVER_URL}" == https://* ]]; then
    strip_trailing_mcp_path "${SERVER_URL}"
  fi
}

codex_oauth_callback_url() {
  local config="${HOME}/.codex/config.toml"
  [[ -f "${config}" ]] || return 0
  awk -F= '
    $1 ~ /^[[:space:]]*mcp_oauth_callback_url[[:space:]]*$/ {
      value = $2
      sub(/^[[:space:]]*"/, "", value)
      sub(/"[[:space:]]*$/, "", value)
      print value
      exit
    }
  ' "${config}"
}

append_csv_unique() {
  local csv="$1"
  local value="$2"
  [[ -n "${value}" ]] || { printf '%s\n' "${csv}"; return; }

  local existing
  IFS=',' read -r -a existing <<< "${csv}"
  for item in "${existing[@]}"; do
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    if [[ "${item}" == "${value}" ]]; then
      printf '%s\n' "${csv}"
      return
    fi
  done

  if [[ -n "${csv}" ]]; then
    printf '%s,%s\n' "${csv}" "${value}"
  else
    printf '%s\n' "${value}"
  fi
}

oauth_env_block() {
  if [[ "${NO_AUTH}" == "true" ]]; then
    return 0
  fi
  if [[ "${AUTH_MODE}" != "bearer" && "${AUTH_MODE}" != "oauth" ]]; then
    echo "ERROR: auth_mode must be bearer or oauth" >&2
    return 1
  fi
  if [[ "${AUTH_MODE}" != "oauth" ]]; then
    return 0
  fi

  local public_url
  public_url="$(derive_public_url)"
  if [[ -z "${public_url}" ]]; then
    echo "ERROR: OAuth mode requires public_url or an https server_url" >&2
    return 1
  fi
  if [[ -z "${GOOGLE_CLIENT_ID}" || -z "${GOOGLE_CLIENT_SECRET}" || -z "${AUTH_ADMIN_EMAIL}" ]]; then
    echo "ERROR: OAuth mode requires google_client_id, google_client_secret, and auth_admin_email" >&2
    return 1
  fi

  local redirects=""
  redirects="$(append_csv_unique "${redirects}" "https://claude.ai/api/mcp/auth_callback")"
  redirects="$(append_csv_unique "${redirects}" "https://claudeai.ai/api/mcp/auth_callback")"

  local codex_callback
  codex_callback="$(codex_oauth_callback_url)"
  if [[ -n "${codex_callback}" ]]; then
    redirects="$(append_csv_unique "${redirects}" "${codex_callback}")"
  fi

  cat << EOF
UNRAID_MCP_AUTH_MODE=oauth
UNRAID_MCP_PUBLIC_URL=${public_url}
UNRAID_MCP_GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
UNRAID_MCP_GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
UNRAID_MCP_AUTH_ADMIN_EMAIL=${AUTH_ADMIN_EMAIL}
UNRAID_MCP_AUTH_ALLOWED_REDIRECT_URIS=${redirects}
EOF
}

# ── Seed token from existing env so redeploy doesn't lose it ─────────────────

NO_AUTH="${CLAUDE_PLUGIN_OPTION_NO_AUTH:-$(existing_env_value NO_AUTH)}"
NO_AUTH="${NO_AUTH:-false}"
NO_AUTH="$(printf '%s' "${NO_AUTH}" | tr '[:upper:]' '[:lower:]')"
AUTH_MODE="${CLAUDE_PLUGIN_OPTION_AUTH_MODE:-$(existing_env_value UNRAID_MCP_AUTH_MODE)}"
AUTH_MODE="${AUTH_MODE:-bearer}"
AUTH_MODE="$(printf '%s' "${AUTH_MODE}" | tr '[:upper:]' '[:lower:]')"

if [[ "${NO_AUTH}" != "true" && -z "${CLAUDE_PLUGIN_OPTION_API_TOKEN:-}" ]]; then
  _tok="$(existing_env_value UNRAID_MCP_TOKEN)"
  [[ -n "${_tok}" ]] && CLAUDE_PLUGIN_OPTION_API_TOKEN="${_tok}"
  unset _tok
fi

# ── Config from userConfig ────────────────────────────────────────────────────

USE_DOCKER="${CLAUDE_PLUGIN_OPTION_USE_DOCKER:-false}"
API_TOKEN="${CLAUDE_PLUGIN_OPTION_API_TOKEN:-}"
SERVER_URL="${CLAUDE_PLUGIN_OPTION_SERVER_URL:-http://localhost:6970}"
MCP_HOST="0.0.0.0"
MCP_PORT="${CLAUDE_PLUGIN_OPTION_MCP_PORT:-6970}"
validate_port_value UNRAID_MCP_PORT "${MCP_PORT}"
DATA_DIR="${CLAUDE_PLUGIN_OPTION_DATA_DIR:-${CLAUDE_PLUGIN_DATA}}"
PUBLIC_URL="${CLAUDE_PLUGIN_OPTION_PUBLIC_URL:-$(existing_env_value UNRAID_MCP_PUBLIC_URL)}"
GOOGLE_CLIENT_ID="${CLAUDE_PLUGIN_OPTION_GOOGLE_CLIENT_ID:-$(existing_env_value UNRAID_MCP_GOOGLE_CLIENT_ID)}"
GOOGLE_CLIENT_SECRET="${CLAUDE_PLUGIN_OPTION_GOOGLE_CLIENT_SECRET:-$(existing_env_value UNRAID_MCP_GOOGLE_CLIENT_SECRET)}"
AUTH_ADMIN_EMAIL="${CLAUDE_PLUGIN_OPTION_AUTH_ADMIN_EMAIL:-$(existing_env_value UNRAID_MCP_AUTH_ADMIN_EMAIL)}"
UNRAID_API_URL="${CLAUDE_PLUGIN_OPTION_UNRAID_API_URL:-$(existing_env_value UNRAID_API_URL)}"
UNRAID_API_KEY="${CLAUDE_PLUGIN_OPTION_UNRAID_API_KEY:-$(existing_env_value UNRAID_API_KEY)}"
UNRAID_SKIP_TLS="${CLAUDE_PLUGIN_OPTION_UNRAID_SKIP_TLS:-false}"
UNRAID_SKIP_TLS="$(printf '%s' "${UNRAID_SKIP_TLS}" | tr '[:upper:]' '[:lower:]')"

if [[ "${NO_AUTH}" != "true" && -z "${API_TOKEN}" ]]; then
  if ! [[ "${AUTH_MODE}" == "oauth" ]] || ! mcp_host_is_loopback "${MCP_HOST}"; then
    echo "ERROR: API token is required unless no_auth is true or OAuth server mode binds MCP to loopback" >&2
    exit 1
  fi
fi

# ── Paths ─────────────────────────────────────────────────────────────────────

ENV_FILE="${CLAUDE_PLUGIN_DATA}/.env"
UNIT_FILE="${HOME}/.config/systemd/user/unraid-mcp.service"
COMPOSE_DIR="${CLAUDE_PLUGIN_DATA}"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.yml"

# ── Write env file ────────────────────────────────────────────────────────────

# Returns 0 if env file was written/changed, 1 if unchanged
write_env() {
  mkdir -p "${CLAUDE_PLUGIN_DATA}"

  local new_env
  new_env=$(cat << EOF
NO_AUTH=${NO_AUTH}
UNRAID_MCP_HOST=${MCP_HOST}
UNRAID_MCP_PORT=${MCP_PORT}
RUST_LOG=info
PUID=$(id -u)
PGID=$(id -g)
EOF
)

  if [[ "${NO_AUTH}" != "true" && -n "${API_TOKEN}" ]]; then
    new_env="${new_env}
UNRAID_MCP_TOKEN=${API_TOKEN}"
  fi

  if [[ -n "${UNRAID_API_URL}" ]]; then
    new_env="${new_env}
UNRAID_API_URL=${UNRAID_API_URL}"
  fi
  if [[ -n "${UNRAID_API_KEY}" ]]; then
    new_env="${new_env}
UNRAID_API_KEY=${UNRAID_API_KEY}"
  fi
  if [[ "${UNRAID_SKIP_TLS}" == "true" ]]; then
    new_env="${new_env}
UNRAID_API_SKIP_TLS_VERIFY=true"
  fi

  local auth_block
  if ! auth_block="$(oauth_env_block)"; then
    return 2
  fi
  [[ -n "${auth_block}" ]] && new_env="${new_env}
${auth_block}"

  if [[ "${USE_DOCKER}" == "true" ]]; then
    new_env="${new_env}
UNRAID_MCP_DATA_VOLUME=${DATA_DIR}"
  fi

  if [[ -f "${ENV_FILE}" ]] && diff -q <(echo "${new_env}") "${ENV_FILE}" >/dev/null 2>&1; then
    return 1  # unchanged
  fi

  echo "${new_env}" > "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
  return 0  # changed
}

ensure_env_written() {
  local rc
  write_env; rc=$?
  if [[ "${rc}" -eq 0 || "${rc}" -eq 1 ]]; then
    return 0
  fi
  return "${rc}"
}

# ── Systemd setup ─────────────────────────────────────────────────────────────

setup_systemd() {
  mkdir -p "${HOME}/.config/systemd/user"

  if [[ ! -x "${CLAUDE_PLUGIN_ROOT}/bin/unraid" ]]; then
    echo "ERROR: unraid binary not found at ${CLAUDE_PLUGIN_ROOT}/bin/unraid" >&2
    return 1
  fi

  local service_running=false
  if systemctl --user is-active --quiet unraid-mcp.service 2>/dev/null; then
    service_running=true
  fi
  if [[ "${service_running}" == "false" ]]; then
    local port="${MCP_PORT}"
    if ss -tlnp "sport = :${port}" 2>/dev/null | awk 'NR>1 && NF>0' | grep -q .; then
      echo "ERROR: port ${port}/tcp is already in use — cannot start unraid-mcp" >&2
      return 1
    fi
  fi

  mkdir -p "${DATA_DIR}"
  if ! touch "${DATA_DIR}/.write_test" 2>/dev/null; then
    echo "ERROR: data dir ${DATA_DIR} is not writable by UID $(id -u)" >&2
    return 1
  fi
  rm -f "${DATA_DIR}/.write_test"

  # Stop docker container if one was running
  if [[ -f "${COMPOSE_FILE}" ]] && command -v docker >/dev/null 2>&1; then
    if (cd "${COMPOSE_DIR}" && docker compose ps --quiet unraid-mcp 2>/dev/null | grep -q .); then
      echo "unraid-mcp: stopping existing docker container before systemd cutover"
      (cd "${COMPOSE_DIR}" && docker compose down)
    fi
  fi

  local new_unit
  new_unit=$(cat << EOF
[Unit]
Description=unraid-mcp server
After=network.target

[Service]
ExecStart=${CLAUDE_PLUGIN_ROOT}/bin/unraid serve mcp
EnvironmentFile=${ENV_FILE}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
)

  local unit_changed=false
  if ! diff -q <(echo "${new_unit}") "${UNIT_FILE}" >/dev/null 2>&1; then
    echo "${new_unit}" > "${UNIT_FILE}"
    unit_changed=true
  fi

  ensure_env_written

  if [[ "${unit_changed}" == "true" ]]; then
    systemctl --user daemon-reload
    systemctl --user enable --now unraid-mcp
  else
    systemctl --user restart unraid-mcp
  fi

  echo "unraid-mcp: systemd service running on ${MCP_HOST}:${MCP_PORT}"
}

# ── Docker setup ──────────────────────────────────────────────────────────────

setup_docker() {
  mkdir -p "${COMPOSE_DIR}"

  if ! docker info >/dev/null 2>&1; then
    echo "ERROR: docker daemon is not reachable — is dockerd running?" >&2
    return 1
  fi

  local container_running=false
  local external_named_container=false
  if [[ -f "${COMPOSE_FILE}" ]] && \
     docker compose -f "${COMPOSE_FILE}" ps --quiet unraid-mcp 2>/dev/null | grep -q .; then
    container_running=true
  elif docker ps --filter 'name=^/unraid-mcp$' --quiet 2>/dev/null | grep -q .; then
    container_running=true
    external_named_container=true
  fi

  if [[ "${container_running}" == "false" ]]; then
    local port="${MCP_PORT}"
    if ss -tlnp "sport = :${port}" 2>/dev/null | awk 'NR>1 && NF>0' | grep -q .; then
      echo "ERROR: port ${port}/tcp is already in use — cannot start unraid-mcp" >&2
      return 1
    fi
  fi

  mkdir -p "${DATA_DIR}"
  if ! touch "${DATA_DIR}/.write_test" 2>/dev/null; then
    echo "ERROR: data dir ${DATA_DIR} is not writable by UID $(id -u)" >&2
    return 1
  fi
  rm -f "${DATA_DIR}/.write_test"

  # Remove systemd unit if switching to docker
  if systemctl --user list-unit-files unraid-mcp.service >/dev/null 2>&1; then
    if systemctl --user is-active --quiet unraid-mcp.service; then
      echo "unraid-mcp: stopping existing systemd unit before docker cutover"
      systemctl --user stop unraid-mcp.service
    fi
    if systemctl --user is-enabled --quiet unraid-mcp.service 2>/dev/null; then
      systemctl --user disable unraid-mcp.service >/dev/null 2>&1 || true
    fi
    if [[ -f "${UNIT_FILE}" ]]; then
      rm -f "${UNIT_FILE}"
      systemctl --user daemon-reload
    fi
  fi

  # Refresh compose file from plugin root
  if ! diff -q "${CLAUDE_PLUGIN_ROOT}/docker-compose.yml" "${COMPOSE_FILE}" >/dev/null 2>&1; then
    cp "${CLAUDE_PLUGIN_ROOT}/docker-compose.yml" "${COMPOSE_FILE}"
  fi

  ensure_env_written

  cd "${COMPOSE_DIR}"

  if ! docker compose config --quiet 2>/dev/null; then
    echo "WARNING: docker compose config validation failed — proceeding anyway" >&2
  fi

  local network_name="${DOCKER_NETWORK:-jakenet}"
  if ! docker network inspect "${network_name}" >/dev/null 2>&1; then
    echo "unraid-mcp: creating docker network ${network_name}"
    docker network create "${network_name}"
  fi

  if [[ "${CLAUDE_PLUGIN_OPTION_BUILD_LOCAL:-false}" == "true" && \
        -f "${CLAUDE_PLUGIN_ROOT}/Cargo.toml" && \
        -f "${CLAUDE_PLUGIN_ROOT}/config/Dockerfile" ]]; then
    (cd "${CLAUDE_PLUGIN_ROOT}" && docker compose build --no-cache unraid-mcp)
  else
    docker compose pull --quiet unraid-mcp 2>&1 || \
      echo "unraid-mcp: pull failed; will try cached image" >&2
  fi

  if [[ "${external_named_container}" == "true" ]]; then
    echo "unraid-mcp: removing existing container before docker compose cutover"
    docker rm -f unraid-mcp >/dev/null
  fi

  if docker compose ps --quiet unraid-mcp 2>/dev/null | grep -q .; then
    docker compose up -d --force-recreate --no-build
  else
    docker compose up -d --no-build
  fi

  echo "unraid-mcp: docker container running on ${MCP_HOST}:${MCP_PORT}"
}

# ── Client validate ───────────────────────────────────────────────────────────

validate_client() {
  if curl -sf "${SERVER_URL}/health" >/dev/null 2>&1; then
    echo "unraid-mcp: connected to ${SERVER_URL}"
  else
    echo "WARNING: unraid-mcp server at ${SERVER_URL} is not reachable" >&2
  fi
}

# ── Link binary into PATH ─────────────────────────────────────────────────────

link_binary() {
  mkdir -p "${HOME}/.local/bin"
  if [[ -f "${CLAUDE_PLUGIN_ROOT}/bin/unraid" ]]; then
    ln -sf "${CLAUDE_PLUGIN_ROOT}/bin/unraid" "${HOME}/.local/bin/unraid"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────

link_binary

if [[ "${USE_DOCKER}" == "true" ]]; then
  setup_docker
else
  # If binary exists in plugin root, run as systemd service.
  # If not (client-only install), just validate connectivity.
  if [[ -f "${CLAUDE_PLUGIN_ROOT}/bin/unraid" ]]; then
    setup_systemd
  else
    validate_client
  fi
fi
