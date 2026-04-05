# Architecture Overview -- unraid-mcp

## Component diagram

```
MCP Client (Claude Code / Codex / Gemini / HTTP)
    |
    | MCP Protocol (stdio or streamable-http)
    |
    v
+----------------------------------------------+
|  ASGI Middleware Stack                        |
|  1. HealthMiddleware     (GET /health)        |
|  2. WellKnownMiddleware  (OAuth discovery)    |
|  3. BearerAuthMiddleware (RFC 6750)           |
+----------------------------------------------+
    |
    v
+----------------------------------------------+
|  FastMCP Server                               |
|  MCP Middleware Chain:                         |
|  1. LoggingMiddleware    (request logging)     |
|  2. ErrorHandlingMiddleware (exception wrap)   |
|  3. RateLimitingMiddleware (540 req/min)       |
|  4. ResponseLimitingMiddleware (512 KB cap)    |
+----------------------------------------------+
    |
    +----> Tools (4 registered)
    |      +-- unraid (action+subaction router)
    |      |   +-- _system.py    (18 subactions)
    |      |   +-- _health.py    (4 subactions)
    |      |   +-- _array.py     (13 subactions)
    |      |   +-- _disk.py      (6 subactions)
    |      |   +-- _docker.py    (7 subactions)
    |      |   +-- _vm.py        (9 subactions)
    |      |   +-- _notification (12 subactions)
    |      |   +-- _key.py       (7 subactions)
    |      |   +-- _plugin.py    (3 subactions)
    |      |   +-- _rclone.py    (4 subactions)
    |      |   +-- _setting.py   (2 subactions)
    |      |   +-- _customization (5 subactions)
    |      |   +-- _oidc.py      (5 subactions)
    |      |   +-- _user.py      (1 subaction)
    |      |   +-- _live.py      (11 subactions)
    |      +-- unraid_help
    |      +-- diagnose_subscriptions
    |      +-- test_subscription_query
    |
    +----> Resources (10 registered)
           +-- unraid://logs/stream
           +-- unraid://live/{action} (9 subscriptions)
                |
                v
        +---------------------------+
        |  SubscriptionManager      |
        |  (WebSocket connections)  |
        +---------------------------+
                |
                | GraphQL-over-WebSocket
                | (graphql-transport-ws)
                |
                v
        +---------------------------+
        |  Unraid GraphQL API       |
        |  (upstream server)        |
        +---------------------------+
```

## Data flow

### Tool call (query)

1. Client sends `tools/call` with `action` + `subaction`
2. ASGI middleware validates bearer token (HTTP) or passes through (stdio)
3. MCP middleware logs, handles errors, checks rate limit, caps response size
4. `unraid()` routes to domain handler (e.g., `_handle_docker`)
5. Handler looks up pre-built GraphQL query from domain `_*_QUERIES` dict
6. `core/client.py` sends async HTTP request to Unraid API with `x-api-key`
7. Response parsed, formatted, returned to client

### Tool call (mutation with destructive gate)

1. Client sends `tools/call` with destructive subaction
2. `gate_destructive_action()` checks if subaction is in `_*_DESTRUCTIVE` set
3. If `confirm=True`: proceed immediately
4. If interactive client: send elicitation request with `_ConfirmAction` form
5. If user confirms: proceed; otherwise raise `ToolError`
6. Handler sends GraphQL mutation
7. Response returned to client

### Resource read (live data)

1. Client reads `unraid://live/<action>`
2. `ensure_subscriptions_started()` initializes WebSocket connections (once)
3. Resource function checks `SubscriptionManager.resource_data` cache
4. If data available: return with `_fetched_at` timestamp
5. If connecting: return "connecting" placeholder
6. If failed (terminal state): return error message
7. If auto-start disabled: fall back to `subscribe_once` one-shot query

### Credential setup (elicitation)

1. Client calls `unraid(action="health", subaction="setup")`
2. If credentials exist: probe connection, ask to reset via elicitation
3. If resetting or first run: send `_UnraidCredentials` elicitation form
4. User fills in API URL and key
5. Write to `~/.unraid-mcp/.env` (atomic: tmp + `os.replace`)
6. Apply to running process via `apply_runtime_config()`
7. Return success message

## Key design decisions

### Consolidated tool pattern

One `unraid` tool with 15 action domains instead of 15+ separate tools. This:
- Reduces MCP context window usage (one tool description covers all operations)
- Simplifies client tool selection
- Enables shared parameters across domains

**Tradeoff**: Caching is disabled because the single tool mixes reads and mutations.

### Pre-built query dicts

GraphQL queries are pre-defined in Python dicts, not constructed dynamically. This:
- Prevents GraphQL injection
- Makes queries discoverable and testable
- Enables schema validation tests (119 tests)

### Persistent subscription manager

WebSocket connections are maintained as long-running async tasks. This:
- Provides instant access to live data via MCP resources
- Reduces latency compared to on-demand connections
- Supports automatic reconnection with exponential backoff

## See Also

- [TECH.md](TECH.md) -- Technology choices
- [../mcp/PATTERNS.md](../mcp/PATTERNS.md) -- Code patterns
- [../mcp/TOOLS.md](../mcp/TOOLS.md) -- Tool reference
