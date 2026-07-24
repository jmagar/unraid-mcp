---
type: "Reference"
title: "MCP Tools"
openwiki_generated: true
---

# MCP Tools

The `unraid` MCP tool and all available actions.

## Tool overview

A single MCP tool named `unraid` is exposed. It accepts an `action` parameter to select the operation.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "unraid",
    "arguments": {
      "action": "server"
    }
  }
}
```

## Scope model

Actions have one of three scope requirements:

| Scope | Description | Actions |
|-------|-------------|---------|
| `None` | No auth required | `help` |
| `unraid:read` | Read access to Unraid data | All queries + `status` |
| `unraid:admin` | Write access to Unraid | Mutations |

**Scopes are enforced in** `src/mcp/rmcp_server.rs` via `required_scope_for(action)`. A token with `unraid:read` cannot access mutations—only `unraid:admin` satisfies write operations.

**Note:** `unraid:admin` satisfies `unraid:read` requirements. An admin-scoped token can access both read and write actions.

## Action inventory

### Core actions

| Action | Description | Scope | Parameters |
|--------|-------------|-------|------------|
| `server` | Server identity (name, IPs, URLs, status) | read | — |
| `array` | Array state, disk health, parity status, capacity | read | — |
| `disks` | Physical disks (device, model, SMART, temp, partitions) | read | — |
| `docker` | Docker containers (name, image, state, ports, updates) | read | `limit`, `offset`, `state` (MCP) |
| `docker_logs` | Container logs | read | `id` (required), `tail` |
| `vms` | Virtual machine domains (id, name, state) | read | — |
| `info` | OS, CPU, memory, versions | read | — |
| `shares` | User shares (size, used, free, cache, LUKS) | read | `limit`, `offset`, `name` (MCP) |
| `notifications` | Active warnings/alerts with overview counts | read | — |

### System actions

| Action | Description | Scope |
|--------|-------------|-------|
| `services` | System services (id, name, online, version, uptime) | read |
| `network` | Network access URLs (type, name, IPv4, IPv6) | read |
| `metrics` | Live CPU %, memory, temperature sensors | read |
| `vars` | System variables (hostname, version, timezone, flags) | read |
| `registration` | License (id, type, state, expiration) | read |
| `flash` | USB flash drive (vendor, product) | read |

### Log actions

| Action | Required args | Optional args | Description | Scope |
|--------|--------------|---------------|-------------|-------|
| `log_files` | — | — | Available log files (name, path, size, modifiedAt) | read |
| `log_file` | `path` | `lines`, `start_line` | Read a log file | read |

### Storage actions

| Action | Description | Scope |
|--------|-------------|-------|
| `parity_history` | Past parity checks (date, duration, speed, status, errors) | read |
| `rclone` | Backup remotes (name, type) and drives (name) | read |

### UPS actions

| Action | Description | Scope |
|--------|-------------|-------|
| `ups` | UPS devices (name, model, status, battery, power) | read |
| `ups_config` | UPS configuration (service, cable, device, thresholds) | read |

### Remote access actions

| Action | Description | Scope |
|--------|-------------|-------|
| `remote_access` | WAN access type, forward type, port | read |
| `connect` | Unraid Connect (enabled/running/error, settings) | read |

### Plugin actions

| Action | Description | Scope |
|--------|-------------|-------|
| `plugins` | Installed community plugins (name, version, API/CLI modules) | read |

### Meta actions

| Action | Description | Scope | Notes |
|--------|-------------|-------|-------|
| `status` | Server observability (version, PID, uptime, counters) | read | MCP-only, no CLI command |
| `help` | Markdown reference for all actions | None | No auth required |

## Mutation actions (write operations)

Mutation actions require the `unraid:admin` scope. These are available in the codebase but not exhaustively listed here—see `src/mcp/schemas.rs::ACTIONS` for the complete list.

Examples of mutation categories:
- VM management (start, stop, restart)
- Docker container operations
- Share settings modifications
- Notification management

**Note:** As of the initial documentation release, the primary focus is on read operations. Mutations follow the same dispatch pattern but require admin scope.

## Parameters

### Common parameters

| Parameter | Type | Used by | Description |
|-----------|------|---------|-------------|
| `action` | string | all | Required — operation to perform |
| `id` | string | `docker_logs` | Container ID |
| `path` | string | `log_file` | Log file path (from `log_files` response) |
| `lines` | integer | `log_file` | Number of lines to read |
| `start_line` | integer | `log_file` | Starting line number (1-indexed) |
| `tail` | integer | `docker_logs` | Log lines to return (default 100) |

### Pagination parameters (MCP-only)

| Parameter | Type | Used by | Description |
|-----------|------|---------|-------------|
| `limit` | integer | list actions | Max items per page (default 50, max 200) |
| `offset` | integer | list actions | Number of items to skip (default 0) |
| `state` | string | `docker` | Filter containers by state |
| `name` | string | `shares`, `plugins` | Filter results by name |

**Pagination envelope:** List actions return:
```json
{
  "items": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true,
  "next_offset": 50
}
```

## Response truncation

MCP tool responses are truncated at approximately **40KB** to stay within token limits. Truncation respects UTF-8 boundaries (no multi-byte character splitting).

See `src/token_limit.rs` for implementation details.

## MCP resources

| URI | MIME type | Description |
|-----|-----------|-------------|
| `unraid://schema/mcp-tool` | `application/json` | JSON Schema for the `unraid` tool and its parameters |

## MCP prompts

| Name | Description |
|------|-------------|
| `server_summary` | Template for generating a server overview summary |

## JSON Schema

The tool's JSON Schema is available via the `unraid://schema/mcp-tool` resource or in `src/mcp/schemas.rs` (derived from the `ACTIONS` slice).

## Adding a new action

See [operations/development.md](../operations/development.md#adding-a-new-action) for step-by-step instructions.

## Source references

- Action registry: `src/mcp/schemas.rs::ACTIONS`
- Dispatch logic: `src/mcp/tools.rs::dispatch_action()`
- Scope enforcement: `src/mcp/rmcp_server.rs::required_scope_for()`
- Complete inventory: `/docs/INVENTORY.md`
