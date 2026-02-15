# Unraid API Feature Gap Analysis

> **Date:** 2026-02-07
> **Purpose:** Comprehensive inventory of every API capability that could become an MCP tool, cross-referenced against our current 26 tools to identify gaps.
> **Sources:** 7 research documents (3,800+ lines), Unraid API source code analysis, community project reviews, official documentation crawl.

---

## Table of Contents

1. [All GraphQL Queries Available](#a-all-graphql-queries-available)
2. [All GraphQL Mutations Available](#b-all-graphql-mutations-available)
3. [All GraphQL Subscriptions Available](#c-all-graphql-subscriptions-available)
4. [All Custom Scalars and Types](#d-all-custom-scalars-and-types)
5. [All Enums](#e-all-enums)
6. [API Capabilities NOT in Current MCP Server](#f-api-capabilities-not-currently-in-the-mcp-server)
7. [Community Project Capabilities](#g-community-project-capabilities)
8. [Known API Bugs and Limitations](#h-known-api-bugs-and-limitations)

---

## A. All GraphQL Queries Available

Every query type identified across all research documents, with their fields and sub-fields.

### A.1 System & Server Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `info` | `time`, `baseboard { manufacturer, model, version, serial }`, `cpu { manufacturer, brand, vendor, family, model, stepping, revision, voltage, speed, speedmin, speedmax, threads, cores, processors, socket, cache, flags }`, `devices`, `display`, `machineId`, `memory { max, total, free, used, active, available, buffcache, swaptotal, swapused, swapfree, layout[] }`, `os { platform, distro, release, codename, kernel, arch, hostname, codepage, logofile, serial, build, uptime }`, `system { manufacturer, model, version, serial, uuid }`, `versions { kernel, docker, unraid, node }`, `apps { installed, started }` | **YES** - `get_system_info()` |
| `vars` | `id`, `version`, `name`, `timeZone`, `comment`, `security`, `workgroup`, `domain`, `useNtp`, `ntpServer1-4`, `useSsl`, `port`, `portssl`, `useTelnet`, `useSsh`, `portssh`, `startPage`, `startArray`, `spindownDelay`, `defaultFormat`, `defaultFsType`, `shutdownTimeout`, `shareDisk`, `shareUser`, `shareSmbEnabled`, `shareNfsEnabled`, `shareAfpEnabled`, `shareCacheEnabled`, `shareMoverSchedule`, `shareMoverLogging`, `safeMode`, `configValid`, `configError`, `deviceCount`, `flashGuid`, `flashProduct`, `flashVendor`, `regState`, `regTo`, `mdState`, `mdNumDisks`, `mdNumDisabled`, `mdNumInvalid`, `mdNumMissing`, `mdResync`, `mdResyncAction`, `fsState`, `fsProgress`, `fsCopyPrcnt`, `shareCount`, `shareSmbCount`, `shareNfsCount`, `csrfToken`, `maxArraysz`, `maxCachesz` | **YES** - `get_unraid_variables()` |
| `online` | `Boolean` | **NO** |
| `owner` | Server owner information | **NO** |
| `server` | Server details | **NO** |
| `servers` | `[Server!]!` - List of all servers (Connect-managed) | **NO** |
| `me` | `id`, `name`, `description`, `roles`, `permissions` (current authenticated user) | **NO** |
| `user(id)` | `id`, `name`, `description`, `roles`, `password`, `permissions` | **NO** |
| `users(input)` | `[User!]!` - List of users | **NO** |
| `config` | `Config!` - System configuration | **NO** |
| `display` | Display settings | **NO** |
| `services` | `[Service!]!` - Running services list | **NO** |
| `cloud` | `error`, `apiKey`, `relay`, `minigraphql`, `cloud`, `allowedOrigins` | **NO** |
| `flash` | Flash drive information | **NO** |

### A.2 Network Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `network` | `id`, `iface`, `ifaceName`, `ipv4`, `ipv6`, `mac`, `internal`, `operstate`, `type`, `duplex`, `mtu`, `speed`, `carrierChanges`, `accessUrls { type, name, ipv4, ipv6 }` | **YES** - `get_network_config()` |

### A.3 Storage & Array Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `array` | `id`, `state`, `previousState`, `pendingState`, `capacity { kilobytes { free, used, total }, disks { free, used, total } }`, `boot { id, idx, name, device, size, fsSize, fsFree, fsUsed, status, rotational, temp, numReads, numWrites, numErrors, type, exportable, warning, critical, fsType, comment, format, transport, color, isSpinning }`, `parities[...]`, `disks[...]`, `caches[...]`, `parityCheckStatus` | **PARTIAL** - `get_array_status()` (missing `previousState`, `pendingState`, `parityCheckStatus`, disk fields like `color`, `isSpinning`, `transport`, `format`) |
| `parityHistory` | `[ParityCheck]` - Historical parity check records | **NO** |
| `disks` | `[Disk]!` - All physical disks with `device`, `type`, `name`, `vendor`, `size`, `bytesPerSector`, `totalCylinders`, `totalHeads`, `totalSectors`, `totalTracks`, `tracksPerCylinder`, `sectorsPerTrack`, `firmwareRevision`, `serialNum`, `interfaceType`, `smartStatus`, `temperature`, `partitions[]` | **YES** - `list_physical_disks()` |
| `disk(id)` | Single disk by PrefixedID | **YES** - `get_disk_details()` |
| `shares` | `name`, `free`, `used`, `size`, `include[]`, `exclude[]`, `cache`, `nameOrig`, `comment`, `allocator`, `splitLevel`, `floor`, `cow`, `color`, `luksStatus` | **PARTIAL** - `get_shares_info()` (may not query all fields like `allocator`, `splitLevel`, `floor`, `cow`, `luksStatus`) |
| `unassignedDevices` | `[UnassignedDevice]` - Devices not assigned to array/pool | **NO** |

### A.4 Docker Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `docker` | `id`, `containers[]`, `networks[]` | **YES** - `list_docker_containers()` |
| `dockerContainers(all)` | `[DockerContainer!]!` - All containers with full details including `id`, `names`, `image`, `imageId`, `command`, `created`, `ports[]`, `lanIpPorts[]`, `sizeRootFs`, `sizeRw`, `sizeLog`, `labels`, `state`, `status`, `hostConfig`, `networkSettings`, `mounts`, `autoStart`, `autoStartOrder`, `autoStartWait`, `templatePath`, `projectUrl`, `registryUrl`, `supportUrl`, `iconUrl`, `webUiUrl`, `shell`, `templatePorts`, `isOrphaned` | **YES** - `list_docker_containers()` / `get_docker_container_details()` |
| `container(id)` (via Docker resolver) | Single container by PrefixedID | **YES** - `get_docker_container_details()` |
| `docker.logs(id, since, tail)` | Container log output with filtering | **NO** |
| `docker.networks` / `dockerNetworks(all)` | `[DockerNetwork]` - name, id, created, scope, driver, enableIPv6, ipam, internal, attachable, ingress, configFrom, configOnly, containers, options, labels | **NO** |
| `dockerNetwork(id)` | Single network by ID | **NO** |
| `docker.portConflicts` | Port conflict detection | **NO** |
| `docker.organizer` | Container organization/folder structure | **NO** |
| `docker.containerUpdateStatuses` | Check for available container image updates (`UpdateStatus`: UP_TO_DATE, UPDATE_AVAILABLE, REBUILD_READY, UNKNOWN) | **NO** |

### A.5 VM Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `vms` | `id`, `domain[{ uuid/id, name, state }]` | **YES** - `list_vms()` / `get_vm_details()` |

### A.6 Notification Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `notifications` | `id`, `overview { unread { info, warning, alert, total }, archive { info, warning, alert, total } }`, `list(filter) [{ id, title, subject, description, importance, link, type, timestamp, formattedTimestamp }]` | **YES** - `get_notifications_overview()` / `list_notifications()` |
| `notifications.warningsAndAlerts` | Deduplicated unread warnings and alerts | **NO** |

### A.7 Registration & Connect Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `registration` | `id`, `type`, `state`, `expiration`, `updateExpiration`, `keyFile { location, contents }` | **YES** - `get_registration_info()` |
| `connect` | `id`, `dynamicRemoteAccess { ... }` | **YES** - `get_connect_settings()` |
| `remoteAccess` | `accessType`, `forwardType`, `port` | **NO** |
| `extraAllowedOrigins` | `[String!]!` | **NO** |

### A.8 RClone Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `rclone.remotes` | `name`, `type`, `parameters`, `config` | **YES** - `list_rclone_remotes()` |
| `rclone.configForm(formOptions)` | `id`, `dataSchema`, `uiSchema` | **YES** - `get_rclone_config_form()` |

### A.9 Logs Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `logFiles` | List available log files | **YES** - `list_available_log_files()` |
| `logFile(path, lines, startLine)` | Specific log file content with pagination | **YES** - `get_logs()` |

### A.10 Settings Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `settings` | `unified { values }`, SSO config | **NO** |

### A.11 API Key Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `apiKeys` | `[ApiKey!]!` - List all API keys with `id`, `name`, `description`, `roles[]`, `createdAt`, `permissions[]` | **NO** |
| `apiKey(id)` | Single API key by ID | **NO** |

### A.12 UPS Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `upsDevices` | List UPS devices with status | **NO** |
| `upsDeviceById(id)` | Specific UPS device | **NO** |
| `upsConfiguration` | UPS configuration settings | **NO** |

### A.13 Metrics Queries

| Query | Fields | Current MCP Coverage |
|-------|--------|---------------------|
| `metrics` | System performance metrics (CPU, memory utilization) | **NO** |

---

## B. All GraphQL Mutations Available

Every mutation identified across all research documents with their parameters and return types.

### B.1 Array Management Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `startArray` | none | `Array` | **NO** |
| `stopArray` | none | `Array` | **NO** |
| `addDiskToArray(input)` | `arrayDiskInput` | `Array` | **NO** |
| `removeDiskFromArray(input)` | `arrayDiskInput` | `Array` | **NO** |
| `mountArrayDisk(id)` | `ID!` | `Disk` | **NO** |
| `unmountArrayDisk(id)` | `ID!` | `Disk` | **NO** |
| `clearArrayDiskStatistics(id)` | `ID!` | `JSON` | **NO** |

### B.2 Parity Check Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `startParityCheck(correct)` | `correct: Boolean` | `JSON` | **NO** |
| `pauseParityCheck` | none | `JSON` | **NO** |
| `resumeParityCheck` | none | `JSON` | **NO** |
| `cancelParityCheck` | none | `JSON` | **NO** |

### B.3 Docker Container Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `docker.start(id)` | `PrefixedID!` | `DockerContainer` | **YES** - `manage_docker_container(action="start")` |
| `docker.stop(id)` | `PrefixedID!` | `DockerContainer` | **YES** - `manage_docker_container(action="stop")` |
| `docker.pause(id)` | `PrefixedID!` | `DockerContainer` | **NO** |
| `docker.unpause(id)` | `PrefixedID!` | `DockerContainer` | **NO** |
| `docker.removeContainer(id, withImage?)` | `PrefixedID!`, `Boolean` | `DockerContainer` | **NO** |
| `docker.updateContainer(id)` | `PrefixedID!` | `DockerContainer` | **NO** |
| `docker.updateContainers(ids)` | `[PrefixedID!]!` | `[DockerContainer]` | **NO** |
| `docker.updateAllContainers` | none | `[DockerContainer]` | **NO** |
| `docker.updateAutostartConfiguration` | auto-start config | varies | **NO** |

### B.4 Docker Organizer Mutations (Feature-Flagged)

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `docker.createDockerFolder` | folder config | varies | **NO** |
| `docker.setDockerFolderChildren` | folder ID, children | varies | **NO** |
| `docker.deleteDockerEntries` | entry IDs | varies | **NO** |
| `docker.moveDockerEntriesToFolder` | entries, folder | varies | **NO** |
| `docker.moveDockerItemsToPosition` | items, position | varies | **NO** |
| `docker.renameDockerFolder` | folder ID, name | varies | **NO** |
| `docker.createDockerFolderWithItems` | folder config, items | varies | **NO** |

### B.5 Docker Template Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `docker.syncDockerTemplatePaths` | none | varies | **NO** |
| `docker.resetDockerTemplateMappings` | none | varies | **NO** |

### B.6 VM Management Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `vm.start(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="start")` |
| `vm.stop(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="stop")` |
| `vm.pause(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="pause")` |
| `vm.resume(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="resume")` |
| `vm.forceStop(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="forceStop")` |
| `vm.reboot(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="reboot")` |
| `vm.reset(id)` | `PrefixedID!` | `Boolean` | **YES** - `manage_vm(action="reset")` |

### B.7 Notification Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `createNotification(input)` | `NotificationData!` | `Notification!` | **NO** |
| `deleteNotification(id, type)` | `String!`, `NotificationType!` | `NotificationOverview!` | **NO** |
| `deleteArchivedNotifications` | none | `NotificationOverview!` | **NO** |
| `archiveNotification(id)` | `String!` | `Notification!` | **NO** |
| `unreadNotification(id)` | `String!` | `Notification!` | **NO** |
| `archiveNotifications(ids)` | `[String!]` | `NotificationOverview!` | **NO** |
| `unarchiveNotifications(ids)` | `[String!]` | `NotificationOverview!` | **NO** |
| `archiveAll(importance?)` | `Importance` (optional) | `NotificationOverview!` | **NO** |
| `unarchiveAll(importance?)` | `Importance` (optional) | `NotificationOverview!` | **NO** |
| `recalculateOverview` | none | `NotificationOverview!` | **NO** |
| `notifyIfUnique(input)` | `NotificationData!` | `Notification!` | **NO** |

### B.8 RClone Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `createRCloneRemote(input)` | name, type, config | `RCloneRemote` | **YES** - `create_rclone_remote()` |
| `deleteRCloneRemote(input)` | name | `Boolean` | **YES** - `delete_rclone_remote()` |

### B.9 Server Power Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `shutdown` | none | `String` | **NO** |
| `reboot` | none | `String` | **NO** |

### B.10 Authentication & User Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `login(username, password)` | `String!`, `String!` | `String` | **NO** |
| `createApiKey(input)` | `CreateApiKeyInput!` | `ApiKeyWithSecret!` | **NO** |
| `addPermission(input)` | `AddPermissionInput!` | `Boolean!` | **NO** |
| `addRoleForUser(input)` | `AddRoleForUserInput!` | `Boolean!` | **NO** |
| `addRoleForApiKey(input)` | `AddRoleForApiKeyInput!` | `Boolean!` | **NO** |
| `removeRoleFromApiKey(input)` | `RemoveRoleFromApiKeyInput!` | `Boolean!` | **NO** |
| `deleteApiKeys(input)` | API key IDs | `Boolean` | **NO** |
| `updateApiKey(input)` | API key update data | `Boolean` | **NO** |
| `addUser(input)` | `addUserInput!` | `User` | **NO** |
| `deleteUser(input)` | `deleteUserInput!` | `User` | **NO** |

### B.11 Connect/Remote Access Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `connectSignIn(input)` | `ConnectSignInInput!` | `Boolean!` | **NO** |
| `connectSignOut` | none | `Boolean!` | **NO** |
| `enableDynamicRemoteAccess(input)` | `EnableDynamicRemoteAccessInput!` | `Boolean!` | **NO** |
| `setAdditionalAllowedOrigins(input)` | `AllowedOriginInput!` | `[String!]!` | **NO** |
| `setupRemoteAccess(input)` | `SetupRemoteAccessInput!` | `Boolean!` | **NO** |

### B.12 UPS Mutations

| Mutation | Parameters | Returns | Current MCP Coverage |
|----------|------------|---------|---------------------|
| `configureUps(config)` | UPS configuration | varies | **NO** |

---

## C. All GraphQL Subscriptions Available

Every subscription channel identified with update intervals and event triggers.

### C.1 PubSub Channel Definitions (from source code)

```
GRAPHQL_PUBSUB_CHANNEL {
  ARRAY                            // Array state changes
  CPU_UTILIZATION                  // 1-second CPU utilization data
  CPU_TELEMETRY                    // 5-second CPU power & temperature
  DASHBOARD                       // Dashboard aggregate updates
  DISPLAY                         // Display settings changes
  INFO                            // System information changes
  MEMORY_UTILIZATION              // 2-second memory utilization
  NOTIFICATION                    // Notification state changes
  NOTIFICATION_ADDED              // New notification created
  NOTIFICATION_OVERVIEW           // Notification count updates
  NOTIFICATION_WARNINGS_AND_ALERTS // Warning/alert changes
  OWNER                           // Owner information changes
  SERVERS                         // Server list changes
  VMS                             // VM state changes
  DOCKER_STATS                    // Container performance stats
  LOG_FILE                        // Real-time log file updates (dynamic path)
  PARITY                          // Parity check progress
}
```

### C.2 GraphQL Subscription Types (from schema)

| Subscription | Channel | Interval | Description | Current MCP Coverage |
|-------------|---------|----------|-------------|---------------------|
| `array` | ARRAY | Event-based | Real-time array state changes | **NO** (diag only) |
| `parityHistory` | PARITY | Event-based | Parity check progress updates | **NO** |
| `ping` | - | - | Connection keepalive | **NO** |
| `info` | INFO | Event-based | System info changes | **NO** (diag only) |
| `online` | - | Event-based | Online status changes | **NO** |
| `config` | - | Event-based | Configuration changes | **NO** |
| `display` | DISPLAY | Event-based | Display settings changes | **NO** |
| `dockerContainer(id)` | DOCKER_STATS | Polling | Single container stats (CPU%, mem, net I/O, block I/O) | **NO** |
| `dockerContainers` | DOCKER_STATS | Polling | All container state changes | **NO** |
| `dockerNetwork(id)` | - | Event-based | Single network changes | **NO** |
| `dockerNetworks` | - | Event-based | All network changes | **NO** |
| `flash` | - | Event-based | Flash drive changes | **NO** |
| `notificationAdded` | NOTIFICATION_ADDED | Event-based | New notification created | **NO** |
| `notificationsOverview` | NOTIFICATION_OVERVIEW | Event-based | Notification count updates | **NO** |
| `notificationsWarningsAndAlerts` | NOTIFICATION_WARNINGS_AND_ALERTS | Event-based | Warning/alert changes | **NO** |
| `owner` | OWNER | Event-based | Owner info changes | **NO** |
| `registration` | - | Event-based | Registration changes | **NO** |
| `server` | - | Event-based | Server status changes | **NO** |
| `service(name)` | - | Event-based | Specific service changes | **NO** |
| `share(id)` | - | Event-based | Single share changes | **NO** |
| `shares` | - | Event-based | All shares changes | **NO** |
| `unassignedDevices` | - | Event-based | Unassigned device changes | **NO** |
| `me` | - | Event-based | Current user changes | **NO** |
| `user(id)` | - | Event-based | Specific user changes | **NO** |
| `users` | - | Event-based | User list changes | **NO** |
| `vars` | - | Event-based | Server variable changes | **NO** |
| `vms` | VMS | Event-based | VM state changes | **NO** |
| `systemMetricsCpu` | CPU_UTILIZATION | 1 second | Real-time CPU utilization | **NO** |
| `systemMetricsCpuTelemetry` | CPU_TELEMETRY | 5 seconds | CPU power & temperature | **NO** |
| `systemMetricsMemory` | MEMORY_UTILIZATION | 2 seconds | Memory utilization | **NO** |
| `logFileSubscription(path)` | LOG_FILE (dynamic) | Event-based | Real-time log tailing | **NO** |
| `upsUpdates` | - | Event-based | UPS status changes | **NO** |

**Note:** The current MCP server has `test_subscription_query()` and `diagnose_subscriptions()` as diagnostic tools but does NOT expose any production subscription-based tools that stream real-time data.

---

## D. All Custom Scalars and Types

### D.1 Custom Scalar Types

| Scalar | Description | Serialization | Usage |
|--------|-------------|---------------|-------|
| `PrefixedID` | Server-prefixed identifiers | String (format: `TypePrefix:uuid`) | Container IDs, VM IDs, disk IDs, share IDs |
| `Long` | 52-bit integers (exceeds GraphQL Int 32-bit limit) | String in JSON | Disk sizes, memory values, operation counters |
| `BigInt` | Large integer values | String in JSON | Same as Long (used in newer schema versions) |
| `DateTime` | ISO 8601 date-time string (RFC 3339) | String | Timestamps, uptime, creation dates |
| `JSON` | Arbitrary JSON data structures | Object | Labels, network settings, mounts, host config |
| `Port` | Valid TCP port number (0-65535) | Integer | Network port references |
| `URL` | Standard URL format | String | Web UI URLs, registry URLs, support URLs |
| `UUID` | Universally Unique Identifier | String | VM domain UUIDs |

### D.2 Core Interface Types

| Interface | Fields | Implementors |
|-----------|--------|-------------|
| `Node` | `id: ID!` | `Array`, `Info`, `Network`, `Notifications`, `Connect`, `ArrayDisk`, `DockerContainer`, `VmDomain`, `Share` |
| `UserAccount` | `id`, `name`, `description`, `roles`, `permissions` | `Me`, `User` |

### D.3 Key Object Types

| Type | Key Fields | Notes |
|------|-----------|-------|
| `Array` | `state`, `previousState`, `pendingState`, `capacity`, `boot`, `parities[]`, `disks[]`, `caches[]`, `parityCheckStatus` | Implements Node |
| `ArrayDisk` | `id`, `idx`, `name`, `device`, `size`, `fsSize`, `fsFree`, `fsUsed`, `status`, `rotational`, `temp`, `numReads`, `numWrites`, `numErrors`, `type`, `exportable`, `warning`, `critical`, `fsType`, `comment`, `format`, `transport`, `color`, `isSpinning` | Implements Node |
| `ArrayCapacity` | `kilobytes { free, used, total }`, `disks { free, used, total }` | |
| `Capacity` | `free`, `used`, `total` | All String type |
| `ParityCheck` | Parity check status/progress data | |
| `DockerContainer` | 25+ fields (see A.4) | Implements Node |
| `Docker` | `id`, `containers[]`, `networks[]` | Implements Node |
| `DockerNetwork` | `name`, `id`, `created`, `scope`, `driver`, `enableIPv6`, `ipam`, etc. | |
| `ContainerPort` | `ip`, `privatePort`, `publicPort`, `type` | |
| `ContainerHostConfig` | JSON host configuration | |
| `VmDomain` | `uuid/id`, `name`, `state` | Implements Node |
| `Vms` | `id`, `domain[]` | |
| `Info` | `time`, `baseboard`, `cpu`, `devices`, `display`, `machineId`, `memory`, `os`, `system`, `versions`, `apps` | Implements Node |
| `InfoCpu` | `manufacturer`, `brand`, `vendor`, `family`, `model`, `stepping`, `revision`, `voltage`, `speed`, `speedmin`, `speedmax`, `threads`, `cores`, `processors`, `socket`, `cache`, `flags` | |
| `InfoMemory` | `max`, `total`, `free`, `used`, `active`, `available`, `buffcache`, `swaptotal`, `swapused`, `swapfree`, `layout[]` | |
| `MemoryLayout` | `bank`, `type`, `clockSpeed`, `manufacturer` | Missing `size` field (known bug) |
| `Os` | `platform`, `distro`, `release`, `codename`, `kernel`, `arch`, `hostname`, `codepage`, `logofile`, `serial`, `build`, `uptime` | |
| `Baseboard` | `manufacturer`, `model`, `version`, `serial` | |
| `SystemInfo` | `manufacturer`, `model`, `version`, `serial`, `uuid` | |
| `Versions` | `kernel`, `docker`, `unraid`, `node` | |
| `InfoApps` | `installed`, `started` | |
| `Network` | `iface`, `ifaceName`, `ipv4`, `ipv6`, `mac`, `internal`, `operstate`, `type`, `duplex`, `mtu`, `speed`, `carrierChanges`, `id`, `accessUrls[]` | Implements Node |
| `AccessUrl` | `type`, `name`, `ipv4`, `ipv6` | |
| `Share` | `name`, `free`, `used`, `size`, `include[]`, `exclude[]`, `cache`, `nameOrig`, `comment`, `allocator`, `splitLevel`, `floor`, `cow`, `color`, `luksStatus` | |
| `Disk` (physical) | `device`, `type`, `name`, `vendor`, `size`, `bytesPerSector`, `totalCylinders`, `totalHeads`, `totalSectors`, `totalTracks`, `tracksPerCylinder`, `sectorsPerTrack`, `firmwareRevision`, `serialNum`, `interfaceType`, `smartStatus`, `temperature`, `partitions[]` | |
| `DiskPartition` | Partition details | |
| `Notification` | `id`, `title`, `subject`, `description`, `importance`, `link`, `type`, `timestamp`, `formattedTimestamp` | Implements Node |
| `NotificationOverview` | `unread { info, warning, alert, total }`, `archive { info, warning, alert, total }` | |
| `NotificationCounts` | `info`, `warning`, `alert`, `total` | |
| `Registration` | `id`, `type`, `state`, `expiration`, `updateExpiration`, `keyFile { location, contents }` | |
| `Connect` | `id`, `dynamicRemoteAccess { ... }` | Implements Node |
| `RemoteAccess` | `accessType`, `forwardType`, `port` | |
| `Cloud` | `error`, `apiKey`, `relay`, `minigraphql`, `cloud`, `allowedOrigins` | |
| `Flash` | Flash drive information | |
| `UnassignedDevice` | Unassigned device details | |
| `Service` | Service name and status | |
| `Server` | Server details (Connect-managed) | |
| `ApiKey` | `id`, `name`, `description`, `roles[]`, `createdAt`, `permissions[]` | |
| `ApiKeyWithSecret` | `id`, `key`, `name`, `description`, `roles[]`, `createdAt`, `permissions[]` | |
| `Permission` | `resource`, `actions[]` | |
| `Config` | System configuration | |
| `Display` | Display settings | |
| `Owner` | Server owner info | |
| `Me` | Current user info | Implements UserAccount |
| `User` | User account info | Implements UserAccount |
| `Vars` | Server variables (40+ fields) | Implements Node |

### D.4 Input Types

| Input Type | Used By | Fields |
|-----------|---------|--------|
| `CreateApiKeyInput` | `createApiKey` | `name!`, `description`, `roles[]`, `permissions[]`, `overwrite` |
| `AddPermissionInput` | `addPermission` | `resource!`, `actions![]` |
| `AddRoleForUserInput` | `addRoleForUser` | User + role assignment |
| `AddRoleForApiKeyInput` | `addRoleForApiKey` | API key + role assignment |
| `RemoveRoleFromApiKeyInput` | `removeRoleFromApiKey` | API key + role removal |
| `arrayDiskInput` | `addDiskToArray`, `removeDiskFromArray` | Disk assignment data |
| `ConnectSignInInput` | `connectSignIn` | Connect credentials |
| `EnableDynamicRemoteAccessInput` | `enableDynamicRemoteAccess` | Remote access config |
| `AllowedOriginInput` | `setAdditionalAllowedOrigins` | Origin URLs |
| `SetupRemoteAccessInput` | `setupRemoteAccess` | Remote access setup |
| `NotificationData` | `createNotification`, `notifyIfUnique` | title, subject, description, importance |
| `NotificationFilter` | `notifications.list` | Filter criteria |
| `addUserInput` | `addUser` | User creation data |
| `deleteUserInput` | `deleteUser` | User deletion target |
| `usersInput` | `users` | User listing filter |

---

## E. All Enums

### E.1 Array & Disk Enums

| Enum | Values |
|------|--------|
| **ArrayState** | `STARTED`, `STOPPED`, `NEW_ARRAY`, `RECON_DISK`, `DISABLE_DISK`, `SWAP_DSBL`, `INVALID_EXPANSION`, `PARITY_NOT_BIGGEST`, `TOO_MANY_MISSING_DISKS`, `NEW_DISK_TOO_SMALL`, `NO_DATA_DISKS` |
| **ArrayPendingState** | Pending state transitions (exact values not documented) |
| **ArrayDiskStatus** | `DISK_NP`, `DISK_OK`, `DISK_NP_MISSING`, `DISK_INVALID`, `DISK_WRONG`, `DISK_DSBL`, `DISK_NP_DSBL`, `DISK_DSBL_NEW`, `DISK_NEW` |
| **ArrayDiskType** | `Data`, `Parity`, `Flash`, `Cache` |
| **ArrayDiskFsColor** | `GREEN_ON`, `GREEN_BLINK`, `BLUE_ON`, `BLUE_BLINK`, `YELLOW_ON`, `YELLOW_BLINK`, `RED_ON`, `RED_OFF`, `GREY_OFF` |
| **DiskInterfaceType** | `SAS`, `SATA`, `USB`, `PCIe`, `UNKNOWN` |
| **DiskFsType** | `xfs`, `btrfs`, `vfat`, `zfs` |
| **DiskSmartStatus** | SMART health assessment values |

### E.2 Docker Enums

| Enum | Values |
|------|--------|
| **ContainerState** | `RUNNING`, `PAUSED`, `EXITED` |
| **ContainerPortType** | `TCP`, `UDP` |
| **UpdateStatus** | `UP_TO_DATE`, `UPDATE_AVAILABLE`, `REBUILD_READY`, `UNKNOWN` |

### E.3 VM Enums

| Enum | Values |
|------|--------|
| **VmState** | `NOSTATE`, `RUNNING`, `IDLE`, `PAUSED`, `SHUTDOWN`, `SHUTOFF`, `CRASHED`, `PMSUSPENDED` |

### E.4 Notification Enums

| Enum | Values |
|------|--------|
| **Importance** | `ALERT`, `INFO`, `WARNING` |
| **NotificationType** | `UNREAD`, `ARCHIVE` |

### E.5 Auth & Permission Enums

| Enum | Values |
|------|--------|
| **Role** | `ADMIN`, `CONNECT`, `GUEST`, `VIEWER` |
| **AuthAction** | `CREATE_ANY`, `CREATE_OWN`, `READ_ANY`, `READ_OWN`, `UPDATE_ANY`, `UPDATE_OWN`, `DELETE_ANY`, `DELETE_OWN` |
| **Resource** (35 total) | `ACTIVATION_CODE`, `API_KEY`, `ARRAY`, `CLOUD`, `CONFIG`, `CONNECT`, `CONNECT__REMOTE_ACCESS`, `CUSTOMIZATIONS`, `DASHBOARD`, `DISK`, `DISPLAY`, `DOCKER`, `FLASH`, `INFO`, `LOGS`, `ME`, `NETWORK`, `NOTIFICATIONS`, `ONLINE`, `OS`, `OWNER`, `PERMISSION`, `REGISTRATION`, `SERVERS`, `SERVICES`, `SHARE`, `USER`, `VARS`, `VMS`, `WELCOME` |

### E.6 Registration Enums

| Enum | Values |
|------|--------|
| **RegistrationState** | `TRIAL`, `BASIC`, `PLUS`, `PRO`, `STARTER`, `UNLEASHED`, `LIFETIME`, `EEXPIRED`, `EGUID`, `EGUID1`, `ETRIAL`, `ENOKEYFILE`, `ENOFLASH`, `EBLACKLISTED`, `ENOCONN` |

### E.7 Configuration Enums

| Enum | Values |
|------|--------|
| **ConfigErrorState** | Configuration error state values |
| **WAN_ACCESS_TYPE** | `DYNAMIC`, `ALWAYS`, `DISABLED` |
| **WAN_FORWARD_TYPE** | WAN forwarding type values |

---

## F. API Capabilities NOT Currently in the MCP Server

The current MCP server has 26 tools. The following capabilities are available in the Unraid API but NOT covered by any existing tool.

### F.1 HIGH PRIORITY - New Tool Candidates

#### Array Management (0 tools currently, 7 mutations available)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `start_array()` | `startArray` mutation | Core server management |
| `stop_array()` | `stopArray` mutation | Core server management |
| `start_parity_check(correct)` | `startParityCheck` mutation | Data integrity management |
| `pause_parity_check()` | `pauseParityCheck` mutation | Parity management |
| `resume_parity_check()` | `resumeParityCheck` mutation | Parity management |
| `cancel_parity_check()` | `cancelParityCheck` mutation | Parity management |
| `get_parity_history()` | `parityHistory` query | Historical parity check results |

#### Server Power Management (0 tools currently, 2 mutations available)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `shutdown_server()` | `shutdown` mutation | Remote server management |
| `reboot_server()` | `reboot` mutation | Remote server management |

#### Notification Management (read-only currently, 10+ mutations available)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `create_notification(input)` | `createNotification` mutation | Proactive alerting from MCP |
| `archive_notification(id)` | `archiveNotification` mutation | Notification lifecycle |
| `archive_all_notifications(importance?)` | `archiveAll` mutation | Bulk management |
| `delete_notification(id, type)` | `deleteNotification` mutation | Cleanup |
| `delete_archived_notifications()` | `deleteArchivedNotifications` mutation | Bulk cleanup |
| `unread_notification(id)` | `unreadNotification` mutation | Mark as unread |
| `get_warnings_and_alerts()` | `notifications.warningsAndAlerts` query | Focused severity view |

#### Docker Extended Operations (3 tools currently, 10+ mutations available)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `pause_docker_container(id)` | `docker.pause` mutation | Container lifecycle |
| `unpause_docker_container(id)` | `docker.unpause` mutation | Container lifecycle |
| `remove_docker_container(id, with_image?)` | `docker.removeContainer` mutation | Container cleanup |
| `update_docker_container(id)` | `docker.updateContainer` mutation | Keep containers current |
| `update_all_docker_containers()` | `docker.updateAllContainers` mutation | Bulk updates |
| `check_docker_updates()` | `containerUpdateStatuses` query | Pre-update assessment |
| `get_docker_container_logs(id, since?, tail?)` | `docker.logs` query | Debugging/monitoring |
| `list_docker_networks(all?)` | `dockerNetworks` query | Network inspection |
| `get_docker_network(id)` | `dockerNetwork` query | Network details |
| `check_docker_port_conflicts()` | `docker.portConflicts` query | Conflict detection |

#### Disk Operations (2 tools currently, 3 mutations available)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `mount_array_disk(id)` | `mountArrayDisk` mutation | Disk management |
| `unmount_array_disk(id)` | `unmountArrayDisk` mutation | Disk management |
| `clear_disk_statistics(id)` | `clearArrayDiskStatistics` mutation | Statistics reset |
| `add_disk_to_array(input)` | `addDiskToArray` mutation | Array expansion |
| `remove_disk_from_array(input)` | `removeDiskFromArray` mutation | Array modification |

### F.2 MEDIUM PRIORITY - New Tool Candidates

#### UPS Monitoring (0 tools currently, 3 queries + 1 mutation + 1 subscription)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `list_ups_devices()` | `upsDevices` query | UPS monitoring |
| `get_ups_device(id)` | `upsDeviceById` query | UPS details |
| `get_ups_configuration()` | `upsConfiguration` query | UPS config |
| `configure_ups(config)` | `configureUps` mutation | UPS management |

#### System Metrics (0 tools currently, 1 query + 3 subscriptions)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_system_metrics()` | `metrics` query | Performance monitoring |
| `get_cpu_utilization()` | `systemMetricsCpu` subscription (polled) | Real-time CPU |
| `get_memory_utilization()` | `systemMetricsMemory` subscription (polled) | Real-time memory |
| `get_cpu_telemetry()` | `systemMetricsCpuTelemetry` subscription (polled) | CPU temp/power |

#### Unassigned Devices (0 tools currently, 1 query + 1 subscription)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `list_unassigned_devices()` | `unassignedDevices` query | Device management |

#### Flash Drive (0 tools currently, 1 query + 1 subscription)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_flash_info()` | `flash` query | Flash drive status |

#### User Management (0 tools currently, 3 queries + 2 mutations)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_current_user()` | `me` query | Identity context |
| `list_users()` | `users` query | User management |
| `get_user(id)` | `user(id)` query | User details |
| `add_user(input)` | `addUser` mutation | User creation |
| `delete_user(input)` | `deleteUser` mutation | User removal |

#### Services (0 tools currently, 1 query + 1 subscription)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `list_services()` | `services` query | Service monitoring |

#### Settings (0 tools currently, 1 query)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_settings()` | `settings` query | Configuration inspection |

### F.3 LOW PRIORITY - New Tool Candidates

#### API Key Management (0 tools currently, 2 queries + 5 mutations)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `list_api_keys()` | `apiKeys` query | Key inventory |
| `get_api_key(id)` | `apiKey(id)` query | Key details |
| `create_api_key(input)` | `createApiKey` mutation | Key provisioning |
| `delete_api_keys(input)` | `deleteApiKeys` mutation | Key cleanup |
| `update_api_key(input)` | `updateApiKey` mutation | Key modification |

#### Remote Access Management (0 tools currently, 1 query + 3 mutations)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_remote_access()` | `remoteAccess` query | Remote access status |
| `setup_remote_access(input)` | `setupRemoteAccess` mutation | Remote access config |
| `enable_dynamic_remote_access(input)` | `enableDynamicRemoteAccess` mutation | Toggle remote access |
| `set_allowed_origins(input)` | `setAdditionalAllowedOrigins` mutation | CORS config |

#### Cloud/Connect Management (0 tools currently, 1 query + 2 mutations)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_cloud_status()` | `cloud` query | Cloud connectivity |
| `connect_sign_in(input)` | `connectSignIn` mutation | Connect auth |
| `connect_sign_out()` | `connectSignOut` mutation | Connect deauth |

#### Server Management (0 tools currently, 2 queries)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_server_info()` | `server` query | Server details |
| `list_servers()` | `servers` query | Multi-server view |
| `get_online_status()` | `online` query | Connectivity check |
| `get_owner_info()` | `owner` query | Server owner |

#### Display & Config (0 tools currently, 2 queries)

| Proposed Tool | API Operation | Why Important |
|--------------|---------------|---------------|
| `get_display_settings()` | `display` query | Display config |
| `get_config()` | `config` query | System config |

### F.4 Summary: Coverage Statistics

| Category | Available in API | Covered by MCP | Gap |
|----------|-----------------|----------------|-----|
| **Queries** | ~30+ | 14 | ~16+ uncovered |
| **Mutations** | ~50+ | 10 (start/stop Docker+VM, RClone CRUD) | ~40+ uncovered |
| **Subscriptions** | ~30+ | 0 (2 diagnostic only) | ~30+ uncovered |
| **Total Operations** | ~110+ | 24 active | ~86+ uncovered |

**Current coverage: approximately 22% of available API operations.**

---

## G. Community Project Capabilities

### G.1 unraid-management-agent (Go Plugin by Ruaan Deysel)

Capabilities this project offers that we do NOT:

| Capability | Details | Our Status |
|-----------|---------|------------|
| **SMART Disk Data** | Detailed SMART attributes, health monitoring | NOT available via GraphQL API (Issue #1839) |
| **Container Logs** | Docker container log retrieval | Available via `docker.logs` query (we don't use it) |
| **GPU Metrics** | GPU utilization, temperature, VRAM | NOT available via GraphQL API |
| **Process Monitoring** | Active process list, resource usage | NOT available via GraphQL API |
| **CPU Load Averages** | Real-time 1/5/15 min load averages | Available via `metrics` query (we don't use it) |
| **Prometheus Metrics** | 41 exportable metrics at `/metrics` | NOT applicable to MCP |
| **MQTT Publishing** | IoT event streaming | NOT applicable to MCP |
| **Home Assistant Auto-Discovery** | MQTT auto-discovery | NOT applicable to MCP |
| **Disk Temperature History** | Historical temp tracking | Limited via API |
| **UPS Data** | UPS status monitoring | Available via API (we don't use it) |
| **Plugin Information** | List installed plugins | NOT available via GraphQL API |
| **Update Status** | Check for OS/plugin updates | NOT available via GraphQL API |
| **Mover Control** | Invoke the mover tool | NOT available via GraphQL API (Issue #1873) |
| **Disk Thresholds** | Warning/critical temp settings | Partially available via `ArrayDisk.warning`/`critical` |
| **54 MCP Tools** | Full MCP tool suite | We have 26 |
| **WebSocket Events** | Real-time event stream | We have diagnostic-only subscriptions |

### G.2 PSUnraid (PowerShell Module)

| Capability | Details | Our Status |
|-----------|---------|------------|
| **Server Status** | Comprehensive server overview | We have `get_system_info()` |
| **Array Status** | Array state and disk health | We have `get_array_status()` |
| **Docker Start/Stop/Restart** | Container lifecycle | We have start/stop only (no restart, no pause) |
| **VM Start/Stop** | VM lifecycle | We have full VM lifecycle |
| **Notification Retrieval** | Read notifications | We have `list_notifications()` |
| **Restart Containers** | Dedicated restart action | We do NOT have restart (would be stop+start) |

### G.3 unraid-ssh-mcp

Chose SSH over GraphQL API due to these gaps:

| Missing from GraphQL API | Impact on Our Project |
|--------------------------|----------------------|
| Container logs | Now available in API (`docker.logs`) -- we should add it |
| Detailed SMART data | Still missing from API (Issue #1839) |
| Real-time CPU load | Now available via `metrics` query -- we should add it |
| Process monitoring | Still missing from API |
| `/proc` and `/sys` access | Not applicable via API |

### G.4 Home Assistant Integrations

#### domalab/ha-unraid

| Capability | Our Status |
|-----------|------------|
| CPU usage, temperature, power consumption | NO - missing metrics tools |
| Memory utilization tracking | NO - missing metrics tools |
| Per-disk and per-share metrics | PARTIAL - have basic disk/share info |
| Docker container start/stop switches | YES |
| VM management controls | YES |
| UPS monitoring with energy dashboard | NO |
| Notification counts | YES |
| Dynamic entity creation | N/A |

#### chris-mc1/unraid_api

| Capability | Our Status |
|-----------|------------|
| Array status, storage utilization | YES |
| RAM and CPU usage | NO - missing metrics |
| Per-share free space | YES |
| Per-disk: temperature, spin state, capacity | PARTIAL |

---

## H. Known API Bugs and Limitations

### H.1 Active Bugs (from GitHub Issues)

| Issue | Title | Impact on MCP Implementation |
|-------|-------|------------------------------|
| **#1837** | GraphQL partial failures | **CRITICAL**: Entire queries fail when VMs/Docker unavailable. Must implement partial failure handling with separate try/catch per section. |
| **#1842** | Temperature inconsistency | SSD temps unavailable in `disks` query but accessible via `array` query. Use Array endpoint for temperature data. |
| **#1840** | Docker cache invalidation | Docker container data may be stale after external changes (docker CLI). Use `skipCache: true` parameter when available. |
| **#1825** | UPS false data | API returns hardcoded/phantom values when NO UPS is connected. Must validate UPS data before presenting to user. |
| **#1861** | VM PMSUSPENDED issues | Cannot unsuspend VMs in `PMSUSPENDED` state. Must handle this state explicitly and warn users. |
| **#1859** | Notification counting errors | Archive counts may include duplicates. Use `recalculateOverview` mutation to fix. |
| **#1818** | Network query failures | GraphQL may return empty lists for network data. Handle gracefully. |
| **#1871** | Container restart/update mutation | Single restart+update operation not yet in API. Must implement as separate stop+start. |
| **#1873** | Mover not invocable via API | No GraphQL mutation to trigger the mover. Cannot implement mover tools. |
| **#1839** | SMART disk data missing | Detailed SMART attributes not yet exposed via GraphQL. Major gap for disk health tools. |
| **#1872** | CLI list missing creation dates | Timestamp data unavailable in some CLI operations. |

### H.2 Schema/Type Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| **Int Overflow** | Memory size fields and disk operation counters can overflow 32-bit Int. API uses `Long`/`BigInt` scalars but some fields remain problematic. | Parse values as strings, convert to Python `int` |
| **NaN Values** | Fields `sysArraySlots`, `sysCacheSlots`, `cacheNumDevices`, `cacheSbNumDisks` in `vars` query can return NaN. | Query only curated subset of `vars` fields (current approach) |
| **Non-nullable Null** | `info.devices` section has non-nullable fields that return null in practice. | Avoid querying `info.devices` entirely (current approach) |
| **Memory Layout Size** | Individual memory stick `size` values not returned by API. | Cannot calculate total memory from layout data |
| **PrefixedID Format** | IDs follow `TypePrefix:uuid` format. Clients must handle as opaque strings. | Already handled in current implementation |

### H.3 Infrastructure Limitations

| Limitation | Description | Impact |
|-----------|-------------|--------|
| **Rate Limiting** | 100 requests per 10 seconds (`@nestjs/throttler`). | Must implement request queuing/backoff for bulk operations |
| **EventEmitter Limit** | Max 30 concurrent subscription listeners. | Limit simultaneous subscription tools |
| **Disk Operation Timeouts** | Disk queries require 90s+ read timeouts. | Already handled with custom timeout config |
| **Docker Size Queries** | `sizeRootFs` query is expensive. | Make it optional in list queries, only include in detail queries |
| **Storage Polling Interval** | SMART query overhead means storage data should poll at 5min minimum. | Rate-limit storage-related subscriptions |
| **Cache TTL** | cache-manager v7 expects TTL in milliseconds (not seconds). | Correct TTL units in any caching implementation |
| **Schema Volatility** | API schema is still evolving between versions. | Consider version-checking at startup, graceful degradation |
| **Nchan Memory** | WebSocket subscriptions can cause Nginx memory exhaustion (mitigated in 7.1.0+ but still possible). | Limit concurrent subscriptions, implement reconnection logic |
| **SSL/TLS** | Self-signed certificates require special handling for local IP access. | Already handled via `UNRAID_VERIFY_SSL` env var |
| **Version Dependency** | Full API requires Unraid 7.2+. Pre-7.2 needs Connect plugin. | Document minimum version requirements per tool |

### H.4 Features Requested but NOT Yet in API

| Feature | GitHub Issue | Status |
|---------|-------------|--------|
| Mover invocation | #1873 | Open feature request |
| SMART disk data | #1839 | Open feature request (was bounty candidate) |
| System temperature monitoring (CPU, GPU, motherboard, NVMe, chipset) | #1597 | Open bounty (not implemented) |
| Container restart+update single mutation | #1871 | Open feature request |
| Docker Compose native support | Roadmap TBD | Under consideration |
| Plugin information/management via API | Not filed | Not exposed |
| File browser/upload/download | Not filed | Legacy PHP WebGUI only |
| Process list monitoring | Not filed | Not exposed |
| GPU metrics | Not filed | Not exposed |

---

## Appendix: Proposed New Tool Count by Priority

| Priority | Category | New Tools | Total After |
|----------|----------|-----------|-------------|
| **HIGH** | Array Management | 7 | |
| **HIGH** | Server Power | 2 | |
| **HIGH** | Notification Mutations | 7 | |
| **HIGH** | Docker Extended | 10 | |
| **HIGH** | Disk Operations | 5 | |
| | **High Priority Subtotal** | **31** | **57** |
| **MEDIUM** | UPS Monitoring | 4 | |
| **MEDIUM** | System Metrics | 4 | |
| **MEDIUM** | Unassigned Devices | 1 | |
| **MEDIUM** | Flash Drive | 1 | |
| **MEDIUM** | User Management | 5 | |
| **MEDIUM** | Services | 1 | |
| **MEDIUM** | Settings | 1 | |
| | **Medium Priority Subtotal** | **17** | **74** |
| **LOW** | API Key Management | 5 | |
| **LOW** | Remote Access | 4 | |
| **LOW** | Cloud/Connect | 3 | |
| **LOW** | Server Management | 4 | |
| **LOW** | Display & Config | 2 | |
| | **Low Priority Subtotal** | **18** | **92** |
| | **GRAND TOTAL NEW TOOLS** | **66** | **92** |

**Current tools: 26 | Potential total: 92 | Gap: 66 tools (72% of potential uncovered)**

---

## Appendix: Data Sources Cross-Reference

| Document | Lines | Key Contributions |
|----------|-------|-------------------|
| `unraid-api-research.md` | 819 | API overview, auth flow, query/mutation examples, version history, recommendations |
| `unraid-api-source-analysis.md` | 998 | Complete resolver listing, PubSub channels, mutation details, open issues, community projects |
| `unraid-api-exa-research.md` | 569 | DeepWiki architecture, rate limits, OIDC providers, Python client library, MCP listings |
| `unraid-api-crawl.md` | 1451 | Complete GraphQL schema (Query/Mutation/Subscription types), CLI reference, all enums/scalars |
| `raw/release-7.0.0.md` | 958 | ZFS support, VM snapshots/clones, File Manager, Tailscale, notification agents |
| `raw/release-7.2.0.md` | 348 | API built into OS, responsive WebGUI, RAIDZ expansion, SSO, Ext2/3/4/NTFS/exFAT support |
| `raw/blog-api-bounty.md` | 139 | Feature Bounty Program, community projects showcase |
