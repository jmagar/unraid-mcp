#!/usr/bin/env bash
# check-docker-security.sh — Verify Dockerfile follows plugin security conventions
# Run standalone: bash scripts/check-docker-security.sh [path/to/Dockerfile]
# Run in pre-commit: add as a hook (see .pre-commit-config.yaml example in plugin-setup-guide)
#
# Checks:
#   1. Multi-stage build (separate builder + runtime stages)
#   2. Non-root user (USER 1000:1000 or ${PUID}:${PGID})
#   3. No sensitive ENV directives baked into the image
#   4. HEALTHCHECK present
set -euo pipefail

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✓ PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }
warn() { echo "  ⚠ WARN: $1 — $2"; WARN=$((WARN + 1)); }

# Find Dockerfile
DOCKERFILE="${1:-Dockerfile}"
if [[ ! -f "$DOCKERFILE" ]]; then
  echo "Error: $DOCKERFILE not found" >&2
  exit 1
fi

echo "=== Docker Security Check: $DOCKERFILE ==="

# ── 1. Multi-stage build ─────────────────────────────────────────────────────
FROM_COUNT=$(grep -cE '^FROM\s' "$DOCKERFILE" || true)
if [[ "$FROM_COUNT" -ge 2 ]]; then
  pass "Multi-stage build ($FROM_COUNT stages)"
else
  fail "Multi-stage build" "Found $FROM_COUNT FROM directive(s) — need at least 2 (builder + runtime)"
fi

# Check for named stages
if grep -qE '^FROM\s.+\sAS\s+builder' "$DOCKERFILE"; then
  pass "Named builder stage"
else
  warn "Named builder stage" "No 'FROM ... AS builder' found — recommend naming stages"
fi

if grep -qE '^FROM\s.+\sAS\s+runtime' "$DOCKERFILE"; then
  pass "Named runtime stage"
else
  warn "Named runtime stage" "No 'FROM ... AS runtime' found — recommend naming stages"
fi

# ── 2. Non-root user ─────────────────────────────────────────────────────────
# Check for USER directive
if grep -qE '^USER\s' "$DOCKERFILE"; then
  USER_LINE=$(grep -E '^USER\s' "$DOCKERFILE" | tail -1)
  USER_VALUE=$(echo "$USER_LINE" | sed 's/^USER\s*//')

  # Check for 1000:1000 or variable-based UID:GID
  if echo "$USER_VALUE" | grep -qE '^\$?\{?PUID|1000:1000|1000$'; then
    pass "Non-root user ($USER_VALUE)"
  else
    warn "Non-root user" "USER is '$USER_VALUE' — expected 1000:1000 or \${PUID}:\${PGID}"
  fi
else
  # Check if docker-compose.yaml handles it via user: directive
  if [[ -f "docker-compose.yaml" ]] && grep -qE '^\s+user:' docker-compose.yaml; then
    warn "Non-root user" "No USER in Dockerfile but docker-compose.yaml sets user: — acceptable if always run via compose"
  else
    fail "Non-root user" "No USER directive found — container runs as root"
  fi
fi

# Check there's no USER root after the runtime stage
RUNTIME_START=$(grep -nE '^FROM\s.+\sAS\s+runtime' "$DOCKERFILE" | head -1 | cut -d: -f1 || true)
if [[ -n "$RUNTIME_START" ]]; then
  if tail -n +"$RUNTIME_START" "$DOCKERFILE" | grep -qE '^USER\s+root'; then
    fail "No root in runtime" "USER root found after runtime stage — never run as root in production"
  else
    pass "No root in runtime stage"
  fi
fi

# ── 3. No sensitive ENV baked in ──────────────────────────────────────────────
SENSITIVE_PATTERNS='(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|AUTH)'
BAKED_ENVS=$(grep -nE "^ENV\s+.*${SENSITIVE_PATTERNS}" "$DOCKERFILE" || true)
if [[ -n "$BAKED_ENVS" ]]; then
  fail "No baked secrets" "Sensitive ENV directives found in Dockerfile:"
  echo "$BAKED_ENVS" | while IFS= read -r line; do
    echo "    $line"
  done
else
  pass "No baked secrets in ENV directives"
fi

# Check for ARG with defaults that look like secrets
BAKED_ARGS=$(grep -nE "^ARG\s+.*${SENSITIVE_PATTERNS}.*=" "$DOCKERFILE" || true)
if [[ -n "$BAKED_ARGS" ]]; then
  warn "No baked ARG secrets" "ARG with sensitive defaults found (may leak via docker history):"
  echo "$BAKED_ARGS" | while IFS= read -r line; do
    echo "    $line"
  done
else
  pass "No baked secrets in ARG defaults"
fi

# ── 4. HEALTHCHECK ────────────────────────────────────────────────────────────
if grep -qE '^HEALTHCHECK\s' "$DOCKERFILE"; then
  pass "HEALTHCHECK directive present"
  if grep -qE '/health' "$DOCKERFILE"; then
    pass "HEALTHCHECK uses /health endpoint"
  else
    warn "HEALTHCHECK endpoint" "HEALTHCHECK doesn't reference /health — ensure it matches your health endpoint"
  fi
else
  warn "HEALTHCHECK" "No HEALTHCHECK in Dockerfile — relying on docker-compose healthcheck only"
fi

# ── 5. Dependency layer caching ───────────────────────────────────────────────
# Check that manifest files are copied before source (for layer caching)
COPY_LINES=$(grep -nE '^COPY\s' "$DOCKERFILE" || true)
FIRST_MANIFEST_COPY=""
FIRST_SOURCE_COPY=""

while IFS= read -r line; do
  linenum=$(echo "$line" | cut -d: -f1)
  content=$(echo "$line" | cut -d: -f2-)
  if echo "$content" | grep -qE '(pyproject\.toml|package.*\.json|Cargo\.(toml|lock)|go\.(mod|sum)|uv\.lock)'; then
    [[ -z "$FIRST_MANIFEST_COPY" ]] && FIRST_MANIFEST_COPY="$linenum"
  elif echo "$content" | grep -qE '\.\s+\.|src/|lib/'; then
    [[ -z "$FIRST_SOURCE_COPY" ]] && FIRST_SOURCE_COPY="$linenum"
  fi
done <<< "$COPY_LINES"

if [[ -n "$FIRST_MANIFEST_COPY" && -n "$FIRST_SOURCE_COPY" ]]; then
  if [[ "$FIRST_MANIFEST_COPY" -lt "$FIRST_SOURCE_COPY" ]]; then
    pass "Dependency manifest copied before source (layer caching)"
  else
    warn "Layer caching" "Source copied before dependency manifest — swap order for better Docker layer caching"
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
[[ "$FAIL" -eq 0 ]] && echo "DOCKER SECURITY CHECK PASSED" && exit 0
echo "DOCKER SECURITY CHECK FAILED" && exit 1
