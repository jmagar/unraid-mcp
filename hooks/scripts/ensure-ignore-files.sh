#!/usr/bin/env bash
set -euo pipefail

CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
  CHECK_MODE=true
fi

GITIGNORE="${CLAUDE_PLUGIN_ROOT}/.gitignore"

REQUIRED=(
  ".env"
  ".env.*"
  "!.env.example"
  "backups/*"
  "!backups/.gitkeep"
  "logs/*"
  "!logs/.gitkeep"
  "__pycache__/"
)

if [ "$CHECK_MODE" = true ]; then
  missing=()
  for pattern in "${REQUIRED[@]}"; do
    if ! grep -qxF "$pattern" "$GITIGNORE" 2>/dev/null; then
      missing+=("$pattern")
    fi
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    echo "ensure-ignore-files: missing patterns in .gitignore:" >&2
    for p in "${missing[@]}"; do
      echo "  $p" >&2
    done
    exit 1
  fi
  exit 0
fi

touch "$GITIGNORE"

existing="$(cat "$GITIGNORE")"
for pattern in "${REQUIRED[@]}"; do
  if ! grep -qxF "$pattern" "$GITIGNORE" 2>/dev/null; then
    existing+=$'\n'"$pattern"
  fi
done

GITIGNORE_TMP="${GITIGNORE}.tmp.$$"
# Join REQUIRED with RS separator (|) — none of the patterns contain |
_pat_list="$(IFS='|'; printf '%s' "${REQUIRED[*]}")"
printf '%s\n' "$existing" | awk -v pat_list="$_pat_list" '
  BEGIN {
    n_pat = split(pat_list, ordered, "|")
    for (i = 1; i <= n_pat; i++) want[ordered[i]] = 1
  }
  { lines[++n]=$0 }
  END {
    emitted[""] = 1
    for (i = 1; i <= n; i++) {
      if (!want[lines[i]] && !emitted[lines[i]]) {
        print lines[i]
        emitted[lines[i]] = 1
      }
    }
    for (i = 1; i <= n_pat; i++) {
      if (!emitted[ordered[i]]) {
        print ordered[i]
        emitted[ordered[i]] = 1
      }
    }
  }
' > "$GITIGNORE_TMP" && mv "$GITIGNORE_TMP" "$GITIGNORE"
