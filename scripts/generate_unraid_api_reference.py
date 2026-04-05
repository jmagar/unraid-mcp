#!/usr/bin/env python3
"""Generate canonical Unraid GraphQL docs from live introspection."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import httpx
from graphql import build_client_schema, print_schema


DOCS_DIR = Path("docs/unraid")
DEFAULT_COMPLETE_OUTPUT = DOCS_DIR / "UNRAID-API-COMPLETE-REFERENCE.md"
DEFAULT_SUMMARY_OUTPUT = DOCS_DIR / "UNRAID-API-SUMMARY.md"
DEFAULT_INTROSPECTION_OUTPUT = DOCS_DIR / "UNRAID-API-INTROSPECTION.json"
DEFAULT_SCHEMA_OUTPUT = DOCS_DIR / "UNRAID-SCHEMA.graphql"
DEFAULT_CHANGES_OUTPUT = DOCS_DIR / "UNRAID-API-CHANGES.md"
LEGACY_INTROSPECTION_OUTPUT = Path("docs/unraid-api-introspection.json")

INTROSPECTION_QUERY = """
query FullIntrospection {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    directives {
      name
      description
      locations
      args {
        name
        description
        defaultValue
        type { ...TypeRef }
      }
    }
    types {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
        args {
          name
          description
          defaultValue
          type { ...TypeRef }
        }
        type { ...TypeRef }
      }
      inputFields {
        name
        description
        defaultValue
        type { ...TypeRef }
      }
      interfaces { kind name }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes { kind name }
    }
  }
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
"""


def _clean(text: str | None) -> str:
    """Collapse multiline description text into a single line."""
    if not text:
        return ""
    return " ".join(text.split())


def _type_to_str(type_ref: dict[str, Any] | None) -> str:
    """Render GraphQL nested type refs to SDL-like notation."""
    if not type_ref:
        return "Unknown"
    kind = type_ref.get("kind")
    if kind == "NON_NULL":
        return f"{_type_to_str(type_ref.get('ofType'))}!"
    if kind == "LIST":
        return f"[{_type_to_str(type_ref.get('ofType'))}]"
    return str(type_ref.get("name") or kind or "Unknown")


def _field_lines(field: dict[str, Any], *, is_input: bool) -> list[str]:
    """Render field/input-field markdown lines."""
    lines: list[str] = []
    lines.append(f"- `{field['name']}`: `{_type_to_str(field.get('type'))}`")

    description = _clean(field.get("description"))
    if description:
        lines.append(f"  - {description}")

    default_value = field.get("defaultValue")
    if default_value is not None:
        lines.append(f"  - Default: `{default_value}`")

    if not is_input:
        args = sorted(field.get("args") or [], key=lambda item: str(item["name"]))
        if args:
            lines.append("  - Arguments:")
            for arg in args:
                arg_line = f"    - `{arg['name']}`: `{_type_to_str(arg.get('type'))}`"
                if arg.get("defaultValue") is not None:
                    arg_line += f" (default: `{arg['defaultValue']}`)"
                lines.append(arg_line)

                arg_description = _clean(arg.get("description"))
                if arg_description:
                    lines.append(f"      - {arg_description}")

        if field.get("isDeprecated"):
            reason = _clean(field.get("deprecationReason"))
            lines.append(f"  - Deprecated: {reason}" if reason else "  - Deprecated")

    return lines


def _build_markdown(
    schema: dict[str, Any],
    *,
    include_introspection: bool,
    source: str,
    generated_at: str,
) -> str:
    """Build full Markdown schema reference."""
    all_types = schema.get("types") or []
    types = [
        item
        for item in all_types
        if item.get("name") and (include_introspection or not str(item["name"]).startswith("__"))
    ]
    types_by_name = {str(item["name"]): item for item in types}

    kind_counts = Counter(str(item.get("kind", "UNKNOWN")) for item in types)
    directives = sorted(schema.get("directives") or [], key=lambda item: str(item["name"]))

    implements_map: dict[str, list[str]] = defaultdict(list)
    for item in types:
        for interface in item.get("interfaces") or []:
            interface_name = interface.get("name")
            if interface_name:
                implements_map[str(interface_name)].append(str(item["name"]))

    query_root = (schema.get("queryType") or {}).get("name")
    mutation_root = (schema.get("mutationType") or {}).get("name")
    subscription_root = (schema.get("subscriptionType") or {}).get("name")

    lines: list[str] = []
    lines.append("# Unraid GraphQL API Complete Schema Reference")
    lines.append("")
    lines.append(f"> Generated from live GraphQL introspection on {generated_at}")
    lines.append(f"> Source: {source}")
    lines.append("")
    lines.append("This is permission-scoped: it contains everything visible to the API key used.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("- [Schema Summary](#schema-summary)")
    lines.append("- [Root Operations](#root-operations)")
    lines.append("- [Directives](#directives)")
    lines.append("- [All Types (Alphabetical)](#all-types-alphabetical)")
    lines.append("")

    lines.append("## Schema Summary")
    lines.append(f"- Query root: `{query_root}`")
    lines.append(f"- Mutation root: `{mutation_root}`")
    lines.append(f"- Subscription root: `{subscription_root}`")
    lines.append(f"- Total types: **{len(types)}**")
    lines.append(f"- Total directives: **{len(directives)}**")
    lines.append("- Type kinds:")
    lines.extend(f"- `{kind}`: {kind_counts[kind]}" for kind in sorted(kind_counts))
    lines.append("")

    def render_root(root_name: str | None, label: str) -> None:
        lines.append(f"### {label}")
        if not root_name or root_name not in types_by_name:
            lines.append("Not exposed.")
            lines.append("")
            return

        root_type = types_by_name[root_name]
        fields = sorted(root_type.get("fields") or [], key=lambda item: str(item["name"]))
        lines.append(f"Total fields: **{len(fields)}**")
        lines.append("")
        for field in fields:
            args = sorted(field.get("args") or [], key=lambda item: str(item["name"]))
            arg_signature: list[str] = []
            for arg in args:
                part = f"{arg['name']}: {_type_to_str(arg.get('type'))}"
                if arg.get("defaultValue") is not None:
                    part += f" = {arg['defaultValue']}"
                arg_signature.append(part)

            signature = (
                f"{field['name']}({', '.join(arg_signature)})"
                if arg_signature
                else f"{field['name']}()"
            )
            lines.append(f"- `{signature}: {_type_to_str(field.get('type'))}`")

            description = _clean(field.get("description"))
            if description:
                lines.append(f"  - {description}")

            if field.get("isDeprecated"):
                reason = _clean(field.get("deprecationReason"))
                lines.append(f"  - Deprecated: {reason}" if reason else "  - Deprecated")
        lines.append("")

    lines.append("## Root Operations")
    render_root(query_root, "Queries")
    render_root(mutation_root, "Mutations")
    render_root(subscription_root, "Subscriptions")

    lines.append("## Directives")
    if not directives:
        lines.append("No directives exposed.")
        lines.append("")
    else:
        for directive in directives:
            lines.append(f"### `@{directive['name']}`")
            description = _clean(directive.get("description"))
            if description:
                lines.append(description)
                lines.append("")
            locations = directive.get("locations") or []
            lines.append(
                f"- Locations: {', '.join(f'`{item}`' for item in locations) if locations else 'None'}"
            )
            args = sorted(directive.get("args") or [], key=lambda item: str(item["name"]))
            if args:
                lines.append("- Arguments:")
                for arg in args:
                    line = f"  - `{arg['name']}`: `{_type_to_str(arg.get('type'))}`"
                    if arg.get("defaultValue") is not None:
                        line += f" (default: `{arg['defaultValue']}`)"
                    lines.append(line)
                    arg_description = _clean(arg.get("description"))
                    if arg_description:
                        lines.append(f"    - {arg_description}")
            lines.append("")

    lines.append("## All Types (Alphabetical)")
    for item in sorted(types, key=lambda row: str(row["name"])):
        name = str(item["name"])
        kind = str(item["kind"])
        lines.append(f"### `{name}` ({kind})")

        description = _clean(item.get("description"))
        if description:
            lines.append(description)
            lines.append("")

        if kind == "OBJECT":
            interfaces = sorted(
                str(interface["name"])
                for interface in (item.get("interfaces") or [])
                if interface.get("name")
            )
            if interfaces:
                lines.append(f"- Implements: {', '.join(f'`{value}`' for value in interfaces)}")

            fields = sorted(item.get("fields") or [], key=lambda row: str(row["name"]))
            lines.append(f"- Fields ({len(fields)}):")
            if fields:
                for field in fields:
                    lines.extend(_field_lines(field, is_input=False))
            else:
                lines.append("- None")

        elif kind == "INPUT_OBJECT":
            fields = sorted(item.get("inputFields") or [], key=lambda row: str(row["name"]))
            lines.append(f"- Input fields ({len(fields)}):")
            if fields:
                for field in fields:
                    lines.extend(_field_lines(field, is_input=True))
            else:
                lines.append("- None")

        elif kind == "ENUM":
            enum_values = sorted(item.get("enumValues") or [], key=lambda row: str(row["name"]))
            lines.append(f"- Enum values ({len(enum_values)}):")
            if enum_values:
                for enum_value in enum_values:
                    lines.append(f"  - `{enum_value['name']}`")
                    enum_description = _clean(enum_value.get("description"))
                    if enum_description:
                        lines.append(f"    - {enum_description}")
                    if enum_value.get("isDeprecated"):
                        reason = _clean(enum_value.get("deprecationReason"))
                        lines.append(
                            f"    - Deprecated: {reason}" if reason else "    - Deprecated"
                        )
            else:
                lines.append("- None")

        elif kind == "INTERFACE":
            fields = sorted(item.get("fields") or [], key=lambda row: str(row["name"]))
            lines.append(f"- Interface fields ({len(fields)}):")
            if fields:
                for field in fields:
                    lines.extend(_field_lines(field, is_input=False))
            else:
                lines.append("- None")

            implementers = sorted(implements_map.get(name, []))
            if implementers:
                lines.append(
                    f"- Implemented by ({len(implementers)}): "
                    + ", ".join(f"`{value}`" for value in implementers)
                )
            else:
                lines.append("- Implemented by (0): None")

        elif kind == "UNION":
            possible_types = sorted(
                str(possible["name"])
                for possible in (item.get("possibleTypes") or [])
                if possible.get("name")
            )
            if possible_types:
                lines.append(
                    f"- Possible types ({len(possible_types)}): "
                    + ", ".join(f"`{value}`" for value in possible_types)
                )
            else:
                lines.append("- Possible types (0): None")

        elif kind == "SCALAR":
            lines.append("- Scalar type")

        else:
            lines.append("- Unhandled type kind")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _visible_types(
    schema: dict[str, Any], *, include_introspection: bool = False
) -> list[dict[str, Any]]:
    """Return visible types from the schema."""
    types = schema.get("types") or []
    return [
        item
        for item in types
        if item.get("name") and (include_introspection or not str(item["name"]).startswith("__"))
    ]


def _types_by_name(
    schema: dict[str, Any], *, include_introspection: bool = False
) -> dict[str, dict[str, Any]]:
    """Map visible types by name."""
    return {
        str(item["name"]): item
        for item in _visible_types(schema, include_introspection=include_introspection)
    }


def _field_signature(field: dict[str, Any]) -> str:
    """Render a stable field signature for change detection."""
    args = sorted(field.get("args") or [], key=lambda item: str(item["name"]))
    rendered_args = []
    for arg in args:
        arg_sig = f"{arg['name']}: {_type_to_str(arg.get('type'))}"
        if arg.get("defaultValue") is not None:
            arg_sig += f" = {arg['defaultValue']}"
        rendered_args.append(arg_sig)
    args_section = f"({', '.join(rendered_args)})" if rendered_args else "()"
    return f"{field['name']}{args_section}: {_type_to_str(field.get('type'))}"


def _input_field_signature(field: dict[str, Any]) -> str:
    """Render a stable input field signature for change detection."""
    signature = f"{field['name']}: {_type_to_str(field.get('type'))}"
    if field.get("defaultValue") is not None:
        signature += f" = {field['defaultValue']}"
    return signature


def _enum_value_signature(enum_value: dict[str, Any]) -> str:
    """Render a stable enum value signature for change detection."""
    signature = str(enum_value["name"])
    if enum_value.get("isDeprecated"):
        reason = _clean(enum_value.get("deprecationReason"))
        signature += f" [deprecated: {reason}]" if reason else " [deprecated]"
    return signature


def _root_field_names(schema: dict[str, Any], root_key: str) -> set[str]:
    """Return root field names for query/mutation/subscription."""
    root_type = (schema.get(root_key) or {}).get("name")
    if not root_type:
        return set()
    types = _types_by_name(schema)
    root = types.get(str(root_type))
    if not root:
        return set()
    return {str(field["name"]) for field in (root.get("fields") or [])}


def _type_member_signatures(type_info: dict[str, Any]) -> set[str]:
    """Return stable member signatures for a type."""
    kind = str(type_info.get("kind", "UNKNOWN"))
    if kind in {"OBJECT", "INTERFACE"}:
        return {_field_signature(field) for field in (type_info.get("fields") or [])}
    if kind == "INPUT_OBJECT":
        return {_input_field_signature(field) for field in (type_info.get("inputFields") or [])}
    if kind == "ENUM":
        return {_enum_value_signature(value) for value in (type_info.get("enumValues") or [])}
    if kind == "UNION":
        return {
            str(possible["name"])
            for possible in (type_info.get("possibleTypes") or [])
            if possible.get("name")
        }
    return set()


def _build_summary_markdown(
    schema: dict[str, Any], *, source: str, generated_at: str, include_introspection: bool
) -> str:
    """Build condensed root-level summary markdown."""
    types = _types_by_name(schema, include_introspection=include_introspection)
    visible_types = _visible_types(schema, include_introspection=include_introspection)
    directives = sorted(schema.get("directives") or [], key=lambda item: str(item["name"]))
    kind_counts = Counter(str(item.get("kind", "UNKNOWN")) for item in visible_types)
    query_root = (schema.get("queryType") or {}).get("name")
    mutation_root = (schema.get("mutationType") or {}).get("name")
    subscription_root = (schema.get("subscriptionType") or {}).get("name")

    lines = [
        "# Unraid API Introspection Summary",
        "",
        f"> Auto-generated from live API introspection on {generated_at}",
        f"> Source: {source}",
        "",
        "## Table of Contents",
        "",
        "- [Schema Summary](#schema-summary)",
        "- [Query Fields](#query-fields)",
        "- [Mutation Fields](#mutation-fields)",
        "- [Subscription Fields](#subscription-fields)",
        "- [Type Kinds](#type-kinds)",
        "",
        "## Schema Summary",
        f"- Query root: `{query_root}`",
        f"- Mutation root: `{mutation_root}`",
        f"- Subscription root: `{subscription_root}`",
        f"- Total types: **{len(visible_types)}**",
        f"- Total directives: **{len(directives)}**",
        "",
    ]

    def render_table(section_title: str, root_name: str | None) -> None:
        lines.append(f"## {section_title}")
        lines.append("")
        lines.append("| Field | Return Type | Arguments |")
        lines.append("|-------|-------------|-----------|")
        root = types.get(str(root_name)) if root_name else None
        for field in (
            sorted(root.get("fields") or [], key=lambda item: str(item["name"])) if root else []
        ):
            args = sorted(field.get("args") or [], key=lambda item: str(item["name"]))
            arg_text = (
                " — "
                if not args
                else ", ".join(
                    (
                        f"{arg['name']}: {_type_to_str(arg.get('type'))}"
                        + (
                            f" (default: {arg['defaultValue']})"
                            if arg.get("defaultValue") is not None
                            else ""
                        )
                    )
                    for arg in args
                )
            )
            lines.append(
                f"| `{field['name']}` | `{_type_to_str(field.get('type'))}` | {arg_text} |"
            )
        lines.append("")

    render_table("Query Fields", query_root)
    render_table("Mutation Fields", mutation_root)
    render_table("Subscription Fields", subscription_root)

    lines.append("## Type Kinds")
    lines.append("")
    for kind in sorted(kind_counts):
        lines.append(f"- `{kind}`: {kind_counts[kind]}")  # noqa: PERF401
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This summary is intentionally condensed; the full schema reference lives in `UNRAID-API-COMPLETE-REFERENCE.md`.",
            "- Raw schema exports live in `UNRAID-API-INTROSPECTION.json` and `UNRAID-SCHEMA.graphql`.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_changes_markdown(
    previous_schema: dict[str, Any] | None,
    current_schema: dict[str, Any],
    *,
    source: str,
    generated_at: str,
    include_introspection: bool,
) -> str:
    """Build a schema change report from a previous introspection snapshot."""
    lines = [
        "# Unraid API Schema Changes",
        "",
        f"> Generated on {generated_at}",
        f"> Source: {source}",
        "",
    ]
    if previous_schema is None:
        lines.extend(
            [
                "No previous introspection snapshot was available, so no diff could be computed.",
                "",
                "The current canonical artifacts were regenerated successfully.",
                "",
            ]
        )
        return "\n".join(lines)

    current_types = _types_by_name(current_schema, include_introspection=include_introspection)
    previous_types = _types_by_name(previous_schema, include_introspection=include_introspection)

    sections = [
        (
            "Query fields",
            _root_field_names(previous_schema, "queryType"),
            _root_field_names(current_schema, "queryType"),
        ),
        (
            "Mutation fields",
            _root_field_names(previous_schema, "mutationType"),
            _root_field_names(current_schema, "mutationType"),
        ),
        (
            "Subscription fields",
            _root_field_names(previous_schema, "subscriptionType"),
            _root_field_names(current_schema, "subscriptionType"),
        ),
    ]

    all_kinds = {"OBJECT", "INPUT_OBJECT", "ENUM", "INTERFACE", "UNION", "SCALAR"}
    previous_by_kind = {
        kind: {name for name, info in previous_types.items() if str(info.get("kind")) == kind}
        for kind in all_kinds
    }
    current_by_kind = {
        kind: {name for name, info in current_types.items() if str(info.get("kind")) == kind}
        for kind in all_kinds
    }

    for label, old_set, new_set in sections:
        added = sorted(new_set - old_set)
        removed = sorted(old_set - new_set)
        lines.append(f"## {label}")
        lines.append("")
        lines.append(f"- Added: {len(added)}")
        if added:
            lines.extend(f"  - `{name}`" for name in added)
        lines.append(f"- Removed: {len(removed)}")
        if removed:
            lines.extend(f"  - `{name}`" for name in removed)
        if not added and not removed:
            lines.append("- No changes")
        lines.append("")

    lines.append("## Type Changes")
    lines.append("")
    for kind in sorted(all_kinds):
        added = sorted(current_by_kind[kind] - previous_by_kind[kind])
        removed = sorted(previous_by_kind[kind] - current_by_kind[kind])
        if not added and not removed:
            continue
        lines.append(f"### {kind}")
        lines.append("")
        lines.append(f"- Added: {len(added)}")
        if added:
            lines.extend(f"  - `{name}`" for name in added)
        lines.append(f"- Removed: {len(removed)}")
        if removed:
            lines.extend(f"  - `{name}`" for name in removed)
        lines.append("")

    changed_types: list[str] = []
    for name in sorted(set(previous_types) & set(current_types)):
        previous_info = previous_types[name]
        current_info = current_types[name]
        if str(previous_info.get("kind")) != str(current_info.get("kind")):
            changed_types.append(name)
            continue
        if _type_member_signatures(previous_info) != _type_member_signatures(current_info):
            changed_types.append(name)

    lines.append("## Type Signature Changes")
    lines.append("")
    if not changed_types:
        lines.append("No existing type signatures changed.")
        lines.append("")
        return "\n".join(lines)

    for name in changed_types:
        previous_info = previous_types[name]
        current_info = current_types[name]
        previous_members = _type_member_signatures(previous_info)
        current_members = _type_member_signatures(current_info)
        added = sorted(current_members - previous_members)
        removed = sorted(previous_members - current_members)
        lines.append(f"### `{name}` ({current_info.get('kind')})")
        lines.append("")
        lines.append(f"- Added members: {len(added)}")
        if added:
            lines.extend(f"  - `{member}`" for member in added)
        lines.append(f"- Removed members: {len(removed)}")
        if removed:
            lines.extend(f"  - `{member}`" for member in removed)
        if not added and not removed and previous_info.get("kind") != current_info.get("kind"):
            lines.append(
                f"- Kind changed: `{previous_info.get('kind')}` -> `{current_info.get('kind')}`"
            )
        lines.append("")
    return "\n".join(lines)


def _extract_schema(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the __schema payload or raise."""
    schema = (payload.get("data") or {}).get("__schema")
    if not schema:
        raise SystemExit("GraphQL introspection returned no __schema payload.")
    return schema


def _load_previous_schema(path: Path) -> dict[str, Any] | None:
    """Load a prior introspection snapshot if available."""
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _extract_schema(payload)


def _write_schema_graphql(path: Path, payload: dict[str, Any]) -> None:
    """Write SDL schema output."""
    schema_graphql = print_schema(build_client_schema(payload["data"]))
    banner = (
        "# ------------------------------------------------------\n"
        "# THIS FILE WAS AUTOMATICALLY GENERATED (DO NOT MODIFY)\n"
        "# ------------------------------------------------------\n\n"
    )
    path.write_text(banner + schema_graphql.rstrip() + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    """Parse CLI args."""
    parser = argparse.ArgumentParser(
        description="Generate canonical Unraid GraphQL docs from introspection."
    )
    parser.add_argument(
        "--api-url",
        default=os.getenv("UNRAID_API_URL", ""),
        help="GraphQL endpoint URL (default: UNRAID_API_URL env var).",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("UNRAID_API_KEY", ""),
        help="API key (default: UNRAID_API_KEY env var).",
    )
    parser.add_argument(
        "--complete-output",
        type=Path,
        default=DEFAULT_COMPLETE_OUTPUT,
        help=f"Full reference output path (default: {DEFAULT_COMPLETE_OUTPUT}).",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT,
        help=f"Summary output path (default: {DEFAULT_SUMMARY_OUTPUT}).",
    )
    parser.add_argument(
        "--introspection-output",
        type=Path,
        default=DEFAULT_INTROSPECTION_OUTPUT,
        help=f"Introspection JSON output path (default: {DEFAULT_INTROSPECTION_OUTPUT}).",
    )
    parser.add_argument(
        "--schema-output",
        type=Path,
        default=DEFAULT_SCHEMA_OUTPUT,
        help=f"SDL schema output path (default: {DEFAULT_SCHEMA_OUTPUT}).",
    )
    parser.add_argument(
        "--changes-output",
        type=Path,
        default=DEFAULT_CHANGES_OUTPUT,
        help=f"Schema changes report path (default: {DEFAULT_CHANGES_OUTPUT}).",
    )
    parser.add_argument(
        "--previous-introspection",
        type=Path,
        default=None,
        help=(
            "Previous introspection JSON used for diffing. Defaults to the current "
            "introspection output path, falling back to the legacy docs path if present."
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=90.0,
        help="HTTP timeout in seconds (default: 90).",
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="Enable SSL cert verification. Default is disabled for local/self-signed setups.",
    )
    parser.add_argument(
        "--include-introspection-types",
        action="store_true",
        help="Include __Schema/__Type/etc in the generated type list.",
    )
    return parser.parse_args()


def main() -> int:
    """Run generator CLI."""
    args = _parse_args()

    if not args.api_url:
        raise SystemExit("Missing API URL. Provide --api-url or set UNRAID_API_URL.")
    if not args.api_key:
        raise SystemExit("Missing API key. Provide --api-key or set UNRAID_API_KEY.")

    headers = {"x-api-key": args.api_key, "Content-Type": "application/json"}

    with httpx.Client(timeout=args.timeout_seconds, verify=args.verify_ssl) as client:
        response = client.post(args.api_url, json={"query": INTROSPECTION_QUERY}, headers=headers)

    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        errors = json.dumps(payload["errors"], indent=2)
        raise SystemExit(f"GraphQL introspection returned errors:\n{errors}")

    schema = _extract_schema(payload)
    generated_at = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    previous_path = args.previous_introspection or (
        args.introspection_output
        if args.introspection_output.exists()
        else LEGACY_INTROSPECTION_OUTPUT
    )
    previous_schema = _load_previous_schema(previous_path)

    for path in {
        args.complete_output,
        args.summary_output,
        args.introspection_output,
        args.schema_output,
        args.changes_output,
    }:
        path.parent.mkdir(parents=True, exist_ok=True)

    full_reference = _build_markdown(
        schema,
        include_introspection=bool(args.include_introspection_types),
        source=args.api_url,
        generated_at=generated_at,
    )
    summary = _build_summary_markdown(
        schema,
        source=args.api_url,
        generated_at=generated_at,
        include_introspection=bool(args.include_introspection_types),
    )
    changes = _build_changes_markdown(
        previous_schema,
        schema,
        source=args.api_url,
        generated_at=generated_at,
        include_introspection=bool(args.include_introspection_types),
    )

    args.complete_output.write_text(full_reference, encoding="utf-8")
    args.summary_output.write_text(summary, encoding="utf-8")
    args.introspection_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_schema_graphql(args.schema_output, payload)
    args.changes_output.write_text(changes, encoding="utf-8")

    print(f"Wrote {args.complete_output}")
    print(f"Wrote {args.summary_output}")
    print(f"Wrote {args.introspection_output}")
    print(f"Wrote {args.schema_output}")
    print(f"Wrote {args.changes_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
