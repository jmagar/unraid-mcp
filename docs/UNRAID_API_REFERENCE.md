# Unraid API v4.29.2 — Complete Reference

> **Source of truth.** Auto-generated from live GraphQL introspection against tootie (10.1.0.2:31337) on 2026-03-15.
> Unraid 7.2.4 · API v4.29.2 · 46 queries · 22 mutations · 11 subscriptions · 156 types

---

## Table of Contents

- [Authentication](#authentication)
- [Scalars & ID Format](#scalars--id-format)
- [Queries](#queries)
  - [System & Server Info](#system--server-info)
  - [Array & Storage](#array--storage)
  - [Docker](#docker)
  - [Virtual Machines](#virtual-machines)
  - [Notifications](#notifications)
  - [API Keys & Permissions](#api-keys--permissions)
  - [Users & Auth](#users--auth)
  - [RClone / Backup](#rclone--backup)
  - [UPS / Power](#ups--power)
  - [Settings & Configuration](#settings--configuration)
  - [Logs](#logs)
  - [OIDC / SSO](#oidc--sso)
  - [Plugins](#plugins)
- [Mutations](#mutations)
  - [Notification Mutations](#notification-mutations)
  - [Array Mutations](#array-mutations)
  - [Docker Mutations](#docker-mutations)
  - [VM Mutations](#vm-mutations)
  - [Parity Check Mutations](#parity-check-mutations)
  - [API Key Mutations](#api-key-mutations)
  - [Customization Mutations](#customization-mutations)
  - [RClone Mutations](#rclone-mutations)
  - [Flash Backup](#flash-backup)
  - [Settings Mutations](#settings-mutations)
  - [Plugin Mutations](#plugin-mutations)
- [Subscriptions](#subscriptions)
- [Enums](#enums)
- [Input Types](#input-types)
- [Object Types (Full Field Reference)](#object-types-full-field-reference)

---

## Authentication

All requests require an API key passed via the `x-api-key` HTTP header:

```bash
curl -k -X POST \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ online }"}' \
  https://YOUR-SERVER/graphql
```

**Rate limit:** 100 requests per 10 seconds.

---

## Scalars & ID Format

| Scalar | Description |
|--------|-------------|
| `PrefixedID` | Server-prefixed ID: `<serverHash>:<localId>`. Input accepts with or without prefix. Output always includes prefix. |
| `BigInt` | Non-fractional signed whole numbers (for disk sizes in KB, memory in bytes, etc.) |
| `DateTime` | ISO 8601 UTC string, e.g. `2026-03-15T09:54:33Z` |
| `JSON` | Arbitrary JSON value (used for settings, labels, mount info) |
| `Port` | Valid TCP port 0–65535 |

---

## Queries

### System & Server Info

#### `info` → `Info!`
Full hardware and software information. Permission: `READ_ANY` on `INFO`.

```graphql
query {
  info {
    time
    baseboard { manufacturer model version serial memMax memSlots }
    cpu { manufacturer brand cores threads speed speedmax socket topology packages { totalPower power temp } }
    devices {
      gpu { type vendorname productid blacklisted }
      network { iface model vendor mac speed dhcp }
      pci { type vendorname productname vendorid productid }
      usb { name bus device }
    }
    display { theme unit scale tabs resize wwn total usage text warning critical hot max locale
      case { url icon error base64 }
    }
    memory { layout { size bank type clockSpeed manufacturer formFactor partNum serialNum } }
    os { platform distro release kernel arch hostname fqdn uptime uefi }
    system { manufacturer model version serial uuid sku virtual }
    versions { core { unraid api kernel } packages { openssl node npm pm2 git nginx php docker } }
  }
}
```

#### `vars` → `Vars!`
143 system variables including hostname, timezone, array config, share settings, registration state, CSRF token, disk sync parameters, and much more. Permission: `READ_ANY` on `VARS`.

```graphql
query {
  vars {
    version name timeZone comment security workgroup
    port portssl portssh useSsl useSsh useTelnet
    startArray spindownDelay shutdownTimeout
    shareCount shareSmbCount shareNfsCount
    regTy regState regTo
    mdNumDisks mdNumDisabled mdState mdResync
    configValid configError safeMode csrfToken
  }
}
```

#### `metrics` → `Metrics!`
CPU and memory utilization. Permission: `READ_ANY` on `INFO`.

```graphql
query {
  metrics {
    cpu { percentTotal cpus { percentTotal percentUser percentSystem percentIdle } }
    memory { total used free available active buffcache percentTotal swapTotal swapUsed swapFree percentSwapTotal }
  }
}
```

#### `server` → `Server`
Local server info. Permission: `READ_ANY` on `SERVERS`.

```graphql
query {
  server { id name status guid apikey wanip lanip localurl remoteurl owner { username url avatar } }
}
```

#### `servers` → `[Server!]!`
All registered servers (usually just the local one). Permission: `READ_ANY` on `SERVERS`.

#### `online` → `Boolean!`
Simple connectivity check. Permission: `READ_ANY` on `ONLINE`.

#### `owner` → `Owner!`
Server owner info. Permission: `READ_ANY` on `OWNER`. Returns `username`, `url`, `avatar`.

#### `registration` → `Registration`
License info. Permission: `READ_ANY` on `REGISTRATION`. Returns `type`, `state`, `keyFile { location contents }`, `expiration`, `updateExpiration`.

#### `config` → `Config!`
Configuration validity. Permission: `READ_ANY` on `CONFIG`. Returns `valid`, `error`.

#### `services` → `[Service!]!`
Running services. Permission: `READ_ANY` on `SERVICES`. Each: `name`, `online`, `uptime { timestamp }`, `version`.

#### `flash` → `Flash!`
Flash drive info. Permission: `READ_ANY` on `FLASH`. Returns `guid`, `vendor`, `product`.

#### `customization` → `Customization`
UI customization. Permission: `READ_ANY` on `CUSTOMIZATIONS`. Returns `activationCode { ... }`, `partnerInfo { ... }`, `theme { ... }`.

#### `settings` → `Settings!`
All settings including unified form, SSO, and API config.

```graphql
query {
  settings {
    unified { dataSchema uiSchema values }
    sso { oidcProviders { id name clientId issuer scopes } }
    api { version extraOrigins sandbox plugins }
  }
}
```

#### `isInitialSetup` → `Boolean!`
Whether server is in initial setup mode (no permission required).

---

### Array & Storage

#### `array` → `UnraidArray!`
Array state with all disks. Permission: `READ_ANY` on `ARRAY`.

```graphql
query {
  array {
    state
    capacity { kilobytes { free used total } disks { free used total } }
    boot { id name device size status temp type }
    parities { id name device size status temp numReads numWrites numErrors }
    parityCheckStatus { status progress speed errors duration correcting paused running }
    disks { id idx name device size status temp fsSize fsFree fsUsed type fsType color isSpinning numReads numWrites numErrors }
    caches { id name device size status temp fsSize fsFree fsUsed type }
  }
}
```

#### `shares` → `[Share!]!`
User shares. Permission: `READ_ANY` on `SHARE`.

```graphql
query {
  shares { id name free used size include exclude cache nameOrig comment allocator splitLevel floor cow color luksStatus }
}
```

#### `disks` → `[Disk!]!`
Physical disks (hardware-level). Permission: `READ_ANY` on `DISK`.

```graphql
query {
  disks { id device type name vendor size serialNum firmwareRevision interfaceType smartStatus temperature isSpinning
    partitions { name fsType size } }
}
```

#### `disk(id: PrefixedID!)` → `Disk!`
Single disk by ID. Permission: `READ_ANY` on `DISK`.

#### `parityHistory` → `[ParityCheck!]!`
Parity check history. Permission: `READ_ANY` on `ARRAY`.

```graphql
query {
  parityHistory { date duration speed status errors progress correcting paused running }
}
```

---

### Docker

#### `docker` → `Docker!`
Container and network queries. Permission: `READ_ANY` on `DOCKER`.

**Available sub-fields on Docker type:**
- `containers(skipCache: Boolean! = false)` → `[DockerContainer!]!`
- `networks(skipCache: Boolean! = false)` → `[DockerNetwork!]!`

**That's it.** No `logs`, no `portConflicts`, no `containerUpdateStatuses`. Only `containers` and `networks`.

```graphql
query {
  docker {
    containers(skipCache: false) {
      id names image imageId command created state status autoStart
      ports { ip privatePort publicPort type }
      sizeRootFs labels hostConfig { networkMode } networkSettings mounts
    }
    networks(skipCache: false) {
      id name created scope driver enableIPv6
      internal attachable ingress configOnly
      ipam containers options labels
    }
  }
}
```

**DockerContainer fields:** `id`, `names`, `image`, `imageId`, `command`, `created`, `ports`, `sizeRootFs`, `labels`, `state` (RUNNING/EXITED), `status`, `hostConfig`, `networkSettings`, `mounts`, `autoStart`.

**DockerNetwork fields:** `id`, `name`, `created`, `scope`, `driver`, `enableIPv6`, `ipam`, `internal`, `attachable`, `ingress`, `configFrom`, `configOnly`, `containers`, `options`, `labels`.

---

### Virtual Machines

#### `vms` → `Vms!`
All VMs. Permission: `READ_ANY` on `VMS`.

```graphql
query {
  vms {
    domains { id name state uuid }
    domain { id name state }
  }
}
```

**VmState enum:** `NOSTATE`, `RUNNING`, `IDLE`, `PAUSED`, `SHUTDOWN`, `SHUTOFF`, `CRASHED`, `PMSUSPENDED`.

---

### Notifications

#### `notifications` → `Notifications!`
Overview and list. Permission: `READ_ANY` on `NOTIFICATIONS`.

```graphql
# Overview (counts by severity)
query {
  notifications {
    overview {
      unread { info warning alert total }
      archive { info warning alert total }
    }
  }
}

# List with filter
query {
  notifications {
    list(filter: { type: UNREAD, offset: 0, limit: 20, importance: WARNING }) {
      id title subject description importance link type timestamp formattedTimestamp
    }
  }
}
```

**NotificationFilter input:** `type` (UNREAD/ARCHIVE, required), `offset` (required), `limit` (required), `importance` (optional: INFO/WARNING/ALERT).

---

### API Keys & Permissions

#### `apiKeys` → `[ApiKey!]!`
All API keys. Permission: `READ_ANY` on `API_KEY`.

```graphql
query { apiKeys { id key name description roles createdAt permissions { resource actions } } }
```

#### `apiKey(id: PrefixedID!)` → `ApiKey`
Single API key by ID. Permission: `READ_ANY` on `API_KEY`.

#### `apiKeyPossibleRoles` → `[Role!]!`
Available roles (ADMIN, CONNECT, GUEST, VIEWER). Permission: `READ_ANY` on `PERMISSION`.

#### `apiKeyPossiblePermissions` → `[Permission!]!`
All possible permissions. Permission: `READ_ANY` on `PERMISSION`.

#### `getPermissionsForRoles(roles: [Role!]!)` → `[Permission!]!`
Resolve roles to actual permissions. Permission: `READ_ANY` on `PERMISSION`.

#### `previewEffectivePermissions(roles: [Role!], permissions: [AddPermissionInput!])` → `[Permission!]!`
Preview effective permissions for a role/permission combo. Permission: `READ_ANY` on `PERMISSION`.

#### `getAvailableAuthActions` → `[AuthAction!]!`
All auth actions (CREATE_ANY, READ_OWN, etc.).

#### `getApiKeyCreationFormSchema` → `ApiKeyFormSettings!`
JSON Schema for API key creation form. Permission: `READ_ANY` on `API_KEY`. Returns `dataSchema`, `uiSchema`, `values`.

---

### Users & Auth

#### `me` → `UserAccount!`
Current authenticated user. Permission: `READ_ANY` on `ME`.

```graphql
query { me { id name description roles permissions { resource actions } } }
```

---

### RClone / Backup

#### `rclone` → `RCloneBackupSettings!`
RClone configuration. Permission: `READ_ANY` on `FLASH`.

```graphql
query {
  rclone {
    remotes { name type parameters config }
    drives { name options }
    configForm(formOptions: { providerType: "drive", showAdvanced: false }) {
      id dataSchema uiSchema
    }
  }
}
```

---

### UPS / Power

#### `upsDevices` → `[UPSDevice!]!`
All UPS devices.

```graphql
query {
  upsDevices {
    id name model status
    battery { chargeLevel estimatedRuntime health }
    power { inputVoltage outputVoltage loadPercentage }
  }
}
```

#### `upsDeviceById(id: String!)` → `UPSDevice`
Single UPS by ID.

#### `upsConfiguration` → `UPSConfiguration!`
UPS daemon configuration.

```graphql
query {
  upsConfiguration {
    service upsCable customUpsCable upsType device
    overrideUpsCapacity batteryLevel minutes timeout killUps
    nisIp netServer upsName modelName
  }
}
```

---

### Logs

#### `logFiles` → `[LogFile!]!`
Available log files. Permission: `READ_ANY` on `LOGS`.

```graphql
query { logFiles { name path size modifiedAt } }
```

#### `logFile(path: String!, lines: Int, startLine: Int)` → `LogFileContent!`
Read a log file. Permission: `READ_ANY` on `LOGS`.

```graphql
query { logFile(path: "/var/log/syslog", lines: 100, startLine: 1) { path content totalLines startLine } }
```

---

### OIDC / SSO

#### `isSSOEnabled` → `Boolean!`
Whether SSO is enabled.

#### `publicOidcProviders` → `[PublicOidcProvider!]!`
Public OIDC provider info for login buttons. Returns `id`, `name`, `buttonText`, `buttonIcon`, `buttonVariant`, `buttonStyle`.

#### `oidcProviders` → `[OidcProvider!]!`
All configured OIDC providers (admin only). Permission: `READ_ANY` on `CONFIG`.

#### `oidcProvider(id: PrefixedID!)` → `OidcProvider`
Single OIDC provider by ID. Permission: `READ_ANY` on `CONFIG`.

#### `oidcConfiguration` → `OidcConfiguration!`
Full OIDC configuration. Permission: `READ_ANY` on `CONFIG`. Returns `providers` list and `defaultAllowedOrigins`.

#### `validateOidcSession(token: String!)` → `OidcSessionValidation!`
Validate an OIDC session token. Permission: `READ_ANY` on `CONFIG`. Returns `valid`, `username`.

---

### Plugins

#### `plugins` → `[Plugin!]!`
Installed plugins. Permission: `READ_ANY` on `CONFIG`.

```graphql
query { plugins { name version hasApiModule hasCliModule } }
```

---

## Mutations

### Notification Mutations

All notification mutations are **root-level** on the Mutation type.

| Mutation | Args | Returns | Description |
|----------|------|---------|-------------|
| `createNotification` | `input: NotificationData!` | `Notification!` | Create a new notification |
| `archiveNotification` | `id: PrefixedID!` | `Notification!` | Mark as archived |
| `archiveNotifications` | `ids: [PrefixedID!]!` | `NotificationOverview!` | Archive multiple |
| `archiveAll` | `importance: NotificationImportance` | `NotificationOverview!` | Archive all (optional filter) |
| `unreadNotification` | `id: PrefixedID!` | `Notification!` | Mark as unread |
| `unarchiveNotifications` | `ids: [PrefixedID!]!` | `NotificationOverview!` | Unarchive multiple |
| `unarchiveAll` | `importance: NotificationImportance` | `NotificationOverview!` | Unarchive all (optional filter) |
| `deleteNotification` | `id: PrefixedID!`, `type: NotificationType!` | `NotificationOverview!` | Delete one notification |
| `deleteArchivedNotifications` | — | `NotificationOverview!` | Delete ALL archived |
| `recalculateOverview` | — | `NotificationOverview!` | Recompute counts from disk |

---

### Array Mutations

Nested under `mutation { array { ... } }` → `ArrayMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `setState` | `input: ArrayStateInput!` | `UnraidArray!` | `UPDATE_ANY` on `ARRAY` | Start/stop array (`desiredState: START/STOP`) |
| `addDiskToArray` | `input: ArrayDiskInput!` | `UnraidArray!` | `UPDATE_ANY` on `ARRAY` | Add disk to array |
| `removeDiskFromArray` | `input: ArrayDiskInput!` | `UnraidArray!` | `UPDATE_ANY` on `ARRAY` | Remove disk (array must be stopped) |
| `mountArrayDisk` | `id: PrefixedID!` | `ArrayDisk!` | `UPDATE_ANY` on `ARRAY` | Mount a disk |
| `unmountArrayDisk` | `id: PrefixedID!` | `ArrayDisk!` | `UPDATE_ANY` on `ARRAY` | Unmount a disk |
| `clearArrayDiskStatistics` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `ARRAY` | Clear disk I/O stats |

---

### Docker Mutations

Nested under `mutation { docker { ... } }` → `DockerMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `start` | `id: PrefixedID!` | `DockerContainer!` | `UPDATE_ANY` on `DOCKER` | Start a container |
| `stop` | `id: PrefixedID!` | `DockerContainer!` | `UPDATE_ANY` on `DOCKER` | Stop a container |

**That's it.** No pause, unpause, remove, update, or organizer mutations exist.

---

### VM Mutations

Nested under `mutation { vm { ... } }` → `VmMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `start` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Start VM |
| `stop` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Graceful stop |
| `pause` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Pause VM |
| `resume` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Resume paused VM |
| `forceStop` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Force stop (hard power off) |
| `reboot` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Reboot VM |
| `reset` | `id: PrefixedID!` | `Boolean!` | `UPDATE_ANY` on `VMS` | Reset VM (hard reboot) |

---

### Parity Check Mutations

Nested under `mutation { parityCheck { ... } }` → `ParityCheckMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `start` | `correct: Boolean!` | `JSON!` | `UPDATE_ANY` on `ARRAY` | Start parity check (correct=true writes fixes) |
| `pause` | — | `JSON!` | `UPDATE_ANY` on `ARRAY` | Pause running check |
| `resume` | — | `JSON!` | `UPDATE_ANY` on `ARRAY` | Resume paused check |
| `cancel` | — | `JSON!` | `UPDATE_ANY` on `ARRAY` | Cancel running check |

> **Note:** Response types are `JSON!` — this API is marked WIP and types will change.

---

### API Key Mutations

Nested under `mutation { apiKey { ... } }` → `ApiKeyMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `create` | `input: CreateApiKeyInput!` | `ApiKey!` | `CREATE_ANY` on `API_KEY` | Create API key |
| `update` | `input: UpdateApiKeyInput!` | `ApiKey!` | `UPDATE_ANY` on `API_KEY` | Update API key |
| `delete` | `input: DeleteApiKeyInput!` | `Boolean!` | `DELETE_ANY` on `API_KEY` | Delete one or more keys |
| `addRole` | `input: AddRoleForApiKeyInput!` | `Boolean!` | `UPDATE_ANY` on `API_KEY` | Add role to key |
| `removeRole` | `input: RemoveRoleFromApiKeyInput!` | `Boolean!` | `UPDATE_ANY` on `API_KEY` | Remove role from key |

---

### Customization Mutations

Nested under `mutation { customization { ... } }` → `CustomizationMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `setTheme` | `theme: ThemeName!` | `Theme!` | `UPDATE_ANY` on `CUSTOMIZATIONS` | Update UI theme (azure/black/gray/white) |

---

### RClone Mutations

Nested under `mutation { rclone { ... } }` → `RCloneMutations!`

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `createRCloneRemote` | `input: CreateRCloneRemoteInput!` | `RCloneRemote!` | `CREATE_ANY` on `FLASH` | Create remote |
| `deleteRCloneRemote` | `input: DeleteRCloneRemoteInput!` | `Boolean!` | `DELETE_ANY` on `FLASH` | Delete remote |

---

### Flash Backup

Root-level mutation.

| Mutation | Args | Returns | Description |
|----------|------|---------|-------------|
| `initiateFlashBackup` | `input: InitiateFlashBackupInput!` | `FlashBackupStatus!` | Start flash backup to remote |

**InitiateFlashBackupInput:** `remoteName: String!`, `sourcePath: String!`, `destinationPath: String!`, `options: JSON`

Returns: `status: String!`, `jobId: String`

---

### Settings Mutations

Root-level mutations.

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `updateSettings` | `input: JSON!` | `UpdateSettingsResponse!` | `UPDATE_ANY` on `CONFIG` | Update server settings |
| `configureUps` | `config: UPSConfigInput!` | `Boolean!` | — | Configure UPS daemon |

**UpdateSettingsResponse:** `restartRequired: Boolean!`, `values: JSON!`, `warnings: [String!]`

---

### Plugin Mutations

Root-level mutations.

| Mutation | Args | Returns | Permission | Description |
|----------|------|---------|------------|-------------|
| `addPlugin` | `input: PluginManagementInput!` | `Boolean!` | `UPDATE_ANY` on `CONFIG` | Install plugin(s). Returns false if auto-restart triggered. |
| `removePlugin` | `input: PluginManagementInput!` | `Boolean!` | `DELETE_ANY` on `CONFIG` | Remove plugin(s). Returns false if auto-restart triggered. |

---

## Subscriptions

WebSocket-based real-time data (graphql-ws protocol).

| Subscription | Returns | Permission | Description |
|-------------|---------|------------|-------------|
| `notificationAdded` | `Notification!` | `READ_ANY` on `NOTIFICATIONS` | New notification created |
| `notificationsOverview` | `NotificationOverview!` | `READ_ANY` on `NOTIFICATIONS` | Overview counts change |
| `ownerSubscription` | `Owner!` | `READ_ANY` on `OWNER` | Owner info change |
| `serversSubscription` | `Server!` | `READ_ANY` on `SERVERS` | Server state change |
| `parityHistorySubscription` | `ParityCheck!` | `READ_ANY` on `ARRAY` | Parity check updates |
| `arraySubscription` | `UnraidArray!` | `READ_ANY` on `ARRAY` | Array state changes |
| `logFile(path: String!)` | `LogFileContent!` | `READ_ANY` on `LOGS` | Live log file tail |
| `systemMetricsCpu` | `CpuUtilization!` | `READ_ANY` on `INFO` | CPU utilization stream |
| `systemMetricsCpuTelemetry` | `CpuPackages!` | `READ_ANY` on `INFO` | CPU power/temp stream |
| `systemMetricsMemory` | `MemoryUtilization!` | `READ_ANY` on `INFO` | Memory utilization stream |
| `upsUpdates` | `UPSDevice!` | — | UPS state changes |

---

## Enums

### ArrayDiskFsColor
`GREEN_ON` · `GREEN_BLINK` · `BLUE_ON` · `BLUE_BLINK` · `YELLOW_ON` · `YELLOW_BLINK` · `RED_ON` · `RED_OFF` · `GREY_OFF`

### ArrayDiskStatus
`DISK_NP` · `DISK_OK` · `DISK_NP_MISSING` · `DISK_INVALID` · `DISK_WRONG` · `DISK_DSBL` · `DISK_NP_DSBL` · `DISK_DSBL_NEW` · `DISK_NEW`

### ArrayDiskType
`DATA` · `PARITY` · `FLASH` · `CACHE`

### ArrayState
`STARTED` · `STOPPED` · `NEW_ARRAY` · `RECON_DISK` · `DISABLE_DISK` · `SWAP_DSBL` · `INVALID_EXPANSION` · `PARITY_NOT_BIGGEST` · `TOO_MANY_MISSING_DISKS` · `NEW_DISK_TOO_SMALL` · `NO_DATA_DISKS`

### ArrayStateInputState
`START` · `STOP`

### AuthAction
`CREATE_ANY` · `CREATE_OWN` · `READ_ANY` · `READ_OWN` · `UPDATE_ANY` · `UPDATE_OWN` · `DELETE_ANY` · `DELETE_OWN`

### AuthorizationOperator
`EQUALS` · `CONTAINS` · `ENDS_WITH` · `STARTS_WITH`

### AuthorizationRuleMode
`OR` · `AND`

### ConfigErrorState
`UNKNOWN_ERROR` · `INELIGIBLE` · `INVALID` · `NO_KEY_SERVER` · `WITHDRAWN`

### ContainerPortType
`TCP` · `UDP`

### ContainerState
`RUNNING` · `EXITED`

### DiskFsType
`XFS` · `BTRFS` · `VFAT` · `ZFS` · `EXT4` · `NTFS`

### DiskInterfaceType
`SAS` · `SATA` · `USB` · `PCIE` · `UNKNOWN`

### DiskSmartStatus
`OK` · `UNKNOWN`

### NotificationImportance
`ALERT` · `INFO` · `WARNING`

### NotificationType
`UNREAD` · `ARCHIVE`

### ParityCheckStatus
`NEVER_RUN` · `RUNNING` · `PAUSED` · `COMPLETED` · `CANCELLED` · `FAILED`

### RegistrationState
`TRIAL` · `BASIC` · `PLUS` · `PRO` · `STARTER` · `UNLEASHED` · `LIFETIME` · `EEXPIRED` · `EGUID` · `EGUID1` · `ETRIAL` · `ENOKEYFILE` · `ENOKEYFILE1` · `ENOKEYFILE2` · `ENOFLASH` · `ENOFLASH1` · `ENOFLASH2` · `ENOFLASH3` · `ENOFLASH4` · `ENOFLASH5` · `ENOFLASH6` · `ENOFLASH7` · `EBLACKLISTED` · `EBLACKLISTED1` · `EBLACKLISTED2` · `ENOCONN`

### Resource
`ACTIVATION_CODE` · `API_KEY` · `ARRAY` · `CLOUD` · `CONFIG` · `CONNECT` · `CONNECT__REMOTE_ACCESS` · `CUSTOMIZATIONS` · `DASHBOARD` · `DISK` · `DISPLAY` · `DOCKER` · `FLASH` · `INFO` · `LOGS` · `ME` · `NETWORK` · `NOTIFICATIONS` · `ONLINE` · `OS` · `OWNER` · `PERMISSION` · `REGISTRATION` · `SERVERS` · `SERVICES` · `SHARE` · `VARS` · `VMS` · `WELCOME`

### Role
- `ADMIN` — Full administrative access
- `CONNECT` — Internal role for Unraid Connect
- `GUEST` — Basic read access (user profile only)
- `VIEWER` — Read-only access to all resources

### ServerStatus
`ONLINE` · `OFFLINE` · `NEVER_CONNECTED`

### Temperature
`CELSIUS` · `FAHRENHEIT`

### ThemeName
`azure` · `black` · `gray` · `white`

### UPSCableType
`USB` · `SIMPLE` · `SMART` · `ETHER` · `CUSTOM`

### UPSKillPower
`YES` · `NO`

### UPSServiceState
`ENABLE` · `DISABLE`

### UPSType
`USB` · `APCSMART` · `NET` · `SNMP` · `DUMB` · `PCNET` · `MODBUS`

### UpdateStatus
`UP_TO_DATE` · `UPDATE_AVAILABLE` · `REBUILD_READY` · `UNKNOWN`

### VmState
`NOSTATE` · `RUNNING` · `IDLE` · `PAUSED` · `SHUTDOWN` · `SHUTOFF` · `CRASHED` · `PMSUSPENDED`

### registrationType
`BASIC` · `PLUS` · `PRO` · `STARTER` · `UNLEASHED` · `LIFETIME` · `INVALID` · `TRIAL`

---

## Input Types

### NotificationData
```graphql
input NotificationData {
  title: String!
  subject: String!
  description: String!
  importance: NotificationImportance!
  link: String
}
```

### NotificationFilter
```graphql
input NotificationFilter {
  importance: NotificationImportance  # optional filter
  type: NotificationType!             # UNREAD or ARCHIVE
  offset: Int!
  limit: Int!
}
```

### ArrayStateInput
```graphql
input ArrayStateInput {
  desiredState: ArrayStateInputState!  # START or STOP
}
```

### ArrayDiskInput
```graphql
input ArrayDiskInput {
  id: PrefixedID!
  slot: Int  # optional slot number
}
```

### CreateApiKeyInput
```graphql
input CreateApiKeyInput {
  name: String!
  description: String
  roles: [Role!]
  permissions: [AddPermissionInput!]
  overwrite: Boolean  # replace existing key with same name
}
```

### UpdateApiKeyInput
```graphql
input UpdateApiKeyInput {
  id: PrefixedID!
  name: String
  description: String
  roles: [Role!]
  permissions: [AddPermissionInput!]
}
```

### DeleteApiKeyInput
```graphql
input DeleteApiKeyInput {
  ids: [PrefixedID!]!
}
```

### AddPermissionInput
```graphql
input AddPermissionInput {
  resource: Resource!
  actions: [AuthAction!]!
}
```

### AddRoleForApiKeyInput / RemoveRoleFromApiKeyInput
```graphql
input AddRoleForApiKeyInput {
  apiKeyId: PrefixedID!
  role: Role!
}
input RemoveRoleFromApiKeyInput {
  apiKeyId: PrefixedID!
  role: Role!
}
```

### CreateRCloneRemoteInput
```graphql
input CreateRCloneRemoteInput {
  name: String!
  type: String!        # e.g. "drive", "s3", "sftp"
  parameters: JSON!    # provider-specific config
}
```

### DeleteRCloneRemoteInput
```graphql
input DeleteRCloneRemoteInput {
  name: String!
}
```

### RCloneConfigFormInput
```graphql
input RCloneConfigFormInput {
  providerType: String
  showAdvanced: Boolean = false
  parameters: JSON
}
```

### InitiateFlashBackupInput
```graphql
input InitiateFlashBackupInput {
  remoteName: String!       # configured remote name
  sourcePath: String!       # e.g. "/boot"
  destinationPath: String!  # remote destination path
  options: JSON             # e.g. {"--dry-run": true}
}
```

### UPSConfigInput
```graphql
input UPSConfigInput {
  service: UPSServiceState        # ENABLE or DISABLE
  upsCable: UPSCableType          # USB, SIMPLE, SMART, ETHER, CUSTOM
  customUpsCable: String           # only when upsCable=CUSTOM
  upsType: UPSType                # USB, APCSMART, NET, SNMP, DUMB, PCNET, MODBUS
  device: String                   # /dev/ttyUSB0 or IP:port
  overrideUpsCapacity: Int         # watts
  batteryLevel: Int                # 0-100 percent shutdown threshold
  minutes: Int                     # runtime minutes shutdown threshold
  timeout: Int                     # seconds, 0=disable
  killUps: UPSKillPower           # YES or NO
}
```

### PluginManagementInput
```graphql
input PluginManagementInput {
  names: [String!]!
  bundled: Boolean! = false  # treat as bundled plugins
  restart: Boolean! = true   # auto-restart API after operation
}
```

---

## Object Types (Full Field Reference)

### Key Types Quick Reference

| Type | Key Fields |
|------|-----------|
| `UnraidArray` | `state`, `capacity`, `boot`, `parities[]`, `parityCheckStatus`, `disks[]`, `caches[]` |
| `ArrayDisk` | `id`, `idx`, `name`, `device`, `size`, `status`, `temp`, `numReads/Writes/Errors`, `fsSize/Free/Used`, `type`, `color`, `isSpinning` |
| `Disk` | `id`, `device`, `type`, `name`, `vendor`, `size`, `serialNum`, `interfaceType`, `smartStatus`, `temperature`, `partitions[]`, `isSpinning` |
| `DockerContainer` | `id`, `names[]`, `image`, `state`, `status`, `ports[]`, `autoStart`, `labels`, `mounts[]` |
| `DockerNetwork` | `id`, `name`, `driver`, `scope`, `internal`, `attachable`, `containers`, `ipam` |
| `VmDomain` | `id`, `name`, `state`, `uuid` (deprecated) |
| `Notification` | `id`, `title`, `subject`, `description`, `importance`, `type`, `timestamp` |
| `Info` | `time`, `baseboard`, `cpu`, `devices`, `display`, `memory`, `os`, `system`, `versions` |
| `Metrics` | `cpu { percentTotal, cpus[] }`, `memory { total, used, free, percentTotal }` |
| `Share` | `id`, `name`, `free`, `used`, `size`, `include[]`, `exclude[]`, `cache`, `comment` |
| `ApiKey` | `id`, `key`, `name`, `description`, `roles[]`, `permissions[]`, `createdAt` |
| `UserAccount` | `id`, `name`, `description`, `roles[]`, `permissions[]` |
| `Server` | `id`, `name`, `status`, `guid`, `wanip`, `lanip`, `localurl`, `remoteurl`, `owner` |
| `Service` | `id`, `name`, `online`, `uptime`, `version` |
| `Owner` | `username`, `url`, `avatar` |
| `Registration` | `type`, `state`, `keyFile`, `expiration`, `updateExpiration` |
| `Vars` | 143 fields — hostname, timezone, array state, share config, registration, tuning params |
| `UPSDevice` | `id`, `name`, `model`, `status`, `battery { chargeLevel, estimatedRuntime, health }`, `power { inputVoltage, outputVoltage, loadPercentage }` |
| `UPSConfiguration` | `service`, `upsCable`, `upsType`, `device`, `batteryLevel`, `minutes`, `timeout`, `killUps`, + 4 more |
| `RCloneRemote` | `name`, `type`, `parameters`, `config` |
| `Settings` | `unified { dataSchema, uiSchema, values }`, `sso { oidcProviders[] }`, `api { version, extraOrigins }` |
| `Flash` | `guid`, `vendor`, `product` |
| `ParityCheck` | `date`, `duration`, `speed`, `status`, `errors`, `progress`, `correcting`, `paused`, `running` |
| `Plugin` | `name`, `version`, `hasApiModule`, `hasCliModule` |

---

## Schema Statistics

| Category | Count |
|----------|-------|
| Query fields | 46 |
| Mutation fields | 22 |
| Subscription fields | 11 |
| Object types | 94 |
| Input types | 16 |
| Enum types | 30 |
| Scalar types | 10 |
| Union types | 1 |
| Interface types | 2 |
| **Total types** | **156** |
