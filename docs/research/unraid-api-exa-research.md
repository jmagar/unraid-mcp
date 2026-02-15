# ExaAI Research Findings: Unraid API Ecosystem

**Date:** 2026-02-07
**Research Topic:** Unraid API Ecosystem - Architecture, Authentication, GraphQL Schema, Integrations, and MCP Server
**Specialist:** ExaAI Semantic Search

## Methodology

- **Total queries executed:** 22
- **Total unique URLs discovered:** 55+
- **Sources deep-read:** 14
- **Search strategy:** Multi-perspective semantic search covering official docs, source code analysis, community integrations, DeepWiki architecture analysis, feature roadmap, and third-party client libraries

---

## Key Findings

### 1. Unraid API Overview and Availability

The Unraid API provides a **GraphQL interface** for programmatic interaction with Unraid servers. Starting with **Unraid 7.2** (released 2025-10-29), the API comes **built into the operating system** with no plugin installation required ([source](https://docs.unraid.net/API/)).

Key capabilities include:
- Automation, monitoring, and integration through a modern, strongly-typed API
- Multiple authentication methods (API keys, session cookies, SSO/OIDC)
- Comprehensive system coverage
- Built-in developer tools including a GraphQL Sandbox

For **pre-7.2 versions**, the API is available via the Unraid Connect plugin from Community Applications. Users do **not** need to sign in to Unraid Connect to use the API locally ([source](https://docs.unraid.net/API/)).

The API was announced alongside Unraid 7.2.0 which also brought RAIDZ expansion, responsive WebGUI, and SSO login capabilities ([source](https://docs.unraid.net/unraid-os/release-notes/7.2.0/)).

### 2. Architecture and Technology Stack

The Unraid API is organized as a **pnpm workspace monorepo** containing 8+ packages ([source](https://deepwiki.com/unraid/api), [source](https://github.com/unraid/api)):

**Core Packages:**
| Package | Location | Purpose |
|---------|----------|---------|
| `@unraid/api` | `api/` | NestJS-based GraphQL server, service layer, OS integration |
| `@unraid/web` | `web/` | Vue 3 web application, Apollo Client integration |
| `@unraid/ui` | `unraid-ui/` | Reusable Vue components, web component builds |
| `@unraid/shared` | `packages/unraid-shared/` | Shared TypeScript types, utilities, constants |
| `unraid-api-plugin-connect` | `packages/unraid-api-plugin-connect/` | Remote access, UPnP, dynamic DNS |

**Backend Technology Stack:**
- **NestJS 11.1.6** with **Fastify 5.5.0** HTTP server
- **Apollo Server 4.12.2** for GraphQL
- **GraphQL 16.11.0** reference implementation
- **graphql-ws 6.0.6** for WebSocket subscriptions
- **TypeScript 5.9.2** (77.4% of codebase)
- **Redux Toolkit** for state management
- **Casbin 5.38.0** for RBAC authorization
- **PM2 6.0.8** for process management
- **dockerode 4.0.7** for Docker container management
- **@unraid/libvirt 2.1.0** for VM lifecycle control
- **systeminformation 5.27.8** for hardware metrics
- **chokidar 4.0.3** for file watching

**Frontend Technology Stack:**
- **Vue 3.5.20** with Composition API
- **Apollo Client 3.14.0** with WebSocket subscriptions
- **Pinia 3.0.3** for state management
- **TailwindCSS 4.1.12** for styling
- **Vite 7.1.3** as build tool

**Current Version:** 4.29.2 (core packages) ([source](https://deepwiki.com/unraid/api))

### 3. GraphQL API Layer

The API uses a **code-first approach** where the GraphQL schema is generated automatically from TypeScript decorators ([source](https://deepwiki.com/unraid/api/2.1-graphql-api-layer)):

- `@ObjectType()` - Defines GraphQL object types
- `@InputType()` - Specifies input types for mutations
- `@Resolver()` - Declares resolver classes
- `@Query()`, `@Mutation()`, `@Subscription()` - Operation decorators

**Schema Generation Pipeline:**
```
TypeScript Classes with Decorators
    -> @nestjs/graphql processes decorators
    -> Schema generated at runtime
    -> @graphql-codegen extracts schema
    -> TypedDocumentNode generated for frontend
    -> Type-safe operations in Vue 3 client
```

**Key Configuration:**
- **autoSchemaFile**: Code-first generation enabled
- **introspection**: Always enabled (controlled by security guards)
- **subscriptions**: WebSocket via `graphql-ws` protocol
- **fieldResolverEnhancers**: Guards enabled for field-level authorization
- **transformSchema**: Applies permission checks and conditional field removal

The GraphQL Sandbox is accessible at `http://YOUR_SERVER_IP/graphql` when enabled through Settings -> Management Access -> Developer Options, or via CLI: `unraid-api developer --sandbox true` ([source](https://docs.unraid.net/API/how-to-use-the-api/)).

**Live API documentation** is available through Apollo GraphQL Studio for exploring the complete schema ([source](https://docs.unraid.net/API/how-to-use-the-api/)).

### 4. Authentication and Authorization

The API implements a **multi-layered security architecture** separating authentication from authorization ([source](https://deepwiki.com/unraid/api/2.2-authentication-and-authorization)):

#### Authentication Methods

1. **API Keys** - Programmatic access via `x-api-key` HTTP header
   - Created via WebGUI (Settings -> Management Access -> API Keys) or CLI
   - Validated using `passport-http-header-strategy`
   - JWT verification via `jose 6.0.13`

2. **Session Cookies** - Automatic when signed into WebGUI

3. **SSO/OIDC** - External identity providers via `openid-client 6.6.4`
   - Supported providers: Unraid.net, Google, Microsoft/Azure AD, Keycloak, Authelia, Authentik, Okta
   - Configuration via Settings -> Management Access -> API -> OIDC
   - Two authorization modes: Simple (email domain/address) and Advanced (claim-based rules)
   ([source](https://docs.unraid.net/API/oidc-provider-setup/))

#### API Key Authorization Flow for Third-Party Apps

Applications can request API access via a self-service flow ([source](https://docs.unraid.net/API/api-key-app-developer-authorization-flow/)):

```
https://[unraid-server]/ApiKeyAuthorize?name=MyApp&&scopes=docker:read,vm:*&&redirect_uri=https://myapp.com/callback&&state=abc123
```

**Scope Format:** `resource:action` pattern
- Resources: docker, vm, system, share, user, network, disk
- Actions: create, read, update, delete, * (full access)

#### Programmatic API Key Management

CLI-based CRUD operations for automation ([source](https://docs.unraid.net/API/programmatic-api-key-management/)):

```bash
# Create with granular permissions
unraid-api apikey --create \
  --name "monitoring key" \
  --permissions "DOCKER:READ_ANY,ARRAY:READ_ANY" \
  --description "Read-only access" --json

# Delete
unraid-api apikey --delete --name "monitoring key"
```

**Available Roles:** ADMIN, CONNECT, VIEWER, GUEST

**Available Resources:** ACTIVATION_CODE, API_KEY, ARRAY, CLOUD, CONFIG, CONNECT, DOCKER, FLASH, INFO, LOGS, NETWORK, NOTIFICATIONS, OS, SERVICES, SHARE, VMS

**Available Actions:** CREATE_ANY, CREATE_OWN, READ_ANY, READ_OWN, UPDATE_ANY, UPDATE_OWN, DELETE_ANY, DELETE_OWN

#### RBAC Implementation

- **Casbin 5.38.0** with **nest-authz 2.17.0** for policy-based access control
- **accesscontrol 2.2.1** maintains the permission matrix
- **@UsePermissions() directive** provides field-level authorization by removing protected fields from the GraphQL schema dynamically
- **Rate limiting:** 100 requests per 10 seconds via `@nestjs/throttler 6.4.0`
- **Security headers:** `@fastify/helmet 13.0.1` with minimal CSP

### 5. CLI Reference

All commands follow the pattern: `unraid-api <command> [options]` ([source](https://docs.unraid.net/API/cli)):

| Command | Purpose |
|---------|---------|
| `unraid-api start [--log-level <level>]` | Start API service |
| `unraid-api stop [--delete]` | Stop API service |
| `unraid-api restart` | Restart API service |
| `unraid-api logs [-l <lines>]` | View logs (default 100 lines) |
| `unraid-api config` | Display configuration |
| `unraid-api switch-env [-e <env>]` | Toggle production/staging |
| `unraid-api developer [--sandbox true/false]` | Developer mode |
| `unraid-api apikey [options]` | API key management |
| `unraid-api sso add-user/remove-user/list-users` | SSO user management |
| `unraid-api sso validate-token <token>` | Token validation |
| `unraid-api report [-r] [-j]` | Generate system report |

Log levels: trace, debug, info, warn, error, fatal

### 6. Docker Container Management

The Docker Management Service provides comprehensive container lifecycle management through GraphQL ([source](https://deepwiki.com/unraid/api/2.4.2-notification-system)):

**Container Lifecycle Mutations:**
- `start(id)` - Start a stopped container
- `stop(id)` - Stop with 10-second timeout
- `pause(id)` / `unpause(id)` - Suspend/resume
- `removeContainer(id, options)` - Remove container and optionally images
- `updateContainer(id)` - Upgrade to latest image version
- `updateAllContainers()` - Batch update all containers

**Container Data Enrichment:**
- Canonical name extraction via `autostartService`
- Auto-start configuration details
- Port deduplication (IPv4/IPv6)
- LAN-accessible URL computation
- State normalization: RUNNING, PAUSED, EXITED

**Update Detection:**
- Compares local image digests against remote registry manifests
- Returns `UpdateStatus`: UP_TO_DATE, UPDATE_AVAILABLE, REBUILD_READY, UNKNOWN
- Legacy PHP script integration for status computation

**Real-Time Event Monitoring:**
- Watches `/var/run` for Docker socket via chokidar
- Filters: start, stop, die, kill, pause, unpause, restart, oom events
- Publishes to `PUBSUB_CHANNEL.INFO` for subscription updates

**Container Organizer:**
- Folder-based hierarchical organization
- Operations: createFolder, setFolderChildren, deleteEntries, moveEntriesToFolder, renameFolder
- Behind `ENABLE_NEXT_DOCKER_RELEASE` feature flag

**Statistics Streaming:**
- Real-time resource metrics via subscriptions
- CPU percent, memory usage/percent, network I/O, block I/O
- Auto-start/stop streams based on subscription count

### 7. VM Management

VM management uses the `@unraid/libvirt` package (v2.1.0) for QEMU/KVM integration ([source](https://github.com/unraid/libvirt), [source](https://deepwiki.com/unraid/api)):

- Domain state management (start, stop, pause, resume)
- Snapshot creation and restoration
- Domain XML inspection
- Retry logic (up to 2 minutes) for libvirt daemon initialization

Unraid 7.x enhancements include VM clones, snapshots, user-created VM templates, inline XML editing, and advanced GPU passthrough ([source](https://docs.unraid.net/unraid-os/manual/vm/vm-management/)).

### 8. Storage and Array Management

**Array Operations** (available via Python client library):
- `start_array()` / `stop_array()`
- `start_parity_check(correct)` / `pause_parity_check()` / `resume_parity_check()` / `cancel_parity_check()`
- `spin_up_disk(id)` / `spin_down_disk(id)`

**GraphQL Queries for Storage:**

```graphql
# Disk Information
{ disks { device name type size vendor temperature smartStatus } }

# Share Information
{ shares { name comment free size used } }

# Array Status (from official docs example)
{ array { state capacity { free used total } disks { name size status temp } } }
```

([source](https://deepwiki.com/domalab/unraid-api-client/4.3-network-and-storage-queries), [source](https://docs.unraid.net/API/how-to-use-the-api/))

**ZFS Support:** Unraid supports ZFS pools with automatic data integrity, built-in RAID (mirrors, RAIDZ), snapshots, and send/receive ([source](https://docs.unraid.net/unraid-os/advanced-configurations/optimize-storage/zfs-storage/)).

### 9. Network Management

**Network Query Fields:**

| Field | Type | Description |
|-------|------|-------------|
| iface | String | Interface identifier |
| ifaceName | String | Interface name |
| ipv4/ipv6 | String | IP addresses |
| mac | String | MAC address |
| operstate | String | Operational state (up/down) |
| type | String | Interface type |
| duplex | String | Duplex mode |
| speed | Number | Interface speed |
| accessUrls | Array | Access URLs for the interface |

```graphql
{ network { iface ifaceName ipv4 ipv6 mac operstate type duplex speed accessUrls { type name ipv4 ipv6 } } }
```

([source](https://deepwiki.com/domalab/unraid-api-client/4.3-network-and-storage-queries))

### 10. Notification System

The Unraid API exposes a notification system with the following features ([source](https://deepwiki.com/unraid/api)):

- File-based notifications stored in `/unread/` and `/archive/` directories
- GraphQL queries for notification overview (counts by type)
- Notification listing with filters
- Notification agents: email, Discord, Slack (built-in); custom agents via scripts

Community solutions for additional notification targets include ntfy.sh, Matrix, and webhook-based approaches ([source](https://forums.unraid.net/topic/88464-webhook-notification-method/), [source](https://lder.dev/posts/ntfy-Notifications-With-unRAID/)).

### 11. WebSocket Subscriptions (Real-Time)

The API implements real-time subscriptions via the `graphql-ws` protocol (v6.0.6) ([source](https://deepwiki.com/unraid/api/2.1-graphql-api-layer)):

- **PubSub Engine:** `graphql-subscriptions@3.0.0` for event publishing
- **Transport:** WebSocket via `graphql-ws` protocol
- **Trigger:** Redux store updates from file watchers propagate to subscribed clients
- **Available subscriptions include:**
  - Container state changes
  - Container statistics (CPU, memory, I/O)
  - System metrics updates
  - Array status changes

The subscription system is event-driven: file changes on disk (detected by chokidar) -> Redux store update -> PubSub event -> WebSocket push to clients.

### 12. MCP Server Integrations

**jmagar/unraid-mcp** (this project) is the primary MCP server for Unraid ([source](https://glama.ai/mcp/servers/@jmagar/unraid-mcp), [source](https://mcpmarket.com/server/unraid)):

- Python-based MCP server using FastMCP framework
- 26 tools for comprehensive Unraid management
- Read-only access by default for safety
- Listed on Glama, MCP Market, MCPServers.com, LangDB, UBOS, JuheAPI
- 21 GitHub stars
- Communicates via stdio transport

**Alternative MCP implementations:**
- `lwsinclair/unraid-mcp` - Another MCP implementation ([source](https://github.com/lwsinclair/unraid-mcp))
- `ruaan-deysel/unraid-management-agent` - Go-based plugin with REST API + WebSocket + MCP integration ([source](https://github.com/ruaan-deysel/unraid-management-agent))

### 13. Third-Party Client Libraries

#### Python Client: `unraid-api` (PyPI)

**Author:** DomaLab (Ruaan Deysel)
**Version:** 1.3.1 (as of Jan 2026)
**Requirements:** Python 3.11+, Unraid 7.1.4+, API v4.21.0+

Features ([source](https://github.com/domalab/unraid-api-client), [source](https://unraid-api.domalab.net/)):
- Async/await with aiohttp
- Home Assistant ready (accepts external ClientSession)
- Pydantic models for all responses
- SSL auto-discovery
- Redirect handling for myunraid.net

**Supported Operations:**
- Docker: start/stop/restart containers
- VMs: start/stop/force_stop/pause/resume
- Array: start/stop, parity check (start/pause/resume/cancel), disk spin up/down
- System: metrics, shares, UPS, services, plugins, log files, notifications
- Custom GraphQL queries

#### Home Assistant Integration

`chris-mc1/unraid_api` (60 stars) - Full Home Assistant integration using the local GraphQL API ([source](https://github.com/chris-mc1/unraid_api)):
- Monitors array state, disk status, temperatures
- Docker container status
- Network information
- HACS compatible

#### Homey Smart Home

Unraid API integration available for the Homey smart home platform ([source](https://homey.app/no-no/app/community.unraid.api/Unraid-API/)).

#### Legacy APIs (Pre-GraphQL)

- `ElectricBrainUK/UnraidAPI` (127 stars) - Original Node.js API using web scraping ([source](https://github.com/ElectricBrainUK/UnraidAPI))
- `BoKKeR/UnraidAPI-RE` (68 stars) - Reverse-engineered Node.js API ([source](https://github.com/BoKKeR/UnraidAPI-RE))
- `ridenui/unraid` - TypeScript client via SSH ([source](https://github.com/ridenui/unraid))

### 14. Unraid Connect and Remote Access

Unraid Connect provides cloud-enabled server management ([source](https://docs.unraid.net/connect/), [source](https://unraid.net/connect)):

- **Dynamic Remote Access:** Toggle on/off server accessibility via UPnP
- **Server Management:** Manage multiple servers from Connect web UI
- **Deep Linking:** Links to relevant WebGUI sections
- **Online Flash Backup:** Cloud-based configuration backups
- **Real-time Monitoring:** Server health and resource usage monitoring
- **Notifications:** Server health, storage status, critical events

The Connect plugin (`unraid-api-plugin-connect`) handles remote access, UPnP, dynamic DNS, and Mothership API communication ([source](https://deepwiki.com/unraid/api)).

### 15. Plugin Architecture

The API supports a plugin system for extending functionality ([source](https://deepwiki.com/unraid/api)):

- Plugins are NPM packages implementing the `UnraidPlugin` interface
- Access to NestJS dependency injection
- Can extend the GraphQL schema
- Dynamic loading via `PluginLoaderService` at runtime
- `@unraid/create-api-plugin` CLI scaffolding tool available
- Plugin documentation at `api/docs/developer/api-plugins.md`

### 16. Feature Bounty Program

Unraid launched a **Feature Bounty Program** in September 2025 ([source](https://unraid.net/blog/api-feature-bounty-program)):

- Community developers implement specific API features for monetary rewards
- Bounty board: `github.com/orgs/unraid/projects/3/views/1`
- Accelerates feature development beyond core team capacity

**Notable Open Bounty: System Temperature Monitoring** ([source](https://github.com/unraid/api/issues/1597)):
- Current API provides only disk temperatures via smartctl
- Proposed comprehensive monitoring: CPU, motherboard, GPU, NVMe, chipset
- Proposed GraphQL schema with TemperatureSensor, TemperatureSummary types
- Would use lm-sensors, smartctl, nvidia-smi, IPMI

### 17. Monitoring and Grafana Integration

While the Unraid API does not natively expose Prometheus metrics, the community has established monitoring patterns ([source](https://unraid.net/blog/prometheus)):

- **Prometheus Node Exporter** plugin for Unraid
- **Grafana dashboards** available:
  - Unraid System Dashboard V2 (ID: 7233) ([source](https://grafana.com/grafana/dashboards/7233-unraid-system-dashboard-v2/))
  - Unraid UPS Monitoring (ID: 19243) ([source](https://grafana.com/grafana/dashboards/19243-unraid-ups-monitoring/))
- **cAdvisor** for container-level metrics

### 18. Development and Contribution

**Development Environment Requirements:**
- Node.js 22.x (enforced)
- pnpm 10.15.0
- Bash, Docker, libvirt, jq

**Key Development Commands:**
```bash
pnpm dev          # All dev servers in parallel
pnpm build        # Production builds
pnpm codegen      # Generate GraphQL types
pnpm test         # Run test suites (Vitest)
pnpm lint         # ESLint
pnpm type-check   # TypeScript checking
```

**Deployment to Unraid:**
```bash
pnpm unraid:deploy <SERVER_IP>
```

**CI/CD Pipeline:**
1. PR previews with unique build URLs
2. Staging deployment for merged PRs
3. Production releases via release-please with semantic versioning

([source](https://github.com/unraid/api/blob/main/CLAUDE.md))

---

## Expert Opinions and Analysis

The DeepWiki auto-generated documentation characterizes the Unraid API as "a modern GraphQL API and web interface for managing Unraid servers" that "replaces portions of the legacy PHP-based WebGUI with a type-safe, real-time API built on NestJS and Vue 3, while maintaining backward compatibility through hybrid integration" ([source](https://deepwiki.com/unraid/api)).

The Feature Bounty Program blog post indicates Unraid is actively investing in the API ecosystem: "The new Unraid API has already come a long way as a powerful, open-source toolkit that unlocks endless possibilities for automation, integrations, and third-party applications" ([source](https://unraid.net/blog/api-feature-bounty-program)).

---

## Contradictions and Debates

1. **Code-first vs Schema-first:** The CLAUDE.md mentions "GraphQL schema-first approach with code generation" while the DeepWiki analysis describes a "code-first approach with NestJS decorators that generate the GraphQL schema." The DeepWiki analysis appears more accurate based on the `autoSchemaFile` configuration and NestJS decorator usage.

2. **File Manager API:** No dedicated file browser/upload/download API was found in the GraphQL schema. File operations appear to be handled through the legacy PHP WebGUI rather than the new API.

3. **RClone via API:** While our MCP server project has RClone tools, these appear to interface with rclone config files rather than a native GraphQL API for cloud storage management.

---

## Data Points and Statistics

| Metric | Value | Source |
|--------|-------|--------|
| Unraid API native since | v7.2.0 (2025-10-29) | [docs.unraid.net](https://docs.unraid.net/unraid-os/release-notes/7.2.0/) |
| GitHub stars (official repo) | 86 | [github.com/unraid/api](https://github.com/unraid/api) |
| Total releases | 102 | [github.com/unraid/api](https://github.com/unraid/api) |
| Codebase language | TypeScript 77.4%, Vue 11.8%, PHP 5.6% | [github.com/unraid/api](https://github.com/unraid/api) |
| Current package version | 4.29.2 | [deepwiki.com](https://deepwiki.com/unraid/api) |
| Rate limit | 100 req/10 sec | [deepwiki.com](https://deepwiki.com/unraid/api/2.2-authentication-and-authorization) |
| Python client PyPI version | 1.3.1 | [pypi.org](https://pypi.org/project/unraid-api/1.3.1/) |
| Home Assistant integration stars | 60 | [github.com](https://github.com/chris-mc1/unraid_api) |
| jmagar/unraid-mcp stars | 21 | [github.com](https://github.com/jmagar/unraid-mcp) |

---

## Gaps Identified

1. **Full GraphQL Schema Dump:** No publicly accessible introspection dump or SDL file was found. The live schema is only available via the GraphQL Sandbox on a running Unraid server.

2. **File Manager API:** No evidence of file browse/upload/download GraphQL mutations. This appears to remain in the PHP WebGUI layer.

3. **Temperature Monitoring:** Currently limited to disk temperatures via smartctl. Comprehensive temperature monitoring is an open feature bounty (not yet implemented).

4. **Parity/Array Operation Mutations:** While the Python client library implements `start_array()`/`stop_array()`, the specific GraphQL mutations and their schemas were not found in public documentation.

5. **RClone GraphQL API:** The extent of rclone integration through the GraphQL API versus legacy integration is unclear.

6. **Flash Backup API:** Flash backups appear to be handled through Unraid Connect (cloud-based) rather than a local GraphQL API.

7. **Network Configuration Mutations:** While network queries return interface data, mutations for VLAN/bonding configuration were not found in the API documentation.

8. **WebSocket Subscription Schema:** The specific subscription types and their exact GraphQL definitions are not publicly documented outside the running API.

9. **Plugin API Documentation:** The plugin developer guide (`api/docs/developer/api-plugins.md`) was not publicly accessible outside the repository.

10. **Rate Limiting Details:** Only the default rate (100 req/10 sec) was found; per-endpoint or per-role rate limits were not documented.

---

## All URLs Discovered

### Primary Sources (Official Unraid Documentation)
- [Welcome to Unraid API](https://docs.unraid.net/API/) - API landing page
- [Using the Unraid API](https://docs.unraid.net/API/how-to-use-the-api/) - Usage guide with examples
- [API Key Authorization Flow](https://docs.unraid.net/API/api-key-app-developer-authorization-flow/) - Third-party auth flow
- [Programmatic API Key Management](https://docs.unraid.net/API/programmatic-api-key-management/) - CLI key management
- [CLI Reference](https://docs.unraid.net/API/cli) - Full CLI command reference
- [OIDC Provider Setup](https://docs.unraid.net/API/oidc-provider-setup/) - SSO configuration
- [Unraid 7.2.0 Release Notes](https://docs.unraid.net/unraid-os/release-notes/7.2.0/) - Release notes
- [Automated Flash Backup](https://docs.unraid.net/connect/flash-backup/) - Flash backup docs
- [Unraid Connect Overview](https://docs.unraid.net/connect/) - Connect service
- [Remote Access](https://docs.unraid.net/unraid-connect/remote-access/) - Remote access docs
- [Unraid Connect Setup](https://docs.unraid.net/unraid-connect/overview-and-setup/) - Setup guide
- [Arrays Overview](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/array/overview/) - Storage management
- [ZFS Storage](https://docs.unraid.net/unraid-os/advanced-configurations/optimize-storage/zfs-storage/) - ZFS guide
- [SMART Reports](https://docs.unraid.net/unraid-os/system-administration/monitor-performance/smart-reports-and-disk-health/) - Disk health
- [User Management](https://docs.unraid.net/unraid-os/system-administration/secure-your-server/user-management/) - User system
- [Array Health](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/array/array-health-and-maintenance/) - Parity/maintenance
- [VM Management](https://docs.unraid.net/unraid-os/manual/vm/vm-management/) - VM setup guide
- [Plugins](https://docs.unraid.net/unraid-os/using-unraid-to/customize-your-experience/plugins/) - Plugin overview

### Official Source Code
- [unraid/api GitHub](https://github.com/unraid/api) - Official monorepo (86 stars)
- [unraid/api CLAUDE.md](https://github.com/unraid/api/blob/main/CLAUDE.md) - Development guidelines
- [unraid/libvirt GitHub](https://github.com/unraid/libvirt) - Libvirt bindings
- [unraid/api Issues](https://github.com/unraid/api/issues) - Issue tracker
- [Temperature Monitoring Bounty](https://github.com/unraid/api/issues/1597) - Feature bounty issue
- [API Feature Bounty Program](https://unraid.net/blog/api-feature-bounty-program) - Program announcement
- [Unraid Connect](https://unraid.net/connect) - Connect product page
- [Connect Dashboard](https://connect.myunraid.net/) - Live Connect dashboard

### Architecture Analysis (DeepWiki)
- [Unraid API Overview](https://deepwiki.com/unraid/api) - Full architecture
- [Backend API System](https://deepwiki.com/unraid/api/2-api-server) - Backend details
- [GraphQL API Layer](https://deepwiki.com/unraid/api/2.1-graphql-api-layer) - GraphQL implementation
- [Authentication and Authorization](https://deepwiki.com/unraid/api/2.2-authentication-and-authorization) - Auth system
- [Core Services](https://deepwiki.com/unraid/api/2.4-docker-integration) - Docker/services
- [Docker Management Service](https://deepwiki.com/unraid/api/2.4.2-notification-system) - Docker details
- [Configuration Files](https://deepwiki.com/unraid/api/5.2-connect-settings-and-remote-access) - Config system

### Community Client Libraries
- [domalab/unraid-api-client GitHub](https://github.com/domalab/unraid-api-client) - Python client
- [unraid-api PyPI](https://pypi.org/project/unraid-api/1.3.1/) - PyPI package
- [Unraid API Documentation (DomaLab)](https://unraid-api.domalab.net/) - Python docs
- [Network and Storage Queries](https://deepwiki.com/domalab/unraid-api-client/4.3-network-and-storage-queries) - Query reference
- [chris-mc1/unraid_api GitHub](https://github.com/chris-mc1/unraid_api) - Home Assistant integration (60 stars)
- [Homey Unraid API](https://homey.app/no-no/app/community.unraid.api/Unraid-API/) - Homey integration

### MCP Server Listings
- [jmagar/unraid-mcp GitHub](https://github.com/jmagar/unraid-mcp) - This project
- [Glama MCP Listing](https://glama.ai/mcp/servers/@jmagar/unraid-mcp) - Glama listing
- [MCP Market Listing](https://mcpmarket.com/server/unraid) - MCP Market
- [MCPServers.com Listing](https://mcpservers.com/servers/jmagar-unraid) - MCPServers.com
- [LangDB Listing](https://langdb.ai/app/mcp-servers/unraid-mcp-server-8605b018-ce29-48d5-8132-48cf0792501f) - LangDB
- [UBOS Listing](https://ubos.tech/mcp/unraid-mcp-server/) - UBOS
- [JuheAPI Listing](https://www.juheapi.com/mcp-servers/jmagar/unraid-mcp) - JuheAPI
- [AIBase Listing](https://mcp.aibase.com/server/1916341265568079874) - AIBase
- [lwsinclair/unraid-mcp GitHub](https://github.com/lwsinclair/unraid-mcp) - Alternative MCP

### Alternative/Legacy APIs
- [ruaan-deysel/unraid-management-agent](https://github.com/ruaan-deysel/unraid-management-agent) - Go REST+WebSocket (5 stars)
- [BoKKeR/UnraidAPI-RE](https://github.com/BoKKeR/UnraidAPI-RE) - Node.js API (68 stars)
- [ElectricBrainUK/UnraidAPI](https://github.com/ElectricBrainUK/UnraidAPI) - Original API (127 stars)
- [ridenui/unraid](https://github.com/ridenui/unraid) - TypeScript SSH client (3 stars)

### Monitoring Integration
- [Unraid Prometheus Guide](https://unraid.net/blog/prometheus) - Official guide
- [Grafana UPS Dashboard](https://grafana.com/grafana/dashboards/19243-unraid-ups-monitoring/) - Dashboard 19243
- [Grafana System Dashboard V2](https://grafana.com/grafana/dashboards/7233-unraid-system-dashboard-v2/) - Dashboard 7233
- [Prometheus/Grafana Forum Thread](https://forums.unraid.net/topic/77593-monitoring-unraid-with-prometheus-grafana-cadvisor-nodeexporter-and-alertmanager/) - Community guide

### Community Discussion
- [Webhook Notification Forum Thread](https://forums.unraid.net/topic/88464-webhook-notification-method/) - Notification customization
- [Matrix Notification Agent](https://forums.unraid.net/topic/122107-matrix-notification-agent/) - Matrix integration
- [ntfy.sh Notifications](https://lder.dev/posts/ntfy-Notifications-With-unRAID/) - ntfy.sh setup
- [MCP HomeLab Tutorial (YouTube)](https://www.youtube.com/watch?v=AydDDYn09QA) - Christian Lempa MCP tutorial
- [Build with the Unraid API (YouTube)](https://www.youtube.com/shorts/0JJQdFfh4e0) - Short video
