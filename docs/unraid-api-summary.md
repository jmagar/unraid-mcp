# Unraid API v4.29.2 — Introspection Summary

> Auto-generated from live API introspection on 2026-03-15
> Source: tootie (10.1.0.2:31337)

## Table of Contents

- [Query Fields](#query-fields)
- [Mutation Fields](#mutation-fields)
- [Subscription Fields](#subscription-fields)
- [Enum Types](#enum-types)
- [Input Types](#input-types)
- [Object Types](#object-types)

## Query Fields

**46 fields**

| Field | Return Type | Arguments |
|-------|-------------|-----------|
| `apiKey` | `ApiKey` | `id: PrefixedID!` |
| `apiKeyPossiblePermissions` | `[Permission!]!` | — |
| `apiKeyPossibleRoles` | `[Role!]!` | — |
| `apiKeys` | `[ApiKey!]!` | — |
| `array` | `UnraidArray!` | — |
| `config` | `Config!` | — |
| `customization` | `Customization` | — |
| `disk` | `Disk!` | `id: PrefixedID!` |
| `disks` | `[Disk!]!` | — |
| `docker` | `Docker!` | — |
| `flash` | `Flash!` | — |
| `getApiKeyCreationFormSchema` | `ApiKeyFormSettings!` | — |
| `getAvailableAuthActions` | `[AuthAction!]!` | — |
| `getPermissionsForRoles` | `[Permission!]!` | `roles: [Role!]!` |
| `info` | `Info!` | — |
| `isInitialSetup` | `Boolean!` | — |
| `isSSOEnabled` | `Boolean!` | — |
| `logFile` | `LogFileContent!` | `path: String!`, `lines: Int`, `startLine: Int` |
| `logFiles` | `[LogFile!]!` | — |
| `me` | `UserAccount!` | — |
| `metrics` | `Metrics!` | — |
| `notifications` | `Notifications!` | — |
| `oidcConfiguration` | `OidcConfiguration!` | — |
| `oidcProvider` | `OidcProvider` | `id: PrefixedID!` |
| `oidcProviders` | `[OidcProvider!]!` | — |
| `online` | `Boolean!` | — |
| `owner` | `Owner!` | — |
| `parityHistory` | `[ParityCheck!]!` | — |
| `plugins` | `[Plugin!]!` | — |
| `previewEffectivePermissions` | `[Permission!]!` | `roles: [Role!]`, `permissions: [AddPermissionInput!]` |
| `publicOidcProviders` | `[PublicOidcProvider!]!` | — |
| `publicPartnerInfo` | `PublicPartnerInfo` | — |
| `publicTheme` | `Theme!` | — |
| `rclone` | `RCloneBackupSettings!` | — |
| `registration` | `Registration` | — |
| `server` | `Server` | — |
| `servers` | `[Server!]!` | — |
| `services` | `[Service!]!` | — |
| `settings` | `Settings!` | — |
| `shares` | `[Share!]!` | — |
| `upsConfiguration` | `UPSConfiguration!` | — |
| `upsDeviceById` | `UPSDevice` | `id: String!` |
| `upsDevices` | `[UPSDevice!]!` | — |
| `validateOidcSession` | `OidcSessionValidation!` | `token: String!` |
| `vars` | `Vars!` | — |
| `vms` | `Vms!` | — |

## Mutation Fields

**22 fields**

| Field | Return Type | Arguments |
|-------|-------------|-----------|
| `addPlugin` | `Boolean!` | `input: PluginManagementInput!` |
| `apiKey` | `ApiKeyMutations!` | — |
| `archiveAll` | `NotificationOverview!` | `importance: NotificationImportance` |
| `archiveNotification` | `Notification!` | `id: PrefixedID!` |
| `archiveNotifications` | `NotificationOverview!` | `ids: [PrefixedID!]!` |
| `array` | `ArrayMutations!` | — |
| `configureUps` | `Boolean!` | `config: UPSConfigInput!` |
| `createNotification` | `Notification!` | `input: NotificationData!` |
| `customization` | `CustomizationMutations!` | — |
| `deleteArchivedNotifications` | `NotificationOverview!` | — |
| `deleteNotification` | `NotificationOverview!` | `id: PrefixedID!`, `type: NotificationType!` |
| `docker` | `DockerMutations!` | — |
| `initiateFlashBackup` | `FlashBackupStatus!` | `input: InitiateFlashBackupInput!` |
| `parityCheck` | `ParityCheckMutations!` | — |
| `rclone` | `RCloneMutations!` | — |
| `recalculateOverview` | `NotificationOverview!` | — |
| `removePlugin` | `Boolean!` | `input: PluginManagementInput!` |
| `unarchiveAll` | `NotificationOverview!` | `importance: NotificationImportance` |
| `unarchiveNotifications` | `NotificationOverview!` | `ids: [PrefixedID!]!` |
| `unreadNotification` | `Notification!` | `id: PrefixedID!` |
| `updateSettings` | `UpdateSettingsResponse!` | `input: JSON!` |
| `vm` | `VmMutations!` | — |

## Subscription Fields

**11 fields**

| Field | Return Type | Arguments |
|-------|-------------|-----------|
| `arraySubscription` | `UnraidArray!` | — |
| `logFile` | `LogFileContent!` | `path: String!` |
| `notificationAdded` | `Notification!` | — |
| `notificationsOverview` | `NotificationOverview!` | — |
| `ownerSubscription` | `Owner!` | — |
| `parityHistorySubscription` | `ParityCheck!` | — |
| `serversSubscription` | `Server!` | — |
| `systemMetricsCpu` | `CpuUtilization!` | — |
| `systemMetricsCpuTelemetry` | `CpuPackages!` | — |
| `systemMetricsMemory` | `MemoryUtilization!` | — |
| `upsUpdates` | `UPSDevice!` | — |

## Enum Types

**30 enums**

### `ArrayDiskFsColor`

```
GREEN_ON
GREEN_BLINK
BLUE_ON
BLUE_BLINK
YELLOW_ON
YELLOW_BLINK
RED_ON
RED_OFF
GREY_OFF
```

### `ArrayDiskStatus`

```
DISK_NP
DISK_OK
DISK_NP_MISSING
DISK_INVALID
DISK_WRONG
DISK_DSBL
DISK_NP_DSBL
DISK_DSBL_NEW
DISK_NEW
```

### `ArrayDiskType`

```
DATA
PARITY
FLASH
CACHE
```

### `ArrayState`

```
STARTED
STOPPED
NEW_ARRAY
RECON_DISK
DISABLE_DISK
SWAP_DSBL
INVALID_EXPANSION
PARITY_NOT_BIGGEST
TOO_MANY_MISSING_DISKS
NEW_DISK_TOO_SMALL
NO_DATA_DISKS
```

### `ArrayStateInputState`

```
START
STOP
```

### `AuthAction`
> Authentication actions with possession (e.g., create:any, read:own)

```
CREATE_ANY
CREATE_OWN
READ_ANY
READ_OWN
UPDATE_ANY
UPDATE_OWN
DELETE_ANY
DELETE_OWN
```

### `AuthorizationOperator`
> Operators for authorization rule matching

```
EQUALS
CONTAINS
ENDS_WITH
STARTS_WITH
```

### `AuthorizationRuleMode`
> Mode for evaluating authorization rules - OR (any rule passes) or AND (all rules must pass)

```
OR
AND
```

### `ConfigErrorState`
> Possible error states for configuration

```
UNKNOWN_ERROR
INELIGIBLE
INVALID
NO_KEY_SERVER
WITHDRAWN
```

### `ContainerPortType`

```
TCP
UDP
```

### `ContainerState`

```
RUNNING
EXITED
```

### `DiskFsType`
> The type of filesystem on the disk partition

```
XFS
BTRFS
VFAT
ZFS
EXT4
NTFS
```

### `DiskInterfaceType`
> The type of interface the disk uses to connect to the system

```
SAS
SATA
USB
PCIE
UNKNOWN
```

### `DiskSmartStatus`
> The SMART (Self-Monitoring, Analysis and Reporting Technology) status of the disk

```
OK
UNKNOWN
```

### `NotificationImportance`

```
ALERT
INFO
WARNING
```

### `NotificationType`

```
UNREAD
ARCHIVE
```

### `ParityCheckStatus`

```
NEVER_RUN
RUNNING
PAUSED
COMPLETED
CANCELLED
FAILED
```

### `RegistrationState`

```
TRIAL
BASIC
PLUS
PRO
STARTER
UNLEASHED
LIFETIME
EEXPIRED
EGUID
EGUID1
ETRIAL
ENOKEYFILE
ENOKEYFILE1
ENOKEYFILE2
ENOFLASH
ENOFLASH1
ENOFLASH2
ENOFLASH3
ENOFLASH4
ENOFLASH5
ENOFLASH6
ENOFLASH7
EBLACKLISTED
EBLACKLISTED1
EBLACKLISTED2
ENOCONN
```

### `Resource`
> Available resources for permissions

```
ACTIVATION_CODE
API_KEY
ARRAY
CLOUD
CONFIG
CONNECT
CONNECT__REMOTE_ACCESS
CUSTOMIZATIONS
DASHBOARD
DISK
DISPLAY
DOCKER
FLASH
INFO
LOGS
ME
NETWORK
NOTIFICATIONS
ONLINE
OS
OWNER
PERMISSION
REGISTRATION
SERVERS
SERVICES
SHARE
VARS
VMS
WELCOME
```

### `Role`
> Available roles for API keys and users

```
ADMIN
CONNECT
GUEST
VIEWER
```

### `ServerStatus`

```
ONLINE
OFFLINE
NEVER_CONNECTED
```

### `Temperature`
> Temperature unit

```
CELSIUS
FAHRENHEIT
```

### `ThemeName`
> The theme name

```
azure
black
gray
white
```

### `UPSCableType`
> UPS cable connection types

```
USB
SIMPLE
SMART
ETHER
CUSTOM
```

### `UPSKillPower`
> Kill UPS power after shutdown option

```
YES
NO
```

### `UPSServiceState`
> Service state for UPS daemon

```
ENABLE
DISABLE
```

### `UPSType`
> UPS communication protocols

```
USB
APCSMART
NET
SNMP
DUMB
PCNET
MODBUS
```

### `UpdateStatus`
> Update status of a container.

```
UP_TO_DATE
UPDATE_AVAILABLE
REBUILD_READY
UNKNOWN
```

### `VmState`
> The state of a virtual machine

```
NOSTATE
RUNNING
IDLE
PAUSED
SHUTDOWN
SHUTOFF
CRASHED
PMSUSPENDED
```

### `registrationType`

```
BASIC
PLUS
PRO
STARTER
UNLEASHED
LIFETIME
INVALID
TRIAL
```

## Input Types

**16 input types**

### `AddPermissionInput`

| Field | Type | Default |
|-------|------|---------|
| `resource` | `Resource!` | — |
| `actions` | `[AuthAction!]!` | — |

### `AddRoleForApiKeyInput`

| Field | Type | Default |
|-------|------|---------|
| `apiKeyId` | `PrefixedID!` | — |
| `role` | `Role!` | — |

### `ArrayDiskInput`

| Field | Type | Default |
|-------|------|---------|
| `id` | `PrefixedID!` | — |
| `slot` | `Int` | — |

### `ArrayStateInput`

| Field | Type | Default |
|-------|------|---------|
| `desiredState` | `ArrayStateInputState!` | — |

### `CreateApiKeyInput`

| Field | Type | Default |
|-------|------|---------|
| `name` | `String!` | — |
| `description` | `String` | — |
| `roles` | `[Role!]` | — |
| `permissions` | `[AddPermissionInput!]` | — |
| `overwrite` | `Boolean` | — |

### `CreateRCloneRemoteInput`

| Field | Type | Default |
|-------|------|---------|
| `name` | `String!` | — |
| `type` | `String!` | — |
| `parameters` | `JSON!` | — |

### `DeleteApiKeyInput`

| Field | Type | Default |
|-------|------|---------|
| `ids` | `[PrefixedID!]!` | — |

### `DeleteRCloneRemoteInput`

| Field | Type | Default |
|-------|------|---------|
| `name` | `String!` | — |

### `InitiateFlashBackupInput`

| Field | Type | Default |
|-------|------|---------|
| `remoteName` | `String!` | — |
| `sourcePath` | `String!` | — |
| `destinationPath` | `String!` | — |
| `options` | `JSON` | — |

### `NotificationData`

| Field | Type | Default |
|-------|------|---------|
| `title` | `String!` | — |
| `subject` | `String!` | — |
| `description` | `String!` | — |
| `importance` | `NotificationImportance!` | — |
| `link` | `String` | — |

### `NotificationFilter`

| Field | Type | Default |
|-------|------|---------|
| `importance` | `NotificationImportance` | — |
| `type` | `NotificationType!` | — |
| `offset` | `Int!` | — |
| `limit` | `Int!` | — |

### `PluginManagementInput`

| Field | Type | Default |
|-------|------|---------|
| `names` | `[String!]!` | — |
| `bundled` | `Boolean!` | false |
| `restart` | `Boolean!` | true |

### `RCloneConfigFormInput`

| Field | Type | Default |
|-------|------|---------|
| `providerType` | `String` | — |
| `showAdvanced` | `Boolean` | false |
| `parameters` | `JSON` | — |

### `RemoveRoleFromApiKeyInput`

| Field | Type | Default |
|-------|------|---------|
| `apiKeyId` | `PrefixedID!` | — |
| `role` | `Role!` | — |

### `UPSConfigInput`

| Field | Type | Default |
|-------|------|---------|
| `service` | `UPSServiceState` | — |
| `upsCable` | `UPSCableType` | — |
| `customUpsCable` | `String` | — |
| `upsType` | `UPSType` | — |
| `device` | `String` | — |
| `overrideUpsCapacity` | `Int` | — |
| `batteryLevel` | `Int` | — |
| `minutes` | `Int` | — |
| `timeout` | `Int` | — |
| `killUps` | `UPSKillPower` | — |

### `UpdateApiKeyInput`

| Field | Type | Default |
|-------|------|---------|
| `id` | `PrefixedID!` | — |
| `name` | `String` | — |
| `description` | `String` | — |
| `roles` | `[Role!]` | — |
| `permissions` | `[AddPermissionInput!]` | — |

## Object Types

**94 object types**

| Type | Fields | Description |
|------|--------|-------------|
| `ActivationCode` | 11 | — |
| `ApiConfig` | 5 | — |
| `ApiKey` | 7 | — |
| `ApiKeyFormSettings` | 4 | — |
| `ApiKeyMutations` | 5 | API Key related mutations |
| `ArrayCapacity` | 2 | — |
| `ArrayDisk` | 24 | — |
| `ArrayMutations` | 6 | — |
| `Capacity` | 3 | — |
| `Config` | 3 | — |
| `ContainerHostConfig` | 1 | — |
| `ContainerPort` | 4 | — |
| `CoreVersions` | 3 | — |
| `CpuLoad` | 8 | CPU load for a single core |
| `CpuPackages` | 4 | — |
| `CpuUtilization` | 3 | — |
| `Customization` | 3 | — |
| `CustomizationMutations` | 1 | Customization related mutations |
| `Disk` | 20 | — |
| `DiskPartition` | 3 | — |
| `Docker` | 3 | — |
| `DockerContainer` | 15 | — |
| `DockerMutations` | 2 | — |
| `DockerNetwork` | 15 | — |
| `ExplicitStatusItem` | 2 | — |
| `Flash` | 4 | — |
| `FlashBackupStatus` | 2 | — |
| `Info` | 11 | — |
| `InfoBaseboard` | 8 | — |
| `InfoCpu` | 20 | — |
| `InfoDevices` | 5 | — |
| `InfoDisplay` | 16 | — |
| `InfoDisplayCase` | 5 | — |
| `InfoGpu` | 7 | — |
| `InfoMemory` | 2 | — |
| `InfoNetwork` | 8 | — |
| `InfoOs` | 15 | — |
| `InfoPci` | 9 | — |
| `InfoSystem` | 8 | — |
| `InfoUsb` | 4 | — |
| `InfoVersions` | 3 | — |
| `KeyFile` | 2 | — |
| `LogFile` | 4 | — |
| `LogFileContent` | 4 | — |
| `MemoryLayout` | 12 | — |
| `MemoryUtilization` | 12 | — |
| `Metrics` | 3 | System metrics including CPU and memory utilization |
| `Notification` | 9 | — |
| `NotificationCounts` | 4 | — |
| `NotificationOverview` | 2 | — |
| `Notifications` | 3 | — |
| `OidcAuthorizationRule` | 3 | — |
| `OidcConfiguration` | 2 | — |
| `OidcProvider` | 15 | — |
| `OidcSessionValidation` | 2 | — |
| `OrganizerContainerResource` | 4 | — |
| `OrganizerResource` | 4 | — |
| `Owner` | 3 | — |
| `PackageVersions` | 8 | — |
| `ParityCheck` | 9 | — |
| `ParityCheckMutations` | 4 | Parity check related mutations, WIP, response types and functionaliy will change |
| `Permission` | 2 | — |
| `Plugin` | 4 | — |
| `ProfileModel` | 4 | — |
| `PublicOidcProvider` | 6 | — |
| `PublicPartnerInfo` | 4 | — |
| `RCloneBackupConfigForm` | 3 | — |
| `RCloneBackupSettings` | 3 | — |
| `RCloneDrive` | 2 | — |
| `RCloneMutations` | 2 | RClone related mutations |
| `RCloneRemote` | 4 | — |
| `Registration` | 6 | — |
| `ResolvedOrganizerFolder` | 4 | — |
| `ResolvedOrganizerV1` | 2 | — |
| `ResolvedOrganizerView` | 4 | — |
| `Server` | 10 | — |
| `Service` | 5 | — |
| `Settings` | 4 | — |
| `Share` | 16 | — |
| `SsoSettings` | 2 | — |
| `Theme` | 7 | — |
| `UPSBattery` | 3 | — |
| `UPSConfiguration` | 14 | — |
| `UPSDevice` | 6 | — |
| `UPSPower` | 3 | — |
| `UnifiedSettings` | 4 | — |
| `UnraidArray` | 8 | — |
| `UpdateSettingsResponse` | 3 | — |
| `Uptime` | 1 | — |
| `UserAccount` | 5 | — |
| `Vars` | 143 | — |
| `VmDomain` | 4 | — |
| `VmMutations` | 7 | — |
| `Vms` | 3 | — |

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
