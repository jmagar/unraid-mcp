# MCP Server Documentation

Documentation for the unraid-mcp MCP server.

## Files

| File | Description |
|------|-------------|
| [TOOLS.md](TOOLS.md) | Tool definitions, action/subaction routing, parameters, and examples |
| [RESOURCES.md](RESOURCES.md) | MCP resource URIs for live subscription data |
| [SCHEMA.md](SCHEMA.md) | Pydantic models and input validation |
| [ENV.md](ENV.md) | All environment variables with types, defaults, and sensitivity |
| [AUTH.md](AUTH.md) | Bearer token auth (inbound) and API key auth (outbound to Unraid) |
| [TRANSPORT.md](TRANSPORT.md) | stdio, streamable-http, and SSE configuration |
| [DEPLOY.md](DEPLOY.md) | Docker, local, and PyPI deployment patterns |
| [LOGS.md](LOGS.md) | Structured logging, log rotation, and error handling |
| [TESTS.md](TESTS.md) | Unit, schema, safety, property, and contract test suites |
| [MCPORTER.md](MCPORTER.md) | End-to-end HTTP and stdio smoke tests |
| [CICD.md](CICD.md) | GitHub Actions workflows for CI, Docker publish, and PyPI release |
| [PRE-COMMIT.md](PRE-COMMIT.md) | Ruff lint/format and PostToolUse hook enforcement |
| [PUBLISH.md](PUBLISH.md) | Versioning, PyPI, Docker, and MCP registry publishing |
| [CONNECT.md](CONNECT.md) | Client connection guides for Claude Code, Codex, Gemini, and direct HTTP |
| [DEV.md](DEV.md) | Day-to-day development workflow with uv and Justfile recipes |
| [ELICITATION.md](ELICITATION.md) | Interactive credential setup and destructive action confirmation |
| [PATTERNS.md](PATTERNS.md) | Common code patterns: action routing, GraphQL queries, error handling |
| [WEBMCP.md](WEBMCP.md) | Health endpoint, well-known discovery, and CORS configuration |
| [MCPUI.md](MCPUI.md) | Protocol-level UI hints for tool rendering |

## Reading Order

**New to this MCP server:**
1. ENV.md -- understand required configuration
2. AUTH.md -- set up authentication
3. TRANSPORT.md -- choose a transport and connect
4. TOOLS.md -- learn available operations (15 domains, 107 subactions)
5. RESOURCES.md -- discover live subscription data endpoints
6. ELICITATION.md -- understand the setup wizard and destructive action gates

**Experienced developers:**
- TOOLS.md and RESOURCES.md for the API surface
- ENV.md for configuration reference
- PATTERNS.md for code conventions
- TESTS.md for test suite structure

## Cross-References

- [plugin/](../plugin/) -- Plugin manifests, hooks, skills, and marketplace config
- [stack/](../stack/) -- Python/FastMCP/uv implementation details
- [upstream/](../upstream/) -- Unraid GraphQL API documentation
- [repo/](../repo/) -- Repository structure and development workflow
