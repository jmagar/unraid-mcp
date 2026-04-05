# MCP UI Patterns

Protocol-level UI hints for MCP servers to improve client-side rendering of tools and results.

## Tool descriptions

The `unraid` tool includes an ASCII table in its docstring that MCP clients render when displaying tool information:

```
+-------------------+----------------------------------------------------------------------+
| action            | subactions                                                           |
+-------------------+----------------------------------------------------------------------+
| system            | overview, array, network, registration, variables, metrics, ...      |
| health            | check, test_connection, diagnose, setup                              |
| ...               | ...                                                                  |
+-------------------+----------------------------------------------------------------------+
```

This helps clients display the full action matrix without requiring a separate `unraid_help` call.

## Help tool

The `unraid_help` tool returns a complete markdown document with:
- Table of all actions and subactions
- Destructive action markers (`*`)
- Parameter reference table
- Usage examples

Clients that support markdown rendering display this as formatted documentation.

## Elicitation forms

### Credential setup form

The `_UnraidCredentials` dataclass generates a two-field form:
- `api_url` (string): "Your Unraid GraphQL endpoint"
- `api_key` (string): "Found in Unraid > Settings > Management Access > API Keys"

### Destructive confirmation form

The `_ConfirmAction` Pydantic model generates a single checkbox:
- `confirmed` (boolean, default False): "Check the box to confirm and proceed"

The confirmation message includes:
- Bold action name
- Human-readable description of the impact
- "Are you sure you want to proceed?"

### Reset confirmation

Uses a simple `bool` response type, rendering as a yes/no prompt.

## Response formatting

Tool responses are formatted for LLM consumption:

- **Health check**: Structured dict with severity indicators and recommendations
- **System overview**: Nested dict with server info, resources, array status
- **Docker list**: List of dicts with container names, states, images
- **Live data**: JSON with `_fetched_at` timestamp for staleness detection

## Error messages

`ToolError` messages are written for both human and LLM consumption:
- Include the action/subaction context
- Provide actionable next steps (e.g., "Run unraid(action='health', subaction='setup')")
- Reference environment variables and file paths when relevant

## See Also

- [TOOLS.md](TOOLS.md) -- Tool interface details
- [ELICITATION.md](ELICITATION.md) -- Interactive form patterns
- [RESOURCES.md](RESOURCES.md) -- Resource data formats
