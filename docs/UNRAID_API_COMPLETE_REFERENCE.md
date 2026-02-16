# Unraid GraphQL API Complete Schema Reference

Generated via live GraphQL introspection for the configured endpoint and API key.

This is permission-scoped: it contains everything visible to the API key used.

## Table of Contents
- [Schema Summary](#schema-summary)
- [Root Operations](#root-operations)
- [Directives](#directives)
- [All Types (Alphabetical)](#all-types-alphabetical)

## Schema Summary
- Query root: `Query`
- Mutation root: `Mutation`
- Subscription root: `Subscription`
- Total types: **156**
- Total directives: **6**
- Type kinds:
- `ENUM`: 30
- `INPUT_OBJECT`: 16
- `INTERFACE`: 2
- `OBJECT`: 97
- `SCALAR`: 10
- `UNION`: 1

## Root Operations
### Queries
Total fields: **46**

- `apiKey(id: PrefixedID!): ApiKey`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**
- `apiKeyPossiblePermissions(): [Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible permissions for API keys
- `apiKeyPossibleRoles(): [Role!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible roles for API keys
- `apiKeys(): [ApiKey!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**
- `array(): UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `config(): Config!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
- `customization(): Customization`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS**
- `disk(id: PrefixedID!): Disk!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `disks(): [Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `docker(): Docker!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `flash(): Flash!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `getApiKeyCreationFormSchema(): ApiKeyFormSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY** #### Description: Get JSON Schema for API key creation form
- `getAvailableAuthActions(): [AuthAction!]!`
  - Get all available authentication actions with possession
- `getPermissionsForRoles(roles: [Role!]!): [Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Get the actual permissions that would be granted by a set of roles
- `info(): Info!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `isInitialSetup(): Boolean!`
- `isSSOEnabled(): Boolean!`
- `logFile(lines: Int, path: String!, startLine: Int): LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `logFiles(): [LogFile!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `me(): UserAccount!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ME**
- `metrics(): Metrics!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `notifications(): Notifications!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS** #### Description: Get all notifications
- `oidcConfiguration(): OidcConfiguration!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get the full OIDC configuration (admin only)
- `oidcProvider(id: PrefixedID!): OidcProvider`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get a specific OIDC provider by ID
- `oidcProviders(): [OidcProvider!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get all configured OIDC providers (admin only)
- `online(): Boolean!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ONLINE**
- `owner(): Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistory(): [ParityCheck!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `plugins(): [Plugin!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all installed plugins with their metadata
- `previewEffectivePermissions(permissions: [AddPermissionInput!], roles: [Role!]): [Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Preview the effective permissions for a combination of roles and explicit permissions
- `publicOidcProviders(): [PublicOidcProvider!]!`
  - Get public OIDC provider information for login buttons
- `publicPartnerInfo(): PublicPartnerInfo`
- `publicTheme(): Theme!`
- `rclone(): RCloneBackupSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `registration(): Registration`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **REGISTRATION**
- `server(): Server`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `servers(): [Server!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `services(): [Service!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVICES**
- `settings(): Settings!`
- `shares(): [Share!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SHARE**
- `upsConfiguration(): UPSConfiguration!`
- `upsDeviceById(id: String!): UPSDevice`
- `upsDevices(): [UPSDevice!]!`
- `validateOidcSession(token: String!): OidcSessionValidation!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Validate an OIDC session token (internal use for CLI validation)
- `vars(): Vars!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VARS**
- `vms(): Vms!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VMS** #### Description: Get information about all VMs on the system

### Mutations
Total fields: **22**

- `addPlugin(input: PluginManagementInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Add one or more plugins to the API. Returns false if restart was triggered automatically, true if manual restart is required.
- `apiKey(): ApiKeyMutations!`
- `archiveAll(importance: NotificationImportance): NotificationOverview!`
- `archiveNotification(id: PrefixedID!): Notification!`
  - Marks a notification as archived.
- `archiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
- `array(): ArrayMutations!`
- `configureUps(config: UPSConfigInput!): Boolean!`
- `createNotification(input: NotificationData!): Notification!`
  - Creates a new notification record
- `customization(): CustomizationMutations!`
- `deleteArchivedNotifications(): NotificationOverview!`
  - Deletes all archived notifications on server.
- `deleteNotification(id: PrefixedID!, type: NotificationType!): NotificationOverview!`
- `docker(): DockerMutations!`
- `initiateFlashBackup(input: InitiateFlashBackupInput!): FlashBackupStatus!`
  - Initiates a flash drive backup using a configured remote.
- `parityCheck(): ParityCheckMutations!`
- `rclone(): RCloneMutations!`
- `recalculateOverview(): NotificationOverview!`
  - Reads each notification to recompute & update the overview.
- `removePlugin(input: PluginManagementInput!): Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **CONFIG** #### Description: Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required.
- `unarchiveAll(importance: NotificationImportance): NotificationOverview!`
- `unarchiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
- `unreadNotification(id: PrefixedID!): Notification!`
  - Marks a notification as unread.
- `updateSettings(input: JSON!): UpdateSettingsResponse!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
- `vm(): VmMutations!`

### Subscriptions
Total fields: **11**

- `arraySubscription(): UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `logFile(path: String!): LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `notificationAdded(): Notification!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsOverview(): NotificationOverview!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `ownerSubscription(): Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistorySubscription(): ParityCheck!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `serversSubscription(): Server!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `systemMetricsCpu(): CpuUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsCpuTelemetry(): CpuPackages!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsMemory(): MemoryUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `upsUpdates(): UPSDevice!`

## Directives
### `@deprecated`
Marks an element of a GraphQL schema as no longer supported.

- Locations: `FIELD_DEFINITION`, `ARGUMENT_DEFINITION`, `INPUT_FIELD_DEFINITION`, `ENUM_VALUE`
- Arguments:
  - `reason`: `String` (default: `"No longer supported"`)
    - Explains why this element was deprecated, usually also including a suggestion for how to access supported similar data. Formatted using the Markdown syntax, as specified by [CommonMark](https://commonmark.org/).

### `@include`
Directs the executor to include this field or fragment only when the `if` argument is true.

- Locations: `FIELD`, `FRAGMENT_SPREAD`, `INLINE_FRAGMENT`
- Arguments:
  - `if`: `Boolean!`
    - Included when true.

### `@oneOf`
Indicates exactly one field must be supplied and this field must not be `null`.

- Locations: `INPUT_OBJECT`

### `@skip`
Directs the executor to skip this field or fragment when the `if` argument is true.

- Locations: `FIELD`, `FRAGMENT_SPREAD`, `INLINE_FRAGMENT`
- Arguments:
  - `if`: `Boolean!`
    - Skipped when true.

### `@specifiedBy`
Exposes a URL that specifies the behavior of this scalar.

- Locations: `SCALAR`
- Arguments:
  - `url`: `String!`
    - The URL that specifies the behavior of this scalar.

### `@usePermissions`
Directive to document required permissions for fields

- Locations: `FIELD_DEFINITION`
- Arguments:
  - `action`: `String`
    - The action required for access (must be a valid AuthAction enum value)
  - `resource`: `String`
    - The resource required for access (must be a valid Resource enum value)

## All Types (Alphabetical)
### `ActivationCode` (OBJECT)
- Fields (11):
- `background`: `String`
- `code`: `String`
- `comment`: `String`
- `header`: `String`
- `headermetacolor`: `String`
- `partnerName`: `String`
- `partnerUrl`: `String`
- `serverName`: `String`
- `showBannerGradient`: `Boolean`
- `sysModel`: `String`
- `theme`: `String`

### `AddPermissionInput` (INPUT_OBJECT)
- Input fields (2):
- `actions`: `[AuthAction!]!`
- `resource`: `Resource!`

### `AddRoleForApiKeyInput` (INPUT_OBJECT)
- Input fields (2):
- `apiKeyId`: `PrefixedID!`
- `role`: `Role!`

### `ApiConfig` (OBJECT)
- Fields (5):
- `extraOrigins`: `[String!]!`
- `plugins`: `[String!]!`
- `sandbox`: `Boolean`
- `ssoSubIds`: `[String!]!`
- `version`: `String!`

### `ApiKey` (OBJECT)
- Implements: `Node`
- Fields (7):
- `createdAt`: `String!`
- `description`: `String`
- `id`: `PrefixedID!`
- `key`: `String!`
- `name`: `String!`
- `permissions`: `[Permission!]!`
- `roles`: `[Role!]!`

### `ApiKeyFormSettings` (OBJECT)
- Implements: `FormSchema`, `Node`
- Fields (4):
- `dataSchema`: `JSON!`
  - The data schema for the API key form
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
  - The UI schema for the API key form
- `values`: `JSON!`
  - The current values of the API key form

### `ApiKeyMutations` (OBJECT)
API Key related mutations

- Fields (5):
- `addRole`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **API_KEY** #### Description: Add a role to an API key
  - Arguments:
    - `input`: `AddRoleForApiKeyInput!`
- `create`: `ApiKey!`
  - #### Required Permissions: - Action: **CREATE_ANY** - Resource: **API_KEY** #### Description: Create an API key
  - Arguments:
    - `input`: `CreateApiKeyInput!`
- `delete`: `Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **API_KEY** #### Description: Delete one or more API keys
  - Arguments:
    - `input`: `DeleteApiKeyInput!`
- `removeRole`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **API_KEY** #### Description: Remove a role from an API key
  - Arguments:
    - `input`: `RemoveRoleFromApiKeyInput!`
- `update`: `ApiKey!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **API_KEY** #### Description: Update an API key
  - Arguments:
    - `input`: `UpdateApiKeyInput!`

### `ArrayCapacity` (OBJECT)
- Fields (2):
- `disks`: `Capacity!`
  - Capacity in number of disks
- `kilobytes`: `Capacity!`
  - Capacity in kilobytes

### `ArrayDisk` (OBJECT)
- Implements: `Node`
- Fields (24):
- `color`: `ArrayDiskFsColor`
- `comment`: `String`
  - User comment on disk
- `critical`: `Int`
  - (%) Disk space left for critical
- `device`: `String`
- `exportable`: `Boolean`
- `format`: `String`
  - File format (ex MBR: 4KiB-aligned)
- `fsFree`: `BigInt`
  - (KB) Free Size on the FS (Not present on Parity type drive)
- `fsSize`: `BigInt`
  - (KB) Total Size of the FS (Not present on Parity type drive)
- `fsType`: `String`
  - File system type for the disk
- `fsUsed`: `BigInt`
  - (KB) Used Size on the FS (Not present on Parity type drive)
- `id`: `PrefixedID!`
- `idx`: `Int!`
  - Array slot number. Parity1 is always 0 and Parity2 is always 29. Array slots will be 1 - 28. Cache slots are 30 - 53. Flash is 54.
- `isSpinning`: `Boolean`
  - Whether the disk is currently spinning
- `name`: `String`
- `numErrors`: `BigInt`
  - Number of unrecoverable errors reported by the device I/O drivers. Missing data due to unrecoverable array read errors is filled in on-the-fly using parity reconstruct (and we attempt to write this data back to the sector(s) which failed). Any unrecoverable write error results in disabling the disk.
- `numReads`: `BigInt`
  - Count of I/O read requests sent to the device I/O drivers. These statistics may be cleared at any time.
- `numWrites`: `BigInt`
  - Count of I/O writes requests sent to the device I/O drivers. These statistics may be cleared at any time.
- `rotational`: `Boolean`
  - Is the disk a HDD or SSD.
- `size`: `BigInt`
  - (KB) Disk Size total
- `status`: `ArrayDiskStatus`
- `temp`: `Int`
  - Disk temp - will be NaN if array is not started or DISK_NP
- `transport`: `String`
  - ata | nvme | usb | (others)
- `type`: `ArrayDiskType!`
  - Type of Disk - used to differentiate Cache / Flash / Array / Parity
- `warning`: `Int`
  - (%) Disk space left to warn

### `ArrayDiskFsColor` (ENUM)
- Enum values (9):
  - `BLUE_BLINK`
  - `BLUE_ON`
  - `GREEN_BLINK`
  - `GREEN_ON`
  - `GREY_OFF`
  - `RED_OFF`
  - `RED_ON`
  - `YELLOW_BLINK`
  - `YELLOW_ON`

### `ArrayDiskInput` (INPUT_OBJECT)
- Input fields (2):
- `id`: `PrefixedID!`
  - Disk ID
- `slot`: `Int`
  - The slot for the disk

### `ArrayDiskStatus` (ENUM)
- Enum values (9):
  - `DISK_DSBL`
  - `DISK_DSBL_NEW`
  - `DISK_INVALID`
  - `DISK_NEW`
  - `DISK_NP`
  - `DISK_NP_DSBL`
  - `DISK_NP_MISSING`
  - `DISK_OK`
  - `DISK_WRONG`

### `ArrayDiskType` (ENUM)
- Enum values (4):
  - `CACHE`
  - `DATA`
  - `FLASH`
  - `PARITY`

### `ArrayMutations` (OBJECT)
- Fields (6):
- `addDiskToArray`: `UnraidArray!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Add new disk to array
  - Arguments:
    - `input`: `ArrayDiskInput!`
- `clearArrayDiskStatistics`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Clear statistics for a disk in the array
  - Arguments:
    - `id`: `PrefixedID!`
- `mountArrayDisk`: `ArrayDisk!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Mount a disk in the array
  - Arguments:
    - `id`: `PrefixedID!`
- `removeDiskFromArray`: `UnraidArray!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Remove existing disk from array. NOTE: The array must be stopped before running this otherwise it'll throw an error.
  - Arguments:
    - `input`: `ArrayDiskInput!`
- `setState`: `UnraidArray!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Set array state
  - Arguments:
    - `input`: `ArrayStateInput!`
- `unmountArrayDisk`: `ArrayDisk!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Unmount a disk from the array
  - Arguments:
    - `id`: `PrefixedID!`

### `ArrayState` (ENUM)
- Enum values (11):
  - `DISABLE_DISK`
  - `INVALID_EXPANSION`
  - `NEW_ARRAY`
  - `NEW_DISK_TOO_SMALL`
  - `NO_DATA_DISKS`
  - `PARITY_NOT_BIGGEST`
  - `RECON_DISK`
  - `STARTED`
  - `STOPPED`
  - `SWAP_DSBL`
  - `TOO_MANY_MISSING_DISKS`

### `ArrayStateInput` (INPUT_OBJECT)
- Input fields (1):
- `desiredState`: `ArrayStateInputState!`
  - Array state

### `ArrayStateInputState` (ENUM)
- Enum values (2):
  - `START`
  - `STOP`

### `AuthAction` (ENUM)
Authentication actions with possession (e.g., create:any, read:own)

- Enum values (8):
  - `CREATE_ANY`
    - Create any resource
  - `CREATE_OWN`
    - Create own resource
  - `DELETE_ANY`
    - Delete any resource
  - `DELETE_OWN`
    - Delete own resource
  - `READ_ANY`
    - Read any resource
  - `READ_OWN`
    - Read own resource
  - `UPDATE_ANY`
    - Update any resource
  - `UPDATE_OWN`
    - Update own resource

### `AuthorizationOperator` (ENUM)
Operators for authorization rule matching

- Enum values (4):
  - `CONTAINS`
  - `ENDS_WITH`
  - `EQUALS`
  - `STARTS_WITH`

### `AuthorizationRuleMode` (ENUM)
Mode for evaluating authorization rules - OR (any rule passes) or AND (all rules must pass)

- Enum values (2):
  - `AND`
  - `OR`

### `BigInt` (SCALAR)
The `BigInt` scalar type represents non-fractional signed whole numeric values.

- Scalar type

### `Boolean` (SCALAR)
The `Boolean` scalar type represents `true` or `false`.

- Scalar type

### `Capacity` (OBJECT)
- Fields (3):
- `free`: `String!`
  - Free capacity
- `total`: `String!`
  - Total capacity
- `used`: `String!`
  - Used capacity

### `Config` (OBJECT)
- Implements: `Node`
- Fields (3):
- `error`: `String`
- `id`: `PrefixedID!`
- `valid`: `Boolean`

### `ConfigErrorState` (ENUM)
Possible error states for configuration

- Enum values (5):
  - `INELIGIBLE`
  - `INVALID`
  - `NO_KEY_SERVER`
  - `UNKNOWN_ERROR`
  - `WITHDRAWN`

### `ContainerHostConfig` (OBJECT)
- Fields (1):
- `networkMode`: `String!`

### `ContainerPort` (OBJECT)
- Fields (4):
- `ip`: `String`
- `privatePort`: `Port`
- `publicPort`: `Port`
- `type`: `ContainerPortType!`

### `ContainerPortType` (ENUM)
- Enum values (2):
  - `TCP`
  - `UDP`

### `ContainerState` (ENUM)
- Enum values (2):
  - `EXITED`
  - `RUNNING`

### `CoreVersions` (OBJECT)
- Fields (3):
- `api`: `String`
  - Unraid API version
- `kernel`: `String`
  - Kernel version
- `unraid`: `String`
  - Unraid version

### `CpuLoad` (OBJECT)
CPU load for a single core

- Fields (8):
- `percentGuest`: `Float!`
  - The percentage of time the CPU spent running virtual machines (guest).
- `percentIdle`: `Float!`
  - The percentage of time the CPU was idle.
- `percentIrq`: `Float!`
  - The percentage of time the CPU spent servicing hardware interrupts.
- `percentNice`: `Float!`
  - The percentage of time the CPU spent on low-priority (niced) user space processes.
- `percentSteal`: `Float!`
  - The percentage of CPU time stolen by the hypervisor.
- `percentSystem`: `Float!`
  - The percentage of time the CPU spent in kernel space.
- `percentTotal`: `Float!`
  - The total CPU load on a single core, in percent.
- `percentUser`: `Float!`
  - The percentage of time the CPU spent in user space.

### `CpuPackages` (OBJECT)
- Implements: `Node`
- Fields (4):
- `id`: `PrefixedID!`
- `power`: `[Float!]!`
  - Power draw per package (W)
- `temp`: `[Float!]!`
  - Temperature per package (°C)
- `totalPower`: `Float!`
  - Total CPU package power draw (W)

### `CpuUtilization` (OBJECT)
- Implements: `Node`
- Fields (3):
- `cpus`: `[CpuLoad!]!`
  - CPU load for each core
- `id`: `PrefixedID!`
- `percentTotal`: `Float!`
  - Total CPU load in percent

### `CreateApiKeyInput` (INPUT_OBJECT)
- Input fields (5):
- `description`: `String`
- `name`: `String!`
- `overwrite`: `Boolean`
  - This will replace the existing key if one already exists with the same name, otherwise returns the existing key
- `permissions`: `[AddPermissionInput!]`
- `roles`: `[Role!]`

### `CreateRCloneRemoteInput` (INPUT_OBJECT)
- Input fields (3):
- `name`: `String!`
- `parameters`: `JSON!`
- `type`: `String!`

### `Customization` (OBJECT)
- Fields (3):
- `activationCode`: `ActivationCode`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ACTIVATION_CODE**
- `partnerInfo`: `PublicPartnerInfo`
- `theme`: `Theme!`

### `CustomizationMutations` (OBJECT)
Customization related mutations

- Fields (1):
- `setTheme`: `Theme!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CUSTOMIZATIONS** #### Description: Update the UI theme (writes dynamix.cfg)
  - Arguments:
    - `theme`: `ThemeName!`
      - Theme to apply

### `DateTime` (SCALAR)
A date-time string at UTC, such as 2019-12-03T09:54:33Z, compliant with the date-time format.

- Scalar type

### `DeleteApiKeyInput` (INPUT_OBJECT)
- Input fields (1):
- `ids`: `[PrefixedID!]!`

### `DeleteRCloneRemoteInput` (INPUT_OBJECT)
- Input fields (1):
- `name`: `String!`

### `Disk` (OBJECT)
- Implements: `Node`
- Fields (20):
- `bytesPerSector`: `Float!`
  - The number of bytes per sector
- `device`: `String!`
  - The device path of the disk (e.g. /dev/sdb)
- `firmwareRevision`: `String!`
  - The firmware revision of the disk
- `id`: `PrefixedID!`
- `interfaceType`: `DiskInterfaceType!`
  - The interface type of the disk
- `isSpinning`: `Boolean!`
  - Whether the disk is spinning or not
- `name`: `String!`
  - The model name of the disk
- `partitions`: `[DiskPartition!]!`
  - The partitions on the disk
- `sectorsPerTrack`: `Float!`
  - The number of sectors per track
- `serialNum`: `String!`
  - The serial number of the disk
- `size`: `Float!`
  - The total size of the disk in bytes
- `smartStatus`: `DiskSmartStatus!`
  - The SMART status of the disk
- `temperature`: `Float`
  - The current temperature of the disk in Celsius
- `totalCylinders`: `Float!`
  - The total number of cylinders on the disk
- `totalHeads`: `Float!`
  - The total number of heads on the disk
- `totalSectors`: `Float!`
  - The total number of sectors on the disk
- `totalTracks`: `Float!`
  - The total number of tracks on the disk
- `tracksPerCylinder`: `Float!`
  - The number of tracks per cylinder
- `type`: `String!`
  - The type of disk (e.g. SSD, HDD)
- `vendor`: `String!`
  - The manufacturer of the disk

### `DiskFsType` (ENUM)
The type of filesystem on the disk partition

- Enum values (6):
  - `BTRFS`
  - `EXT4`
  - `NTFS`
  - `VFAT`
  - `XFS`
  - `ZFS`

### `DiskInterfaceType` (ENUM)
The type of interface the disk uses to connect to the system

- Enum values (5):
  - `PCIE`
  - `SAS`
  - `SATA`
  - `UNKNOWN`
  - `USB`

### `DiskPartition` (OBJECT)
- Fields (3):
- `fsType`: `DiskFsType!`
  - The filesystem type of the partition
- `name`: `String!`
  - The name of the partition
- `size`: `Float!`
  - The size of the partition in bytes

### `DiskSmartStatus` (ENUM)
The SMART (Self-Monitoring, Analysis and Reporting Technology) status of the disk

- Enum values (2):
  - `OK`
  - `UNKNOWN`

### `Docker` (OBJECT)
- Implements: `Node`
- Fields (3):
- `containers`: `[DockerContainer!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
  - Arguments:
    - `skipCache`: `Boolean!` (default: `false`)
- `id`: `PrefixedID!`
- `networks`: `[DockerNetwork!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
  - Arguments:
    - `skipCache`: `Boolean!` (default: `false`)

### `DockerContainer` (OBJECT)
- Implements: `Node`
- Fields (15):
- `autoStart`: `Boolean!`
- `command`: `String!`
- `created`: `Int!`
- `hostConfig`: `ContainerHostConfig`
- `id`: `PrefixedID!`
- `image`: `String!`
- `imageId`: `String!`
- `labels`: `JSON`
- `mounts`: `[JSON!]`
- `names`: `[String!]!`
- `networkSettings`: `JSON`
- `ports`: `[ContainerPort!]!`
- `sizeRootFs`: `BigInt`
  - Total size of all files in the container (in bytes)
- `state`: `ContainerState!`
- `status`: `String!`

### `DockerMutations` (OBJECT)
- Fields (2):
- `start`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Start a container
  - Arguments:
    - `id`: `PrefixedID!`
- `stop`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Stop a container
  - Arguments:
    - `id`: `PrefixedID!`

### `DockerNetwork` (OBJECT)
- Implements: `Node`
- Fields (15):
- `attachable`: `Boolean!`
- `configFrom`: `JSON!`
- `configOnly`: `Boolean!`
- `containers`: `JSON!`
- `created`: `String!`
- `driver`: `String!`
- `enableIPv6`: `Boolean!`
- `id`: `PrefixedID!`
- `ingress`: `Boolean!`
- `internal`: `Boolean!`
- `ipam`: `JSON!`
- `labels`: `JSON!`
- `name`: `String!`
- `options`: `JSON!`
- `scope`: `String!`

### `ExplicitStatusItem` (OBJECT)
- Fields (2):
- `name`: `String!`
- `updateStatus`: `UpdateStatus!`

### `Flash` (OBJECT)
- Implements: `Node`
- Fields (4):
- `guid`: `String!`
- `id`: `PrefixedID!`
- `product`: `String!`
- `vendor`: `String!`

### `FlashBackupStatus` (OBJECT)
- Fields (2):
- `jobId`: `String`
  - Job ID if available, can be used to check job status.
- `status`: `String!`
  - Status message indicating the outcome of the backup initiation.

### `Float` (SCALAR)
The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).

- Scalar type

### `FormSchema` (INTERFACE)
- Interface fields (3):
- `dataSchema`: `JSON!`
  - The data schema for the form
- `uiSchema`: `JSON!`
  - The UI schema for the form
- `values`: `JSON!`
  - The current values of the form
- Implemented by (2): `ApiKeyFormSettings`, `UnifiedSettings`

### `ID` (SCALAR)
The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.

- Scalar type

### `Info` (OBJECT)
- Implements: `Node`
- Fields (11):
- `baseboard`: `InfoBaseboard!`
  - Motherboard information
- `cpu`: `InfoCpu!`
  - CPU information
- `devices`: `InfoDevices!`
  - Device information
- `display`: `InfoDisplay!`
  - Display configuration
- `id`: `PrefixedID!`
- `machineId`: `ID`
  - Machine ID
- `memory`: `InfoMemory!`
  - Memory information
- `os`: `InfoOs!`
  - Operating system information
- `system`: `InfoSystem!`
  - System information
- `time`: `DateTime!`
  - Current server time
- `versions`: `InfoVersions!`
  - Software versions

### `InfoBaseboard` (OBJECT)
- Implements: `Node`
- Fields (8):
- `assetTag`: `String`
  - Motherboard asset tag
- `id`: `PrefixedID!`
- `manufacturer`: `String`
  - Motherboard manufacturer
- `memMax`: `Float`
  - Maximum memory capacity in bytes
- `memSlots`: `Float`
  - Number of memory slots
- `model`: `String`
  - Motherboard model
- `serial`: `String`
  - Motherboard serial number
- `version`: `String`
  - Motherboard version

### `InfoCpu` (OBJECT)
- Implements: `Node`
- Fields (20):
- `brand`: `String`
  - CPU brand name
- `cache`: `JSON`
  - CPU cache information
- `cores`: `Int`
  - Number of CPU cores
- `family`: `String`
  - CPU family
- `flags`: `[String!]`
  - CPU feature flags
- `id`: `PrefixedID!`
- `manufacturer`: `String`
  - CPU manufacturer
- `model`: `String`
  - CPU model
- `packages`: `CpuPackages!`
- `processors`: `Int`
  - Number of physical processors
- `revision`: `String`
  - CPU revision
- `socket`: `String`
  - CPU socket type
- `speed`: `Float`
  - Current CPU speed in GHz
- `speedmax`: `Float`
  - Maximum CPU speed in GHz
- `speedmin`: `Float`
  - Minimum CPU speed in GHz
- `stepping`: `Int`
  - CPU stepping
- `threads`: `Int`
  - Number of CPU threads
- `topology`: `[[[Int!]!]!]!`
  - Per-package array of core/thread pairs, e.g. [[[0,1],[2,3]], [[4,5],[6,7]]]
- `vendor`: `String`
  - CPU vendor
- `voltage`: `String`
  - CPU voltage

### `InfoDevices` (OBJECT)
- Implements: `Node`
- Fields (5):
- `gpu`: `[InfoGpu!]`
  - List of GPU devices
- `id`: `PrefixedID!`
- `network`: `[InfoNetwork!]`
  - List of network interfaces
- `pci`: `[InfoPci!]`
  - List of PCI devices
- `usb`: `[InfoUsb!]`
  - List of USB devices

### `InfoDisplay` (OBJECT)
- Implements: `Node`
- Fields (16):
- `case`: `InfoDisplayCase!`
  - Case display configuration
- `critical`: `Int!`
  - Critical temperature threshold
- `hot`: `Int!`
  - Hot temperature threshold
- `id`: `PrefixedID!`
- `locale`: `String`
  - Locale setting
- `max`: `Int`
  - Maximum temperature threshold
- `resize`: `Boolean!`
  - Enable UI resize
- `scale`: `Boolean!`
  - Enable UI scaling
- `tabs`: `Boolean!`
  - Show tabs in UI
- `text`: `Boolean!`
  - Show text labels
- `theme`: `ThemeName!`
  - UI theme name
- `total`: `Boolean!`
  - Show totals
- `unit`: `Temperature!`
  - Temperature unit (C or F)
- `usage`: `Boolean!`
  - Show usage statistics
- `warning`: `Int!`
  - Warning temperature threshold
- `wwn`: `Boolean!`
  - Show WWN identifiers

### `InfoDisplayCase` (OBJECT)
- Implements: `Node`
- Fields (5):
- `base64`: `String!`
  - Base64 encoded case image
- `error`: `String!`
  - Error message if any
- `icon`: `String!`
  - Case icon identifier
- `id`: `PrefixedID!`
- `url`: `String!`
  - Case image URL

### `InfoGpu` (OBJECT)
- Implements: `Node`
- Fields (7):
- `blacklisted`: `Boolean!`
  - Whether GPU is blacklisted
- `class`: `String!`
  - Device class
- `id`: `PrefixedID!`
- `productid`: `String!`
  - Product ID
- `type`: `String!`
  - GPU type/manufacturer
- `typeid`: `String!`
  - GPU type identifier
- `vendorname`: `String`
  - Vendor name

### `InfoMemory` (OBJECT)
- Implements: `Node`
- Fields (2):
- `id`: `PrefixedID!`
- `layout`: `[MemoryLayout!]!`
  - Physical memory layout

### `InfoNetwork` (OBJECT)
- Implements: `Node`
- Fields (8):
- `dhcp`: `Boolean`
  - DHCP enabled flag
- `id`: `PrefixedID!`
- `iface`: `String!`
  - Network interface name
- `mac`: `String`
  - MAC address
- `model`: `String`
  - Network interface model
- `speed`: `String`
  - Network speed
- `vendor`: `String`
  - Network vendor
- `virtual`: `Boolean`
  - Virtual interface flag

### `InfoOs` (OBJECT)
- Implements: `Node`
- Fields (15):
- `arch`: `String`
  - OS architecture
- `build`: `String`
  - OS build identifier
- `codename`: `String`
  - OS codename
- `distro`: `String`
  - Linux distribution name
- `fqdn`: `String`
  - Fully qualified domain name
- `hostname`: `String`
  - Hostname
- `id`: `PrefixedID!`
- `kernel`: `String`
  - Kernel version
- `logofile`: `String`
  - OS logo name
- `platform`: `String`
  - Operating system platform
- `release`: `String`
  - OS release version
- `serial`: `String`
  - OS serial number
- `servicepack`: `String`
  - Service pack version
- `uefi`: `Boolean`
  - OS started via UEFI
- `uptime`: `String`
  - Boot time ISO string

### `InfoPci` (OBJECT)
- Implements: `Node`
- Fields (9):
- `blacklisted`: `String!`
  - Blacklisted status
- `class`: `String!`
  - Device class
- `id`: `PrefixedID!`
- `productid`: `String!`
  - Product ID
- `productname`: `String`
  - Product name
- `type`: `String!`
  - Device type/manufacturer
- `typeid`: `String!`
  - Type identifier
- `vendorid`: `String!`
  - Vendor ID
- `vendorname`: `String`
  - Vendor name

### `InfoSystem` (OBJECT)
- Implements: `Node`
- Fields (8):
- `id`: `PrefixedID!`
- `manufacturer`: `String`
  - System manufacturer
- `model`: `String`
  - System model
- `serial`: `String`
  - System serial number
- `sku`: `String`
  - System SKU
- `uuid`: `String`
  - System UUID
- `version`: `String`
  - System version
- `virtual`: `Boolean`
  - Virtual machine flag

### `InfoUsb` (OBJECT)
- Implements: `Node`
- Fields (4):
- `bus`: `String`
  - USB bus number
- `device`: `String`
  - USB device number
- `id`: `PrefixedID!`
- `name`: `String!`
  - USB device name

### `InfoVersions` (OBJECT)
- Implements: `Node`
- Fields (3):
- `core`: `CoreVersions!`
  - Core system versions
- `id`: `PrefixedID!`
- `packages`: `PackageVersions`
  - Software package versions

### `InitiateFlashBackupInput` (INPUT_OBJECT)
- Input fields (4):
- `destinationPath`: `String!`
  - Destination path on the remote.
- `options`: `JSON`
  - Additional options for the backup operation, such as --dry-run or --transfers.
- `remoteName`: `String!`
  - The name of the remote configuration to use for the backup.
- `sourcePath`: `String!`
  - Source path to backup (typically the flash drive).

### `Int` (SCALAR)
The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.

- Scalar type

### `JSON` (SCALAR)
The `JSON` scalar type represents JSON values as specified by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

- Scalar type

### `KeyFile` (OBJECT)
- Fields (2):
- `contents`: `String`
- `location`: `String`

### `LogFile` (OBJECT)
- Fields (4):
- `modifiedAt`: `DateTime!`
  - Last modified timestamp
- `name`: `String!`
  - Name of the log file
- `path`: `String!`
  - Full path to the log file
- `size`: `Int!`
  - Size of the log file in bytes

### `LogFileContent` (OBJECT)
- Fields (4):
- `content`: `String!`
  - Content of the log file
- `path`: `String!`
  - Path to the log file
- `startLine`: `Int`
  - Starting line number of the content (1-indexed)
- `totalLines`: `Int!`
  - Total number of lines in the file

### `MemoryLayout` (OBJECT)
- Implements: `Node`
- Fields (12):
- `bank`: `String`
  - Memory bank location (e.g., BANK 0)
- `clockSpeed`: `Int`
  - Memory clock speed in MHz
- `formFactor`: `String`
  - Form factor (e.g., DIMM, SODIMM)
- `id`: `PrefixedID!`
- `manufacturer`: `String`
  - Memory manufacturer
- `partNum`: `String`
  - Part number of the memory module
- `serialNum`: `String`
  - Serial number of the memory module
- `size`: `BigInt!`
  - Memory module size in bytes
- `type`: `String`
  - Memory type (e.g., DDR4, DDR5)
- `voltageConfigured`: `Int`
  - Configured voltage in millivolts
- `voltageMax`: `Int`
  - Maximum voltage in millivolts
- `voltageMin`: `Int`
  - Minimum voltage in millivolts

### `MemoryUtilization` (OBJECT)
- Implements: `Node`
- Fields (12):
- `active`: `BigInt!`
  - Active memory in bytes
- `available`: `BigInt!`
  - Available memory in bytes
- `buffcache`: `BigInt!`
  - Buffer/cache memory in bytes
- `free`: `BigInt!`
  - Free memory in bytes
- `id`: `PrefixedID!`
- `percentSwapTotal`: `Float!`
  - Swap usage percentage
- `percentTotal`: `Float!`
  - Memory usage percentage
- `swapFree`: `BigInt!`
  - Free swap memory in bytes
- `swapTotal`: `BigInt!`
  - Total swap memory in bytes
- `swapUsed`: `BigInt!`
  - Used swap memory in bytes
- `total`: `BigInt!`
  - Total system memory in bytes
- `used`: `BigInt!`
  - Used memory in bytes

### `Metrics` (OBJECT)
System metrics including CPU and memory utilization

- Implements: `Node`
- Fields (3):
- `cpu`: `CpuUtilization`
  - Current CPU utilization metrics
- `id`: `PrefixedID!`
- `memory`: `MemoryUtilization`
  - Current memory utilization metrics

### `Mutation` (OBJECT)
- Fields (22):
- `addPlugin`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Add one or more plugins to the API. Returns false if restart was triggered automatically, true if manual restart is required.
  - Arguments:
    - `input`: `PluginManagementInput!`
- `apiKey`: `ApiKeyMutations!`
- `archiveAll`: `NotificationOverview!`
  - Arguments:
    - `importance`: `NotificationImportance`
- `archiveNotification`: `Notification!`
  - Marks a notification as archived.
  - Arguments:
    - `id`: `PrefixedID!`
- `archiveNotifications`: `NotificationOverview!`
  - Arguments:
    - `ids`: `[PrefixedID!]!`
- `array`: `ArrayMutations!`
- `configureUps`: `Boolean!`
  - Arguments:
    - `config`: `UPSConfigInput!`
- `createNotification`: `Notification!`
  - Creates a new notification record
  - Arguments:
    - `input`: `NotificationData!`
- `customization`: `CustomizationMutations!`
- `deleteArchivedNotifications`: `NotificationOverview!`
  - Deletes all archived notifications on server.
- `deleteNotification`: `NotificationOverview!`
  - Arguments:
    - `id`: `PrefixedID!`
    - `type`: `NotificationType!`
- `docker`: `DockerMutations!`
- `initiateFlashBackup`: `FlashBackupStatus!`
  - Initiates a flash drive backup using a configured remote.
  - Arguments:
    - `input`: `InitiateFlashBackupInput!`
- `parityCheck`: `ParityCheckMutations!`
- `rclone`: `RCloneMutations!`
- `recalculateOverview`: `NotificationOverview!`
  - Reads each notification to recompute & update the overview.
- `removePlugin`: `Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **CONFIG** #### Description: Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required.
  - Arguments:
    - `input`: `PluginManagementInput!`
- `unarchiveAll`: `NotificationOverview!`
  - Arguments:
    - `importance`: `NotificationImportance`
- `unarchiveNotifications`: `NotificationOverview!`
  - Arguments:
    - `ids`: `[PrefixedID!]!`
- `unreadNotification`: `Notification!`
  - Marks a notification as unread.
  - Arguments:
    - `id`: `PrefixedID!`
- `updateSettings`: `UpdateSettingsResponse!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
  - Arguments:
    - `input`: `JSON!`
- `vm`: `VmMutations!`

### `Node` (INTERFACE)
- Interface fields (1):
- `id`: `PrefixedID!`
- Implemented by (43): `ApiKey`, `ApiKeyFormSettings`, `ArrayDisk`, `Config`, `CpuPackages`, `CpuUtilization`, `Disk`, `Docker`, `DockerContainer`, `DockerNetwork`, `Flash`, `Info`, `InfoBaseboard`, `InfoCpu`, `InfoDevices`, `InfoDisplay`, `InfoDisplayCase`, `InfoGpu`, `InfoMemory`, `InfoNetwork`, `InfoOs`, `InfoPci`, `InfoSystem`, `InfoUsb`, `InfoVersions`, `MemoryLayout`, `MemoryUtilization`, `Metrics`, `Notification`, `Notifications`, `ProfileModel`, `Registration`, `Server`, `Service`, `Settings`, `Share`, `SsoSettings`, `UnifiedSettings`, `UnraidArray`, `UserAccount`, `Vars`, `VmDomain`, `Vms`

### `Notification` (OBJECT)
- Implements: `Node`
- Fields (9):
- `description`: `String!`
- `formattedTimestamp`: `String`
- `id`: `PrefixedID!`
- `importance`: `NotificationImportance!`
- `link`: `String`
- `subject`: `String!`
- `timestamp`: `String`
  - ISO Timestamp for when the notification occurred
- `title`: `String!`
  - Also known as 'event'
- `type`: `NotificationType!`

### `NotificationCounts` (OBJECT)
- Fields (4):
- `alert`: `Int!`
- `info`: `Int!`
- `total`: `Int!`
- `warning`: `Int!`

### `NotificationData` (INPUT_OBJECT)
- Input fields (5):
- `description`: `String!`
- `importance`: `NotificationImportance!`
- `link`: `String`
- `subject`: `String!`
- `title`: `String!`

### `NotificationFilter` (INPUT_OBJECT)
- Input fields (4):
- `importance`: `NotificationImportance`
- `limit`: `Int!`
- `offset`: `Int!`
- `type`: `NotificationType!`

### `NotificationImportance` (ENUM)
- Enum values (3):
  - `ALERT`
  - `INFO`
  - `WARNING`

### `NotificationOverview` (OBJECT)
- Fields (2):
- `archive`: `NotificationCounts!`
- `unread`: `NotificationCounts!`

### `NotificationType` (ENUM)
- Enum values (2):
  - `ARCHIVE`
  - `UNREAD`

### `Notifications` (OBJECT)
- Implements: `Node`
- Fields (3):
- `id`: `PrefixedID!`
- `list`: `[Notification!]!`
  - Arguments:
    - `filter`: `NotificationFilter!`
- `overview`: `NotificationOverview!`
  - A cached overview of the notifications in the system & their severity.

### `OidcAuthorizationRule` (OBJECT)
- Fields (3):
- `claim`: `String!`
  - The claim to check (e.g., email, sub, groups, hd)
- `operator`: `AuthorizationOperator!`
  - The comparison operator
- `value`: `[String!]!`
  - The value(s) to match against

### `OidcConfiguration` (OBJECT)
- Fields (2):
- `defaultAllowedOrigins`: `[String!]`
  - Default allowed redirect origins that apply to all OIDC providers (e.g., Tailscale domains)
- `providers`: `[OidcProvider!]!`
  - List of configured OIDC providers

### `OidcProvider` (OBJECT)
- Fields (15):
- `authorizationEndpoint`: `String`
  - OAuth2 authorization endpoint URL. If omitted, will be auto-discovered from issuer/.well-known/openid-configuration
- `authorizationRuleMode`: `AuthorizationRuleMode`
  - Mode for evaluating authorization rules - OR (any rule passes) or AND (all rules must pass). Defaults to OR.
- `authorizationRules`: `[OidcAuthorizationRule!]`
  - Flexible authorization rules based on claims
- `buttonIcon`: `String`
  - URL or base64 encoded icon for the login button
- `buttonStyle`: `String`
  - Custom CSS styles for the button (e.g., "background: linear-gradient(to right, #4f46e5, #7c3aed); border-radius: 9999px;")
- `buttonText`: `String`
  - Custom text for the login button
- `buttonVariant`: `String`
  - Button variant style from Reka UI. See https://reka-ui.com/docs/components/button
- `clientId`: `String!`
  - OAuth2 client ID registered with the provider
- `clientSecret`: `String`
  - OAuth2 client secret (if required by provider)
- `id`: `PrefixedID!`
  - The unique identifier for the OIDC provider
- `issuer`: `String`
  - OIDC issuer URL (e.g., https://accounts.google.com). Required for auto-discovery via /.well-known/openid-configuration
- `jwksUri`: `String`
  - JSON Web Key Set URI for token validation. If omitted, will be auto-discovered from issuer/.well-known/openid-configuration
- `name`: `String!`
  - Display name of the OIDC provider
- `scopes`: `[String!]!`
  - OAuth2 scopes to request (e.g., openid, profile, email)
- `tokenEndpoint`: `String`
  - OAuth2 token endpoint URL. If omitted, will be auto-discovered from issuer/.well-known/openid-configuration

### `OidcSessionValidation` (OBJECT)
- Fields (2):
- `username`: `String`
- `valid`: `Boolean!`

### `OrganizerContainerResource` (OBJECT)
- Fields (4):
- `id`: `String!`
- `meta`: `DockerContainer`
- `name`: `String!`
- `type`: `String!`

### `OrganizerResource` (OBJECT)
- Fields (4):
- `id`: `String!`
- `meta`: `JSON`
- `name`: `String!`
- `type`: `String!`

### `Owner` (OBJECT)
- Fields (3):
- `avatar`: `String!`
- `url`: `String!`
- `username`: `String!`

### `PackageVersions` (OBJECT)
- Fields (8):
- `docker`: `String`
  - Docker version
- `git`: `String`
  - Git version
- `nginx`: `String`
  - nginx version
- `node`: `String`
  - Node.js version
- `npm`: `String`
  - npm version
- `openssl`: `String`
  - OpenSSL version
- `php`: `String`
  - PHP version
- `pm2`: `String`
  - pm2 version

### `ParityCheck` (OBJECT)
- Fields (9):
- `correcting`: `Boolean`
  - Whether corrections are being written to parity
- `date`: `DateTime`
  - Date of the parity check
- `duration`: `Int`
  - Duration of the parity check in seconds
- `errors`: `Int`
  - Number of errors during the parity check
- `paused`: `Boolean`
  - Whether the parity check is paused
- `progress`: `Int`
  - Progress percentage of the parity check
- `running`: `Boolean`
  - Whether the parity check is running
- `speed`: `String`
  - Speed of the parity check, in MB/s
- `status`: `ParityCheckStatus!`
  - Status of the parity check

### `ParityCheckMutations` (OBJECT)
Parity check related mutations, WIP, response types and functionaliy will change

- Fields (4):
- `cancel`: `JSON!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Cancel a parity check
- `pause`: `JSON!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Pause a parity check
- `resume`: `JSON!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Resume a parity check
- `start`: `JSON!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **ARRAY** #### Description: Start a parity check
  - Arguments:
    - `correct`: `Boolean!`

### `ParityCheckStatus` (ENUM)
- Enum values (6):
  - `CANCELLED`
  - `COMPLETED`
  - `FAILED`
  - `NEVER_RUN`
  - `PAUSED`
  - `RUNNING`

### `Permission` (OBJECT)
- Fields (2):
- `actions`: `[AuthAction!]!`
  - Actions allowed on this resource
- `resource`: `Resource!`

### `Plugin` (OBJECT)
- Fields (4):
- `hasApiModule`: `Boolean`
  - Whether the plugin has an API module
- `hasCliModule`: `Boolean`
  - Whether the plugin has a CLI module
- `name`: `String!`
  - The name of the plugin package
- `version`: `String!`
  - The version of the plugin package

### `PluginManagementInput` (INPUT_OBJECT)
- Input fields (3):
- `bundled`: `Boolean!`
  - Whether to treat plugins as bundled plugins. Bundled plugins are installed to node_modules at build time and controlled via config only.
  - Default: `false`
- `names`: `[String!]!`
  - Array of plugin package names to add or remove
- `restart`: `Boolean!`
  - Whether to restart the API after the operation. When false, a restart has already been queued.
  - Default: `true`

### `Port` (SCALAR)
A field whose value is a valid TCP port within the range of 0 to 65535: https://en.wikipedia.org/wiki/Transmission_Control_Protocol#TCP_ports

- Scalar type

### `PrefixedID` (SCALAR)
### Description: ID scalar type that prefixes the underlying ID with the server identifier on output and strips it on input. We use this scalar type to ensure that the ID is unique across all servers, allowing the same underlying resource ID to be used across different server instances. #### Input Behavior: When providing an ID as input (e.g., in arguments or input objects), the server identifier prefix ('<serverId>:') is optional. - If the prefix is present (e.g., '123:456'), it will be automatically stripped, and only the underlying ID ('456') will be used internally. - If the prefix is absent (e.g., '456'), the ID will be used as-is. This makes it flexible for clients, as they don't strictly need to know or provide the server ID. #### Output Behavior: When an ID is returned in the response (output), it will *always* be prefixed with the current server's unique identifier (e.g., '123:456'). #### Example: Note: The server identifier is '123' in this example. ##### Input (Prefix Optional): ```graphql # Both of these are valid inputs resolving to internal ID '456' { someQuery(id: "123:456") { ... } anotherQuery(id: "456") { ... } } ``` ##### Output (Prefix Always Added): ```graphql # Assuming internal ID is '456' { "data": { "someResource": { "id": "123:456" } } } ```

- Scalar type

### `ProfileModel` (OBJECT)
- Implements: `Node`
- Fields (4):
- `avatar`: `String!`
- `id`: `PrefixedID!`
- `url`: `String!`
- `username`: `String!`

### `PublicOidcProvider` (OBJECT)
- Fields (6):
- `buttonIcon`: `String`
- `buttonStyle`: `String`
- `buttonText`: `String`
- `buttonVariant`: `String`
- `id`: `ID!`
- `name`: `String!`

### `PublicPartnerInfo` (OBJECT)
- Fields (4):
- `hasPartnerLogo`: `Boolean!`
  - Indicates if a partner logo exists
- `partnerLogoUrl`: `String`
  - The path to the partner logo image on the flash drive, relative to the activation code file
- `partnerName`: `String`
- `partnerUrl`: `String`

### `Query` (OBJECT)
- Fields (46):
- `apiKey`: `ApiKey`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**
  - Arguments:
    - `id`: `PrefixedID!`
- `apiKeyPossiblePermissions`: `[Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible permissions for API keys
- `apiKeyPossibleRoles`: `[Role!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible roles for API keys
- `apiKeys`: `[ApiKey!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**
- `array`: `UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `config`: `Config!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
- `customization`: `Customization`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS**
- `disk`: `Disk!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
  - Arguments:
    - `id`: `PrefixedID!`
- `disks`: `[Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `docker`: `Docker!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `flash`: `Flash!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `getApiKeyCreationFormSchema`: `ApiKeyFormSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY** #### Description: Get JSON Schema for API key creation form
- `getAvailableAuthActions`: `[AuthAction!]!`
  - Get all available authentication actions with possession
- `getPermissionsForRoles`: `[Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Get the actual permissions that would be granted by a set of roles
  - Arguments:
    - `roles`: `[Role!]!`
- `info`: `Info!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `isInitialSetup`: `Boolean!`
- `isSSOEnabled`: `Boolean!`
- `logFile`: `LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
  - Arguments:
    - `lines`: `Int`
    - `path`: `String!`
    - `startLine`: `Int`
- `logFiles`: `[LogFile!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `me`: `UserAccount!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ME**
- `metrics`: `Metrics!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `notifications`: `Notifications!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS** #### Description: Get all notifications
- `oidcConfiguration`: `OidcConfiguration!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get the full OIDC configuration (admin only)
- `oidcProvider`: `OidcProvider`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get a specific OIDC provider by ID
  - Arguments:
    - `id`: `PrefixedID!`
- `oidcProviders`: `[OidcProvider!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get all configured OIDC providers (admin only)
- `online`: `Boolean!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ONLINE**
- `owner`: `Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistory`: `[ParityCheck!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `plugins`: `[Plugin!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all installed plugins with their metadata
- `previewEffectivePermissions`: `[Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Preview the effective permissions for a combination of roles and explicit permissions
  - Arguments:
    - `permissions`: `[AddPermissionInput!]`
    - `roles`: `[Role!]`
- `publicOidcProviders`: `[PublicOidcProvider!]!`
  - Get public OIDC provider information for login buttons
- `publicPartnerInfo`: `PublicPartnerInfo`
- `publicTheme`: `Theme!`
- `rclone`: `RCloneBackupSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `registration`: `Registration`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **REGISTRATION**
- `server`: `Server`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `servers`: `[Server!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `services`: `[Service!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVICES**
- `settings`: `Settings!`
- `shares`: `[Share!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SHARE**
- `upsConfiguration`: `UPSConfiguration!`
- `upsDeviceById`: `UPSDevice`
  - Arguments:
    - `id`: `String!`
- `upsDevices`: `[UPSDevice!]!`
- `validateOidcSession`: `OidcSessionValidation!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Validate an OIDC session token (internal use for CLI validation)
  - Arguments:
    - `token`: `String!`
- `vars`: `Vars!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VARS**
- `vms`: `Vms!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VMS** #### Description: Get information about all VMs on the system

### `RCloneBackupConfigForm` (OBJECT)
- Fields (3):
- `dataSchema`: `JSON!`
- `id`: `ID!`
- `uiSchema`: `JSON!`

### `RCloneBackupSettings` (OBJECT)
- Fields (3):
- `configForm`: `RCloneBackupConfigForm!`
  - Arguments:
    - `formOptions`: `RCloneConfigFormInput`
- `drives`: `[RCloneDrive!]!`
- `remotes`: `[RCloneRemote!]!`

### `RCloneConfigFormInput` (INPUT_OBJECT)
- Input fields (3):
- `parameters`: `JSON`
- `providerType`: `String`
- `showAdvanced`: `Boolean`
  - Default: `false`

### `RCloneDrive` (OBJECT)
- Fields (2):
- `name`: `String!`
  - Provider name
- `options`: `JSON!`
  - Provider options and configuration schema

### `RCloneMutations` (OBJECT)
RClone related mutations

- Fields (2):
- `createRCloneRemote`: `RCloneRemote!`
  - #### Required Permissions: - Action: **CREATE_ANY** - Resource: **FLASH** #### Description: Create a new RClone remote
  - Arguments:
    - `input`: `CreateRCloneRemoteInput!`
- `deleteRCloneRemote`: `Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **FLASH** #### Description: Delete an existing RClone remote
  - Arguments:
    - `input`: `DeleteRCloneRemoteInput!`

### `RCloneRemote` (OBJECT)
- Fields (4):
- `config`: `JSON!`
  - Complete remote configuration
- `name`: `String!`
- `parameters`: `JSON!`
- `type`: `String!`

### `Registration` (OBJECT)
- Implements: `Node`
- Fields (6):
- `expiration`: `String`
- `id`: `PrefixedID!`
- `keyFile`: `KeyFile`
- `state`: `RegistrationState`
- `type`: `registrationType`
- `updateExpiration`: `String`

### `RegistrationState` (ENUM)
- Enum values (26):
  - `BASIC`
  - `EBLACKLISTED`
  - `EBLACKLISTED1`
  - `EBLACKLISTED2`
  - `EEXPIRED`
  - `EGUID`
  - `EGUID1`
  - `ENOCONN`
  - `ENOFLASH`
  - `ENOFLASH1`
  - `ENOFLASH2`
  - `ENOFLASH3`
  - `ENOFLASH4`
  - `ENOFLASH5`
  - `ENOFLASH6`
  - `ENOFLASH7`
  - `ENOKEYFILE`
  - `ENOKEYFILE1`
  - `ENOKEYFILE2`
  - `ETRIAL`
  - `LIFETIME`
  - `PLUS`
  - `PRO`
  - `STARTER`
  - `TRIAL`
  - `UNLEASHED`

### `RemoveRoleFromApiKeyInput` (INPUT_OBJECT)
- Input fields (2):
- `apiKeyId`: `PrefixedID!`
- `role`: `Role!`

### `ResolvedOrganizerEntry` (UNION)
- Possible types (3): `OrganizerContainerResource`, `OrganizerResource`, `ResolvedOrganizerFolder`

### `ResolvedOrganizerFolder` (OBJECT)
- Fields (4):
- `children`: `[ResolvedOrganizerEntry!]!`
- `id`: `String!`
- `name`: `String!`
- `type`: `String!`

### `ResolvedOrganizerV1` (OBJECT)
- Fields (2):
- `version`: `Float!`
- `views`: `[ResolvedOrganizerView!]!`

### `ResolvedOrganizerView` (OBJECT)
- Fields (4):
- `id`: `String!`
- `name`: `String!`
- `prefs`: `JSON`
- `root`: `ResolvedOrganizerEntry!`

### `Resource` (ENUM)
Available resources for permissions

- Enum values (29):
  - `ACTIVATION_CODE`
  - `API_KEY`
  - `ARRAY`
  - `CLOUD`
  - `CONFIG`
  - `CONNECT`
  - `CONNECT__REMOTE_ACCESS`
  - `CUSTOMIZATIONS`
  - `DASHBOARD`
  - `DISK`
  - `DISPLAY`
  - `DOCKER`
  - `FLASH`
  - `INFO`
  - `LOGS`
  - `ME`
  - `NETWORK`
  - `NOTIFICATIONS`
  - `ONLINE`
  - `OS`
  - `OWNER`
  - `PERMISSION`
  - `REGISTRATION`
  - `SERVERS`
  - `SERVICES`
  - `SHARE`
  - `VARS`
  - `VMS`
  - `WELCOME`

### `Role` (ENUM)
Available roles for API keys and users

- Enum values (4):
  - `ADMIN`
    - Full administrative access to all resources
  - `CONNECT`
    - Internal Role for Unraid Connect
  - `GUEST`
    - Basic read access to user profile only
  - `VIEWER`
    - Read-only access to all resources

### `Server` (OBJECT)
- Implements: `Node`
- Fields (10):
- `apikey`: `String!`
- `guid`: `String!`
- `id`: `PrefixedID!`
- `lanip`: `String!`
- `localurl`: `String!`
- `name`: `String!`
- `owner`: `ProfileModel!`
- `remoteurl`: `String!`
- `status`: `ServerStatus!`
  - Whether this server is online or offline
- `wanip`: `String!`

### `ServerStatus` (ENUM)
- Enum values (3):
  - `NEVER_CONNECTED`
  - `OFFLINE`
  - `ONLINE`

### `Service` (OBJECT)
- Implements: `Node`
- Fields (5):
- `id`: `PrefixedID!`
- `name`: `String`
- `online`: `Boolean`
- `uptime`: `Uptime`
- `version`: `String`

### `Settings` (OBJECT)
- Implements: `Node`
- Fields (4):
- `api`: `ApiConfig!`
  - The API setting values
- `id`: `PrefixedID!`
- `sso`: `SsoSettings!`
  - SSO settings
- `unified`: `UnifiedSettings!`
  - A view of all settings

### `Share` (OBJECT)
- Implements: `Node`
- Fields (16):
- `allocator`: `String`
  - Allocator
- `cache`: `Boolean`
  - Is this share cached
- `color`: `String`
  - Color
- `comment`: `String`
  - User comment
- `cow`: `String`
  - COW
- `exclude`: `[String!]`
  - Disks that are excluded from this share
- `floor`: `String`
  - Floor
- `free`: `BigInt`
  - (KB) Free space
- `id`: `PrefixedID!`
- `include`: `[String!]`
  - Disks that are included in this share
- `luksStatus`: `String`
  - LUKS status
- `name`: `String`
  - Display name
- `nameOrig`: `String`
  - Original name
- `size`: `BigInt`
  - (KB) Total size
- `splitLevel`: `String`
  - Split level
- `used`: `BigInt`
  - (KB) Used Size

### `SsoSettings` (OBJECT)
- Implements: `Node`
- Fields (2):
- `id`: `PrefixedID!`
- `oidcProviders`: `[OidcProvider!]!`
  - List of configured OIDC providers

### `String` (SCALAR)
The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

- Scalar type

### `Subscription` (OBJECT)
- Fields (11):
- `arraySubscription`: `UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `logFile`: `LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
  - Arguments:
    - `path`: `String!`
- `notificationAdded`: `Notification!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsOverview`: `NotificationOverview!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `ownerSubscription`: `Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistorySubscription`: `ParityCheck!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `serversSubscription`: `Server!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `systemMetricsCpu`: `CpuUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsCpuTelemetry`: `CpuPackages!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsMemory`: `MemoryUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `upsUpdates`: `UPSDevice!`

### `Temperature` (ENUM)
Temperature unit

- Enum values (2):
  - `CELSIUS`
  - `FAHRENHEIT`

### `Theme` (OBJECT)
- Fields (7):
- `headerBackgroundColor`: `String`
  - The background color of the header
- `headerPrimaryTextColor`: `String`
  - The text color of the header
- `headerSecondaryTextColor`: `String`
  - The secondary text color of the header
- `name`: `ThemeName!`
  - The theme name
- `showBannerGradient`: `Boolean!`
  - Whether to show the banner gradient
- `showBannerImage`: `Boolean!`
  - Whether to show the header banner image
- `showHeaderDescription`: `Boolean!`
  - Whether to show the description in the header

### `ThemeName` (ENUM)
The theme name

- Enum values (4):
  - `azure`
  - `black`
  - `gray`
  - `white`

### `UPSBattery` (OBJECT)
- Fields (3):
- `chargeLevel`: `Int!`
  - Battery charge level as a percentage (0-100). Unit: percent (%). Example: 100 means battery is fully charged
- `estimatedRuntime`: `Int!`
  - Estimated runtime remaining on battery power. Unit: seconds. Example: 3600 means 1 hour of runtime remaining
- `health`: `String!`
  - Battery health status. Possible values: 'Good', 'Replace', 'Unknown'. Indicates if the battery needs replacement

### `UPSCableType` (ENUM)
UPS cable connection types

- Enum values (5):
  - `CUSTOM`
  - `ETHER`
  - `SIMPLE`
  - `SMART`
  - `USB`

### `UPSConfigInput` (INPUT_OBJECT)
- Input fields (10):
- `batteryLevel`: `Int`
  - Battery level percentage to initiate shutdown. Unit: percent (%) - Valid range: 0-100
- `customUpsCable`: `String`
  - Custom cable configuration (only used when upsCable is CUSTOM). Format depends on specific UPS model
- `device`: `String`
  - Device path or network address for UPS connection. Examples: '/dev/ttyUSB0' for USB, '192.168.1.100:3551' for network
- `killUps`: `UPSKillPower`
  - Turn off UPS power after system shutdown. Useful for ensuring complete power cycle
- `minutes`: `Int`
  - Runtime left in minutes to initiate shutdown. Unit: minutes
- `overrideUpsCapacity`: `Int`
  - Override UPS capacity for runtime calculations. Unit: watts (W). Leave unset to use UPS-reported capacity
- `service`: `UPSServiceState`
  - Enable or disable the UPS monitoring service
- `timeout`: `Int`
  - Time on battery before shutdown. Unit: seconds. Set to 0 to disable timeout-based shutdown
- `upsCable`: `UPSCableType`
  - Type of cable connecting the UPS to the server
- `upsType`: `UPSType`
  - UPS communication protocol

### `UPSConfiguration` (OBJECT)
- Fields (14):
- `batteryLevel`: `Int`
  - Battery level threshold for shutdown. Unit: percent (%). Example: 10 means shutdown when battery reaches 10%. System will shutdown when battery drops to this level
- `customUpsCable`: `String`
  - Custom cable configuration string. Only used when upsCable is set to 'custom'. Format depends on specific UPS model
- `device`: `String`
  - Device path or network address for UPS connection. Examples: '/dev/ttyUSB0' for USB, '192.168.1.100:3551' for network. Depends on upsType setting
- `killUps`: `String`
  - Kill UPS power after shutdown. Values: 'yes' or 'no'. If 'yes', tells UPS to cut power after system shutdown. Useful for ensuring complete power cycle
- `minutes`: `Int`
  - Runtime threshold for shutdown. Unit: minutes. Example: 5 means shutdown when 5 minutes runtime remaining. System will shutdown when estimated runtime drops below this
- `modelName`: `String`
  - Override UPS model name. Used for display purposes. Leave unset to use UPS-reported model
- `netServer`: `String`
  - Network server mode. Values: 'on' or 'off'. Enable to allow network clients to monitor this UPS
- `nisIp`: `String`
  - Network Information Server (NIS) IP address. Default: '0.0.0.0' (listen on all interfaces). IP address for apcupsd network information server
- `overrideUpsCapacity`: `Int`
  - Override UPS capacity for runtime calculations. Unit: volt-amperes (VA). Example: 1500 for a 1500VA UPS. Leave unset to use UPS-reported capacity
- `service`: `String`
  - UPS service state. Values: 'enable' or 'disable'. Controls whether the UPS monitoring service is running
- `timeout`: `Int`
  - Timeout for UPS communications. Unit: seconds. Example: 0 means no timeout. Time to wait for UPS response before considering it offline
- `upsCable`: `String`
  - Type of cable connecting the UPS to the server. Common values: 'usb', 'smart', 'ether', 'custom'. Determines communication protocol
- `upsName`: `String`
  - UPS name for network monitoring. Used to identify this UPS on the network. Example: 'SERVER_UPS'
- `upsType`: `String`
  - UPS communication type. Common values: 'usb', 'net', 'snmp', 'dumb', 'pcnet', 'modbus'. Defines how the server communicates with the UPS

### `UPSDevice` (OBJECT)
- Fields (6):
- `battery`: `UPSBattery!`
  - Battery-related information
- `id`: `ID!`
  - Unique identifier for the UPS device. Usually based on the model name or a generated ID
- `model`: `String!`
  - UPS model name/number. Example: 'APC Back-UPS Pro 1500'
- `name`: `String!`
  - Display name for the UPS device. Can be customized by the user
- `power`: `UPSPower!`
  - Power-related information
- `status`: `String!`
  - Current operational status of the UPS. Common values: 'Online', 'On Battery', 'Low Battery', 'Replace Battery', 'Overload', 'Offline'. 'Online' means running on mains power, 'On Battery' means running on battery backup

### `UPSKillPower` (ENUM)
Kill UPS power after shutdown option

- Enum values (2):
  - `NO`
  - `YES`

### `UPSPower` (OBJECT)
- Fields (3):
- `inputVoltage`: `Float!`
  - Input voltage from the wall outlet/mains power. Unit: volts (V). Example: 120.5 for typical US household voltage
- `loadPercentage`: `Int!`
  - Current load on the UPS as a percentage of its capacity. Unit: percent (%). Example: 25 means UPS is loaded at 25% of its maximum capacity
- `outputVoltage`: `Float!`
  - Output voltage being delivered to connected devices. Unit: volts (V). Example: 120.5 - should match input voltage when on mains power

### `UPSServiceState` (ENUM)
Service state for UPS daemon

- Enum values (2):
  - `DISABLE`
  - `ENABLE`

### `UPSType` (ENUM)
UPS communication protocols

- Enum values (7):
  - `APCSMART`
  - `DUMB`
  - `MODBUS`
  - `NET`
  - `PCNET`
  - `SNMP`
  - `USB`

### `UnifiedSettings` (OBJECT)
- Implements: `FormSchema`, `Node`
- Fields (4):
- `dataSchema`: `JSON!`
  - The data schema for the settings
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
  - The UI schema for the settings
- `values`: `JSON!`
  - The current values of the settings

### `UnraidArray` (OBJECT)
- Implements: `Node`
- Fields (8):
- `boot`: `ArrayDisk`
  - Current boot disk
- `caches`: `[ArrayDisk!]!`
  - Caches in the current array
- `capacity`: `ArrayCapacity!`
  - Current array capacity
- `disks`: `[ArrayDisk!]!`
  - Data disks in the current array
- `id`: `PrefixedID!`
- `parities`: `[ArrayDisk!]!`
  - Parity disks in the current array
- `parityCheckStatus`: `ParityCheck!`
  - Current parity check status
- `state`: `ArrayState!`
  - Current array state

### `UpdateApiKeyInput` (INPUT_OBJECT)
- Input fields (5):
- `description`: `String`
- `id`: `PrefixedID!`
- `name`: `String`
- `permissions`: `[AddPermissionInput!]`
- `roles`: `[Role!]`

### `UpdateSettingsResponse` (OBJECT)
- Fields (3):
- `restartRequired`: `Boolean!`
  - Whether a restart is required for the changes to take effect
- `values`: `JSON!`
  - The updated settings values
- `warnings`: `[String!]`
  - Warning messages about configuration issues found during validation

### `UpdateStatus` (ENUM)
Update status of a container.

- Enum values (4):
  - `REBUILD_READY`
  - `UNKNOWN`
  - `UPDATE_AVAILABLE`
  - `UP_TO_DATE`

### `Uptime` (OBJECT)
- Fields (1):
- `timestamp`: `String`

### `UserAccount` (OBJECT)
- Implements: `Node`
- Fields (5):
- `description`: `String!`
  - A description of the user
- `id`: `PrefixedID!`
- `name`: `String!`
  - The name of the user
- `permissions`: `[Permission!]`
  - The permissions of the user
- `roles`: `[Role!]!`
  - The roles of the user

### `Vars` (OBJECT)
- Implements: `Node`
- Fields (143):
- `bindMgt`: `Boolean`
- `cacheNumDevices`: `Int`
- `cacheSbNumDisks`: `Int`
- `comment`: `String`
- `configError`: `ConfigErrorState`
- `configValid`: `Boolean`
- `csrfToken`: `String`
- `defaultFormat`: `String`
- `defaultFsType`: `String`
- `deviceCount`: `Int`
- `domain`: `String`
- `domainLogin`: `String`
- `domainShort`: `String`
- `enableFruit`: `String`
- `flashGuid`: `String`
- `flashProduct`: `String`
- `flashVendor`: `String`
- `fsCopyPrcnt`: `Int`
  - Percentage from 0 - 100 while upgrading a disk or swapping parity drives
- `fsNumMounted`: `Int`
- `fsNumUnmountable`: `Int`
- `fsProgress`: `String`
  - Human friendly string of array events happening
- `fsState`: `String`
- `fsUnmountableMask`: `String`
- `fuseDirectio`: `String`
- `fuseDirectioDefault`: `String`
- `fuseDirectioStatus`: `String`
- `fuseRemember`: `String`
- `fuseRememberDefault`: `String`
- `fuseRememberStatus`: `String`
- `hideDotFiles`: `Boolean`
- `id`: `PrefixedID!`
- `joinStatus`: `String`
- `localMaster`: `Boolean`
- `localTld`: `String`
- `luksKeyfile`: `String`
- `maxArraysz`: `Int`
- `maxCachesz`: `Int`
- `mdColor`: `String`
- `mdNumDisabled`: `Int`
- `mdNumDisks`: `Int`
- `mdNumErased`: `Int`
- `mdNumInvalid`: `Int`
- `mdNumMissing`: `Int`
- `mdNumNew`: `Int`
- `mdNumStripes`: `Int`
- `mdNumStripesDefault`: `Int`
- `mdNumStripesStatus`: `String`
- `mdResync`: `Int`
- `mdResyncAction`: `String`
- `mdResyncCorr`: `String`
- `mdResyncDb`: `String`
- `mdResyncDt`: `String`
- `mdResyncPos`: `String`
- `mdResyncSize`: `Int`
- `mdState`: `String`
- `mdSyncThresh`: `Int`
- `mdSyncThreshDefault`: `Int`
- `mdSyncThreshStatus`: `String`
- `mdSyncWindow`: `Int`
- `mdSyncWindowDefault`: `Int`
- `mdSyncWindowStatus`: `String`
- `mdVersion`: `String`
- `mdWriteMethod`: `Int`
- `mdWriteMethodDefault`: `String`
- `mdWriteMethodStatus`: `String`
- `name`: `String`
  - Machine hostname
- `nrRequests`: `Int`
- `nrRequestsDefault`: `Int`
- `nrRequestsStatus`: `String`
- `ntpServer1`: `String`
  - NTP Server 1
- `ntpServer2`: `String`
  - NTP Server 2
- `ntpServer3`: `String`
  - NTP Server 3
- `ntpServer4`: `String`
  - NTP Server 4
- `pollAttributes`: `String`
- `pollAttributesDefault`: `String`
- `pollAttributesStatus`: `String`
- `port`: `Int`
  - Port for the webui via HTTP
- `portssh`: `Int`
- `portssl`: `Int`
  - Port for the webui via HTTPS
- `porttelnet`: `Int`
- `queueDepth`: `String`
- `regCheck`: `String`
- `regFile`: `String`
- `regGen`: `String`
- `regGuid`: `String`
- `regState`: `RegistrationState`
- `regTm`: `String`
- `regTm2`: `String`
- `regTo`: `String`
  - Registration owner
- `regTy`: `registrationType`
- `safeMode`: `Boolean`
- `sbClean`: `Boolean`
- `sbEvents`: `Int`
- `sbName`: `String`
- `sbNumDisks`: `Int`
- `sbState`: `String`
- `sbSyncErrs`: `Int`
- `sbSyncExit`: `String`
- `sbSynced`: `Int`
- `sbSynced2`: `Int`
- `sbUpdated`: `String`
- `sbVersion`: `String`
- `security`: `String`
- `shareAfpCount`: `Int`
  - Total amount shares with AFP enabled
- `shareAfpEnabled`: `Boolean`
- `shareAvahiAfpModel`: `String`
- `shareAvahiAfpName`: `String`
- `shareAvahiEnabled`: `Boolean`
- `shareAvahiSmbModel`: `String`
- `shareAvahiSmbName`: `String`
- `shareCacheEnabled`: `Boolean`
- `shareCacheFloor`: `String`
- `shareCount`: `Int`
  - Total amount of user shares
- `shareDisk`: `String`
- `shareInitialGroup`: `String`
- `shareInitialOwner`: `String`
- `shareMoverActive`: `Boolean`
- `shareMoverLogging`: `Boolean`
- `shareMoverSchedule`: `String`
- `shareNfsCount`: `Int`
  - Total amount shares with NFS enabled
- `shareNfsEnabled`: `Boolean`
- `shareSmbCount`: `Int`
  - Total amount shares with SMB enabled
- `shareSmbEnabled`: `Boolean`
- `shareUser`: `String`
- `shareUserExclude`: `String`
- `shareUserInclude`: `String`
- `shutdownTimeout`: `Int`
- `spindownDelay`: `String`
- `spinupGroups`: `Boolean`
- `startArray`: `Boolean`
- `startMode`: `String`
- `startPage`: `String`
- `sysArraySlots`: `Int`
- `sysCacheSlots`: `Int`
- `sysFlashSlots`: `Int`
- `sysModel`: `String`
- `timeZone`: `String`
- `useNtp`: `Boolean`
  - Should a NTP server be used for time sync?
- `useSsh`: `Boolean`
- `useSsl`: `Boolean`
- `useTelnet`: `Boolean`
  - Should telnet be enabled?
- `version`: `String`
  - Unraid version
- `workgroup`: `String`

### `VmDomain` (OBJECT)
- Implements: `Node`
- Fields (4):
- `id`: `PrefixedID!`
  - The unique identifier for the vm (uuid)
- `name`: `String`
  - A friendly name for the vm
- `state`: `VmState!`
  - Current domain vm state
- `uuid`: `String`
  - The UUID of the vm
  - Deprecated: Use id instead

### `VmMutations` (OBJECT)
- Fields (7):
- `forceStop`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Force stop a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `pause`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Pause a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `reboot`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Reboot a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `reset`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Reset a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `resume`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Resume a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `start`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Start a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`
- `stop`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VMS** #### Description: Stop a virtual machine
  - Arguments:
    - `id`: `PrefixedID!`

### `VmState` (ENUM)
The state of a virtual machine

- Enum values (8):
  - `CRASHED`
  - `IDLE`
  - `NOSTATE`
  - `PAUSED`
  - `PMSUSPENDED`
  - `RUNNING`
  - `SHUTDOWN`
  - `SHUTOFF`

### `Vms` (OBJECT)
- Implements: `Node`
- Fields (3):
- `domain`: `[VmDomain!]`
- `domains`: `[VmDomain!]`
- `id`: `PrefixedID!`

### `registrationType` (ENUM)
- Enum values (8):
  - `BASIC`
  - `INVALID`
  - `LIFETIME`
  - `PLUS`
  - `PRO`
  - `STARTER`
  - `TRIAL`
  - `UNLEASHED`
