#!/usr/bin/env -S uv run python
"""Print the complete GraphQL operation inventory for live smoke tooling."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_cases() -> list[tuple[str, str, str]]:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    from tests.schema.operation_inventory import all_operation_cases

    return all_operation_cases()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    rows = [
        {"action": action, "subaction": subaction, "operation": _operation_name(query)}
        for action, subaction, query in _load_cases()
    ]

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0

    width_action = max(len(row["action"]) for row in rows)
    width_subaction = max(len(row["subaction"]) for row in rows)
    for row in rows:
        print(
            f"{row['action']:<{width_action}}  "
            f"{row['subaction']:<{width_subaction}}  "
            f"{row['operation']}"
        )
    print(f"\n{len(rows)} GraphQL operations")
    return 0


def _operation_name(query: str) -> str:
    words = query.strip().split()
    if len(words) >= 2 and words[0] in {"query", "mutation", "subscription"}:
        return words[1].split("(", 1)[0]
    return words[0] if words else ""


if __name__ == "__main__":
    raise SystemExit(main())
