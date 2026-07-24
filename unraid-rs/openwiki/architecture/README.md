---
type: "Reference"
title: "Architecture"
openwiki_generated: true
---

# Architecture

This section describes how unrust is structured and how requests flow through the system.

## Pages in this section

- **[Runtime architecture](runtime.md)** - Request flow, transport modes, auth modes, and key components
- **[Module map](module-map.md)** - Source file organization and where to make changes

## Key architectural principles

**Thin shims.** Neither the CLI nor the MCP tool layer contains business logic. They parse their input format and delegate to `UnraidService`. The service delegates to `UnraidClient`. All data retrieval is in the client's GraphQL queries.

**Action-based dispatch.** The single MCP tool `unraid` uses an `action` string parameter. `src/mcp/tools.rs` matches on `action` and calls the corresponding service method.

**GraphQL as the data layer.** `graphql.rs` POSTs to `UNRAID_API_URL` with `x-api-key: UNRAID_API_KEY`. Responses are `serde_json::Value` throughout the dispatch/CLI/MCP layers.

**Typed at the wire, Value downstream.** Most operations are defined as typed cynic structs in `gql_typed.rs`, checked against the vendored SDL at **compile time**. Operations run over the existing reqwest client and serialize back to `Value` for compatibility.

**Single source of truth.** The `ACTIONS` slice in `schemas.rs` is the only place where valid actions are defined. The schema enum, error-message action list, and MCP scope gating are all derived from it.

See [runtime.md](runtime.md) for details on how these principles play out in the request flow.
