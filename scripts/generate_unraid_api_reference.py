#!/usr/bin/env python3
"""Generate a complete Markdown reference from Unraid GraphQL introspection."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import httpx


DEFAULT_OUTPUT = Path("docs/UNRAID_API_COMPLETE_REFERENCE.md")

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


def _build_markdown(schema: dict[str, Any], *, include_introspection: bool) -> str:
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
    lines.append(
        "Generated via live GraphQL introspection for the configured endpoint and API key."
    )
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


def _parse_args() -> argparse.Namespace:
    """Parse CLI args."""
    parser = argparse.ArgumentParser(
        description="Generate complete Unraid GraphQL schema reference Markdown from introspection."
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
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output markdown file path (default: {DEFAULT_OUTPUT}).",
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

    headers = {"Authorization": f"Bearer {args.api_key}", "Content-Type": "application/json"}

    with httpx.Client(timeout=args.timeout_seconds, verify=args.verify_ssl) as client:
        response = client.post(args.api_url, json={"query": INTROSPECTION_QUERY}, headers=headers)

    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        errors = json.dumps(payload["errors"], indent=2)
        raise SystemExit(f"GraphQL introspection returned errors:\n{errors}")

    schema = (payload.get("data") or {}).get("__schema")
    if not schema:
        raise SystemExit("GraphQL introspection returned no __schema payload.")

    markdown = _build_markdown(schema, include_introspection=bool(args.include_introspection_types))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
