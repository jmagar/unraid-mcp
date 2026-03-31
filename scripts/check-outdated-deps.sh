#!/usr/bin/env bash
# check-outdated-deps.sh — Report outdated dependencies for Python/TypeScript/Rust projects
# Run standalone: bash scripts/check-outdated-deps.sh [project-dir]
#
# Auto-detects language from manifest files and reports outdated packages.
# Exit code: 0 = all current, 1 = outdated found, 2 = tool error
#
# Not recommended for pre-commit (requires network, slow). Run periodically or in CI.
set -euo pipefail

PROJECT_DIR="${1:-.}"
FOUND_OUTDATED=0
CHECKED=0

echo "=== Outdated Dependencies Check: $PROJECT_DIR ==="
echo

# ── Python (uv) ──────────────────────────────────────────────────────────────
if [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
  CHECKED=$((CHECKED + 1))
  echo "── Python (uv) ──"

  if command -v uv &>/dev/null; then
    # Check if lock file is current
    if [[ -f "$PROJECT_DIR/uv.lock" ]]; then
      if (cd "$PROJECT_DIR" && uv lock --check 2>/dev/null); then
        echo "  ✓ uv.lock is up to date"
      else
        echo "  ⚠ uv.lock is out of sync with pyproject.toml — run 'uv lock'"
        FOUND_OUTDATED=1
      fi
    fi

    # Show outdated packages
    echo "  Checking for outdated packages..."
    OUTDATED=$(cd "$PROJECT_DIR" && uv pip list --outdated 2>/dev/null || true)
    if [[ -n "$OUTDATED" && "$OUTDATED" != *"No outdated packages"* ]]; then
      LINE_COUNT=$(echo "$OUTDATED" | wc -l)
      if [[ "$LINE_COUNT" -gt 2 ]]; then  # Header lines
        echo "$OUTDATED" | head -20
        FOUND_OUTDATED=1
      else
        echo "  ✓ All Python packages are current"
      fi
    else
      echo "  ✓ All Python packages are current"
    fi

    # Check pyproject.toml for pinned versions that may be outdated
    echo "  Checking pyproject.toml dependency pins..."
    PINNED=$(grep -E '^\s*"[^"]+==\d' "$PROJECT_DIR/pyproject.toml" 2>/dev/null || true)
    if [[ -n "$PINNED" ]]; then
      echo "  ⚠ Found exact-pinned dependencies (consider using >= or ~=):"
      echo "$PINNED" | head -10 | while IFS= read -r line; do
        echo "    $line"
      done
    fi
  else
    echo "  ⚠ uv not found — install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi
  echo
fi

# ── TypeScript / JavaScript (npm) ────────────────────────────────────────────
if [[ -f "$PROJECT_DIR/package.json" ]]; then
  CHECKED=$((CHECKED + 1))
  echo "── TypeScript / JavaScript ──"

  if command -v npm &>/dev/null; then
    echo "  Checking for outdated packages..."
    OUTDATED=$(cd "$PROJECT_DIR" && npm outdated --json 2>/dev/null || true)
    if [[ -n "$OUTDATED" && "$OUTDATED" != "{}" ]]; then
      # Parse JSON output for readable display
      echo "$OUTDATED" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data:
        print(f'  Found {len(data)} outdated package(s):')
        print(f'  {\"Package\":<30} {\"Current\":<15} {\"Wanted\":<15} {\"Latest\":<15}')
        print(f'  {\"─\"*30} {\"─\"*15} {\"─\"*15} {\"─\"*15}')
        for pkg, info in sorted(data.items()):
            current = info.get('current', '?')
            wanted = info.get('wanted', '?')
            latest = info.get('latest', '?')
            marker = ' ← MAJOR' if current.split('.')[0] != latest.split('.')[0] else ''
            print(f'  {pkg:<30} {current:<15} {wanted:<15} {latest:<15}{marker}')
except (json.JSONDecodeError, KeyError):
    print('  ⚠ Could not parse npm outdated output')
" 2>/dev/null || echo "  ⚠ Could not parse npm outdated output"
      FOUND_OUTDATED=1
    else
      echo "  ✓ All npm packages are current"
    fi

    # Check for npm audit vulnerabilities
    echo "  Checking for known vulnerabilities..."
    AUDIT=$(cd "$PROJECT_DIR" && npm audit --json 2>/dev/null || true)
    VULN_COUNT=$(echo "$AUDIT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    total = data.get('metadata', {}).get('vulnerabilities', {})
    count = sum(v for k, v in total.items() if k != 'info')
    print(count)
except:
    print(0)
" 2>/dev/null || echo "0")
    if [[ "$VULN_COUNT" -gt 0 ]]; then
      echo "  ⚠ Found $VULN_COUNT known vulnerabilities — run 'npm audit' for details"
    else
      echo "  ✓ No known vulnerabilities"
    fi
  else
    echo "  ⚠ npm not found"
  fi
  echo
fi

# ── Rust (cargo) ──────────────────────────────────────────────────────────────
if [[ -f "$PROJECT_DIR/Cargo.toml" ]]; then
  CHECKED=$((CHECKED + 1))
  echo "── Rust (cargo) ──"

  if command -v cargo &>/dev/null; then
    # Check if cargo-outdated is installed
    if cargo outdated --version &>/dev/null 2>&1; then
      echo "  Checking for outdated crates..."
      OUTDATED=$(cd "$PROJECT_DIR" && cargo outdated --root-deps-only 2>/dev/null || true)
      if echo "$OUTDATED" | grep -qE '^\w'; then
        echo "$OUTDATED" | head -20
        FOUND_OUTDATED=1
      else
        echo "  ✓ All Rust crates are current"
      fi
    else
      echo "  ⚠ cargo-outdated not installed — install with: cargo install cargo-outdated"
      echo "  Falling back to Cargo.lock age check..."

      if [[ -f "$PROJECT_DIR/Cargo.lock" ]]; then
        LOCK_AGE_DAYS=$(( ($(date +%s) - $(stat -c %Y "$PROJECT_DIR/Cargo.lock")) / 86400 ))
        if [[ "$LOCK_AGE_DAYS" -gt 30 ]]; then
          echo "  ⚠ Cargo.lock is $LOCK_AGE_DAYS days old — consider running 'cargo update'"
        else
          echo "  ✓ Cargo.lock updated within last 30 days ($LOCK_AGE_DAYS days ago)"
        fi
      fi
    fi

    # Check for cargo audit
    if cargo audit --version &>/dev/null 2>&1; then
      echo "  Checking for known vulnerabilities..."
      if (cd "$PROJECT_DIR" && cargo audit --quiet 2>/dev/null); then
        echo "  ✓ No known vulnerabilities"
      else
        echo "  ⚠ Vulnerabilities found — run 'cargo audit' for details"
        FOUND_OUTDATED=1
      fi
    else
      echo "  ⚠ cargo-audit not installed — install with: cargo install cargo-audit"
    fi
  else
    echo "  ⚠ cargo not found"
  fi
  echo
fi

# ── Summary ───────────────────────────────────────────────────────────────────
if [[ "$CHECKED" -eq 0 ]]; then
  echo "No recognized project manifests found (pyproject.toml, package.json, Cargo.toml)"
  exit 2
fi

echo "=== Summary ==="
if [[ "$FOUND_OUTDATED" -eq 0 ]]; then
  echo "All dependencies are current across $CHECKED project(s)."
  exit 0
else
  echo "Outdated dependencies found. Review above and update as needed."
  exit 1
fi
