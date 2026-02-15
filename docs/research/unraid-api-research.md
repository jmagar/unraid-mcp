# Unraid API Research Findings

**Date:** 2026-02-07
**Research Topic:** Unraid GraphQL API, Connect Cloud Service, MCP Integration
**Specialist:** NotebookLM Deep Research
**Notebook ID:** 4e217d5d-d68b-4bfa-881a-42f7c01d3e44

## Research Summary

- **Deep research mode:** deep (47 web sources discovered)
- **Sources indexed:** 51 ready / 77 total (26 error)
- **Q&A questions asked:** 23 comprehensive questions with follow-ups
- **Deep research status:** completed
- **Key source categories:** Official Unraid docs, GitHub repos, community forums, GraphQL references, third-party integrations

---

## Table of Contents

1. [Unraid API Overview](#1-unraid-api-overview)
2. [Architecture and Deployment](#2-architecture-and-deployment)
3. [Authentication and Security](#3-authentication-and-security)
4. [GraphQL Schema and Endpoints](#4-graphql-schema-and-endpoints)
5. [WebSocket Subscriptions](#5-websocket-subscriptions)
6. [Unraid Connect Cloud Service](#6-unraid-connect-cloud-service)
7. [Version History and API Changes](#7-version-history-and-api-changes)
8. [Community Integrations](#8-community-integrations)
9. [Known Issues and Limitations](#9-known-issues-and-limitations)
10. [API Roadmap and Future Features](#10-api-roadmap-and-future-features)
11. [Recommendations for unraid-mcp](#11-recommendations-for-unraid-mcp)
12. [Source Bibliography](#12-source-bibliography)

---

## 1. Unraid API Overview

The **Unraid API** is a programmatic interface that provides automation, monitoring, and integration capabilities for Unraid servers. It uses a **GraphQL** interface, offering a modern, strongly-typed method for developers and third-party applications to interact directly with the Unraid operating system.

### Key Facts

- **Protocol:** GraphQL (queries, mutations, subscriptions)
- **Endpoint:** `http(s)://[SERVER_IP]/graphql`
- **Authentication:** API Keys, Session Cookies, SSO/OIDC
- **Native since:** Unraid 7.2 (no plugin required)
- **Pre-7.2:** Requires Unraid Connect plugin installation

The API exposes nearly all management functions available in the Unraid WebGUI, including server management, storage operations, Docker/VM lifecycle, remote access, and backup capabilities.

**Sources:**
- [Welcome to Unraid API | Unraid Docs](https://docs.unraid.net/API/) -- Official API landing page [Tier: Primary]
- [Using the Unraid API](https://docs.unraid.net/API/how-to-use-the-api/) -- Official usage guide [Tier: Primary]

---

## 2. Architecture and Deployment

### Monorepo Structure

The Unraid API is developed in the [unraid/api](https://github.com/unraid/api) monorepo which houses:

| Directory | Purpose |
|-----------|---------|
| `api/` | GraphQL backend server (TypeScript/Node.js) |
| `web/` | Frontend interface (Nuxt/Vue.js) |
| `plugin/` | Unraid plugin packaging (.plg format) |
| `packages/` | Shared internal libraries |
| `unraid-ui/` | UI component library |
| `scripts/` | Build and maintenance utilities |

### Technology Stack

| Component | Technology |
|-----------|------------|
| Primary language | TypeScript (77.4%) |
| Frontend | Vue.js (11.8%) via Nuxt |
| Runtime | Node.js v22 |
| Package manager | pnpm v9.0+ |
| API protocol | GraphQL |
| Dev environment | Nix (optional), Docker |
| Build tool | Justfile |

### Deployment Modes

1. **Native (Unraid 7.2+):** API is built into the OS, starts automatically with the system. Managed via **Settings > Management Access > API**.
2. **Plugin (Pre-7.2):** Requires installing the Unraid Connect plugin from Community Applications. Installing the plugin on 7.2+ provides access to newer API features before they are merged into the stable OS release.
3. **Development:** Supports local Docker builds (`pnpm run docker:build-and-run` on port 5858), direct deployment to a running server (`pnpm unraid:deploy <SERVER_IP>`), and hot-reloading dev servers (API port 3001, Web port 3000).

### Integration with Nginx

The API integrates with Unraid's Nginx web server. Nginx acts as a reverse proxy, handling external requests on standard web ports (80/443) and routing `/graphql` traffic to the internal API backend. This means the API shares the same IP and port as the WebGUI.

**Sources:**
- [GitHub - unraid/api: Unraid API / Connect / UI Monorepo](https://github.com/unraid/api) [Tier: Official]
- [api/api/docs/developer/development.md](https://github.com/unraid/api/blob/main/api/docs/developer/development.md) [Tier: Official]

---

## 3. Authentication and Security

### Authentication Methods

The Unraid API supports three primary authentication mechanisms:

1. **API Keys** -- Standard method for programmatic access
   - Created via WebGUI: **Settings > Management Access > API Keys**
   - Created via CLI: `unraid-api apikey --create --name "mykey" --roles ADMIN --json`
   - Sent in HTTP header: `x-api-key: YOUR_API_KEY`
   - Displayed only once upon creation

2. **Session Cookies** -- Used for browser-based WebGUI access
   - Automatic when logged into WebGUI
   - Used internally by the GraphQL Sandbox

3. **SSO / OIDC (OpenID Connect)** -- Enterprise identity management
   - Added in API v4.0.0
   - Supports external identity providers

### API Key Authorization Flow (OAuth-like)

For third-party applications, Unraid provides an OAuth-like authorization flow:

1. App redirects user to: `https://[server]/ApiKeyAuthorize?name=MyApp&scopes=docker:read,vm:*&redirect_uri=https://myapp.com/callback&state=abc123`
2. User authenticates (if not already logged in)
3. User sees consent screen with requested permissions
4. Upon approval, API key is created and shown to user once
5. If `redirect_uri` provided, user is redirected with `?api_key=xxx&state=abc123`

**Query Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Application name |
| `scopes` | Yes | Comma-separated permissions (e.g., `docker:read,vm:*`) |
| `redirect_uri` | No | HTTPS callback URL (localhost allowed for dev) |
| `state` | No | CSRF prevention token |

### Programmatic API Key Management (CLI)

```bash
# Create a key with admin role
unraid-api apikey --create --name "workflow key" --roles ADMIN --json

# Create a key with specific permissions
unraid-api apikey --create --name "monitor" --permissions "DOCKER:READ_ANY,ARRAY:READ_ANY" --json

# Overwrite existing key
unraid-api apikey --create --name "workflow key" --roles ADMIN --overwrite --json

# Delete a key
unraid-api apikey --delete --name "workflow key"
```

### Roles and Permissions

**Roles (pre-defined access levels):**

| Role | Description |
|------|-------------|
| `ADMIN` | Full system access (all permissions) |
| `VIEWER` | Read-only access |
| `GUEST` | Limited access |
| `CONNECT` | Unraid Connect cloud features |

**Permission Scope Format:** `RESOURCE:ACTION`

**Available Resources:**
- Core: `ACTIVATION_CODE`, `API_KEY`, `CONFIG`, `CUSTOMIZATIONS`, `INFO`, `LOGS`, `OS`, `REGISTRATION`, `VARS`, `WELCOME`
- Storage: `ARRAY`, `DISK`, `FLASH`
- Services: `DOCKER`, `VMS`, `SERVICES`, `NETWORK`
- Management: `DASHBOARD`, `DISPLAY`, `ME`, `NOTIFICATIONS`, `OWNER`, `PERMISSION`, `SHARE`, `USER`
- Cloud: `CLOUD`, `CONNECT`, `CONNECT__REMOTE_ACCESS`, `ONLINE`, `SERVERS`

**Available Actions:**
- `CREATE_ANY`, `CREATE_OWN`
- `READ_ANY`, `READ_OWN`
- `UPDATE_ANY`, `UPDATE_OWN`
- `DELETE_ANY`, `DELETE_OWN`
- `*` (wildcard for all actions)

### SSL/TLS Certificate Handling

| Scenario | Recommendation |
|----------|---------------|
| Self-signed cert (local IP) | Either trust the specific CA or disable SSL verification (dev only) |
| `myunraid.net` cert (Let's Encrypt) | SSL verification works normally; use the `myunraid.net` URL |
| Strict SSL mode | Enforces HTTPS for all connections including local |

For self-signed certs in client code:
```bash
curl -k "https://your-unraid-server/graphql" -H "x-api-key: YOUR_KEY"
```

**Sources:**
- [API key authorization flow | Unraid Docs](https://docs.unraid.net/API/api-key-app-developer-authorization-flow/) [Tier: Primary]
- [Programmatic API key management | Unraid Docs](https://docs.unraid.net/API/programmatic-api-key-management/) [Tier: Primary]

---

## 4. GraphQL Schema and Endpoints

### Endpoint URLs

| Purpose | URL |
|---------|-----|
| GraphQL API | `http(s)://[SERVER_IP]/graphql` |
| GraphQL Sandbox | `http(s)://[SERVER_IP]/graphql` (must be enabled) |
| WebSocket (subscriptions) | `ws(s)://[SERVER_IP]/graphql` |
| Internal dev API | `http://localhost:3001/graphql` |

### Enabling the GraphQL Sandbox

Two methods:
1. **WebGUI:** Settings > Management Access > Developer Options > Toggle GraphQL Sandbox to "On"
2. **CLI:** `unraid-api developer --sandbox true`

Then access at `http://YOUR_SERVER_IP/graphql` to explore the schema via Apollo Sandbox.

### Query Types

#### System Information (`info`)
```graphql
query {
  info {
    os { platform distro release uptime hostname arch kernel }
    cpu { manufacturer brand cores threads }
    memory { layout { bank type clockSpeed manufacturer } }
    baseboard { manufacturer model version serial }
    system { manufacturer model version serial uuid }
    versions { kernel docker unraid node }
    apps { installed started }
    machineId
    time
  }
}
```

#### Array Status (`array`)
```graphql
query {
  array {
    id
    state
    capacity {
      kilobytes { free used total }
      disks { free used total }
    }
    boot { id name device size status temp fsType }
    parities { id name device size status temp numErrors }
    disks { id name device size status temp numReads numWrites numErrors }
    caches { id name device size status temp }
  }
}
```

#### Docker Containers (`docker`)
```graphql
query {
  docker {
    containers(skipCache: false) {
      id names image state status autoStart
      ports { ip privatePort publicPort type }
      labels
      networkSettings
      mounts
    }
  }
}
```

#### Virtual Machines (`vms`)
```graphql
query {
  vms {
    id
    domains {
      id name state uuid
    }
  }
}
```

#### Network (`network`)
```graphql
query {
  network {
    id
    accessUrls { type name ipv4 ipv6 }
  }
}
```

#### Registration (`registration`)
```graphql
query {
  registration {
    id type state expiration updateExpiration
    keyFile { location contents }
  }
}
```

#### Settings (`settings`)
```graphql
query {
  settings {
    unified { values }
  }
}
```

#### System Variables (`vars`)
```graphql
query {
  vars {
    id version name timeZone security workgroup
    useSsl port portssl
    shareSmbEnabled shareNfsEnabled
    mdState mdVersion
    csrfToken
    # Many more fields available -- some have Int overflow issues
  }
}
```

#### RClone Remotes (`rclone`)

```graphql
query {
  rclone {
    remotes { name type parameters config }
    configForm(formOptions: { providerType: "s3" }) {
      id dataSchema uiSchema
    }
  }
}
```

#### Notifications

```graphql
query {
  notifications {
    id subject message importance unread
  }
}
```

#### Shares

```graphql
query {
  shares {
    name comment free used
  }
}
```

### Mutation Types

#### Docker Container Management

```graphql
mutation {
  docker {
    start(id: $id) { id names state status }
    stop(id: $id) { id names state status }
  }
}
```
- Uses `PrefixedID` type for container identification
- Mutations are idempotent (starting an already-running container returns success)

#### VM Management

```graphql
mutation {
  vm {
    start(id: $id)    # Returns Boolean
    stop(id: $id)
    pause(id: $id)
    resume(id: $id)
    forceStop(id: $id)
    reboot(id: $id)
    reset(id: $id)
  }
}
```

#### RClone Remote Management
```graphql
mutation {
  rclone {
    createRCloneRemote(input: { name: "...", type: "s3", config: {...} }) {
      name type parameters
    }
    deleteRCloneRemote(input: { name: "..." })
  }
}
```

#### System Operations (via API)
The following operations are confirmed available through the API (exact mutation names should be discovered via introspection):
- Array start/stop
- Parity check trigger
- Server reboot/shutdown
- Flash backup trigger
- Notification management

### The `PrefixedID` Type

The API uses a `PrefixedID` custom scalar type for global object identification. This follows the GraphQL `Node` interface pattern, combining the object type and its internal ID (e.g., `DockerContainer:abc123`). Client libraries must handle this as a string.

### The `Long` Scalar Type

The API defines a custom `Long` scalar type for 64-bit integers to handle values that exceed the standard GraphQL `Int` (32-bit signed). This is used for:
- Disk/array capacity values (size, free, used, total)
- Memory values (total, free)
- Disk operation counters (numReads, numWrites)

These are typically serialized as strings in JSON responses.

**Sources:**
- [Welcome to Unraid API | Unraid Docs](https://docs.unraid.net/API/) [Tier: Primary]
- [Using the Unraid API](https://docs.unraid.net/API/how-to-use-the-api/) [Tier: Primary]
- [GitHub - jmagar/unraid-mcp](https://github.com/jmagar/unraid-mcp) [Tier: Official]

---

## 5. WebSocket Subscriptions

### Protocol

The Unraid API uses the **`graphql-transport-ws`** protocol (the modern standard, superseding the older `subscriptions-transport-ws`).

### Connection Flow

1. Client connects to `ws(s)://[SERVER_IP]/graphql`
2. Client sends `connection_init` with auth payload:
   ```json
   {
     "type": "connection_init",
     "payload": {
       "x-api-key": "YOUR_API_KEY"
     }
   }
   ```
3. Server responds with `connection_ack`
4. Client sends `subscribe` message with GraphQL subscription query
5. Server streams `next` messages with data as events occur
6. Server sends `complete` when subscription ends

### Known Subscription Types

| Subscription | Purpose |
|-------------|---------|
| `syslog` / `logFile` | Real-time system log streaming |
| Array events | State changes, parity check progress |
| Docker events | Container state changes |
| Notifications | Real-time alert streaming |

### Authentication for WebSockets

Since standard WebSocket APIs in browsers cannot set custom headers, the API key is passed in the `connectionParams` payload of the `connection_init` message. Alternatively, session cookies work automatically for WebGUI-based tools.

### Infrastructure Notes

- Unraid uses **Nchan** (Nginx module) for WebSocket connections internally
- Unraid 7.0.1 fixed Nchan memory leaks affecting subscription stability
- Unraid 7.1.0 added automatic Nchan shared memory recovery (restarts Nginx when memory runs out)
- A setting was added in 7.1.0 to disable real-time updates on inactive browsers to prevent memory issues

**Sources:**
- [Subscriptions - GraphQL](https://graphql.org/learn/subscriptions/) [Tier: Primary]
- [Subscriptions - Apollo GraphQL Docs](https://www.apollographql.com/docs/react/data/subscriptions) [Tier: Official]

---

## 6. Unraid Connect Cloud Service

### Overview

**Unraid Connect** is a cloud-enabled companion service that functions as a centralized "remote command center" for Unraid servers. It provides:

- **Centralized Dashboard:** View status, uptime, storage, and license details for multiple servers
- **Remote Management:** Start/stop arrays, manage Docker/VMs, reboot servers
- **Flash Backup:** Automated cloud-based backups of USB flash drive configuration
- **Deep Linking:** Jump directly from cloud dashboard to local WebGUI pages

### Relationship to Local API

- Pre-7.2: The Unraid Connect plugin provides both cloud features AND the local GraphQL API
- Post-7.2: The API is native to the OS; the Connect plugin adds cloud features
- The cloud dashboard communicates through a secure tunnel to execute commands locally

### Data Transmitted to Cloud

The local server transmits to `Unraid.net`:
- Server hostname and keyfile details
- Local/remote IP addresses
- Array usage statistics (numbers only, no file names)
- Container and VM counts

**Privacy:** The service explicitly does NOT collect or share user content, file details, or personal information beyond necessary metadata.

### Remote Access Mechanisms

1. **Dynamic Remote Access (Recommended):**
   - On-demand; WebGUI closed to internet by default
   - Uses UPnP for automatic port forwarding (or manual rules)
   - Port lease expires after inactivity (~10 minutes)

2. **Static Remote Access:**
   - Always-on; WebGUI continuously accessible
   - Requires forwarding WAN port (high random number >1000) to HTTPS port

3. **VPN Alternatives:**
   - WireGuard (built-in)
   - Tailscale (native since Unraid 7.0+)

### Flash Backup Details

- Configuration files are encrypted and uploaded
- Excludes sensitive data: passwords, WireGuard keys
- Retained as latest backup only; older/inactive backups are purged
- Can be triggered and monitored via the API

**Sources:**
- [Unraid Connect overview & setup | Unraid Docs](https://docs.unraid.net/connect/about/) [Tier: Primary]
- [Remote access | Unraid Docs](https://docs.unraid.net/connect/remote-access/) [Tier: Primary]
- [Automated flash backup | Unraid Docs](https://docs.unraid.net/connect/flash-backup/) [Tier: Primary]

---

## 7. Version History and API Changes

### Unraid 7.0.0 (2025-01-09)

**Developer & System Capabilities:**
- Notification agents stored as individual XML files (easier programmatic management)
- `Content-Security-Policy frame-ancestors` support (iframe embedding for dashboards)
- JavaScript console logging restored
- VM Manager inline XML mode (read-only libvirt XML view)
- Docker PID limits (default 2048)
- Full ZFS support (hybrid pools, subpools, encryption)
- Native Tailscale integration
- File Manager merged into core OS
- QEMU snapshots and clones for VMs

**Note:** API was still plugin-based (Unraid Connect plugin required).

### Unraid 7.0.1 (2025-02-25)

- **Nchan memory leak fix** -- Critical for WebSocket subscription stability
- Tailscale integration security restrictions for Host-network containers

### Unraid 7.1.0 (2025-05-05)

- **Nchan shared memory recovery** -- Automatic Nginx restart on memory exhaustion
- **Real-time updates toggle** -- Disable updates on inactive browsers
- Native WiFi support (`wlan0`) -- New network interface data
- User VM templates (create, export, import)
- CSS rework for WebGUI

### Unraid 7.2.0 (Stable Release)

**Major Milestone: API becomes native to the OS.**

- No plugin required for local API access
- API starts automatically with system
- Deep system integration
- Settings accessible at **Settings > Management Access > API**
- OIDC/SSO support added
- Permissions system rewritten (API v4.0.0)
- Built-in GraphQL Sandbox
- CLI key management (`unraid-api apikey`)
- Open-sourced API code

**Sources:**
- [Version 7.0.0 | Unraid Docs](https://docs.unraid.net/unraid-os/release-notes/7.0.0/) [Tier: Primary]
- [Version 7.0.1 | Unraid Docs](https://docs.unraid.net/unraid-os/release-notes/7.0.1/) [Tier: Primary]
- [Version 7.1.0 | Unraid Docs](https://docs.unraid.net/unraid-os/release-notes/7.1.0/) [Tier: Primary]
- [Unraid 7.2.0 Blog Post](https://unraid.net/blog/unraid-7-2-0) [Tier: Official]

---

## 8. Community Integrations

### Third-Party Projects Using the Unraid API

#### 1. unraid-mcp (Python MCP Server) -- This Project
- **Interface:** Official Unraid GraphQL API via HTTP/HTTPS + WebSockets
- **Auth:** `UNRAID_API_URL` + `UNRAID_API_KEY` environment variables
- **Transport:** HTTP header `X-API-Key` for queries; WebSocket `connection_init` payload for subscriptions
- **Tools:** 26+ MCP tools for Docker, VM, storage, system management

#### 2. PSUnraid (PowerShell Module)
- **Developer:** Community member "Jagula"
- **Status:** Alpha / proof of concept
- **Interface:** Official Unraid GraphQL API
- **Install:** `Install-Module PSUnraid`
- **Capabilities:** Server/array/disk status, Docker/VM start/stop/restart, notifications
- **Requires:** Unraid 7.2.2+ for full feature support
- **Key insight:** Remote-only (no SSH needed), converts JSON to PowerShell objects

#### 3. unraid-management-agent (Go Plugin)
- **Interface:** **NOT** the official GraphQL API -- independent REST API + WebSocket
- **Port:** Default 8043
- **Architecture:** Standalone Go binary, collects data via native libraries
- **Endpoints:** 50+ REST endpoints, `/metrics` for Prometheus, WebSocket at `/api/v1/ws`
- **Integrations:** Prometheus (41 metrics), MQTT, Home Assistant (auto-discovery), MCP (54 tools)
- **Key insight:** Provides data the official API lacks (SMART data, container logs, process monitoring, GPU stats, UPS data)

#### 4. unraid-ssh-mcp
- **Interface:** SSH (explicitly chose NOT to use GraphQL API)
- **Reason:** API lacked container logs, SMART data, real-time CPU load, process monitoring
- **Advantage:** Works on any Unraid version, no rate limits

#### Other Projects
- **U-Manager:** Android app for remote Unraid management
- **Unraid Deck:** Native iOS client (SwiftUI)
- **hass-unraid:** Home Assistant integration with SMART attribute notifications

**Sources:**
- [PSUnraid Reddit Thread](https://www.reddit.com/r/unRAID/comments/1ph08wi/psunraid_powershell_m) [Tier: Community]
- [unraid-management-agent GitHub](https://github.com/ruaan-deysel/unraid-management-agent) [Tier: Official]
- [Unraid MCP Reddit Thread](https://www.reddit.com/r/unRAID/comments/1pl4s4j/unraid_mcp_server_que) [Tier: Community]

---

## 9. Known Issues and Limitations

### GraphQL Schema Issues (Discovered in unraid-mcp Development)

Based on the existing unraid-mcp codebase, the following issues have been encountered:

1. **Int Overflow on Large Values:** Memory size fields (total, used, free) and some disk operation counters can overflow GraphQL's standard 32-bit `Int` type. The API uses a custom `Long` scalar but some fields still return problematic values.

2. **NaN Values:** Certain fields in the `vars` query (e.g., `sysArraySlots`, `sysCacheSlots`, `cacheNumDevices`, `cacheSbNumDisks`) can return NaN, causing type errors. The existing codebase works around this by querying a curated subset of fields.

3. **Non-nullable Fields Returning Null:** The `info.devices` section has non-nullable fields that may be null in practice. The codebase avoids querying this section entirely.

4. **Memory Layout Size Missing:** Individual memory stick `size` values are not returned by the API, preventing total memory calculation from layout data.

### API Coverage Gaps

According to the unraid-ssh-mcp developer, the GraphQL API currently lacks:
- Docker container logs
- Detailed SMART data for drives
- Real-time CPU load averages
- Process monitoring capabilities
- Some system-level metrics available via `/proc` and `/sys`

### General Limitations

- **Rate Limiting:** The API implements rate limiting (specific limits not documented publicly)
- **Version Dependency:** Full API requires Unraid 7.2+; pre-7.2 versions need the Connect plugin
- **Self-Signed Certificates:** Client must handle SSL verification for local IP access
- **Schema Volatility:** The API schema is still evolving; field names and types may change between versions

---

## 10. API Roadmap and Future Features

### Completed (as of 7.2)
- API native to Unraid OS
- Separated from Connect Plugin
- Open-sourced
- OIDC/SSO support
- Permissions system rewrite (v4.0.0)

### Q1 2025
- New Connect Settings Interface

### Q2 2025
- New modernized Settings Pages
- Storage Pool Creation Interface (simplified)
- Storage Pool Status Interface (real-time)
- Developer Tools for Plugins
- Custom Theme Creator (start)

### Q3 2025
- Custom Theme Creator (completion)
- New Docker Status Interface
- Docker Container Setup Interface (streamlined)
- New Plugins Interface (redesigned)

### TBD (Planned but Unscheduled)
- **Native Docker Compose support** -- Highly anticipated
- Plugin Development SDK and tooling
- Advanced Plugin Management interface
- Storage Share Creation & Settings interfaces
- Storage Share Management Dashboard

### In Development
- User Interface Component Library (security components)

**Sources:**
- [Roadmap & Features | Unraid Docs](https://docs.unraid.net/API/upcoming-features/) [Tier: Primary]

---

## 11. Recommendations for unraid-mcp

Based on this research, the following improvements are recommended for the unraid-mcp project:

### High Priority

1. **ZFS/Pool Management Tools**
   - Add `get_pool_status` for ZFS/BTRFS storage pools
   - Current `get_array_status` insufficient for multi-pool setups introduced in Unraid 7.0

2. **Scope-Based Tool Filtering**
   - Before registering tools with MCP, verify the API key has appropriate permissions
   - Prevent exposing tools the key cannot use (avoid hallucinated capabilities)
   - Query current key permissions at startup

3. **Improved Error Handling**
   - Implement exponential backoff for rate limit errors (HTTP 429)
   - Better handling of `Long` scalar type values
   - Graceful degradation for unavailable schema fields

4. **API Key Authorization Flow**
   - Consider implementing the OAuth-like flow (`/ApiKeyAuthorize`) for user-friendly key generation
   - Enables scope-based consent before key creation

### Medium Priority

5. **Real-Time Notification Streaming**
   - Add WebSocket subscription for notifications
   - Allows proactive alerting (e.g., "Disk 5 is overheating") without user request

6. **File Manager Integration**
   - Add `list_files`, `read_file` tools using the native File Manager API (merged in 7.0)
   - Enables LLM to organize media or clean up `appdata`

7. **Pagination for Large Queries**
   - Implement `limit` and `offset` for log listings and file browsing
   - Prevent timeouts from massive result sets

8. **Flash Backup Trigger**
   - Add tool to trigger flash backup via API mutation
   - Monitor backup status

### Low Priority

9. **VM Snapshot Management**
   - Add `create_vm_snapshot`, `revert_to_snapshot`, `clone_vm`
   - Leverages QEMU snapshot support from Unraid 7.0

10. **Tailscale/VPN Status**
    - Query network schemas for Tailnet IPs and VPN connection status
    - Useful for remote management diagnostics

11. **Query Complexity Optimization**
    - Separate list queries (lightweight) from detail queries (heavy)
    - `list_docker_containers` should fetch only id/names/state
    - Detail queries should be on-demand

### Implementation Notes

- **GraphQL Sandbox Discovery:** Use the built-in sandbox at `http://SERVER/graphql` to discover exact mutation names and field types for any new tools
- **Version Compatibility:** Consider checking the Unraid API version at startup and adjusting available tools accordingly
- **SSL Configuration:** The `UNRAID_VERIFY_SSL` environment variable is already implemented -- ensure documentation guides users toward `myunraid.net` certificates for proper SSL
- **PrefixedID Handling:** Container and VM IDs use the `PrefixedID` custom scalar -- ensure all ID-based operations handle this string type correctly

---

## 12. Source Bibliography

### Primary Sources (Official Documentation)
- [Welcome to Unraid API | Unraid Docs](https://docs.unraid.net/API/)
- [Using the Unraid API](https://docs.unraid.net/API/how-to-use-the-api/)
- [API key authorization flow | Unraid Docs](https://docs.unraid.net/API/api-key-app-developer-authorization-flow/)
- [Programmatic API key management | Unraid Docs](https://docs.unraid.net/API/programmatic-api-key-management/)
- [Roadmap & Features | Unraid Docs](https://docs.unraid.net/API/upcoming-features/)
- [Unraid Connect overview & setup | Unraid Docs](https://docs.unraid.net/connect/about/)
- [Remote access | Unraid Docs](https://docs.unraid.net/connect/remote-access/)
- [Automated flash backup | Unraid Docs](https://docs.unraid.net/connect/flash-backup/)
- [Version 7.0.0 Release Notes](https://docs.unraid.net/unraid-os/release-notes/7.0.0/)
- [Version 7.0.1 Release Notes](https://docs.unraid.net/unraid-os/release-notes/7.0.1/)
- [Version 7.1.0 Release Notes](https://docs.unraid.net/unraid-os/release-notes/7.1.0/)

### Official / GitHub Sources
- [GitHub - unraid/api: Unraid API / Connect / UI Monorepo](https://github.com/unraid/api)
- [GitHub - jmagar/unraid-mcp](https://github.com/jmagar/unraid-mcp)
- [api/docs/developer/development.md](https://github.com/unraid/api/blob/main/api/docs/developer/development.md)
- [Unraid OS 7.2.0 Blog Post](https://unraid.net/blog/unraid-7-2-0)

### Community Sources
- [PSUnraid PowerShell Module (Reddit)](https://www.reddit.com/r/unRAID/comments/1ph08wi/psunraid_powershell_m)
- [Unraid MCP Server (Reddit)](https://www.reddit.com/r/unRAID/comments/1pl4s4j/unraid_mcp_server_que)
- [unraid-management-agent (GitHub)](https://github.com/ruaan-deysel/unraid-management-agent)
- [Unraid API Discussion (Reddit)](https://www.reddit.com/r/unRAID/comments/1h7xkjr/unraid_api/)
- [API Key Location Question (Reddit)](https://www.reddit.com/r/unRAID/comments/1nk2jjk/i_couldnt_find_the_ap)

### Reference Sources
- [GraphQL Specification](https://spec.graphql.org/)
- [Learn GraphQL](https://graphql.org/learn/)
- [GraphQL Subscriptions](https://graphql.org/learn/subscriptions/)
- [Apollo GraphQL Sandbox](https://www.apollographql.com/docs/graphos/platform/sandbox)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)

---

## Cross-Source Analysis

### Where Sources Agree
- The API is GraphQL-based with queries, mutations, and subscriptions
- Unraid 7.2 is the version where API became native
- API Keys are the primary authentication method for programmatic access
- The endpoint is at `/graphql` on the server
- The API supports Docker/VM lifecycle management
- The monorepo is TypeScript/Node.js based

### Where Sources Disagree or Have Gaps
- **Exact mutation names** are not documented publicly -- must use GraphQL Sandbox introspection
- **Rate limit specifics** (thresholds, headers) are not publicly documented
- **Container logs** -- the unraid-ssh-mcp developer claims they're unavailable via API, but this may have changed in newer versions
- **Schema type issues** (Int overflow, NaN) are documented only in the unraid-mcp codebase, not in official docs

### Notable Insights
1. The unraid-management-agent project provides capabilities the official API lacks, suggesting areas for API expansion
2. PSUnraid confirms the API schema includes mutations for Docker/VM lifecycle with boolean return types
3. The OAuth-like authorization flow is a sophisticated feature not commonly found in self-hosted server APIs
4. The `Long` scalar type and `PrefixedID` type are custom additions critical for proper client implementation
