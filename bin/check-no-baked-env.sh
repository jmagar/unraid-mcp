#!/usr/bin/env bash
# check-no-baked-env.sh — Verify env vars aren't baked into Docker artifacts
# Run standalone: bash scripts/check-no-baked-env.sh [project-dir]
# Run in pre-commit: add as a hook (see .pre-commit-config.yaml example in plugin-setup-guide)
#
# Checks:
#   1. docker-compose.yaml has no `environment:` block (all config via env_file only)
#   2. Dockerfile has no ENV with real/sensitive values
#   3. No hardcoded URLs, tokens, or credentials in Dockerfile or docker-compose.yaml
set -euo pipefail

PROJECT_DIR="${1:-.}"
PASS=0
FAIL=0
WARN=0

pass() { echo "  ✓ PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }
warn() { echo "  ⚠ WARN: $1 — $2"; WARN=$((WARN + 1)); }

echo "=== No Baked Env Vars Check: $PROJECT_DIR ==="

# ── 1. docker-compose.yaml — no environment: block ───────────────────────────
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yaml"
if [[ -f "$COMPOSE_FILE" ]]; then
  # Check for environment: key under services
  if grep -qE '^\s+environment:' "$COMPOSE_FILE"; then
    fail "No environment: block in docker-compose.yaml" \
      "Found 'environment:' block — all env vars must come from env_file: .env only"
    echo "    Offending lines:"
    grep -nE '^\s+environment:|^\s+-\s+\w+=' "$COMPOSE_FILE" | head -10 | while IFS= read -r line; do
      echo "      $line"
    done
    echo
    echo "    Fix: Remove the environment: block entirely."
    echo "    Add all variables to .env and .env.example instead."
    echo "    docker-compose.yaml should only use 'env_file: .env'"
  else
    pass "No environment: block in docker-compose.yaml"
  fi

  # Verify env_file is present
  if grep -qE '^\s+env_file:' "$COMPOSE_FILE"; then
    pass "env_file: directive present"
  else
    fail "env_file: directive" "No env_file: found — services won't receive credentials"
  fi

  # Check for hardcoded values in compose environment blocks (not variable references)
  # Filter: lines that set KEY=VALUE where VALUE doesn't start with $ (variable ref)
  HARDCODED=$(grep -nE '^\s+-\s+\w+=[^$]' "$COMPOSE_FILE" | grep -vE '=(true|false)$' || true)
  if [[ -n "$HARDCODED" ]]; then
    # Filter out known safe patterns
    SUSPICIOUS=$(echo "$HARDCODED" | grep -vE '(build:|image:|container_name:|restart:|test:|interval:|timeout:|retries:|start_period:|memory:|cpus:|name:)' || true)
    if [[ -n "$SUSPICIOUS" ]]; then
      warn "Hardcoded values in compose" "Found potentially hardcoded values:"
      echo "$SUSPICIOUS" | head -5 | while IFS= read -r line; do
        echo "      $line"
      done
    fi
  fi
else
  warn "docker-compose.yaml" "File not found at $COMPOSE_FILE — skipping compose checks"
fi

# ── 2. Dockerfile — no sensitive ENV values ───────────────────────────────────
DOCKERFILE="$PROJECT_DIR/Dockerfile"
if [[ -f "$DOCKERFILE" ]]; then
  # Sensitive patterns that should never be in ENV
  SENSITIVE_RE='(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|AUTH_TOKEN|BEARER)'

  # Check ENV directives for sensitive variable names with values
  SENSITIVE_ENVS=$(grep -nE "^ENV\s+\S*${SENSITIVE_RE}\S*\s*=" "$DOCKERFILE" || true)
  if [[ -n "$SENSITIVE_ENVS" ]]; then
    fail "No sensitive ENV in Dockerfile" "Found ENV directives with sensitive variable names:"
    echo "$SENSITIVE_ENVS" | while IFS= read -r line; do
      echo "      $line"
    done
  else
    pass "No sensitive ENV in Dockerfile"
  fi

  # Check for ENV with hardcoded URLs (might contain credentials)
  URL_ENVS=$(grep -nE '^ENV\s+\S+\s*=\s*https?://' "$DOCKERFILE" || true)
  if [[ -n "$URL_ENVS" ]]; then
    warn "Hardcoded URLs in ENV" "Found ENV with hardcoded URLs (may contain credentials):"
    echo "$URL_ENVS" | while IFS= read -r line; do
      echo "      $line"
    done
  else
    pass "No hardcoded URLs in ENV"
  fi

  # Check for COPY .env into image
  if grep -qE '^COPY\s+.*\.env\s' "$DOCKERFILE"; then
    fail "No .env in image" "Dockerfile copies .env into the image — credentials will be baked in"
  else
    pass "No .env copied into image"
  fi

  # Check .dockerignore excludes .env
  DOCKERIGNORE="$PROJECT_DIR/.dockerignore"
  if [[ -f "$DOCKERIGNORE" ]]; then
    if grep -qE '^\s*\.env\s*$' "$DOCKERIGNORE"; then
      pass ".dockerignore excludes .env"
    else
      fail ".dockerignore" ".env not excluded — secrets may leak into build context"
    fi
  else
    warn ".dockerignore" "File not found — create one that excludes .env"
  fi
else
  warn "Dockerfile" "File not found at $DOCKERFILE — skipping Dockerfile checks"
fi

# ── 3. entrypoint.sh — no hardcoded credentials ──────────────────────────────
ENTRYPOINT="$PROJECT_DIR/entrypoint.sh"
if [[ -f "$ENTRYPOINT" ]]; then
  CRED_PATTERNS='(password|secret|token|api.key)\s*=\s*["\x27][^$]'
  HARDCODED_CREDS=$(grep -inE "$CRED_PATTERNS" "$ENTRYPOINT" || true)
  if [[ -n "$HARDCODED_CREDS" ]]; then
    fail "No hardcoded creds in entrypoint.sh" "Found suspicious hardcoded values:"
    echo "$HARDCODED_CREDS" | while IFS= read -r line; do
      echo "      $line"
    done
  else
    pass "No hardcoded credentials in entrypoint.sh"
  fi
else
  # entrypoint.sh is optional
  true
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
[[ "$FAIL" -eq 0 ]] && echo "NO BAKED ENV CHECK PASSED" && exit 0
echo "NO BAKED ENV CHECK FAILED" && exit 1
