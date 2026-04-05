#!/usr/bin/env bash
# ensure-ignore-files.sh — Ensure .gitignore and .dockerignore have all required patterns
#
# Modes:
#   (default)   Append missing patterns to the files (SessionStart hook)
#   --check     Report missing patterns and exit non-zero if any are missing (pre-commit/CI)
#
# Usage:
#   bash scripts/ensure-ignore-files.sh [--check] [project-dir]
#
# As a plugin hook:
#   "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/ensure-ignore-files.sh"
set -euo pipefail

CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
  CHECK_MODE=true
  shift
fi

PROJECT_DIR="${1:-${CLAUDE_PLUGIN_ROOT:-.}}"
PASS=0
FAIL=0
WARN=0

pass() { PASS=$((PASS + 1)); if $CHECK_MODE; then echo "  ✓ $1"; fi; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ FAIL: $1 — $2"; }
warn() { WARN=$((WARN + 1)); if $CHECK_MODE; then echo "  ⚠ WARN: $1 — $2"; fi; }

ensure_pattern() {
  local file="$1"
  local pattern="$2"
  local label="$3"

  if grep -qxF "$pattern" "$file" 2>/dev/null; then
    pass "$label: '$pattern'"
  elif $CHECK_MODE; then
    fail "$label: '$pattern'" "missing"
  else
    echo "$pattern" >> "$file"
    pass "$label: '$pattern' (added)"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# .gitignore — full required pattern list from plugin-setup-guide
# ═══════════════════════════════════════════════════════════════════════════════
GITIGNORE="$PROJECT_DIR/.gitignore"

if $CHECK_MODE; then echo "=== Ignore Files Check: $PROJECT_DIR ==="; echo "── .gitignore ──"; fi

if [[ ! -f "$GITIGNORE" ]] && $CHECK_MODE; then
  fail ".gitignore" "File not found — every plugin repo must have a .gitignore"
else
  touch "$GITIGNORE"

  # ── Secrets ──
  REQUIRED_GIT=(
    ".env"
    ".env.*"
    "!.env.example"
  )

  # ── Runtime / hook artifacts ──
  REQUIRED_GIT+=(
    "*.log"
  )

  # ── Claude Code / AI tooling ──
  REQUIRED_GIT+=(
    ".claude/settings.local.json"
    ".claude/worktrees/"
    ".omc/"
    ".lavra/"
    ".beads/"
    ".serena/"
    ".worktrees"
    ".full-review/"
    ".full-review-archive-*"
  )

  # ── IDE / editor ──
  REQUIRED_GIT+=(
    ".vscode/"
    ".cursor/"
    ".windsurf/"
    ".1code/"
  )

  # ── Caches ──
  REQUIRED_GIT+=(
    ".cache/"
  )

  # ── Documentation artifacts ──
  REQUIRED_GIT+=(
    "docs/plans/"
    "docs/sessions/"
    "docs/reports/"
    "docs/research/"
    "docs/superpowers/"
  )

  for pattern in "${REQUIRED_GIT[@]}"; do
    ensure_pattern "$GITIGNORE" "$pattern" ".gitignore"
  done

  # ── Language-specific (check only, don't auto-add — user must uncomment) ──
  if $CHECK_MODE; then
    if [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
      echo "  Detected: Python project"
      for p in ".venv/" "__pycache__/" "*.py[oc]" "*.egg-info/" "dist/" "build/"; do
        if grep -qxF "$p" "$GITIGNORE" 2>/dev/null; then
          pass ".gitignore (Python): '$p'"
        else
          warn ".gitignore (Python)" "'$p' not found — uncomment Python section"
        fi
      done
    fi

    if [[ -f "$PROJECT_DIR/package.json" ]]; then
      echo "  Detected: TypeScript/JavaScript project"
      for p in "node_modules/" "dist/" "build/"; do
        if grep -qxF "$p" "$GITIGNORE" 2>/dev/null; then
          pass ".gitignore (TypeScript): '$p'"
        else
          warn ".gitignore (TypeScript)" "'$p' not found — uncomment TS section"
        fi
      done
    fi

    if [[ -f "$PROJECT_DIR/Cargo.toml" ]]; then
      echo "  Detected: Rust project"
      for p in "target/"; do
        if grep -qxF "$p" "$GITIGNORE" 2>/dev/null; then
          pass ".gitignore (Rust): '$p'"
        else
          warn ".gitignore (Rust)" "'$p' not found — uncomment Rust section"
        fi
      done
    fi

    # Verify .env.example is NOT ignored
    if git -C "$PROJECT_DIR" check-ignore .env.example > /dev/null 2>&1; then
      fail ".gitignore" ".env.example is being ignored — '!.env.example' must come after '.env.*'"
    else
      pass ".gitignore: .env.example is tracked (not ignored)"
    fi
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# .dockerignore — full required pattern list from plugin-setup-guide
# ═══════════════════════════════════════════════════════════════════════════════
DOCKERIGNORE="$PROJECT_DIR/.dockerignore"

# Skip if no Dockerfile
if [[ ! -f "$PROJECT_DIR/Dockerfile" ]]; then
  if $CHECK_MODE; then echo; echo "── .dockerignore ──"; echo "  No Dockerfile found — skipping"; fi
else
  if $CHECK_MODE; then echo; echo "── .dockerignore ──"; fi

  if [[ ! -f "$DOCKERIGNORE" ]] && $CHECK_MODE; then
    fail ".dockerignore" "File not found — required when Dockerfile exists"
  else
    touch "$DOCKERIGNORE"

    # ── Version control ──
    REQUIRED_DOCKER=(
      ".git"
      ".github"
    )

    # ── Secrets ──
    REQUIRED_DOCKER+=(
      ".env"
      ".env.*"
      "!.env.example"
    )

    # ── Claude Code / AI tooling ──
    REQUIRED_DOCKER+=(
      ".claude"
      ".claude-plugin"
      ".codex-plugin"
      ".omc"
      ".lavra"
      ".beads"
      ".serena"
      ".worktrees"
      ".full-review"
      ".full-review-archive-*"
    )

    # ── IDE / editor ──
    REQUIRED_DOCKER+=(
      ".vscode"
      ".cursor"
      ".windsurf"
      ".1code"
    )

    # ── Docs, tests, scripts — not needed at runtime ──
    REQUIRED_DOCKER+=(
      "docs"
      "tests"
      "scripts"
      "*.md"
      "!README.md"
    )

    # ── Runtime artifacts ──
    REQUIRED_DOCKER+=(
      "logs"
      "backups"
      "*.log"
      ".cache"
    )

    for pattern in "${REQUIRED_DOCKER[@]}"; do
      ensure_pattern "$DOCKERIGNORE" "$pattern" ".dockerignore"
    done

    # ── Language-specific (check only) ──
    if $CHECK_MODE; then
      if [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
        for p in ".venv" "__pycache__/" "*.py[oc]" "*.egg-info" "dist/"; do
          if grep -qxF "$p" "$DOCKERIGNORE" 2>/dev/null; then
            pass ".dockerignore (Python): '$p'"
          else
            warn ".dockerignore (Python)" "'$p' not found — uncomment Python section"
          fi
        done
      fi

      if [[ -f "$PROJECT_DIR/package.json" ]]; then
        for p in "node_modules/" "dist/" "coverage/"; do
          if grep -qxF "$p" "$DOCKERIGNORE" 2>/dev/null; then
            pass ".dockerignore (TypeScript): '$p'"
          else
            warn ".dockerignore (TypeScript)" "'$p' not found — uncomment TS section"
          fi
        done
      fi

      if [[ -f "$PROJECT_DIR/Cargo.toml" ]]; then
        for p in "target/"; do
          if grep -qxF "$p" "$DOCKERIGNORE" 2>/dev/null; then
            pass ".dockerignore (Rust): '$p'"
          else
            warn ".dockerignore (Rust)" "'$p' not found — uncomment Rust section"
          fi
        done
      fi
    fi
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
if $CHECK_MODE; then
  echo
  echo "Results: $PASS passed, $FAIL failed, $WARN warnings"
  [[ "$FAIL" -eq 0 ]] && echo "IGNORE FILES CHECK PASSED" && exit 0
  echo "IGNORE FILES CHECK FAILED" && exit 1
fi
