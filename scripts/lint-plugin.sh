#!/usr/bin/env bash
# lint-plugin.sh — Comprehensive plugin linter for MCP server plugin repos
# Validates against conventions in docs/plugin-setup-guide.md
#
# Usage: bash scripts/lint-plugin.sh [project-dir]
#   project-dir defaults to current directory
#
# Exit codes:
#   0 — all required checks passed (warnings are OK)
#   1 — one or more required checks failed
set -euo pipefail

PROJECT_DIR="${1:-.}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✓ PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }
warn() { echo "  ⚠ WARN: $1 — $2"; WARN=$((WARN + 1)); }

echo "=== Plugin Lint: $PROJECT_DIR ==="
echo

# ── 1. Manifest files exist ──────────────────────────────────────────────────
echo "── 1. Manifests exist ──"

for manifest in \
  ".claude-plugin/plugin.json" \
  ".codex-plugin/plugin.json" \
  ".mcp.json" \
  ".app.json"; do
  if [[ -f "$PROJECT_DIR/$manifest" ]]; then
    pass "$manifest exists"
  else
    fail "$manifest" "File not found"
  fi
done
echo

# ── 2. plugin.json required fields ───────────────────────────────────────────
echo "── 2. Manifest fields (.claude-plugin/plugin.json) ──"

CLAUDE_PLUGIN="$PROJECT_DIR/.claude-plugin/plugin.json"
if [[ -f "$CLAUDE_PLUGIN" ]]; then
  for field in name version description author repository license keywords userConfig; do
    if jq -e ".$field" "$CLAUDE_PLUGIN" >/dev/null 2>&1; then
      pass "plugin.json has '$field'"
    else
      fail "plugin.json field '$field'" "Missing required field"
    fi
  done
else
  warn "plugin.json fields" "Skipped — .claude-plugin/plugin.json not found"
fi
echo

# ── 3. userConfig field validation ────────────────────────────────────────────
echo "── 3. userConfig fields ──"

if [[ -f "$CLAUDE_PLUGIN" ]] && jq -e '.userConfig' "$CLAUDE_PLUGIN" >/dev/null 2>&1; then
  USER_CONFIG_KEYS=$(jq -r '.userConfig | keys[]' "$CLAUDE_PLUGIN" 2>/dev/null || true)
  if [[ -z "$USER_CONFIG_KEYS" ]]; then
    fail "userConfig" "No userConfig entries found"
  else
    while IFS= read -r key; do
      MISSING=""
      for attr in type title description sensitive; do
        if ! jq -e ".userConfig[\"$key\"].$attr" "$CLAUDE_PLUGIN" >/dev/null 2>&1; then
          MISSING="${MISSING:+$MISSING, }$attr"
        fi
      done
      if [[ -z "$MISSING" ]]; then
        pass "userConfig.$key has all required attributes"
      else
        fail "userConfig.$key" "Missing: $MISSING"
      fi
    done <<< "$USER_CONFIG_KEYS"
  fi
else
  warn "userConfig fields" "Skipped — no userConfig in plugin.json"
fi
echo

# ── 4. Codex manifest — interface.displayName ─────────────────────────────────
echo "── 4. Codex manifest ──"

CODEX_PLUGIN="$PROJECT_DIR/.codex-plugin/plugin.json"
if [[ -f "$CODEX_PLUGIN" ]]; then
  if jq -e '.interface' "$CODEX_PLUGIN" >/dev/null 2>&1; then
    pass ".codex-plugin/plugin.json has 'interface' object"
    if jq -e '.interface.displayName' "$CODEX_PLUGIN" >/dev/null 2>&1; then
      pass "interface.displayName present"
    else
      fail "interface.displayName" "Missing in .codex-plugin/plugin.json"
    fi
  else
    fail "Codex interface" ".codex-plugin/plugin.json missing 'interface' object"
  fi
else
  warn "Codex manifest" "Skipped — .codex-plugin/plugin.json not found"
fi
echo

# ── 5. Version sync ──────────────────────────────────────────────────────────
echo "── 5. Version sync ──"

PLUGIN_VERSION=""
if [[ -f "$CLAUDE_PLUGIN" ]]; then
  PLUGIN_VERSION=$(jq -r '.version // empty' "$CLAUDE_PLUGIN" 2>/dev/null || true)
fi

if [[ -n "$PLUGIN_VERSION" ]]; then
  VERSION_CHECKED=false

  # pyproject.toml
  if [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
    PY_VERSION=$(grep -E '^\s*version\s*=' "$PROJECT_DIR/pyproject.toml" | head -1 | sed 's/.*=\s*"\(.*\)".*/\1/' || true)
    if [[ -n "$PY_VERSION" ]]; then
      VERSION_CHECKED=true
      if [[ "$PY_VERSION" == "$PLUGIN_VERSION" ]]; then
        pass "pyproject.toml version ($PY_VERSION) matches plugin.json ($PLUGIN_VERSION)"
      else
        fail "Version sync" "pyproject.toml=$PY_VERSION vs plugin.json=$PLUGIN_VERSION"
      fi
    fi
  fi

  # package.json
  if [[ -f "$PROJECT_DIR/package.json" ]]; then
    PKG_VERSION=$(jq -r '.version // empty' "$PROJECT_DIR/package.json" 2>/dev/null || true)
    if [[ -n "$PKG_VERSION" ]]; then
      VERSION_CHECKED=true
      if [[ "$PKG_VERSION" == "$PLUGIN_VERSION" ]]; then
        pass "package.json version ($PKG_VERSION) matches plugin.json ($PLUGIN_VERSION)"
      else
        fail "Version sync" "package.json=$PKG_VERSION vs plugin.json=$PLUGIN_VERSION"
      fi
    fi
  fi

  # Cargo.toml
  if [[ -f "$PROJECT_DIR/Cargo.toml" ]]; then
    CARGO_VERSION=$(grep -E '^\s*version\s*=' "$PROJECT_DIR/Cargo.toml" | head -1 | sed 's/.*=\s*"\(.*\)".*/\1/' || true)
    if [[ -n "$CARGO_VERSION" ]]; then
      VERSION_CHECKED=true
      if [[ "$CARGO_VERSION" == "$PLUGIN_VERSION" ]]; then
        pass "Cargo.toml version ($CARGO_VERSION) matches plugin.json ($PLUGIN_VERSION)"
      else
        fail "Version sync" "Cargo.toml=$CARGO_VERSION vs plugin.json=$PLUGIN_VERSION"
      fi
    fi
  fi

  if [[ "$VERSION_CHECKED" == "false" ]]; then
    warn "Version sync" "No language manifest found (pyproject.toml, package.json, Cargo.toml)"
  fi
else
  warn "Version sync" "Skipped — no version in plugin.json"
fi
echo

# ── 6. Env naming — no generic vars ──────────────────────────────────────────
echo "── 6. Env naming (no generic vars) ──"

# Generic env var patterns that should be prefixed with the service name
GENERIC_PATTERNS='^\s*(MCP_BEARER_TOKEN|API_KEY|PORT|HOST|TOKEN|SECRET|PASSWORD|AUTH_TOKEN|BEARER_TOKEN|MCP_TOKEN|MCP_PORT|MCP_HOST|DATABASE_URL|DB_URL|DB_HOST|DB_PORT|DB_NAME|DB_USER|DB_PASSWORD)\s*='

GENERIC_FOUND=false
for check_file in \
  "$PROJECT_DIR/.env.example" \
  "$PROJECT_DIR/docker-compose.yaml"; do
  if [[ -f "$check_file" ]]; then
    MATCHES=$(grep -nE "$GENERIC_PATTERNS" "$check_file" 2>/dev/null || true)
    if [[ -n "$MATCHES" ]]; then
      GENERIC_FOUND=true
      BASENAME=$(basename "$check_file")
      fail "Generic env var in $BASENAME" "All vars must be prefixed with service name"
      echo "$MATCHES" | head -5 | while IFS= read -r line; do
        echo "      $line"
      done
    fi
  fi
done

# Scan source code directories for generic env var usage
for src_dir in "$PROJECT_DIR"/*/; do
  dir_name=$(basename "$src_dir")
  # Skip non-source directories
  case "$dir_name" in
    .git|.cache|node_modules|__pycache__|target|.venv|venv|logs|backups|assets|docs|hooks|skills|commands|agents|scripts|tests|.claude-plugin|.codex-plugin|.github) continue ;;
  esac
  if [[ -d "$src_dir" ]]; then
    SRC_MATCHES=$(grep -rnE '(os\.getenv|os\.environ|env::var|process\.env)\s*\(?\s*["\x27]?(MCP_BEARER_TOKEN|API_KEY|PORT|HOST|TOKEN|SECRET|PASSWORD|AUTH_TOKEN|BEARER_TOKEN|MCP_TOKEN)["\x27]?' "$src_dir" 2>/dev/null || true)
    if [[ -n "$SRC_MATCHES" ]]; then
      GENERIC_FOUND=true
      fail "Generic env var in source ($dir_name/)" "All vars must be prefixed with service name"
      echo "$SRC_MATCHES" | head -5 | while IFS= read -r line; do
        echo "      $line"
      done
    fi
  fi
done

if [[ "$GENERIC_FOUND" == "false" ]]; then
  pass "No generic env vars found"
fi
echo

# ── 7. Tool pair — domain tool + help tool ────────────────────────────────────
echo "── 7. Tool pair (domain + help) ──"

# Derive expected tool names from plugin name
PLUGIN_NAME=""
if [[ -f "$CLAUDE_PLUGIN" ]]; then
  PLUGIN_NAME=$(jq -r '.name // empty' "$CLAUDE_PLUGIN" 2>/dev/null || true)
fi

if [[ -n "$PLUGIN_NAME" ]]; then
  # Convert plugin name (e.g. "gotify-mcp") to tool name (e.g. "gotify")
  # Strip -mcp suffix, replace hyphens with underscores
  TOOL_BASE=$(echo "$PLUGIN_NAME" | sed 's/-mcp$//' | tr '-' '_')
  HELP_TOOL="${TOOL_BASE}_help"

  # Search source code for tool registration patterns
  TOOL_FOUND=false
  HELP_FOUND=false

  # Look in all source files (Python, TypeScript, Rust)
  TOOL_PATTERN="(def ${TOOL_BASE}|\"${TOOL_BASE}\"|'${TOOL_BASE}'|name\s*=\s*\"${TOOL_BASE}\")"
  HELP_PATTERN="(def ${HELP_TOOL}|\"${HELP_TOOL}\"|'${HELP_TOOL}'|name\s*=\s*\"${HELP_TOOL}\")"

  if grep -rqE "$TOOL_PATTERN" "$PROJECT_DIR" \
    --include="*.py" --include="*.ts" --include="*.js" --include="*.rs" --include="*.mjs" \
    2>/dev/null; then
    TOOL_FOUND=true
  fi

  if grep -rqE "$HELP_PATTERN" "$PROJECT_DIR" \
    --include="*.py" --include="*.ts" --include="*.js" --include="*.rs" --include="*.mjs" \
    2>/dev/null; then
    HELP_FOUND=true
  fi

  if [[ "$TOOL_FOUND" == "true" ]]; then
    pass "Domain tool '$TOOL_BASE' found in source"
  else
    fail "Domain tool" "Expected tool '$TOOL_BASE' not found in source code"
  fi

  if [[ "$HELP_FOUND" == "true" ]]; then
    pass "Help tool '$HELP_TOOL' found in source"
  else
    fail "Help tool" "Expected tool '$HELP_TOOL' not found in source code"
  fi
else
  warn "Tool pair" "Skipped — could not determine plugin name"
fi
echo

# ── 8. Required files exist ───────────────────────────────────────────────────
echo "── 8. Required files ──"

for req_file in \
  CLAUDE.md \
  AGENTS.md \
  GEMINI.md \
  README.md \
  CHANGELOG.md \
  LICENSE \
  .gitignore \
  .env.example \
  Justfile \
  entrypoint.sh \
  Dockerfile \
  docker-compose.yaml \
  .dockerignore \
  .pre-commit-config.yaml; do
  if [[ -e "$PROJECT_DIR/$req_file" ]]; then
    pass "$req_file exists"
  else
    fail "$req_file" "Required file not found"
  fi
done
echo

# ── 9. Symlinks — AGENTS.md and GEMINI.md → CLAUDE.md ────────────────────────
echo "── 9. Symlinks ──"

for symfile in AGENTS.md GEMINI.md; do
  if [[ -L "$PROJECT_DIR/$symfile" ]]; then
    TARGET=$(readlink "$PROJECT_DIR/$symfile")
    if [[ "$TARGET" == "CLAUDE.md" || "$TARGET" == "./CLAUDE.md" ]]; then
      pass "$symfile is symlink to CLAUDE.md"
    else
      fail "$symfile symlink" "Points to '$TARGET' instead of CLAUDE.md"
    fi
  elif [[ -f "$PROJECT_DIR/$symfile" ]]; then
    fail "$symfile" "Exists but is not a symlink — must be symlink to CLAUDE.md"
  else
    fail "$symfile" "Not found — must be symlink to CLAUDE.md"
  fi
done
echo

# ── 10. Skills exist ─────────────────────────────────────────────────────────
echo "── 10. Skills ──"

SKILL_FILES=$(find "$PROJECT_DIR/skills" -name "SKILL.md" -type f 2>/dev/null || true)
if [[ -n "$SKILL_FILES" ]]; then
  SKILL_COUNT=$(echo "$SKILL_FILES" | wc -l)
  pass "Found $SKILL_COUNT SKILL.md file(s) in skills/"
else
  if [[ -d "$PROJECT_DIR/skills" ]]; then
    fail "Skills" "skills/ directory exists but no SKILL.md found (expected skills/*/SKILL.md)"
  else
    fail "Skills" "skills/ directory not found"
  fi
fi
echo

# ── 11. Hooks exist ──────────────────────────────────────────────────────────
echo "── 11. Hooks ──"

for hook_file in \
  "hooks/hooks.json" \
  "hooks/scripts/sync-env.sh" \
  "hooks/scripts/fix-env-perms.sh" \
  "hooks/scripts/ensure-ignore-files.sh"; do
  if [[ -f "$PROJECT_DIR/$hook_file" ]]; then
    pass "$hook_file exists"
  else
    fail "$hook_file" "Required hook file not found"
  fi
done
echo

# ── 12. Hook scripts executable ──────────────────────────────────────────────
echo "── 12. Hook scripts executable ──"

if [[ -d "$PROJECT_DIR/hooks/scripts" ]]; then
  HOOK_SCRIPTS=$(find "$PROJECT_DIR/hooks/scripts" -name "*.sh" -type f 2>/dev/null || true)
  if [[ -n "$HOOK_SCRIPTS" ]]; then
    while IFS= read -r script; do
      BASENAME=$(basename "$script")
      if [[ -x "$script" ]]; then
        pass "hooks/scripts/$BASENAME is executable"
      else
        fail "hooks/scripts/$BASENAME" "Not executable — run: chmod +x hooks/scripts/$BASENAME"
      fi
    done <<< "$HOOK_SCRIPTS"
  else
    warn "Hook scripts" "No .sh files found in hooks/scripts/"
  fi
else
  warn "Hook scripts" "hooks/scripts/ directory not found"
fi
echo

# ── 13. docker-compose.yaml checks ───────────────────────────────────────────
echo "── 13. docker-compose.yaml ──"

COMPOSE="$PROJECT_DIR/docker-compose.yaml"
if [[ -f "$COMPOSE" ]]; then
  # env_file: .env present
  if grep -qE '^\s+env_file:' "$COMPOSE"; then
    pass "docker-compose.yaml has env_file directive"
  else
    fail "docker-compose.yaml env_file" "No env_file: directive — services need env_file: .env"
  fi

  # user: directive present
  if grep -qE '^\s+user:' "$COMPOSE"; then
    pass "docker-compose.yaml has user: directive"
  else
    fail "docker-compose.yaml user" "No user: directive — must set user: for non-root execution"
  fi

  # NO environment: block
  if grep -qE '^\s+environment:' "$COMPOSE"; then
    fail "docker-compose.yaml environment" "Found 'environment:' block — all config must come from env_file: .env only"
  else
    pass "docker-compose.yaml has no environment: block"
  fi
else
  warn "docker-compose.yaml" "File not found — skipping compose checks"
fi
echo

# ── 14. SWAG config ──────────────────────────────────────────────────────────
echo "── 14. SWAG config ──"

SWAG_FILES=$(find "$PROJECT_DIR" -maxdepth 1 -name "*.subdomain.conf" -type f 2>/dev/null || true)
if [[ -n "$SWAG_FILES" ]]; then
  SWAG_COUNT=$(echo "$SWAG_FILES" | wc -l)
  pass "Found $SWAG_COUNT .subdomain.conf file(s)"
else
  fail "SWAG config" "No *.subdomain.conf found at repo root"
fi
echo

# ── 15. No committed secrets ─────────────────────────────────────────────────
echo "── 15. No committed secrets ──"

if git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  TRACKED_ENV=$(git -C "$PROJECT_DIR" ls-files .env 2>/dev/null || true)
  if [[ -n "$TRACKED_ENV" ]]; then
    fail "Committed .env" ".env is tracked in git — remove with: git rm --cached .env"
  else
    pass "No .env tracked in git"
  fi
else
  warn "Committed secrets" "Not a git repo — cannot check git ls-files"
fi
echo

# ── 16. Directories exist ────────────────────────────────────────────────────
echo "── 16. Required directories ──"

for req_dir in \
  "backups" \
  "logs" \
  "tests" \
  "skills"; do
  if [[ -d "$PROJECT_DIR/$req_dir" ]]; then
    pass "$req_dir/ exists"
  else
    fail "$req_dir/" "Required directory not found"
  fi
done

# Check .gitkeep files
for gitkeep in \
  "backups/.gitkeep" \
  "logs/.gitkeep"; do
  if [[ -f "$PROJECT_DIR/$gitkeep" ]]; then
    pass "$gitkeep exists"
  else
    warn "$gitkeep" "Missing — add empty .gitkeep to track empty directory"
  fi
done
echo

# ── 17. assets/ directory ────────────────────────────────────────────────────
echo "── 17. Assets directory ──"

if [[ -d "$PROJECT_DIR/assets" ]]; then
  ICON_FILES=$(find "$PROJECT_DIR/assets" -maxdepth 1 -type f \( -name "*.png" -o -name "*.svg" -o -name "*.ico" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" \) 2>/dev/null || true)
  if [[ -n "$ICON_FILES" ]]; then
    ICON_COUNT=$(echo "$ICON_FILES" | wc -l)
    pass "assets/ directory has $ICON_COUNT icon/image file(s)"
  else
    fail "assets/ icons" "assets/ directory exists but contains no icon files (png, svg, ico, jpg, webp)"
  fi
else
  fail "assets/" "assets/ directory not found — required for Codex install surfaces"
fi
echo

# ── Summary ───────────────────────────────────────────────────────────────────
echo "════════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "════════════════════════════════════════════════════════"
if [[ "$FAIL" -eq 0 ]]; then
  echo "PLUGIN LINT PASSED"
  exit 0
fi
echo "PLUGIN LINT FAILED"
exit 1
