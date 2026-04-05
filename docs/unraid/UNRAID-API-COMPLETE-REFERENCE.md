# Unraid GraphQL API Complete Schema Reference

> Generated from live GraphQL introspection on 2026-04-05T12:03:27+00:00
> Source: https://10-1-0-2.95d289568cc4a4bdc8e0d50284d6f455ec0eae5f.myunraid.net:31337/graphql

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
- Total types: **239**
- Total directives: **6**
- Type kinds:
- `ENUM`: 40
- `INPUT_OBJECT`: 43
- `INTERFACE`: 2
- `OBJECT`: 143
- `SCALAR`: 11

## Root Operations
### Queries
Total fields: **57**

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
- `assignableDisks(): [Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `cloud(): Cloud!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CLOUD**
- `config(): Config!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
- `connect(): Connect!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONNECT**
- `customization(): Customization`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS**
- `disk(id: PrefixedID!): Disk!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `disks(): [Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `display(): InfoDisplay!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISPLAY**
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
- `installedUnraidPlugins(): [String!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List installed Unraid OS plugins by .plg filename
- `internalBootContext(): OnboardingInternalBootContext!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **WELCOME** #### Description: Get the latest onboarding context for configuring internal boot
- `isFreshInstall(): Boolean!`
  - Whether the system is a fresh install (no license key)
- `isSSOEnabled(): Boolean!`
- `logFile(lines: Int, path: String!, startLine: Int): LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `logFiles(): [LogFile!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `me(): UserAccount!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ME**
- `metrics(): Metrics!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `network(): Network!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NETWORK**
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
- `pluginInstallOperation(operationId: ID!): PluginInstallOperation`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Retrieve a plugin installation operation by identifier
- `pluginInstallOperations(): [PluginInstallOperation!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all tracked plugin installation operations
- `plugins(): [Plugin!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all installed plugins with their metadata
- `previewEffectivePermissions(permissions: [AddPermissionInput!], roles: [Role!]): [Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Preview the effective permissions for a combination of roles and explicit permissions
- `publicOidcProviders(): [PublicOidcProvider!]!`
  - Get public OIDC provider information for login buttons
- `publicTheme(): Theme!`
- `rclone(): RCloneBackupSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `registration(): Registration`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **REGISTRATION**
- `remoteAccess(): RemoteAccess!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONNECT**
- `server(): Server`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `servers(): [Server!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `services(): [Service!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVICES**
- `settings(): Settings!`
- `shares(): [Share!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SHARE**
- `systemTime(): SystemTime!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VARS** #### Description: Retrieve current system time configuration
- `timeZoneOptions(): [TimeZoneOption!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Retrieve available time zone options
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
Total fields: **45**

- `addPlugin(input: PluginManagementInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Add one or more plugins to the API. Returns false if restart was triggered automatically, true if manual restart is required.
- `apiKey(): ApiKeyMutations!`
- `archiveAll(importance: NotificationImportance): NotificationOverview!`
- `archiveNotification(id: PrefixedID!): Notification!`
  - Marks a notification as archived.
- `archiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
- `array(): ArrayMutations!`
- `configureUps(config: UPSConfigInput!): Boolean!`
- `connectSignIn(input: ConnectSignInInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
- `connectSignOut(): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
- `createDockerFolder(childrenIds: [String!], name: String!, parentId: String): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `createDockerFolderWithItems(name: String!, parentId: String, position: Float, sourceEntryIds: [String!]): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `createNotification(input: NotificationData!): Notification!`
  - Creates a new notification record
- `customization(): CustomizationMutations!`
- `deleteArchivedNotifications(): NotificationOverview!`
  - Deletes all archived notifications on server.
- `deleteDockerEntries(entryIds: [String!]!): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `deleteNotification(id: PrefixedID!, type: NotificationType!): NotificationOverview!`
- `docker(): DockerMutations!`
- `enableDynamicRemoteAccess(input: EnableDynamicRemoteAccessInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT__REMOTE_ACCESS**
- `initiateFlashBackup(input: InitiateFlashBackupInput!): FlashBackupStatus!`
  - Initiates a flash drive backup using a configured remote.
- `moveDockerEntriesToFolder(destinationFolderId: String!, sourceEntryIds: [String!]!): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `moveDockerItemsToPosition(destinationFolderId: String!, position: Float!, sourceEntryIds: [String!]!): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `notifyIfUnique(input: NotificationData!): Notification`
  - Creates a notification if an equivalent unread notification does not already exist.
- `onboarding(): OnboardingMutations!`
- `parityCheck(): ParityCheckMutations!`
- `rclone(): RCloneMutations!`
- `recalculateOverview(): NotificationOverview!`
  - Reads each notification to recompute & update the overview.
- `refreshDockerDigests(): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `removePlugin(input: PluginManagementInput!): Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **CONFIG** #### Description: Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required.
- `renameDockerFolder(folderId: String!, newName: String!): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `resetDockerTemplateMappings(): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Reset Docker template mappings to defaults. Use this to recover from corrupted state.
- `setDockerFolderChildren(childrenIds: [String!]!, folderId: String): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `setupRemoteAccess(input: SetupRemoteAccessInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
- `syncDockerTemplatePaths(): DockerTemplateSyncResult!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `unarchiveAll(importance: NotificationImportance): NotificationOverview!`
- `unarchiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
- `unraidPlugins(): UnraidPluginsMutations!`
- `unreadNotification(id: PrefixedID!): Notification!`
  - Marks a notification as unread.
- `updateApiSettings(input: ConnectSettingsInput!): ConnectSettingsValues!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
- `updateDockerViewPreferences(prefs: JSON!, viewId: String = "default"): ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `updateServerIdentity(comment: String, name: String!, sysModel: String): Server!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **SERVERS** #### Description: Update server name, comment, and model
- `updateSettings(input: JSON!): UpdateSettingsResponse!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
- `updateSshSettings(input: UpdateSshInput!): Vars!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VARS**
- `updateSystemTime(input: UpdateSystemTimeInput!): SystemTime!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Update system time configuration
- `updateTemperatureConfig(input: TemperatureConfigInput!): Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **INFO**
- `vm(): VmMutations!`

### Subscriptions
Total fields: **16**

- `arraySubscription(): UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `displaySubscription(): InfoDisplay!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISPLAY**
- `dockerContainerStats(): DockerContainerStats!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `logFile(path: String!): LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
- `notificationAdded(): Notification!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsOverview(): NotificationOverview!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsWarningsAndAlerts(): [Notification!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `ownerSubscription(): Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistorySubscription(): ParityCheck!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `pluginInstallUpdates(operationId: ID!): PluginInstallEvent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
- `serversSubscription(): Server!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `systemMetricsCpu(): CpuUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsCpuTelemetry(): CpuPackages!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsMemory(): MemoryUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsTemperature(): TemperatureMetrics`
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
### `AccessUrl` (OBJECT)
- Fields (4):
- `ipv4`: `URL`
- `ipv6`: `URL`
- `name`: `String`
- `type`: `URL_TYPE!`

### `AccessUrlInput` (INPUT_OBJECT)
- Input fields (4):
- `ipv4`: `URL`
- `ipv6`: `URL`
- `name`: `String`
- `type`: `URL_TYPE!`

### `AccessUrlObject` (OBJECT)
- Fields (4):
- `ipv4`: `String`
- `ipv6`: `String`
- `name`: `String`
- `type`: `URL_TYPE!`

### `AccessUrlObjectInput` (INPUT_OBJECT)
- Input fields (4):
- `ipv4`: `String`
- `ipv6`: `String`
- `name`: `String`
- `type`: `URL_TYPE!`

### `ActivationCode` (OBJECT)
- Fields (4):
- `branding`: `BrandingConfig`
- `code`: `String`
- `partner`: `PartnerConfig`
- `system`: `SystemConfig`

### `ActivationCodeOverrideInput` (INPUT_OBJECT)
Activation code override input

- Input fields (4):
- `branding`: `BrandingConfigInput`
- `code`: `String`
- `partner`: `PartnerConfigInput`
- `system`: `SystemConfigInput`

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

### `ApiKeyResponse` (OBJECT)
- Fields (2):
- `error`: `String`
- `valid`: `Boolean!`

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
  - Type of Disk - used to differentiate Boot / Cache / Flash / Data (DATA) / Parity
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
- Enum values (5):
  - `BOOT`
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
- Input fields (3):
- `decryptionKeyfile`: `String`
  - Optional keyfile contents used to unlock encrypted array disks when starting the array. Accepts a data URL or raw base64 payload.
- `decryptionPassword`: `String`
  - Optional password used to unlock encrypted array disks when starting the array
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

### `BrandingConfig` (OBJECT)
- Fields (21):
- `background`: `String`
- `bannerImage`: `String`
  - Banner image source. Supports local path, remote URL, or data URI/base64.
- `caseModel`: `String`
  - Built-in case model value written to case-model.cfg when no custom override is supplied.
- `caseModelImage`: `String`
  - Case model image source. Supports local path, remote URL, or data URI/base64.
- `hasPartnerLogo`: `Boolean`
  - Indicates if a partner logo exists
- `header`: `String`
- `headermetacolor`: `String`
- `onboardingSubtitle`: `String`
  - Custom subtitle for onboarding welcome step
- `onboardingSubtitleDowngrade`: `String`
  - Custom subtitle for downgrade onboarding
- `onboardingSubtitleFreshInstall`: `String`
  - Custom subtitle for fresh install onboarding
- `onboardingSubtitleIncomplete`: `String`
  - Custom subtitle for incomplete onboarding
- `onboardingSubtitleUpgrade`: `String`
  - Custom subtitle for upgrade onboarding
- `onboardingTitle`: `String`
  - Custom title for onboarding welcome step
- `onboardingTitleDowngrade`: `String`
  - Custom title for downgrade onboarding
- `onboardingTitleFreshInstall`: `String`
  - Custom title for fresh install onboarding
- `onboardingTitleIncomplete`: `String`
  - Custom title for incomplete onboarding
- `onboardingTitleUpgrade`: `String`
  - Custom title for upgrade onboarding
- `partnerLogoDarkUrl`: `String`
  - Partner logo source for dark themes (black/gray). Supports local path, remote URL, or data URI/base64.
- `partnerLogoLightUrl`: `String`
  - Partner logo source for light themes (azure/white). Supports local path, remote URL, or data URI/base64.
- `showBannerGradient`: `Boolean`
- `theme`: `String`

### `BrandingConfigInput` (INPUT_OBJECT)
- Input fields (21):
- `background`: `String`
- `bannerImage`: `String`
- `caseModel`: `String`
- `caseModelImage`: `String`
- `hasPartnerLogo`: `Boolean`
- `header`: `String`
- `headermetacolor`: `String`
- `onboardingSubtitle`: `String`
- `onboardingSubtitleDowngrade`: `String`
- `onboardingSubtitleFreshInstall`: `String`
- `onboardingSubtitleIncomplete`: `String`
- `onboardingSubtitleUpgrade`: `String`
- `onboardingTitle`: `String`
- `onboardingTitleDowngrade`: `String`
- `onboardingTitleFreshInstall`: `String`
- `onboardingTitleIncomplete`: `String`
- `onboardingTitleUpgrade`: `String`
- `partnerLogoDarkUrl`: `String`
- `partnerLogoLightUrl`: `String`
- `showBannerGradient`: `Boolean`
- `theme`: `String`

### `Capacity` (OBJECT)
- Fields (3):
- `free`: `String!`
  - Free capacity
- `total`: `String!`
  - Total capacity
- `used`: `String!`
  - Used capacity

### `Cloud` (OBJECT)
- Fields (6):
- `allowedOrigins`: `[String!]!`
- `apiKey`: `ApiKeyResponse!`
- `cloud`: `CloudResponse!`
- `error`: `String`
- `minigraphql`: `MinigraphqlResponse!`
- `relay`: `RelayResponse`

### `CloudResponse` (OBJECT)
- Fields (3):
- `error`: `String`
- `ip`: `String`
- `status`: `String!`

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

### `Connect` (OBJECT)
- Implements: `Node`
- Fields (3):
- `dynamicRemoteAccess`: `DynamicRemoteAccessStatus!`
  - The status of dynamic remote access
- `id`: `PrefixedID!`
- `settings`: `ConnectSettings!`
  - The settings for the Connect instance

### `ConnectSettings` (OBJECT)
- Implements: `Node`
- Fields (4):
- `dataSchema`: `JSON!`
  - The data schema for the Connect settings
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
  - The UI schema for the Connect settings
- `values`: `ConnectSettingsValues!`
  - The values for the Connect settings

### `ConnectSettingsInput` (INPUT_OBJECT)
- Input fields (3):
- `accessType`: `WAN_ACCESS_TYPE`
  - The type of WAN access to use for Remote Access
- `forwardType`: `WAN_FORWARD_TYPE`
  - The type of port forwarding to use for Remote Access
- `port`: `Int`
  - The port to use for Remote Access. Not required for UPNP forwardType. Required for STATIC forwardType. Ignored if accessType is DISABLED or forwardType is UPNP.

### `ConnectSettingsValues` (OBJECT)
- Fields (3):
- `accessType`: `WAN_ACCESS_TYPE!`
  - The type of WAN access used for Remote Access
- `forwardType`: `WAN_FORWARD_TYPE`
  - The type of port forwarding used for Remote Access
- `port`: `Int`
  - The port used for Remote Access

### `ConnectSignInInput` (INPUT_OBJECT)
- Input fields (2):
- `apiKey`: `String!`
  - The API key for authentication
- `userInfo`: `ConnectUserInfoInput`
  - User information for the sign-in

### `ConnectUserInfoInput` (INPUT_OBJECT)
- Input fields (3):
- `avatar`: `String`
  - The avatar URL of the user
- `email`: `String!`
  - The email address of the user
- `preferred_username`: `String!`
  - The preferred username of the user

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
- Enum values (3):
  - `EXITED`
  - `PAUSED`
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

### `CreateInternalBootPoolInput` (INPUT_OBJECT)
Input for creating an internal boot pool during onboarding

- Input fields (5):
- `bootSizeMiB`: `Int!`
- `devices`: `[String!]!`
- `poolName`: `String!`
- `reboot`: `Boolean`
- `updateBios`: `Boolean!`

### `CreateRCloneRemoteInput` (INPUT_OBJECT)
- Input fields (3):
- `name`: `String!`
- `parameters`: `JSON!`
- `type`: `String!`

### `Customization` (OBJECT)
- Fields (3):
- `activationCode`: `ActivationCode`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ACTIVATION_CODE**
- `availableLanguages`: `[Language!]`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISPLAY**
- `onboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS** #### Description: Onboarding completion state and context

### `CustomizationMutations` (OBJECT)
Customization related mutations

- Fields (2):
- `setLocale`: `String!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CUSTOMIZATIONS** #### Description: Update the display locale (language)
  - Arguments:
    - `locale`: `String!`
      - Locale code to apply (e.g. en_US)
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
- Fields (8):
- `container`: `DockerContainer`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
  - Arguments:
    - `id`: `PrefixedID!`
- `containerUpdateStatuses`: `[ExplicitStatusItem!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `containers`: `[DockerContainer!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `id`: `PrefixedID!`
- `logs`: `DockerContainerLogs!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Access container logs. Requires specifying a target container id through resolver arguments.
  - Arguments:
    - `id`: `PrefixedID!`
    - `since`: `DateTime`
    - `tail`: `Int`
- `networks`: `[DockerNetwork!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `organizer`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `portConflicts`: `DockerPortConflicts!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**

### `DockerAutostartEntryInput` (INPUT_OBJECT)
- Input fields (3):
- `autoStart`: `Boolean!`
  - Whether the container should auto-start
- `id`: `PrefixedID!`
  - Docker container identifier
- `wait`: `Int`
  - Number of seconds to wait after starting the container

### `DockerContainer` (OBJECT)
- Implements: `Node`
- Fields (33):
- `autoStart`: `Boolean!`
- `autoStartOrder`: `Int`
  - Zero-based order in the auto-start list
- `autoStartWait`: `Int`
  - Wait time in seconds applied after start
- `command`: `String!`
- `created`: `Int!`
- `hostConfig`: `ContainerHostConfig`
- `iconUrl`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Icon URL
- `id`: `PrefixedID!`
- `image`: `String!`
- `imageId`: `String!`
- `isOrphaned`: `Boolean!`
  - Whether the container is orphaned (no template found)
- `isRebuildReady`: `Boolean`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `isUpdateAvailable`: `Boolean`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `labels`: `JSON`
- `lanIpPorts`: `[String!]`
  - List of LAN-accessible host:port values
- `mounts`: `[JSON!]`
- `names`: `[String!]!`
- `networkSettings`: `JSON`
- `ports`: `[ContainerPort!]!`
- `projectUrl`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Project/Product homepage URL
- `registryUrl`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Registry/Docker Hub URL
- `shell`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Shell to use for console access (from template)
- `sizeLog`: `BigInt`
  - Size of container logs (in bytes)
- `sizeRootFs`: `BigInt`
  - Total size of all files in the container (in bytes)
- `sizeRw`: `BigInt`
  - Size of writable layer (in bytes)
- `state`: `ContainerState!`
- `status`: `String!`
- `supportUrl`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Support page/thread URL
- `tailscaleEnabled`: `Boolean!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Whether Tailscale is enabled for this container
- `tailscaleStatus`: `TailscaleStatus`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Tailscale status for this container (fetched via docker exec)
  - Arguments:
    - `forceRefresh`: `Boolean` (default: `false`)
- `templatePath`: `String`
- `templatePorts`: `[ContainerPort!]`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Port mappings from template (used when container is not running)
- `webUiUrl`: `String`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER** #### Description: Resolved WebUI URL from template

### `DockerContainerLogLine` (OBJECT)
- Fields (2):
- `message`: `String!`
- `timestamp`: `DateTime!`

### `DockerContainerLogs` (OBJECT)
- Fields (3):
- `containerId`: `PrefixedID!`
- `cursor`: `DateTime`
  - Cursor that can be passed back through the since argument to continue streaming logs.
- `lines`: `[DockerContainerLogLine!]!`

### `DockerContainerPortConflict` (OBJECT)
- Fields (3):
- `containers`: `[DockerPortConflictContainer!]!`
- `privatePort`: `Port!`
- `type`: `ContainerPortType!`

### `DockerContainerStats` (OBJECT)
- Fields (6):
- `blockIO`: `String!`
  - Block I/O String (e.g. 100MB / 1GB)
- `cpuPercent`: `Float!`
  - CPU Usage Percentage
- `id`: `PrefixedID!`
- `memPercent`: `Float!`
  - Memory Usage Percentage
- `memUsage`: `String!`
  - Memory Usage String (e.g. 100MB / 1GB)
- `netIO`: `String!`
  - Network I/O String (e.g. 100MB / 1GB)

### `DockerLanPortConflict` (OBJECT)
- Fields (4):
- `containers`: `[DockerPortConflictContainer!]!`
- `lanIpPort`: `String!`
- `publicPort`: `Port`
- `type`: `ContainerPortType!`

### `DockerMutations` (OBJECT)
- Fields (9):
- `pause`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Pause (Suspend) a container
  - Arguments:
    - `id`: `PrefixedID!`
- `removeContainer`: `Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **DOCKER** #### Description: Remove a container
  - Arguments:
    - `id`: `PrefixedID!`
    - `withImage`: `Boolean`
- `start`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Start a container
  - Arguments:
    - `id`: `PrefixedID!`
- `stop`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Stop a container
  - Arguments:
    - `id`: `PrefixedID!`
- `unpause`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Unpause (Resume) a container
  - Arguments:
    - `id`: `PrefixedID!`
- `updateAllContainers`: `[DockerContainer!]!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Update all containers that have available updates
- `updateAutostartConfiguration`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Update auto-start configuration for Docker containers
  - Arguments:
    - `entries`: `[DockerAutostartEntryInput!]!`
    - `persistUserPreferences`: `Boolean`
- `updateContainer`: `DockerContainer!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Update a container to the latest image
  - Arguments:
    - `id`: `PrefixedID!`
- `updateContainers`: `[DockerContainer!]!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Update multiple containers to the latest images
  - Arguments:
    - `ids`: `[PrefixedID!]!`

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

### `DockerPortConflictContainer` (OBJECT)
- Fields (2):
- `id`: `PrefixedID!`
- `name`: `String!`

### `DockerPortConflicts` (OBJECT)
- Fields (2):
- `containerPorts`: `[DockerContainerPortConflict!]!`
- `lanPorts`: `[DockerLanPortConflict!]!`

### `DockerTemplateSyncResult` (OBJECT)
- Fields (4):
- `errors`: `[String!]!`
- `matched`: `Int!`
- `scanned`: `Int!`
- `skipped`: `Int!`

### `DynamicRemoteAccessStatus` (OBJECT)
- Fields (3):
- `enabledType`: `DynamicRemoteAccessType!`
  - The type of dynamic remote access that is enabled
- `error`: `String`
  - Any error message associated with the dynamic remote access
- `runningType`: `DynamicRemoteAccessType!`
  - The type of dynamic remote access that is currently running

### `DynamicRemoteAccessType` (ENUM)
- Enum values (3):
  - `DISABLED`
  - `STATIC`
  - `UPNP`

### `EnableDynamicRemoteAccessInput` (INPUT_OBJECT)
- Input fields (2):
- `enabled`: `Boolean!`
  - Whether to enable or disable dynamic remote access
- `url`: `AccessUrlInput!`
  - The AccessURL Input for dynamic remote access

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

### `FlatOrganizerEntry` (OBJECT)
- Fields (10):
- `childrenIds`: `[String!]!`
- `depth`: `Float!`
- `hasChildren`: `Boolean!`
- `id`: `String!`
- `meta`: `DockerContainer`
- `name`: `String!`
- `parentId`: `String`
- `path`: `[String!]!`
- `position`: `Float!`
- `type`: `String!`

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
- Fields (13):
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
- `networkInterfaces`: `[InfoNetworkInterface!]!`
  - Network interfaces
- `os`: `InfoOs!`
  - Operating system information
- `primaryNetwork`: `InfoNetworkInterface`
  - Primary management interface
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

### `InfoNetworkInterface` (OBJECT)
- Implements: `Node`
- Fields (14):
- `description`: `String`
  - Interface description/label
- `gateway`: `String`
  - IPv4 Gateway
- `id`: `PrefixedID!`
- `ipAddress`: `String`
  - IPv4 Address
- `ipv6Address`: `String`
  - IPv6 Address
- `ipv6Gateway`: `String`
  - IPv6 Gateway
- `ipv6Netmask`: `String`
  - IPv6 Netmask
- `macAddress`: `String`
  - MAC Address
- `name`: `String!`
  - Interface name (e.g. eth0)
- `netmask`: `String`
  - IPv4 Netmask
- `protocol`: `String`
  - IPv4 Protocol mode
- `status`: `String`
  - Connection status
- `useDhcp`: `Boolean`
  - Using DHCP for IPv4
- `useDhcp6`: `Boolean`
  - Using DHCP for IPv6

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

### `InstallPluginInput` (INPUT_OBJECT)
Input payload for installing a plugin

- Input fields (3):
- `forced`: `Boolean`
  - Force installation even when plugin is already present. Defaults to true to mirror the existing UI behaviour.
- `name`: `String`
  - Optional human-readable plugin name used for logging
- `url`: `String!`
  - Plugin installation URL (.plg)

### `Int` (SCALAR)
The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.

- Scalar type

### `IpmiConfig` (OBJECT)
- Fields (2):
- `args`: `[String!]`
- `enabled`: `Boolean`

### `IpmiConfigInput` (INPUT_OBJECT)
- Input fields (2):
- `args`: `[String!]`
- `enabled`: `Boolean`

### `JSON` (SCALAR)
The `JSON` scalar type represents JSON values as specified by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

- Scalar type

### `KeyFile` (OBJECT)
- Fields (2):
- `contents`: `String`
- `location`: `String`

### `Language` (OBJECT)
- Fields (3):
- `code`: `String!`
  - Language code (e.g. en_US)
- `name`: `String!`
  - Language description/name
- `url`: `String`
  - URL to the language pack XML

### `LmSensorsConfig` (OBJECT)
- Fields (2):
- `config_path`: `String`
- `enabled`: `Boolean`

### `LmSensorsConfigInput` (INPUT_OBJECT)
- Input fields (2):
- `config_path`: `String`
- `enabled`: `Boolean`

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
- Fields (4):
- `cpu`: `CpuUtilization`
  - Current CPU utilization metrics
- `id`: `PrefixedID!`
- `memory`: `MemoryUtilization`
  - Current memory utilization metrics
- `temperature`: `TemperatureMetrics`
  - Temperature metrics

### `MinigraphStatus` (ENUM)
The status of the minigraph

- Enum values (5):
  - `CONNECTED`
  - `CONNECTING`
  - `ERROR_RETRYING`
  - `PING_FAILURE`
  - `PRE_INIT`

### `MinigraphqlResponse` (OBJECT)
- Fields (3):
- `error`: `String`
- `status`: `MinigraphStatus!`
- `timeout`: `Int`

### `Mutation` (OBJECT)
- Fields (45):
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
- `connectSignIn`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
  - Arguments:
    - `input`: `ConnectSignInInput!`
- `connectSignOut`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
- `createDockerFolder`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `childrenIds`: `[String!]`
    - `name`: `String!`
    - `parentId`: `String`
- `createDockerFolderWithItems`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `name`: `String!`
    - `parentId`: `String`
    - `position`: `Float`
    - `sourceEntryIds`: `[String!]`
- `createNotification`: `Notification!`
  - Creates a new notification record
  - Arguments:
    - `input`: `NotificationData!`
- `customization`: `CustomizationMutations!`
- `deleteArchivedNotifications`: `NotificationOverview!`
  - Deletes all archived notifications on server.
- `deleteDockerEntries`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `entryIds`: `[String!]!`
- `deleteNotification`: `NotificationOverview!`
  - Arguments:
    - `id`: `PrefixedID!`
    - `type`: `NotificationType!`
- `docker`: `DockerMutations!`
- `enableDynamicRemoteAccess`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT__REMOTE_ACCESS**
  - Arguments:
    - `input`: `EnableDynamicRemoteAccessInput!`
- `initiateFlashBackup`: `FlashBackupStatus!`
  - Initiates a flash drive backup using a configured remote.
  - Arguments:
    - `input`: `InitiateFlashBackupInput!`
- `moveDockerEntriesToFolder`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `destinationFolderId`: `String!`
    - `sourceEntryIds`: `[String!]!`
- `moveDockerItemsToPosition`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `destinationFolderId`: `String!`
    - `position`: `Float!`
    - `sourceEntryIds`: `[String!]!`
- `notifyIfUnique`: `Notification`
  - Creates a notification if an equivalent unread notification does not already exist.
  - Arguments:
    - `input`: `NotificationData!`
- `onboarding`: `OnboardingMutations!`
- `parityCheck`: `ParityCheckMutations!`
- `rclone`: `RCloneMutations!`
- `recalculateOverview`: `NotificationOverview!`
  - Reads each notification to recompute & update the overview.
- `refreshDockerDigests`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `removePlugin`: `Boolean!`
  - #### Required Permissions: - Action: **DELETE_ANY** - Resource: **CONFIG** #### Description: Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required.
  - Arguments:
    - `input`: `PluginManagementInput!`
- `renameDockerFolder`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `folderId`: `String!`
    - `newName`: `String!`
- `resetDockerTemplateMappings`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER** #### Description: Reset Docker template mappings to defaults. Use this to recover from corrupted state.
- `setDockerFolderChildren`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `childrenIds`: `[String!]!`
    - `folderId`: `String`
- `setupRemoteAccess`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONNECT**
  - Arguments:
    - `input`: `SetupRemoteAccessInput!`
- `syncDockerTemplatePaths`: `DockerTemplateSyncResult!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
- `unarchiveAll`: `NotificationOverview!`
  - Arguments:
    - `importance`: `NotificationImportance`
- `unarchiveNotifications`: `NotificationOverview!`
  - Arguments:
    - `ids`: `[PrefixedID!]!`
- `unraidPlugins`: `UnraidPluginsMutations!`
- `unreadNotification`: `Notification!`
  - Marks a notification as unread.
  - Arguments:
    - `id`: `PrefixedID!`
- `updateApiSettings`: `ConnectSettingsValues!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
  - Arguments:
    - `input`: `ConnectSettingsInput!`
- `updateDockerViewPreferences`: `ResolvedOrganizerV1!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **DOCKER**
  - Arguments:
    - `prefs`: `JSON!`
    - `viewId`: `String` (default: `"default"`)
- `updateServerIdentity`: `Server!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **SERVERS** #### Description: Update server name, comment, and model
  - Arguments:
    - `comment`: `String`
    - `name`: `String!`
    - `sysModel`: `String`
- `updateSettings`: `UpdateSettingsResponse!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**
  - Arguments:
    - `input`: `JSON!`
- `updateSshSettings`: `Vars!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **VARS**
  - Arguments:
    - `input`: `UpdateSshInput!`
- `updateSystemTime`: `SystemTime!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Update system time configuration
  - Arguments:
    - `input`: `UpdateSystemTimeInput!`
- `updateTemperatureConfig`: `Boolean!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **INFO**
  - Arguments:
    - `input`: `TemperatureConfigInput!`
- `vm`: `VmMutations!`

### `Network` (OBJECT)
- Implements: `Node`
- Fields (2):
- `accessUrls`: `[AccessUrl!]`
- `id`: `PrefixedID!`

### `Node` (INTERFACE)
- Interface fields (1):
- `id`: `PrefixedID!`
- Implemented by (49): `ApiKey`, `ApiKeyFormSettings`, `ArrayDisk`, `Config`, `Connect`, `ConnectSettings`, `CpuPackages`, `CpuUtilization`, `Disk`, `Docker`, `DockerContainer`, `DockerNetwork`, `Flash`, `Info`, `InfoBaseboard`, `InfoCpu`, `InfoDevices`, `InfoDisplay`, `InfoDisplayCase`, `InfoGpu`, `InfoMemory`, `InfoNetwork`, `InfoNetworkInterface`, `InfoOs`, `InfoPci`, `InfoSystem`, `InfoUsb`, `InfoVersions`, `MemoryLayout`, `MemoryUtilization`, `Metrics`, `Network`, `Notification`, `Notifications`, `ProfileModel`, `Registration`, `Server`, `Service`, `Settings`, `Share`, `SsoSettings`, `TemperatureMetrics`, `TemperatureSensor`, `UnifiedSettings`, `UnraidArray`, `UserAccount`, `Vars`, `VmDomain`, `Vms`

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
- Fields (4):
- `id`: `PrefixedID!`
- `list`: `[Notification!]!`
  - Arguments:
    - `filter`: `NotificationFilter!`
- `overview`: `NotificationOverview!`
  - A cached overview of the notifications in the system & their severity.
- `warningsAndAlerts`: `[Notification!]!`
  - Deduplicated list of unread warning and alert notifications, sorted latest first.

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

### `Onboarding` (OBJECT)
Onboarding completion state and context

- Fields (7):
- `activationCode`: `String`
  - The activation code from the .activationcode file, if present
- `completed`: `Boolean!`
  - Whether the onboarding flow has been completed
- `completedAtVersion`: `String`
  - The OS version when onboarding was completed
- `isPartnerBuild`: `Boolean!`
  - Whether this is a partner/OEM build with activation code
- `onboardingState`: `OnboardingState!`
  - Runtime onboarding state values used by the onboarding flow
- `shouldOpen`: `Boolean!`
  - Whether the onboarding modal should currently be shown
- `status`: `OnboardingStatus!`
  - The current onboarding status (INCOMPLETE, UPGRADE, DOWNGRADE, or COMPLETED)

### `OnboardingInternalBootContext` (OBJECT)
Current onboarding context for configuring internal boot

- Fields (8):
- `arrayStopped`: `Boolean!`
- `assignableDisks`: `[Disk!]!`
- `bootEligible`: `Boolean`
- `bootedFromFlashWithInternalBootSetup`: `Boolean!`
- `enableBootTransfer`: `String`
- `poolNames`: `[String!]!`
- `reservedNames`: `[String!]!`
- `shareNames`: `[String!]!`

### `OnboardingInternalBootResult` (OBJECT)
Result of attempting internal boot pool setup

- Fields (3):
- `code`: `Int`
- `ok`: `Boolean!`
- `output`: `String!`

### `OnboardingMutations` (OBJECT)
Onboarding related mutations

- Fields (10):
- `bypassOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Temporarily bypass onboarding in API memory
- `clearOnboardingOverride`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Clear onboarding override state and reload from disk
- `closeOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Close the onboarding modal
- `completeOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Mark onboarding as completed
- `createInternalBootPool`: `OnboardingInternalBootResult!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Create and configure internal boot pool via emcmd operations
  - Arguments:
    - `input`: `CreateInternalBootPoolInput!`
- `openOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Force the onboarding modal open
- `refreshInternalBootContext`: `OnboardingInternalBootContext!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Refresh the internal boot onboarding context from the latest emhttp state
- `resetOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Reset onboarding progress (for testing)
- `resumeOnboarding`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Clear the temporary onboarding bypass
- `setOnboardingOverride`: `Onboarding!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **WELCOME** #### Description: Override onboarding state for testing (in-memory only)
  - Arguments:
    - `input`: `OnboardingOverrideInput!`

### `OnboardingOverrideCompletionInput` (INPUT_OBJECT)
Onboarding completion override input

- Input fields (3):
- `completed`: `Boolean`
- `completedAtVersion`: `String`
- `forceOpen`: `Boolean`

### `OnboardingOverrideInput` (INPUT_OBJECT)
Onboarding override input for testing

- Input fields (4):
- `activationCode`: `ActivationCodeOverrideInput`
- `onboarding`: `OnboardingOverrideCompletionInput`
- `partnerInfo`: `PartnerInfoOverrideInput`
- `registrationState`: `RegistrationState`

### `OnboardingState` (OBJECT)
- Fields (5):
- `activationRequired`: `Boolean!`
  - Indicates whether activation is required based on current state
- `hasActivationCode`: `Boolean!`
  - Indicates whether an activation code is present
- `isFreshInstall`: `Boolean!`
  - Indicates whether the system is a fresh install
- `isRegistered`: `Boolean!`
  - Indicates whether the system is registered
- `registrationState`: `RegistrationState`

### `OnboardingStatus` (ENUM)
The current onboarding status based on completion state and version relationship

- Enum values (4):
  - `COMPLETED`
  - `DOWNGRADE`
  - `INCOMPLETE`
  - `UPGRADE`

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

### `PartnerConfig` (OBJECT)
- Fields (6):
- `extraLinks`: `[PartnerLink!]`
  - Additional custom links provided by the partner
- `hardwareSpecsUrl`: `String`
  - Link to hardware specifications for this system
- `manualUrl`: `String`
  - Link to the system manual/documentation
- `name`: `String`
- `supportUrl`: `String`
  - Link to manufacturer support page
- `url`: `String`

### `PartnerConfigInput` (INPUT_OBJECT)
- Input fields (6):
- `extraLinks`: `[PartnerLinkInput!]`
- `hardwareSpecsUrl`: `String`
- `manualUrl`: `String`
- `name`: `String`
- `supportUrl`: `String`
- `url`: `String`

### `PartnerInfoOverrideInput` (INPUT_OBJECT)
Partner info override input

- Input fields (2):
- `branding`: `BrandingConfigInput`
- `partner`: `PartnerConfigInput`

### `PartnerLink` (OBJECT)
- Fields (2):
- `title`: `String!`
  - Display title for the link
- `url`: `String!`
  - The URL

### `PartnerLinkInput` (INPUT_OBJECT)
Partner link input for custom links

- Input fields (2):
- `title`: `String!`
- `url`: `String!`

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

### `PluginInstallEvent` (OBJECT)
Emitted event representing progress for a plugin installation

- Fields (4):
- `operationId`: `ID!`
  - Identifier of the related plugin installation operation
- `output`: `[String!]`
  - Output lines newly emitted since the previous event
- `status`: `PluginInstallStatus!`
  - Status reported with this event
- `timestamp`: `DateTime!`
  - Timestamp when the event was emitted

### `PluginInstallOperation` (OBJECT)
Represents a tracked plugin installation operation

- Fields (8):
- `createdAt`: `DateTime!`
  - Timestamp when the operation was created
- `finishedAt`: `DateTime`
  - Timestamp when the operation finished, if applicable
- `id`: `ID!`
  - Unique identifier of the operation
- `name`: `String`
  - Optional plugin name for display purposes
- `output`: `[String!]!`
  - Collected output lines generated by the installer (capped at recent lines)
- `status`: `PluginInstallStatus!`
  - Current status of the operation
- `updatedAt`: `DateTime`
  - Timestamp for the last update to this operation
- `url`: `String!`
  - Plugin URL passed to the installer

### `PluginInstallStatus` (ENUM)
Status of a plugin installation operation

- Enum values (4):
  - `FAILED`
  - `QUEUED`
  - `RUNNING`
  - `SUCCEEDED`

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

### `Query` (OBJECT)
- Fields (57):
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
- `assignableDisks`: `[Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `cloud`: `Cloud!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CLOUD**
- `config`: `Config!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
- `connect`: `Connect!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONNECT**
- `customization`: `Customization`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS**
- `disk`: `Disk!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
  - Arguments:
    - `id`: `PrefixedID!`
- `disks`: `[Disk!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**
- `display`: `InfoDisplay!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISPLAY**
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
- `installedUnraidPlugins`: `[String!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List installed Unraid OS plugins by .plg filename
- `internalBootContext`: `OnboardingInternalBootContext!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **WELCOME** #### Description: Get the latest onboarding context for configuring internal boot
- `isFreshInstall`: `Boolean!`
  - Whether the system is a fresh install (no license key)
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
- `network`: `Network!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NETWORK**
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
- `pluginInstallOperation`: `PluginInstallOperation`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Retrieve a plugin installation operation by identifier
  - Arguments:
    - `operationId`: `ID!`
- `pluginInstallOperations`: `[PluginInstallOperation!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all tracked plugin installation operations
- `plugins`: `[Plugin!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all installed plugins with their metadata
- `previewEffectivePermissions`: `[Permission!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Preview the effective permissions for a combination of roles and explicit permissions
  - Arguments:
    - `permissions`: `[AddPermissionInput!]`
    - `roles`: `[Role!]`
- `publicOidcProviders`: `[PublicOidcProvider!]!`
  - Get public OIDC provider information for login buttons
- `publicTheme`: `Theme!`
- `rclone`: `RCloneBackupSettings!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**
- `registration`: `Registration`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **REGISTRATION**
- `remoteAccess`: `RemoteAccess!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONNECT**
- `server`: `Server`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `servers`: `[Server!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `services`: `[Service!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVICES**
- `settings`: `Settings!`
- `shares`: `[Share!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SHARE**
- `systemTime`: `SystemTime!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **VARS** #### Description: Retrieve current system time configuration
- `timeZoneOptions`: `[TimeZoneOption!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Retrieve available time zone options
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

### `RelayResponse` (OBJECT)
- Fields (3):
- `error`: `String`
- `status`: `String!`
- `timeout`: `String`

### `RemoteAccess` (OBJECT)
- Fields (3):
- `accessType`: `WAN_ACCESS_TYPE!`
  - The type of WAN access used for Remote Access
- `forwardType`: `WAN_FORWARD_TYPE`
  - The type of port forwarding used for Remote Access
- `port`: `Int`
  - The port used for Remote Access

### `RemoveRoleFromApiKeyInput` (INPUT_OBJECT)
- Input fields (2):
- `apiKeyId`: `PrefixedID!`
- `role`: `Role!`

### `ResolvedOrganizerV1` (OBJECT)
- Fields (2):
- `version`: `Float!`
- `views`: `[ResolvedOrganizerView!]!`

### `ResolvedOrganizerView` (OBJECT)
- Fields (5):
- `flatEntries`: `[FlatOrganizerEntry!]!`
- `id`: `String!`
- `name`: `String!`
- `prefs`: `JSON`
- `rootId`: `String!`

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

### `SensorConfig` (OBJECT)
- Fields (1):
- `enabled`: `Boolean`

### `SensorConfigInput` (INPUT_OBJECT)
- Input fields (1):
- `enabled`: `Boolean`

### `SensorType` (ENUM)
Type of temperature sensor

- Enum values (10):
  - `AMBIENT`
  - `CHIPSET`
  - `CPU_CORE`
  - `CPU_PACKAGE`
  - `CUSTOM`
  - `DISK`
  - `GPU`
  - `MOTHERBOARD`
  - `NVME`
  - `VRM`

### `Server` (OBJECT)
- Implements: `Node`
- Fields (11):
- `apikey`: `String!`
- `comment`: `String`
  - Server description/comment
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

### `SetupRemoteAccessInput` (INPUT_OBJECT)
- Input fields (3):
- `accessType`: `WAN_ACCESS_TYPE!`
  - The type of WAN access to use for Remote Access
- `forwardType`: `WAN_FORWARD_TYPE`
  - The type of port forwarding to use for Remote Access
- `port`: `Int`
  - The port to use for Remote Access. Not required for UPNP forwardType. Required for STATIC forwardType. Ignored if accessType is DISABLED or forwardType is UPNP.

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
- Fields (16):
- `arraySubscription`: `UnraidArray!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `displaySubscription`: `InfoDisplay!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DISPLAY**
- `dockerContainerStats`: `DockerContainerStats!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**
- `logFile`: `LogFileContent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**
  - Arguments:
    - `path`: `String!`
- `notificationAdded`: `Notification!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsOverview`: `NotificationOverview!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `notificationsWarningsAndAlerts`: `[Notification!]!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**
- `ownerSubscription`: `Owner!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**
- `parityHistorySubscription`: `ParityCheck!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**
- `pluginInstallUpdates`: `PluginInstallEvent!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**
  - Arguments:
    - `operationId`: `ID!`
- `serversSubscription`: `Server!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**
- `systemMetricsCpu`: `CpuUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsCpuTelemetry`: `CpuPackages!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsMemory`: `MemoryUtilization!`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `systemMetricsTemperature`: `TemperatureMetrics`
  - #### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**
- `upsUpdates`: `UPSDevice!`

### `SystemConfig` (OBJECT)
- Fields (3):
- `comment`: `String`
- `model`: `String`
- `serverName`: `String`

### `SystemConfigInput` (INPUT_OBJECT)
- Input fields (3):
- `comment`: `String`
- `model`: `String`
- `serverName`: `String`

### `SystemTime` (OBJECT)
System time configuration and current status

- Fields (4):
- `currentTime`: `String!`
  - Current server time in ISO-8601 format (UTC)
- `ntpServers`: `[String!]!`
  - Configured NTP servers (empty strings indicate unused slots)
- `timeZone`: `String!`
  - IANA timezone identifier currently in use
- `useNtp`: `Boolean!`
  - Whether NTP/PTP time synchronization is enabled

### `TailscaleExitNodeStatus` (OBJECT)
Tailscale exit node connection status

- Fields (2):
- `online`: `Boolean!`
  - Whether the exit node is online
- `tailscaleIps`: `[String!]`
  - Tailscale IPs of the exit node

### `TailscaleStatus` (OBJECT)
Tailscale status for a Docker container

- Fields (18):
- `authUrl`: `String`
  - Authentication URL if Tailscale needs login
- `backendState`: `String`
  - Tailscale backend state (Running, NeedsLogin, Stopped, etc.)
- `dnsName`: `String`
  - Actual Tailscale DNS name
- `exitNodeStatus`: `TailscaleExitNodeStatus`
  - Status of the connected exit node (if using one)
- `hostname`: `String`
  - Configured Tailscale hostname
- `isExitNode`: `Boolean!`
  - Whether this container is an exit node
- `keyExpired`: `Boolean!`
  - Whether the Tailscale key has expired
- `keyExpiry`: `DateTime`
  - Tailscale key expiry date
- `keyExpiryDays`: `Int`
  - Days until key expires
- `latestVersion`: `String`
  - Latest available Tailscale version
- `online`: `Boolean!`
  - Whether Tailscale is online in the container
- `primaryRoutes`: `[String!]`
  - Advertised subnet routes
- `relay`: `String`
  - DERP relay code
- `relayName`: `String`
  - DERP relay region name
- `tailscaleIps`: `[String!]`
  - Tailscale IPv4 and IPv6 addresses
- `updateAvailable`: `Boolean!`
  - Whether a Tailscale update is available
- `version`: `String`
  - Current Tailscale version
- `webUiUrl`: `String`
  - Tailscale Serve/Funnel WebUI URL

### `Temperature` (ENUM)
Temperature unit

- Enum values (2):
  - `CELSIUS`
  - `FAHRENHEIT`

### `TemperatureConfigInput` (INPUT_OBJECT)
- Input fields (6):
- `default_unit`: `TemperatureUnit`
- `enabled`: `Boolean`
- `history`: `TemperatureHistoryConfigInput`
- `polling_interval`: `Int`
- `sensors`: `TemperatureSensorsConfigInput`
- `thresholds`: `TemperatureThresholdsConfigInput`

### `TemperatureHistoryConfig` (OBJECT)
- Fields (2):
- `max_readings`: `Int`
- `retention_ms`: `Int`

### `TemperatureHistoryConfigInput` (INPUT_OBJECT)
- Input fields (2):
- `max_readings`: `Int`
- `retention_ms`: `Int`

### `TemperatureMetrics` (OBJECT)
- Implements: `Node`
- Fields (3):
- `id`: `PrefixedID!`
- `sensors`: `[TemperatureSensor!]!`
  - All temperature sensors
- `summary`: `TemperatureSummary!`
  - Temperature summary

### `TemperatureReading` (OBJECT)
- Fields (4):
- `status`: `TemperatureStatus!`
  - Temperature status
- `timestamp`: `DateTime!`
  - Timestamp of reading
- `unit`: `TemperatureUnit!`
  - Temperature unit
- `value`: `Float!`
  - Temperature value

### `TemperatureSensor` (OBJECT)
- Implements: `Node`
- Fields (10):
- `critical`: `Float`
  - Critical threshold
- `current`: `TemperatureReading!`
  - Current temperature
- `history`: `[TemperatureReading!]`
  - Historical readings for this sensor
- `id`: `PrefixedID!`
- `location`: `String`
  - Physical location
- `max`: `TemperatureReading`
  - Maximum recorded
- `min`: `TemperatureReading`
  - Minimum recorded
- `name`: `String!`
  - Sensor name
- `type`: `SensorType!`
  - Type of sensor
- `warning`: `Float`
  - Warning threshold

### `TemperatureSensorsConfig` (OBJECT)
- Fields (3):
- `ipmi`: `IpmiConfig`
- `lm_sensors`: `LmSensorsConfig`
- `smartctl`: `SensorConfig`

### `TemperatureSensorsConfigInput` (INPUT_OBJECT)
- Input fields (3):
- `ipmi`: `IpmiConfigInput`
- `lm_sensors`: `LmSensorsConfigInput`
- `smartctl`: `SensorConfigInput`

### `TemperatureStatus` (ENUM)
- Enum values (4):
  - `CRITICAL`
  - `NORMAL`
  - `UNKNOWN`
  - `WARNING`

### `TemperatureSummary` (OBJECT)
- Fields (5):
- `average`: `Float!`
  - Average temperature across all sensors
- `coolest`: `TemperatureSensor!`
  - Coolest sensor
- `criticalCount`: `Int!`
  - Count of sensors at critical level
- `hottest`: `TemperatureSensor!`
  - Hottest sensor
- `warningCount`: `Int!`
  - Count of sensors at warning level

### `TemperatureThresholdsConfig` (OBJECT)
- Fields (6):
- `cpu_critical`: `Int`
- `cpu_warning`: `Int`
- `critical`: `Int`
- `disk_critical`: `Int`
- `disk_warning`: `Int`
- `warning`: `Int`

### `TemperatureThresholdsConfigInput` (INPUT_OBJECT)
- Input fields (6):
- `cpu_critical`: `Int`
- `cpu_warning`: `Int`
- `critical`: `Int`
- `disk_critical`: `Int`
- `disk_warning`: `Int`
- `warning`: `Int`

### `TemperatureUnit` (ENUM)
- Enum values (4):
  - `CELSIUS`
  - `FAHRENHEIT`
  - `KELVIN`
  - `RANKINE`

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

### `TimeZoneOption` (OBJECT)
Selectable timezone option from the system list

- Fields (2):
- `label`: `String!`
  - Display label for the timezone
- `value`: `String!`
  - IANA timezone identifier

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
- Fields (5):
- `currentPower`: `Float`
  - Current power consumption calculated from load percentage and nominal power. Unit: watts (W). Example: 350 means 350 watts currently being used. Calculated as: nominalPower * (loadPercentage / 100)
- `inputVoltage`: `Float!`
  - Input voltage from the wall outlet/mains power. Unit: volts (V). Example: 120.5 for typical US household voltage
- `loadPercentage`: `Int!`
  - Current load on the UPS as a percentage of its capacity. Unit: percent (%). Example: 25 means UPS is loaded at 25% of its maximum capacity
- `nominalPower`: `Int`
  - Nominal power capacity of the UPS. Unit: watts (W). Example: 1000 means the UPS is rated for 1000 watts. This is the maximum power the UPS can deliver
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

### `URL` (SCALAR)
A field whose value conforms to the standard URL format as specified in RFC3986: https://www.ietf.org/rfc/rfc3986.txt.

- Scalar type

### `URL_TYPE` (ENUM)
- Enum values (6):
  - `DEFAULT`
  - `LAN`
  - `MDNS`
  - `OTHER`
  - `WAN`
  - `WIREGUARD`

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
- Fields (9):
- `boot`: `ArrayDisk`
  - Returns the active boot disk
- `bootDevices`: `[ArrayDisk!]!`
  - All detected boot devices: every Boot entry for internal boot, including mirrored members when configured, or the mounted /boot Flash entry for legacy USB boot
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

### `UnraidPluginsMutations` (OBJECT)
Unraid plugin management mutations

- Fields (2):
- `installLanguage`: `PluginInstallOperation!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Install an Unraid language pack and track installation progress
  - Arguments:
    - `input`: `InstallPluginInput!`
- `installPlugin`: `PluginInstallOperation!`
  - #### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Install an Unraid plugin and track installation progress
  - Arguments:
    - `input`: `InstallPluginInput!`

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

### `UpdateSshInput` (INPUT_OBJECT)
- Input fields (2):
- `enabled`: `Boolean!`
- `port`: `Int!`
  - SSH Port (default 22)

### `UpdateStatus` (ENUM)
Update status of a container.

- Enum values (4):
  - `REBUILD_READY`
  - `UNKNOWN`
  - `UPDATE_AVAILABLE`
  - `UP_TO_DATE`

### `UpdateSystemTimeInput` (INPUT_OBJECT)
- Input fields (4):
- `manualDateTime`: `String`
  - Manual date/time to apply when disabling NTP, expected format YYYY-MM-DD HH:mm:ss
- `ntpServers`: `[String!]`
  - Ordered list of up to four NTP servers. Supply empty strings to clear positions.
- `timeZone`: `String`
  - New IANA timezone identifier to apply
- `useNtp`: `Boolean`
  - Enable or disable NTP-based synchronization

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
- Fields (148):
- `bindMgt`: `Boolean`
- `bootEligible`: `Boolean`
- `bootedFromFlashWithInternalBootSetup`: `Boolean`
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
- `enableBootTransfer`: `String`
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
- `reservedNames`: `String`
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
- `tpmGuid`: `String`
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

### `WAN_ACCESS_TYPE` (ENUM)
- Enum values (3):
  - `ALWAYS`
  - `DISABLED`
  - `DYNAMIC`

### `WAN_FORWARD_TYPE` (ENUM)
- Enum values (2):
  - `STATIC`
  - `UPNP`

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
