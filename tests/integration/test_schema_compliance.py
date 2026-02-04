#!/usr/bin/env python3
"""
Unraid MCP Compliance Verification Script
=========================================

This script parses the `unraid_mcp` codebase for GraphQL queries and validates them
against the live GraphQL schema of the configured Unraid server.

It performs the following steps:
1. Connects to the Unraid API using environment variables.
2. Fetches the full GraphQL schema via introspection.
3. Parses Python files in `unraid_mcp/tools/` to extract GraphQL query strings.
4. Validates that the root fields of these queries exist in the authentic schema.
5. Reports any discrepancies or missing fields.

Usage:
    python3 verify_schema.py
"""

import ast
import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

# Add project root to path to allow imports if needed, though we primarily parse text
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Now import from the application config
try:
    from unraid_mcp.config.settings import (
        UNRAID_API_KEY,
        UNRAID_API_URL,
        UNRAID_VERIFY_SSL,
    )
except ImportError:
    # Fallback or error if not found
    print("Error: Could not import unraid_mcp.config.settings")
    sys.exit(1)

console = Console()

INTROSPECTION_QUERY = """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
          args {
            ...InputValue
          }
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }

    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
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


def extract_root_field(query: str) -> tuple[str, str | None]:
    """
    Extracts the operation type and the root field from a GraphQL query string.
    Returns (operation_type, root_field_name).
    Very basic parser: looks for 'query', 'mutation', 'subscription' and the first block.
    """
    cleaned = " ".join(query.split())  # Remove newlines and extra spaces

    op_type = "query"
    if cleaned.strip().startswith("mutation"):
        op_type = "mutation"
    elif cleaned.strip().startswith("subscription"):
        op_type = "subscription"
    elif cleaned.strip().startswith("{"):
        # Shorthand query support
        op_type = "query"

    # Remove operation definition (e.g., "query MyQuery($var: Type) {")
    # This is rough; a real parser is better but requires external deps.
    # We assume standard formatting from our codebase: "query Name { rootField ... }"
    # OR shorthand "{ rootField ... }"

    # helper to find the first opening brace
    start_idx = cleaned.find("{")
    if start_idx == -1:
        return op_type, None

    content = cleaned[start_idx + 1 :].strip()

    # The first word should be the root field
    # Stop at space, (, {, or :
    # e.g. "docker {" or "docker(arg: val)" or "alias: docker"

    # Detect alias: "myAlias: fieldName"
    # We scan for the first token. If it ends with ':' or is followed immediately by ':', it's an alias.
    i = 0
    n = len(content)
    while i < n:
        # Skip leading whitespace
        while i < n and content[i].isspace():
            i += 1

        # Start of token
        start = i
        while i < n and content[i] not in " ({:":
            i += 1

        token = content[start:i]

        if not token:
            return op_type, None

        # Check delimiter
        if i < n and content[i] == ":":
            # It was an alias, skip the colon and continue to find real field
            i += 1
            continue

        # Token found (not an alias)
        return op_type, token

    return op_type, None


class QueryCollector(ast.NodeVisitor):
    def __init__(self):
        self.queries = []  # List of (filename, lineno, query_str)

    def visit_Assign(self, node):
        """Handle assignments: x = 'query ...'"""
        self._check_value(node.value, getattr(node, "lineno", 0))
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        """Handle annotated assignments: x: str = 'query ...'"""
        if node.value:
            self._check_value(node.value, getattr(node, "lineno", 0))
        self.generic_visit(node)

    def visit_Expr(self, node):
        """Handle standalone expressions (like docstrings or Just strings)"""
        self._check_value(node.value, getattr(node, "lineno", 0))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Handle default values in function arguments."""
        # Check defaults
        for default in node.args.defaults:
            self._check_value(default, getattr(node, "lineno", 0))
        # Check kw_defaults
        for default in node.args.kw_defaults:
            if default:
                self._check_value(default, getattr(node, "lineno", 0))
        self.generic_visit(node)

    def _check_value(self, node, lineno):
        val = self._extract_string(node)
        if val:
            stripped = val.strip()
            # Simple heuristic: must look like a GraphQL operation or shorthand
            if (
                stripped.startswith("query ")
                or stripped.startswith("mutation ")
                or stripped.startswith("subscription ")
                or stripped.startswith("{")
            ) and "{" in stripped:
                self.queries.append((lineno, val))

    def _extract_string(self, node):
        """Recursively extract string content from AST nodes."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.JoinedStr):
            # f-string: try to combine parts if they are mostly constant
            # This is a best-effort extraction for simple f-strings
            parts = []
            for value in node.values:
                part = self._extract_string(value)
                if part is None:
                    return None  # Non-string part found (e.g. variable), abort
                parts.append(part)
            return "".join(parts)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            # String concatenation: "a" + "b"
            left = self._extract_string(node.left)
            right = self._extract_string(node.right)
            if left is not None and right is not None:
                return left + right
        return None


async def fetch_schema() -> dict[str, Any]:
    """Fetch schema from Unraid API."""
    if not UNRAID_API_URL or not UNRAID_API_KEY:
        console.print(
            "[bold red]Error:[/bold red] UNRAID_API_URL and UNRAID_API_KEY must be set in .env"
        )
        sys.exit(1)

    # Match the production client headers exactly (client.py)
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": UNRAID_API_KEY,
        "User-Agent": "UnraidMCPServer/0.1.0",
    }

    # Use the configured URL as-is (don't force HTTPS upgrade)
    target_url = UNRAID_API_URL

    console.print(f"[blue]Connecting to {target_url}...[/blue]")
    console.print(f"[dim]SSL verify: {UNRAID_VERIFY_SSL}[/dim]")

    # Don't follow redirects - match production client behavior
    async with httpx.AsyncClient(verify=UNRAID_VERIFY_SSL, follow_redirects=False) as client:
        try:
            response = await client.post(
                target_url, json={"query": INTROSPECTION_QUERY}, headers=headers, timeout=10.0
            )

            # Diagnostic output
            console.print(f"[dim]Status: {response.status_code}[/dim]")
            content_type = response.headers.get("content-type", "unknown")
            console.print(f"[dim]Content-Type: {content_type}[/dim]")

            if response.is_redirect:
                location = response.headers.get("location", "unknown")
                console.print(f"[yellow]Redirect to: {location}[/yellow]")
                console.print("[yellow]The API may require HTTPS or a different URL path.[/yellow]")
                sys.exit(1)

            if "text/html" in content_type:
                console.print(
                    "[bold red]Got HTML instead of JSON.[/bold red] "
                    "The URL may be wrong or the API is not enabled."
                )
                console.print(f"[dim]Response preview: {response.text[:300]}[/dim]")
                sys.exit(1)

            response.raise_for_status()
            try:
                data = response.json()
            except Exception:
                console.print(f"[bold red]Invalid JSON Response:[/bold red] {response.text[:500]}")
                raise
            if "errors" in data:
                console.print(f"[bold red]GraphQL Errors:[/bold red] {data['errors']}")
                sys.exit(1)

            # Guard against missing data or __schema
            if "data" not in data or data["data"] is None or "__schema" not in data["data"]:
                console.print(
                    "[bold red]Invalid Schema Response:[/bold red] Missing 'data.__schema'"
                )
                console.print(f"[dim]Full Response: {data}[/dim]")
                sys.exit(1)

            return data["data"]["__schema"]
        except httpx.ConnectError as e:
            console.print(f"[bold red]Connection Refused:[/bold red] {e}")
            console.print(
                "[yellow]Check that the Unraid server is reachable and the port is correct.[/yellow]"
            )
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Connection Failed:[/bold red] {e}")
            sys.exit(1)


def build_type_map(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Organize schema types by name for easy lookup."""
    type_map = {}
    for type_def in schema["types"]:
        type_map[type_def["name"]] = type_def
    return type_map


def get_root_fields(schema: dict[str, Any], type_map: dict[str, Any], op_type: str) -> set[str]:
    """Get all valid root fields for a given operation type (query/mutation)."""
    root_type_name = None
    if op_type == "query":
        root_type_name = schema.get("queryType", {}).get("name")
    elif op_type == "mutation":
        root_type_name = schema.get("mutationType", {}).get("name")
    elif op_type == "subscription":
        root_type_name = schema.get("subscriptionType", {}).get("name")

    if not root_type_name:
        return set()

    root_type = type_map.get(root_type_name)
    if not root_type:
        return set()

    fields = set()
    if "fields" in root_type and root_type["fields"]:
        for f in root_type["fields"]:
            fields.add(f["name"])
    return fields


def scan_files() -> list[tuple[str, int, str]]:
    """Scan tool files for queries."""
    tools_dir = PROJECT_ROOT / "unraid_mcp" / "tools"
    all_queries = []

    for py_file in tools_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            tree = ast.parse(content)
            collector = QueryCollector()
            collector.visit(tree)

            for lineno, query in collector.queries:
                all_queries.append((str(py_file), lineno, query))
        except Exception as e:
            console.print(f"[yellow]Failed to parse {py_file}: {e}[/yellow]")

    return all_queries


async def main():
    console.print("[bold]Unraid API Compliance Checker[/bold]")
    console.print("===================================")

    # 1. Fetch Schema
    schema = await fetch_schema()
    type_map = build_type_map(schema)

    query_root_fields = get_root_fields(schema, type_map, "query")
    mutation_root_fields = get_root_fields(schema, type_map, "mutation")
    sub_root_fields = get_root_fields(schema, type_map, "subscription")

    console.print("[green]Schema Fetched Successfully[/green]")
    console.print(f"Query Root Fields: {len(query_root_fields)}")
    console.print(f"Mutation Root Fields: {len(mutation_root_fields)}")
    console.print(f"Subscription Root Fields: {len(sub_root_fields)}")

    # 2. Scan Codebase
    console.print("\n[bold]Scanning Codebase for Queries...[/bold]")
    queries = scan_files()
    console.print(f"Found {len(queries)} GraphQL queries in codebase.")

    # 3. Validate
    table = Table(title="Compliance Report")
    table.add_column("File", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Root Field", style="blue")
    table.add_column("Status", style="green")

    # GraphQL introspection meta-fields are valid on every server per the spec
    # but don't appear in the schema's own root query field list.
    INTROSPECTION_META_FIELDS = {"__schema", "__type", "__typename"}

    issues_found = 0

    for filename, lineno, query_str in queries:
        op_type, root_field = extract_root_field(query_str)

        short_file = Path(filename).name

        if root_field is None:
            status = "[red]UNPARSEABLE: could not parse query[/red]"
            issues_found += 1
            table.add_row(f"{short_file}:{lineno}", op_type, "None", status)
            continue

        status = "[green]OK[/green]"
        valid_roots = set()

        if op_type == "query":
            valid_roots = query_root_fields
        elif op_type == "mutation":
            valid_roots = mutation_root_fields
        elif op_type == "subscription":
            valid_roots = sub_root_fields

        if root_field in INTROSPECTION_META_FIELDS:
            status = "[green]OK (introspection)[/green]"
        elif root_field not in valid_roots:
            status = f"[red]INVALID: Field '{root_field}' not found in {op_type} root[/red]"
            issues_found += 1

        table.add_row(f"{short_file}:{lineno}", op_type, root_field, status)

    console.print(table)

    if issues_found > 0:
        console.print(
            f"\n[bold red]Compliance Check Failed: Found {issues_found} invalid queries.[/bold red]"
        )
        sys.exit(1)
    else:
        console.print("\n[bold green]Compliance Check Passed![/bold green]")
        console.print("All scanned queries use valid root fields from the current API schema.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
