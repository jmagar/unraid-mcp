# Unraid API Source Code Analysis

> **Research Date:** 2026-02-07
> **Repository:** https://github.com/unraid/api
> **Latest Version:** v4.29.2 (December 19, 2025)
> **License:** Open-sourced January 2025

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Technology Stack](#2-technology-stack)
3. [GraphQL Schema & Type System](#3-graphql-schema--type-system)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [Resolver Implementations](#5-resolver-implementations)
6. [Subscription System](#6-subscription-system)
7. [State Management](#7-state-management)
8. [Plugin Architecture](#8-plugin-architecture)
9. [Release History](#9-release-history)
10. [Roadmap & Upcoming Features](#10-roadmap--upcoming-features)
11. [Open Issues & Community Requests](#11-open-issues--community-requests)
12. [Community Projects & Integrations](#12-community-projects--integrations)
13. [Architectural Insights for unraid-mcp](#13-architectural-insights-for-unraid-mcp)

---

## 1. Repository Structure

The Unraid API is a **monorepo** managed with pnpm workspaces containing eight interconnected packages:

```
unraid/api/
├── api/                          # NestJS GraphQL backend (port 3001)
│   ├── src/
│   │   ├── __test__/
│   │   ├── common/               # Shared utilities
│   │   ├── core/                 # Core infrastructure
│   │   │   ├── errors/
│   │   │   ├── modules/
│   │   │   ├── notifiers/
│   │   │   ├── types/
│   │   │   ├── utils/
│   │   │   ├── log.ts
│   │   │   └── pubsub.ts         # PubSub for GraphQL subscriptions
│   │   ├── i18n/                 # Internationalization
│   │   ├── mothership/           # Unraid Connect relay communication
│   │   ├── store/                # Redux state management
│   │   │   ├── actions/
│   │   │   ├── listeners/
│   │   │   ├── modules/
│   │   │   ├── services/
│   │   │   ├── state-parsers/
│   │   │   ├── watch/
│   │   │   └── root-reducer.ts
│   │   ├── types/
│   │   ├── unraid-api/           # Main API implementation
│   │   │   ├── app/
│   │   │   ├── auth/             # Authentication system
│   │   │   ├── cli/
│   │   │   ├── config/
│   │   │   ├── cron/
│   │   │   ├── decorators/
│   │   │   ├── exceptions/
│   │   │   ├── graph/            # GraphQL resolvers & services
│   │   │   ├── nginx/
│   │   │   ├── observers/
│   │   │   ├── organizer/
│   │   │   ├── plugin/
│   │   │   ├── rest/             # REST API endpoints
│   │   │   ├── shared/
│   │   │   ├── types/
│   │   │   ├── unraid-file-modifier/
│   │   │   └── utils/
│   │   ├── upnp/                 # UPnP protocol
│   │   ├── cli.ts
│   │   ├── consts.ts
│   │   ├── environment.ts
│   │   └── index.ts
│   ├── generated-schema.graphql  # Auto-generated GraphQL schema
│   ├── codegen.ts                # GraphQL code generation config
│   ├── Dockerfile
│   └── docker-compose.yml
├── web/                          # Nuxt 3 frontend (Vue 3)
│   ├── composables/gql/          # GraphQL composables
│   ├── layouts/
│   ├── src/
│   └── codegen.ts
├── unraid-ui/                    # Vue 3 component library
├── plugin/                       # Plugin packaging
├── packages/
│   ├── unraid-shared/            # Shared types & utilities
│   │   └── src/
│   │       ├── pubsub/           # PubSub channel definitions
│   │       ├── types/
│   │       ├── graphql-enums.ts  # AuthAction, Resource, Role enums
│   │       ├── graphql.model.ts
│   │       └── use-permissions.directive.ts
│   ├── unraid-api-plugin-connect/
│   ├── unraid-api-plugin-generator/
│   └── unraid-api-plugin-health/
├── scripts/
├── pnpm-workspace.yaml
├── .nvmrc                        # Node.js v22
└── flake.nix                     # Nix dev environment
```

---

## 2. Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime | Node.js | v22 |
| Framework | NestJS | 11.1.6 |
| HTTP Server | Fastify | 5.5.0 |
| GraphQL | Apollo Server | 4.12.2 |
| Package Manager | pnpm | 10.15.0 |
| Build Tool | Vite | 7.1.3 |
| Test Framework | Vitest | 3.2.4 |
| Docker SDK | Dockerode | 4.0.7 |
| VM Management | @unraid/libvirt | 2.1.0 |
| System Info | systeminformation | 5.27.8 |
| File Watcher | Chokidar | 4.0.3 |
| Auth RBAC | Casbin + nest-authz | 5.38.0 |
| Auth Passport | Passport.js | Multiple strategies |
| State Mgmt | Redux Toolkit | - |
| Subscriptions | graphql-subscriptions | PubSub with EventEmitter |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Vue 3 + Nuxt | 3.5.20 |
| GraphQL Client | Apollo Client | 3.14.0 |
| State | Pinia | 3.0.3 |
| Styling | Tailwind CSS | v4 |

### Key Patterns
- **Schema-first GraphQL** (migrating to code-first with NestJS decorators)
- NestJS dependency injection with decorators
- TypeScript ESM imports (`.js` extensions)
- Redux for ephemeral runtime state synced with INI config files
- Chokidar filesystem watchers for reactive config synchronization

---

## 3. GraphQL Schema & Type System

### Custom Scalars
- `DateTime` - ISO date/time
- `BigInt` - Large integer values
- `JSON` - Arbitrary JSON data
- `Port` - Network port numbers
- `URL` - URL strings
- `PrefixedID` - Server-prefixed identifiers (format: `server-prefix:uuid`)

### Core Enums

#### ArrayState
```
STARTED, STOPPED, NEW_ARRAY, RECON_DISK, DISABLE_DISK,
SWAP_DSBL, INVALID_EXPANSION, PARITY_NOT_BIGGEST,
TOO_MANY_MISSING_DISKS, NEW_DISK_TOO_SMALL, NO_DATA_DISKS
```

#### ArrayDiskStatus
```
DISK_NP, DISK_OK, DISK_NP_MISSING, DISK_INVALID, DISK_WRONG,
DISK_DSBL, DISK_NP_DSBL, DISK_DSBL_NEW, DISK_NEW
```

#### ArrayDiskType
```
DATA, PARITY, FLASH, CACHE
```

#### ArrayDiskFsColor
```
GREEN_ON, GREEN_BLINK, BLUE_ON, BLUE_BLINK,
YELLOW_ON, YELLOW_BLINK, RED_ON, RED_OFF, GREY_OFF
```

#### ContainerState
```
RUNNING, PAUSED, EXITED
```

#### ContainerPortType
```
TCP, UDP
```

#### VmState
```
NOSTATE, RUNNING, IDLE, PAUSED, SHUTDOWN,
SHUTOFF, CRASHED, PMSUSPENDED
```

#### NotificationImportance / NotificationType
- Importance: Defines severity levels
- Type: Categorizes notification sources

#### Role
```
ADMIN    - Full administrative access
CONNECT  - Read access with remote management
GUEST    - Basic profile access
VIEWER   - Read-only access
```

#### AuthAction
```
CREATE_ANY, CREATE_OWN
READ_ANY,   READ_OWN
UPDATE_ANY, UPDATE_OWN
DELETE_ANY,  DELETE_OWN
```

#### Resource (35 total)
```
ACTIVATION_CODE, API_KEY, ARRAY, CLOUD, CONFIG, CONNECT,
CUSTOMIZATIONS, DASHBOARD, DISK, DOCKER, FLASH, INFO,
LOGS, ME, NETWORK, NOTIFICATIONS, ONLINE, OS, OWNER,
PERMISSION, REGISTRATION, SERVERS, SERVICES, SHARE,
VARS, VMS, WELCOME, ...
```

### Core Type Definitions

#### UnraidArray
```graphql
type UnraidArray {
  state: ArrayState!
  capacity: ArrayCapacity
  boot: ArrayDisk
  parities: [ArrayDisk!]!
  parityCheckStatus: ParityCheck
  disks: [ArrayDisk!]!
  caches: [ArrayDisk!]!
}
```

#### ArrayDisk
```graphql
type ArrayDisk implements Node {
  id: PrefixedID!
  idx: Int
  name: String
  device: String
  size: BigInt
  fsSize: String
  fsFree: String
  fsUsed: String
  status: ArrayDiskStatus
  rotational: Boolean
  temp: Int
  numReads: BigInt
  numWrites: BigInt
  numErrors: BigInt
  type: ArrayDiskType
  exportable: Boolean
  warning: Int
  critical: Int
  fsType: String
  comment: String
  format: String
  transport: String
  color: ArrayDiskFsColor
  isSpinning: Boolean
}
```

#### DockerContainer
```graphql
type DockerContainer implements Node {
  id: PrefixedID!
  names: [String!]
  image: String
  imageId: String
  command: String
  created: DateTime
  ports: [ContainerPort!]
  lanIpPorts: [String]          # LAN-accessible host:port values
  sizeRootFs: BigInt
  sizeRw: BigInt
  sizeLog: BigInt
  labels: JSON
  state: ContainerState
  status: String
  hostConfig: JSON
  networkSettings: JSON
  mounts: JSON
  autoStart: Boolean
  autoStartOrder: Int
  autoStartWait: Int
  templatePath: String
  projectUrl: String
  registryUrl: String
  supportUrl: String
  iconUrl: String
  webUiUrl: String
  shell: String
  templatePorts: JSON
  isOrphaned: Boolean
}
```

#### VmDomain
```graphql
type VmDomain implements Node {
  id: PrefixedID!              # UUID-based identifier
  name: String                 # Friendly name
  state: VmState!              # Current state
  uuid: String @deprecated     # Use id instead
}
```

#### Share
```graphql
type Share implements Node {
  id: PrefixedID!
  name: String
  comment: String
  free: String
  used: String
  total: String
  include: [String]
  exclude: [String]
  # Additional capacity/config fields
}
```

#### Info (System Information)
```graphql
type Info {
  time: DateTime
  baseboard: Baseboard
  cpu: CpuInfo
  devices: Devices
  display: DisplayInfo
  machineId: String
  memory: MemoryInfo
  os: OsInfo
  system: SystemInfo
  versions: Versions
}
```

---

## 4. Authentication & Authorization

### Authentication Methods

#### 1. API Key Authentication
- **Header**: `x-api-key: YOUR_API_KEY`
- Keys stored as JSON files in `/boot/config/plugins/unraid-api/`
- Generated via WebGUI (Settings > Management Access > API Keys) or CLI (`unraid-api apikey --create`)
- 32-byte hexadecimal keys generated using `crypto.randomBytes`
- File system watcher (Chokidar) syncs in-memory cache with disk changes
- Keys support both **roles** (simplified) and **permissions** (granular resource:action pairs)

**API Key Service (`api-key.service.ts`):**
```typescript
// Key creation validates:
// - Name via Unicode-aware regex
// - At least one role or permission required
// - 32-byte hex key generation
// - Overwrite support for existing keys

// Lookup methods:
findById(id)        // UUID-based lookup
findByField(field, value)  // Generic field search
findByKey(key)      // Direct secret key lookup for auth
```

#### 2. Cookie-Based Sessions
- CSRF token validation for non-GET requests
- `timingSafeEqual` comparison prevents timing attacks
- Session user ID: `-1`
- Returns admin role privileges

#### 3. Local Sessions (CLI/System)
- For CLI and system-level operations
- Local session user ID: `-2`
- Returns local admin with elevated privileges

#### 4. SSO/OIDC
- OpenID Connect client implementation
- Separate SSO module with auth, client, core, models, session, and utils subdirectories
- JWT validation using Jose library

### Authorization (RBAC via Casbin)

**Model:** Resource-based access control with `_ANY` (universal) and `_OWN` (owner-limited) permission modifiers.

```typescript
// Permission enforcement via decorators:
@UsePermissions({
  action: AuthAction.READ_ANY,
  resource: Resource.ARRAY,
})
```

**Casbin Implementation (`api/src/unraid-api/auth/casbin/`):**
- `casbin.service.ts` - Core RBAC service
- `policy.ts` - Policy configuration
- `model.ts` - RBAC model definitions
- `resolve-subject.util.ts` - Subject resolution utility
- Wildcard permission expansion (`*` -> full CRUD)
- Role hierarchy with inherited permissions

### Auth Files Structure
```
api/src/unraid-api/auth/
├── casbin/
│   ├── casbin.module.ts
│   ├── casbin.service.ts
│   ├── model.ts
│   ├── policy.ts
│   └── resolve-subject.util.ts
├── api-key.service.ts          # API key CRUD operations
├── auth.interceptor.ts         # HTTP auth interceptor
├── auth.module.ts              # NestJS auth module
├── auth.service.ts             # Core auth logic (3 strategies)
├── authentication.guard.ts     # Route protection guard
├── cookie.service.ts           # Cookie handling
├── cookie.strategy.ts          # Cookie auth strategy
├── fastify-throttler.guard.ts  # Rate limiting
├── header.strategy.ts          # Header-based auth (API keys)
├── local-session-lifecycle.service.ts
├── local-session.service.ts
├── local-session.strategy.ts
├── public.decorator.ts         # Mark endpoints as public
└── user.decorator.ts           # User injection decorator
```

---

## 5. Resolver Implementations

### Resolver Directory Structure
```
api/src/unraid-api/graph/resolvers/
├── api-key/          # API key management (10 files)
├── array/            # Array operations + parity (11 files)
├── cloud/            # Cloud/Connect operations
├── config/           # System configuration
├── customization/    # UI customization
├── disks/            # Disk management (6 files)
├── display/          # Display settings
├── docker/           # Docker management (36 files)
├── flash/            # Flash drive operations
├── flash-backup/     # Flash backup management
├── info/             # System information (7 subdirs)
│   ├── cpu/
│   ├── devices/
│   ├── display/
│   ├── memory/
│   ├── os/
│   ├── system/
│   └── versions/
├── logs/             # Log management (8 files)
├── metrics/          # System metrics (5 files)
├── mutation/         # Root mutation resolver
├── notifications/    # Notification management (7 files)
├── online/           # Online status
├── owner/            # Server owner info
├── rclone/           # Cloud storage (8 files)
├── registration/     # License/registration
├── servers/          # Server management
├── settings/         # Settings management (5 files)
├── sso/              # SSO/OIDC (8 subdirs)
├── ups/              # UPS monitoring (7 files)
├── vars/             # Unraid variables
└── vms/              # VM management (7 files)
```

### Complete API Surface

#### Queries

| Domain | Query | Description | Permission |
|--------|-------|-------------|------------|
| **Array** | `array` | Get array data (state, capacity, disks, parities, caches) | READ_ANY:ARRAY |
| **Disks** | `disks` | List all disks with temp, spin state, capacity | READ_ANY:DISK |
| **Disks** | `disk(id)` | Get specific disk by PrefixedID | READ_ANY:DISK |
| **Docker** | `docker` | Get Docker instance | READ_ANY:DOCKER |
| **Docker** | `container(id)` | Get specific container | READ_ANY:DOCKER |
| **Docker** | `containers` | List all containers (optional size info) | READ_ANY:DOCKER |
| **Docker** | `logs(id, since, tail)` | Container logs with filtering | READ_ANY:DOCKER |
| **Docker** | `networks` | Docker networks | READ_ANY:DOCKER |
| **Docker** | `portConflicts` | Port conflict detection | READ_ANY:DOCKER |
| **Docker** | `organizer` | Container organization structure | READ_ANY:DOCKER |
| **Docker** | `containerUpdateStatuses` | Check update availability | READ_ANY:DOCKER |
| **VMs** | `vms` | Get all VM domains | READ_ANY:VMS |
| **Info** | `info` | System info (CPU, memory, OS, baseboard, devices, versions) | READ_ANY:INFO |
| **Metrics** | `metrics` | System performance metrics | READ_ANY:INFO |
| **Logs** | `logFiles` | List available log files | READ_ANY:LOGS |
| **Logs** | `logFile(path, lines, startLine)` | Get specific log file content | READ_ANY:LOGS |
| **Notifications** | `notifications` | Get all notifications | READ_ANY:NOTIFICATIONS |
| **Notifications** | `overview` | Notification statistics | READ_ANY:NOTIFICATIONS |
| **Notifications** | `list` | Filtered notification list | READ_ANY:NOTIFICATIONS |
| **Notifications** | `warningsAndAlerts` | Deduplicated unread warnings/alerts | READ_ANY:NOTIFICATIONS |
| **RClone** | `rclone` | Cloud storage backup settings | READ_ANY:FLASH |
| **RClone** | `configForm(formOptions)` | Config form schemas | READ_ANY:FLASH |
| **RClone** | `remotes` | List configured remote storage | READ_ANY:FLASH |
| **UPS** | `upsDevices` | List UPS devices with status | READ_ANY:* |
| **UPS** | `upsDeviceById(id)` | Specific UPS device | READ_ANY:* |
| **UPS** | `upsConfiguration` | UPS configuration settings | READ_ANY:* |
| **Settings** | `settings` | System settings + SSO config | READ_ANY:CONFIG |
| **Shares** | `shares` | Storage shares with capacity | READ_ANY:SHARE |

#### Mutations

| Domain | Mutation | Description | Permission |
|--------|---------|-------------|------------|
| **Array** | `setState(input)` | Set array state (start/stop) | UPDATE_ANY:ARRAY |
| **Array** | `addDiskToArray(input)` | Add disk to array | UPDATE_ANY:ARRAY |
| **Array** | `removeDiskFromArray(input)` | Remove disk (array must be stopped) | UPDATE_ANY:ARRAY |
| **Array** | `mountArrayDisk(id)` | Mount a disk | UPDATE_ANY:ARRAY |
| **Array** | `unmountArrayDisk(id)` | Unmount a disk | UPDATE_ANY:ARRAY |
| **Array** | `clearArrayDiskStatistics(id)` | Clear disk statistics | UPDATE_ANY:ARRAY |
| **Parity** | `start(correct)` | Start parity check | UPDATE_ANY:ARRAY |
| **Parity** | `pause` | Pause parity check | UPDATE_ANY:ARRAY |
| **Parity** | `resume` | Resume parity check | UPDATE_ANY:ARRAY |
| **Parity** | `cancel` | Cancel parity check | UPDATE_ANY:ARRAY |
| **Docker** | `start(id)` | Start container | UPDATE_ANY:DOCKER |
| **Docker** | `stop(id)` | Stop container | UPDATE_ANY:DOCKER |
| **Docker** | `pause(id)` | Pause container | UPDATE_ANY:DOCKER |
| **Docker** | `unpause(id)` | Unpause container | UPDATE_ANY:DOCKER |
| **Docker** | `removeContainer(id, withImage?)` | Remove container (optionally with image) | DELETE_ANY:DOCKER |
| **Docker** | `updateContainer(id)` | Update to latest image | UPDATE_ANY:DOCKER |
| **Docker** | `updateContainers(ids)` | Update multiple containers | UPDATE_ANY:DOCKER |
| **Docker** | `updateAllContainers` | Update all with available updates | UPDATE_ANY:DOCKER |
| **Docker** | `updateAutostartConfiguration` | Update auto-start config (feature flag) | UPDATE_ANY:DOCKER |
| **Docker** | `createDockerFolder` | Create organizational folder | UPDATE_ANY:DOCKER |
| **Docker** | `setDockerFolderChildren` | Manage folder contents | UPDATE_ANY:DOCKER |
| **Docker** | `deleteDockerEntries` | Remove folders | UPDATE_ANY:DOCKER |
| **Docker** | `moveDockerEntriesToFolder` | Reorganize containers | UPDATE_ANY:DOCKER |
| **Docker** | `moveDockerItemsToPosition` | Position items | UPDATE_ANY:DOCKER |
| **Docker** | `renameDockerFolder` | Rename folder | UPDATE_ANY:DOCKER |
| **Docker** | `createDockerFolderWithItems` | Create folder with items | UPDATE_ANY:DOCKER |
| **Docker** | `syncDockerTemplatePaths` | Sync template data | UPDATE_ANY:DOCKER |
| **Docker** | `resetDockerTemplateMappings` | Reset to defaults | UPDATE_ANY:DOCKER |
| **VMs** | `start(id)` | Start VM | UPDATE_ANY:VMS |
| **VMs** | `stop(id)` | Stop VM | UPDATE_ANY:VMS |
| **VMs** | `pause(id)` | Pause VM | UPDATE_ANY:VMS |
| **VMs** | `resume(id)` | Resume VM | UPDATE_ANY:VMS |
| **VMs** | `forceStop(id)` | Force stop VM | UPDATE_ANY:VMS |
| **VMs** | `reboot(id)` | Reboot VM | UPDATE_ANY:VMS |
| **VMs** | `reset(id)` | Reset VM | UPDATE_ANY:VMS |
| **Notifications** | `createNotification(input)` | Create notification | CREATE_ANY:NOTIFICATIONS |
| **Notifications** | `deleteNotification(id, type)` | Delete notification | DELETE_ANY:NOTIFICATIONS |
| **Notifications** | `deleteArchivedNotifications` | Clear all archived | DELETE_ANY:NOTIFICATIONS |
| **Notifications** | `archiveNotification(id)` | Archive single | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `archiveNotifications(ids)` | Archive multiple | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `archiveAll(importance?)` | Archive all (optional filter) | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `unreadNotification(id)` | Mark as unread | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `unarchiveNotifications(ids)` | Restore archived | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `unarchiveAll(importance?)` | Restore all archived | UPDATE_ANY:NOTIFICATIONS |
| **Notifications** | `notifyIfUnique(input)` | Create if no equivalent exists | CREATE_ANY:NOTIFICATIONS |
| **Notifications** | `recalculateOverview` | Recompute overview stats | UPDATE_ANY:NOTIFICATIONS |
| **RClone** | `createRCloneRemote(input)` | Create remote storage | CREATE_ANY:FLASH |
| **RClone** | `deleteRCloneRemote(input)` | Delete remote storage | DELETE_ANY:FLASH |
| **UPS** | `configureUps(config)` | Update UPS configuration | UPDATE_ANY:* |
| **API Keys** | `createApiKey(input)` | Create API key | CREATE_ANY:API_KEY |
| **API Keys** | `addRoleForApiKey(input)` | Add role to key | UPDATE_ANY:API_KEY |
| **API Keys** | `removeRoleFromApiKey(input)` | Remove role from key | UPDATE_ANY:API_KEY |
| **API Keys** | `deleteApiKeys(input)` | Delete API keys | DELETE_ANY:API_KEY |
| **API Keys** | `updateApiKey(input)` | Update API key | UPDATE_ANY:API_KEY |

---

## 6. Subscription System

### PubSub Architecture

The subscription system uses `graphql-subscriptions` PubSub with a Node.js EventEmitter (max 30 listeners).

**Core PubSub (`api/src/core/pubsub.ts`):**
```typescript
import EventEmitter from 'events';
import { GRAPHQL_PUBSUB_CHANNEL } from '@unraid/shared/pubsub/graphql.pubsub.js';
import { PubSub } from 'graphql-subscriptions';

const eventEmitter = new EventEmitter();
eventEmitter.setMaxListeners(30);

export const pubsub = new PubSub({ eventEmitter });

export const createSubscription = <T = any>(
  channel: GRAPHQL_PUBSUB_CHANNEL | string
): AsyncIterableIterator<T> => {
  return pubsub.asyncIterableIterator<T>(channel);
};
```

### PubSub Channel Definitions

**Source:** `packages/unraid-shared/src/pubsub/graphql.pubsub.ts`

```typescript
export const GRAPHQL_PUBSUB_TOKEN = "GRAPHQL_PUBSUB";

export enum GRAPHQL_PUBSUB_CHANNEL {
  ARRAY = "ARRAY",
  CPU_UTILIZATION = "CPU_UTILIZATION",
  CPU_TELEMETRY = "CPU_TELEMETRY",
  DASHBOARD = "DASHBOARD",
  DISPLAY = "DISPLAY",
  INFO = "INFO",
  MEMORY_UTILIZATION = "MEMORY_UTILIZATION",
  NOTIFICATION = "NOTIFICATION",
  NOTIFICATION_ADDED = "NOTIFICATION_ADDED",
  NOTIFICATION_OVERVIEW = "NOTIFICATION_OVERVIEW",
  NOTIFICATION_WARNINGS_AND_ALERTS = "NOTIFICATION_WARNINGS_AND_ALERTS",
  OWNER = "OWNER",
  SERVERS = "SERVERS",
  VMS = "VMS",
  DOCKER_STATS = "DOCKER_STATS",
  LOG_FILE = "LOG_FILE",
  PARITY = "PARITY",
}
```

### Available Subscriptions

| Subscription | Channel | Interval | Description |
|-------------|---------|----------|-------------|
| `arraySubscription` | ARRAY | Event-based | Real-time array state changes |
| `systemMetricsCpu` | CPU_UTILIZATION | 1 second | CPU utilization data |
| `systemMetricsCpuTelemetry` | CPU_TELEMETRY | 5 seconds | CPU power & temperature |
| `systemMetricsMemory` | MEMORY_UTILIZATION | 2 seconds | Memory utilization |
| `dockerContainerStats` | DOCKER_STATS | Polling | Container performance stats |
| `logFileSubscription(path)` | LOG_FILE (dynamic) | Event-based | Real-time log file updates |
| `notificationAdded` | NOTIFICATION_ADDED | Event-based | New notification created |
| `notificationsOverview` | NOTIFICATION_OVERVIEW | Event-based | Overview stats updates |
| `notificationsWarningsAndAlerts` | NOTIFICATION_WARNINGS_AND_ALERTS | Event-based | Warning/alert changes |
| `upsUpdates` | - | Event-based | UPS device status changes |

### Subscription Management Services

Three-tier subscription management:

1. **SubscriptionManagerService** (low-level, internal)
   - Manages both polling and event-based subscriptions
   - Polling: Creates intervals via NestJS SchedulerRegistry with overlap guards
   - Event-based: Persistent listeners until explicitly stopped
   - Methods: `startSubscription()`, `stopSubscription()`, `stopAll()`, `isSubscriptionActive()`

2. **SubscriptionTrackerService** (mid-level)
   - Reference-counted subscriptions (auto-cleanup when no subscribers)

3. **SubscriptionHelperService** (high-level, for resolvers)
   - GraphQL subscriptions with automatic cleanup
   - Used directly in resolver decorators

**Dynamic Topics:** The LOG_FILE channel supports dynamic paths like `LOG_FILE:/var/log/test.log` for monitoring specific log files.

---

## 7. State Management

### Redux Store Architecture

The API uses Redux Toolkit for ephemeral runtime state derived from persistent INI configuration files stored in `/boot/config/`.

```
api/src/store/
├── actions/          # Redux action creators
├── listeners/        # State change event listeners
├── modules/          # Modular state slices
├── services/         # Business logic
├── state-parsers/    # INI file parsing utilities
├── watch/            # Filesystem watchers (Chokidar)
├── index.ts          # Store initialization
├── root-reducer.ts   # Combined reducer
└── types.ts          # State type definitions
```

**Key Design:** The StateManager singleton uses Chokidar to watch filesystem changes on INI config files, enabling reactive synchronization without polling. This accommodates legacy CLI tools and scripts that modify configuration outside the API.

---

## 8. Plugin Architecture

### Dynamic Plugin System

The API supports dynamic plugin loading at runtime through NestJS:

```
packages/
├── unraid-api-plugin-connect/   # Remote access, UPnP integration
├── unraid-api-plugin-generator/ # Code generation
├── unraid-api-plugin-health/    # Health monitoring
└── unraid-shared/               # Shared types, enums, utilities
```

**Plugin Loading:** Plugins load conditionally based on installation state. The `unraid-api-plugin-connect` handles remote access as an optional peer dependency.

### Schema Migration Status

The API is **actively migrating** from schema-first to code-first GraphQL:

- **Completed:** API Key Resolver (1/21)
- **Pending (20 resolvers):** Docker, Array, Disks, VMs, Connect, Display, Info, Owner, Unassigned Devices, Cloud, Flash, Config, Vars, Logs, Users, Notifications, Network, Registration, Servers, Services, Shares

**Migration pattern per resolver:**
1. Create model files with `@ObjectType()` and `@InputType()` decorators
2. Define return types and input parameters as classes
3. Update resolver to use new model classes
4. Create module file for dependency registration
5. Test functionality

---

## 9. Release History

### Recent Releases (Reverse Chronological)

| Version | Date | Highlights |
|---------|------|------------|
| **v4.29.2** | Dec 19, 2025 | Fix: connect plugin not loaded when connect installed |
| **v4.29.1** | Dec 19, 2025 | Reverted docker overview web component; fixed GUID/license race |
| **v4.29.0** | Dec 19, 2025 | Feature: Docker overview web component for 7.3+ |
| **v4.28.2** | Dec 16, 2025 | API startup timeout for v7.0 and v6.12 |
| **v4.28.0** | Dec 15, 2025 | Feature: Plugin cleanup on OS upgrade cancel; keyfile polling; dark mode |
| **v4.27.2** | Nov 21, 2025 | Fix: header flashing and trial date display |
| **v4.27.0** | Nov 19, 2025 | Feature: Removed API log download; fixed connect plugin uninstall |
| **v4.26.0** | Nov 17, 2025 | Feature: CPU power query/subscription; Apollo Studio schema publish |
| **v4.25.0** | Sep 26, 2025 | Feature: Tailwind scoping; notification filter pills |
| **v4.24.0** | Sep 18, 2025 | Feature: Optimized DOM content loading |
| **v4.23.0** | Sep 16, 2025 | Feature: API status manager |

### Milestone Releases
- **Open-sourced:** January 2025
- **v4.0.0:** OIDC/SSO support and permissions system
- **Native in Unraid 7.2+:** October 29, 2025

---

## 10. Roadmap & Upcoming Features

### Near-Term (Q1-Q2 2025, some may be completed)
- Developer Tools for Plugins (Q2)
- New modernized settings pages (Q2)
- Redesigned Unraid Connect configuration (Q1)
- Custom theme creation (Q2-Q3)
- Storage pool management (Q2)

### Mid-Term (Q3 2025)
- Modern Docker status interface redesign
- New plugins interface with redesigned management UI
- Streamlined Docker container deployment
- Real-time pool health monitoring

### Under Consideration (TBD)
- Docker Compose native support
- Advanced plugin configuration/development tools
- Storage share creation, settings, and unified management dashboard

---

## 11. Open Issues & Community Requests

### Open Issues: 32 total

#### Feature Requests (Enhancements)
| Issue | Title | Description |
|-------|-------|-------------|
| #1873 | Invoke Mover through API | Programmatic access to the Mover tool |
| #1872 | CLI list with creation dates | Timestamp data in CLI operations |
| #1871 | Container restart/update mutation | Single operation to restart+update containers |
| #1839 | SMART disk data | Detailed disk health monitoring via SMART |
| #1827-1828 | Nuxt UI upgrades | Interface modernization |

#### Reported Bugs
| Issue | Title | Impact |
|-------|-------|--------|
| #1861 | VM suspension issues | Cannot unsuspend PMSUSPENDED VMs |
| #1842 | Temperature inconsistency | SSD temps unavailable in Disk queries but accessible via Array |
| #1840 | Cache invalidation | Docker container data stale after external changes |
| #1837 | GraphQL partial failures | Entire queries fail when VMs/Docker unavailable |
| #1859 | Notification counting errors | Archive counts include duplicates |
| #1818 | Network query failures | GraphQL returns empty lists for network data |
| #1825 | UPS false data | Hardcoded values returned when no UPS connected |

#### Key Takeaways for unraid-mcp
1. **#1837 is critical**: We should handle partial GraphQL failures gracefully
2. **#1842**: Temperature data should be queried from Array endpoint, not Disk
3. **#1840**: Docker cache may return stale data; consider cache-busting strategies
4. **#1825**: UPS data validation needed - API returns fake data with no UPS
5. **#1861**: VM `PMSUSPENDED` state needs special handling
6. **#1871**: Container restart+update is a common need not yet in the API

---

## 12. Community Projects & Integrations

### 1. Unraid Management Agent (Go)
**Repository:** https://github.com/ruaan-deysel/unraid-management-agent
**Author:** Ruaan Deysel
**Language:** Go

A comprehensive third-party plugin providing:
- **57 REST endpoints** at `http://localhost:8043/api/v1`
- **54 MCP tools** for AI agent integration
- **41 Prometheus metrics** for monitoring
- **WebSocket** real-time event streaming
- **MQTT** publishing for IoT integration

**Architecture:** Event-driven with collectors -> event bus -> API cache pattern
- System Collector (15s): CPU, RAM, temperatures
- Array/Disk Collectors (30s): Storage metrics
- Docker/VM Collectors (30s): Container/VM data
- Native Go libraries (Docker SDK, libvirt bindings, /proc/sys access)

**Key Endpoints:**
```
/api/v1/health          # Health check
/api/v1/system          # System info
/api/v1/array           # Array status
/api/v1/disks           # Disk info
/api/v1/docker          # Docker containers
/api/v1/vm              # Virtual machines
/api/v1/network         # Network interfaces
/api/v1/shares          # User shares
/api/v1/gpu             # GPU metrics
/api/v1/ups             # UPS status
/api/v1/settings/*      # Disk thresholds, mover config
/api/v1/plugins         # Plugin info
/api/v1/updates         # Update status
```

### 2. Home Assistant - domalab/ha-unraid
**Repository:** https://github.com/domalab/ha-unraid
**Status:** Active (rebuilt in 2025.12.0 for GraphQL)
**Requires:** Unraid 7.2.0+, API key

**Features:**
- CPU usage, temperature, power consumption monitoring
- Memory utilization tracking
- Array state, per-disk and per-share metrics
- Docker container start/stop switches
- VM management controls
- UPS monitoring with energy dashboard integration
- Notification counts
- Dynamic entity creation (only creates entities for available services)

**Polling:** System data 30s, storage data 5min

### 3. Home Assistant - chris-mc1/unraid_api
**Repository:** https://github.com/chris-mc1/unraid_api
**Status:** Active
**Requires:** Unraid 7.2+, API key with Info/Servers/Array/Disk/Share read permissions

**Features:**
- Array status, storage utilization
- RAM and CPU usage
- Per-share free space (optional)
- Per-disk metrics: temperature, spin state, capacity
- Python-based (99.9%)

### 4. Home Assistant - ruaan-deysel/ha-unraid
**Repository:** https://github.com/ruaan-deysel/ha-unraid
**Status:** Active
**Note:** Uses the management agent's REST API rather than official GraphQL

### 5. Home Assistant - IDmedia/hass-unraid
**Repository:** https://github.com/IDmedia/hass-unraid
**Approach:** Docker container that parses WebSocket messages and forwards to HA via MQTT

### 6. unraid-mcp (This Project)
**Repository:** https://github.com/jmagar/unraid-mcp
**Language:** Python (FastMCP)
**Features:** 26 MCP tools, GraphQL client, WebSocket subscriptions

---

## 13. Architectural Insights for unraid-mcp

### Gaps in Our Current Implementation

Based on this research, potential improvements for unraid-mcp:

#### Missing Queries We Could Add
1. **Metrics subscriptions** - CPU (1s), CPU telemetry (5s), memory (2s) real-time data
2. **Docker port conflicts** - `portConflicts` query
3. **Docker organizer** - Folder management queries/mutations
4. **Docker update statuses** - Check for container image updates
5. **Parity check operations** - Start (with correct flag), pause, resume, cancel
6. **UPS monitoring** - Devices, configuration, real-time updates subscription
7. **API key management** - Full CRUD on API keys
8. **Settings management** - System settings queries
9. **SSO/OIDC configuration** - SSO settings
10. **Disk mount/unmount** - `mountArrayDisk` and `unmountArrayDisk` mutations
11. **Container removal** - `removeContainer` with optional image cleanup
12. **Container bulk updates** - `updateContainers` and `updateAllContainers`
13. **Flash backup** - Flash drive backup operations

#### GraphQL Query Patterns to Match

**Official query examples from Unraid docs:**
```graphql
# System Status
query {
  info {
    os { platform, distro, release, uptime }
    cpu { manufacturer, brand, cores, threads }
  }
}

# Array Monitoring
query {
  array {
    state
    capacity { disks { free, used, total } }
    disks { name, size, status, temp }
  }
}

# Docker Containers
query {
  dockerContainers {
    id, names, state, status, autoStart
  }
}
```

#### Authentication Best Practices
- Use `x-api-key` header (not query parameters)
- API keys need specific resource:action permissions
- For our MCP server, recommend keys with: `READ_ANY` on all resources + `UPDATE_ANY` on DOCKER, VMS, ARRAY for management operations
- Keys are stored at `/boot/config/plugins/unraid-api/`

#### Known Issues to Handle
1. **Partial query failures (#1837):** Wrap individual sections in try/catch; don't let VM failures crash Docker queries
2. **Temperature inconsistency (#1842):** Prefer Array endpoint for temperature data
3. **Docker cache staleness (#1840):** Use cache-busting options when available
4. **UPS phantom data (#1825):** Validate UPS data before presenting
5. **VM PMSUSPENDED (#1861):** Handle this state explicitly; unsuspend may fail
6. **Increased timeouts for disks:** The official API uses 90s read timeouts for disk operations

#### Subscription Channel Mapping

Our subscription implementation should align with the official channels:
```
ARRAY                            -> array state changes
CPU_UTILIZATION                  -> 1s CPU metrics
CPU_TELEMETRY                    -> 5s CPU power/temp
MEMORY_UTILIZATION               -> 2s memory metrics
DOCKER_STATS                     -> container stats
LOG_FILE + dynamic path          -> log file tailing
NOTIFICATION_ADDED               -> new notifications
NOTIFICATION_OVERVIEW            -> notification counts
NOTIFICATION_WARNINGS_AND_ALERTS -> warnings/alerts
PARITY                           -> parity check progress
VMS                              -> VM state changes
```

#### Performance Considerations
- Max 30 concurrent subscription connections (EventEmitter limit)
- Disk operations need extended timeouts (90s+)
- Docker `sizeRootFs` query is expensive; make it optional
- Storage data polling at 5min intervals (not faster) due to SMART query overhead
- cache-manager v7 expects TTL in milliseconds (not seconds)

---

## Appendix: Key Source File References

| File | Purpose |
|------|---------|
| `packages/unraid-shared/src/pubsub/graphql.pubsub.ts` | PubSub channel enum (17 channels) |
| `packages/unraid-shared/src/graphql-enums.ts` | AuthAction, Resource (35), Role enums |
| `packages/unraid-shared/src/graphql.model.ts` | Shared GraphQL models |
| `packages/unraid-shared/src/use-permissions.directive.ts` | Permission enforcement decorator |
| `api/src/core/pubsub.ts` | PubSub singleton + subscription factory |
| `api/src/unraid-api/auth/auth.service.ts` | 3-strategy auth (API key, cookie, local) |
| `api/src/unraid-api/auth/api-key.service.ts` | API key CRUD + validation |
| `api/src/unraid-api/auth/casbin/policy.ts` | RBAC policy definitions |
| `api/src/unraid-api/graph/resolvers/docker/docker.resolver.ts` | Docker queries + organizer |
| `api/src/unraid-api/graph/resolvers/docker/docker.mutations.resolver.ts` | Docker mutations (9 ops) |
| `api/src/unraid-api/graph/resolvers/vms/vms.resolver.ts` | VM queries |
| `api/src/unraid-api/graph/resolvers/vms/vms.mutations.resolver.ts` | VM mutations (7 ops) |
| `api/src/unraid-api/graph/resolvers/array/array.resolver.ts` | Array query + subscription |
| `api/src/unraid-api/graph/resolvers/array/array.mutations.resolver.ts` | Array mutations (6 ops) |
| `api/src/unraid-api/graph/resolvers/array/parity.mutations.resolver.ts` | Parity mutations (4 ops) |
| `api/src/unraid-api/graph/resolvers/notifications/notifications.resolver.ts` | Notification CRUD + subs |
| `api/src/unraid-api/graph/resolvers/metrics/metrics.resolver.ts` | System metrics + subs |
| `api/src/unraid-api/graph/resolvers/logs/logs.resolver.ts` | Log queries + subscription |
| `api/src/unraid-api/graph/resolvers/rclone/rclone.resolver.ts` | RClone queries |
| `api/src/unraid-api/graph/resolvers/rclone/rclone.mutation.resolver.ts` | RClone mutations |
| `api/src/unraid-api/graph/resolvers/ups/ups.resolver.ts` | UPS queries + mutations + sub |
| `api/src/unraid-api/graph/resolvers/api-key/api-key.mutation.ts` | API key mutations (5 ops) |
| `api/generated-schema.graphql` | Complete auto-generated schema |
