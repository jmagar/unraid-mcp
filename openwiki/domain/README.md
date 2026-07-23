---
type: "Reference"
title: "Domain"
openwiki_generated: true
---

# Domain

Core concepts and data models in unrust.

## Pages in this section

- **[MCP tools](mcp-tools.md)** - The `unraid` MCP tool, available actions, scope model, and pagination
- **[GraphQL API integration](graphql-api.md)** - Unraid GraphQL client, typed operations, and schema management

## Key domain concepts

**Action-based dispatch.** A single `unraid` MCP tool accepts an `action` parameter to select operations. All valid actions are defined in `src/mcp/schemas.rs::ACTIONS`—the single source of truth.

**Scope model.** Actions require either no scope (meta actions like `help`), `unraid:read` (queries), or `unraid:admin` (mutations). Scopes are enforced in the MCP layer via `required_scope_for(action)`.

**GraphQL as the data layer.** All data retrieval happens via GraphQL queries to the Unraid API. Queries are typed at compile time via cynic and validated against the vendored SDL.

**Schema as contract.** The vendored Unraid SDL (`schema/unraid-schema.graphql`) is the source of truth for what fields and types are available. A CI job runs daily to detect schema drift.

See [mcp-tools.md](mcp-tools.md) for the complete action inventory and [graphql-api.md](graphql-api.md) for details on the GraphQL integration.
