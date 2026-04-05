# Unraid GraphQL API Complete Schema Reference

Generated via live GraphQL introspection for the configured endpoint and API key.

This is permission-scoped: it contains everything visible to the API key used.

## Table of Contents
- [Schema Summary](#schema-summary)
- [Root Operations](#root-operations)
- [Directives](#directives)
- [All Types (Alphabetical)](#all-types-alphabetical)

## Schema Summary
- Source endpoint: `10-1-0-2.95d289568cc4a4bdc8e0d50284d6f455ec0eae5f.myunraid.net:31337/graphql`
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
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
- `values`: `JSON!`

### `ApiKeyMutations` (OBJECT)
API Key related mutations

- Fields (5):
- `addRole`: `Boolean!`
- `create`: `ApiKey!`
- `delete`: `Boolean!`
- `removeRole`: `Boolean!`
- `update`: `ApiKey!`

### `ApiKeyResponse` (OBJECT)
- Fields (2):
- `error`: `String`
- `valid`: `Boolean!`

### `ArrayCapacity` (OBJECT)
- Fields (2):
- `disks`: `Capacity!`
- `kilobytes`: `Capacity!`

### `ArrayDisk` (OBJECT)
- Implements: `Node`
- Fields (24):
- `color`: `ArrayDiskFsColor`
- `comment`: `String`
- `critical`: `Int`
- `device`: `String`
- `exportable`: `Boolean`
- `format`: `String`
- `fsFree`: `BigInt`
- `fsSize`: `BigInt`
- `fsType`: `String`
- `fsUsed`: `BigInt`
- `id`: `PrefixedID!`
- `idx`: `Int!`
- `isSpinning`: `Boolean`
- `name`: `String`
- `numErrors`: `BigInt`
- `numReads`: `BigInt`
- `numWrites`: `BigInt`
- `rotational`: `Boolean`
- `size`: `BigInt`
- `status`: `ArrayDiskStatus`
- `temp`: `Int`
- `transport`: `String`
- `type`: `ArrayDiskType!`
- `warning`: `Int`

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
- `slot`: `Int`

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
- `clearArrayDiskStatistics`: `Boolean!`
- `mountArrayDisk`: `ArrayDisk!`
- `removeDiskFromArray`: `UnraidArray!`
- `setState`: `UnraidArray!`
- `unmountArrayDisk`: `ArrayDisk!`

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
- `decryptionPassword`: `String`
- `desiredState`: `ArrayStateInputState!`

### `ArrayStateInputState` (ENUM)
- Enum values (2):
- `START`
- `STOP`

### `AuthAction` (ENUM)
Authentication actions with possession (e.g., create:any, read:own)

- Enum values (8):
- `CREATE_ANY`
- `CREATE_OWN`
- `DELETE_ANY`
- `DELETE_OWN`
- `READ_ANY`
- `READ_OWN`
- `UPDATE_ANY`
- `UPDATE_OWN`

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
- `total`: `String!`
- `used`: `String!`

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
- `id`: `PrefixedID!`
- `settings`: `ConnectSettings!`

### `ConnectSettings` (OBJECT)
- Implements: `Node`
- Fields (4):
- `dataSchema`: `JSON!`
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
- `values`: `ConnectSettingsValues!`

### `ConnectSettingsInput` (INPUT_OBJECT)
- Input fields (3):
- `accessType`: `WAN_ACCESS_TYPE`
- `forwardType`: `WAN_FORWARD_TYPE`
- `port`: `Int`

### `ConnectSettingsValues` (OBJECT)
- Fields (3):
- `accessType`: `WAN_ACCESS_TYPE!`
- `forwardType`: `WAN_FORWARD_TYPE`
- `port`: `Int`

### `ConnectSignInInput` (INPUT_OBJECT)
- Input fields (2):
- `apiKey`: `String!`
- `userInfo`: `ConnectUserInfoInput`

### `ConnectUserInfoInput` (INPUT_OBJECT)
- Input fields (3):
- `avatar`: `String`
- `email`: `String!`
- `preferred_username`: `String!`

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
- `kernel`: `String`
- `unraid`: `String`

### `CpuLoad` (OBJECT)
CPU load for a single core

- Fields (8):
- `percentGuest`: `Float!`
- `percentIdle`: `Float!`
- `percentIrq`: `Float!`
- `percentNice`: `Float!`
- `percentSteal`: `Float!`
- `percentSystem`: `Float!`
- `percentTotal`: `Float!`
- `percentUser`: `Float!`

### `CpuPackages` (OBJECT)
- Implements: `Node`
- Fields (4):
- `id`: `PrefixedID!`
- `power`: `[Float!]!`
- `temp`: `[Float!]!`
- `totalPower`: `Float!`

### `CpuUtilization` (OBJECT)
- Implements: `Node`
- Fields (3):
- `cpus`: `[CpuLoad!]!`
- `id`: `PrefixedID!`
- `percentTotal`: `Float!`

### `CreateApiKeyInput` (INPUT_OBJECT)
- Input fields (5):
- `description`: `String`
- `name`: `String!`
- `overwrite`: `Boolean`
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
- `availableLanguages`: `[Language!]`
- `onboarding`: `Onboarding!`

### `CustomizationMutations` (OBJECT)
Customization related mutations

- Fields (2):
- `setLocale`: `String!`
- `setTheme`: `Theme!`

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
- `device`: `String!`
- `firmwareRevision`: `String!`
- `id`: `PrefixedID!`
- `interfaceType`: `DiskInterfaceType!`
- `isSpinning`: `Boolean!`
- `name`: `String!`
- `partitions`: `[DiskPartition!]!`
- `sectorsPerTrack`: `Float!`
- `serialNum`: `String!`
- `size`: `Float!`
- `smartStatus`: `DiskSmartStatus!`
- `temperature`: `Float`
- `totalCylinders`: `Float!`
- `totalHeads`: `Float!`
- `totalSectors`: `Float!`
- `totalTracks`: `Float!`
- `tracksPerCylinder`: `Float!`
- `type`: `String!`
- `vendor`: `String!`

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
- `name`: `String!`
- `size`: `Float!`

### `DiskSmartStatus` (ENUM)
The SMART (Self-Monitoring, Analysis and Reporting Technology) status of the disk

- Enum values (2):
- `OK`
- `UNKNOWN`

### `Docker` (OBJECT)
- Implements: `Node`
- Fields (8):
- `container`: `DockerContainer`
- `containerUpdateStatuses`: `[ExplicitStatusItem!]!`
- `containers`: `[DockerContainer!]!`
- `id`: `PrefixedID!`
- `logs`: `DockerContainerLogs!`
- `networks`: `[DockerNetwork!]!`
- `organizer`: `ResolvedOrganizerV1!`
- `portConflicts`: `DockerPortConflicts!`

### `DockerAutostartEntryInput` (INPUT_OBJECT)
- Input fields (3):
- `autoStart`: `Boolean!`
- `id`: `PrefixedID!`
- `wait`: `Int`

### `DockerContainer` (OBJECT)
- Implements: `Node`
- Fields (33):
- `autoStart`: `Boolean!`
- `autoStartOrder`: `Int`
- `autoStartWait`: `Int`
- `command`: `String!`
- `created`: `Int!`
- `hostConfig`: `ContainerHostConfig`
- `iconUrl`: `String`
- `id`: `PrefixedID!`
- `image`: `String!`
- `imageId`: `String!`
- `isOrphaned`: `Boolean!`
- `isRebuildReady`: `Boolean`
- `isUpdateAvailable`: `Boolean`
- `labels`: `JSON`
- `lanIpPorts`: `[String!]`
- `mounts`: `[JSON!]`
- `names`: `[String!]!`
- `networkSettings`: `JSON`
- `ports`: `[ContainerPort!]!`
- `projectUrl`: `String`
- `registryUrl`: `String`
- `shell`: `String`
- `sizeLog`: `BigInt`
- `sizeRootFs`: `BigInt`
- `sizeRw`: `BigInt`
- `state`: `ContainerState!`
- `status`: `String!`
- `supportUrl`: `String`
- `tailscaleEnabled`: `Boolean!`
- `tailscaleStatus`: `TailscaleStatus`
- `templatePath`: `String`
- `templatePorts`: `[ContainerPort!]`
- `webUiUrl`: `String`

### `DockerContainerLogLine` (OBJECT)
- Fields (2):
- `message`: `String!`
- `timestamp`: `DateTime!`

### `DockerContainerLogs` (OBJECT)
- Fields (3):
- `containerId`: `PrefixedID!`
- `cursor`: `DateTime`
- `lines`: `[DockerContainerLogLine!]!`

### `DockerContainerPortConflict` (OBJECT)
- Fields (3):
- `containers`: `[DockerPortConflictContainer!]!`
- `privatePort`: `Port!`
- `type`: `ContainerPortType!`

### `DockerContainerStats` (OBJECT)
- Fields (6):
- `blockIO`: `String!`
- `cpuPercent`: `Float!`
- `id`: `PrefixedID!`
- `memPercent`: `Float!`
- `memUsage`: `String!`
- `netIO`: `String!`

### `DockerLanPortConflict` (OBJECT)
- Fields (4):
- `containers`: `[DockerPortConflictContainer!]!`
- `lanIpPort`: `String!`
- `publicPort`: `Port`
- `type`: `ContainerPortType!`

### `DockerMutations` (OBJECT)
- Fields (9):
- `pause`: `DockerContainer!`
- `removeContainer`: `Boolean!`
- `start`: `DockerContainer!`
- `stop`: `DockerContainer!`
- `unpause`: `DockerContainer!`
- `updateAllContainers`: `[DockerContainer!]!`
- `updateAutostartConfiguration`: `Boolean!`
- `updateContainer`: `DockerContainer!`
- `updateContainers`: `[DockerContainer!]!`

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
- `error`: `String`
- `runningType`: `DynamicRemoteAccessType!`

### `DynamicRemoteAccessType` (ENUM)
- Enum values (3):
- `DISABLED`
- `STATIC`
- `UPNP`

### `EnableDynamicRemoteAccessInput` (INPUT_OBJECT)
- Input fields (2):
- `enabled`: `Boolean!`
- `url`: `AccessUrlInput!`

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
- `status`: `String!`

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
- `uiSchema`: `JSON!`
- `values`: `JSON!`
- Implemented by (2): `ApiKeyFormSettings`, `UnifiedSettings`

### `ID` (SCALAR)
The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.

- Scalar type

### `Info` (OBJECT)
- Implements: `Node`
- Fields (13):
- `baseboard`: `InfoBaseboard!`
- `cpu`: `InfoCpu!`
- `devices`: `InfoDevices!`
- `display`: `InfoDisplay!`
- `id`: `PrefixedID!`
- `machineId`: `ID`
- `memory`: `InfoMemory!`
- `networkInterfaces`: `[InfoNetworkInterface!]!`
- `os`: `InfoOs!`
- `primaryNetwork`: `InfoNetworkInterface`
- `system`: `InfoSystem!`
- `time`: `DateTime!`
- `versions`: `InfoVersions!`

### `InfoBaseboard` (OBJECT)
- Implements: `Node`
- Fields (8):
- `assetTag`: `String`
- `id`: `PrefixedID!`
- `manufacturer`: `String`
- `memMax`: `Float`
- `memSlots`: `Float`
- `model`: `String`
- `serial`: `String`
- `version`: `String`

### `InfoCpu` (OBJECT)
- Implements: `Node`
- Fields (20):
- `brand`: `String`
- `cache`: `JSON`
- `cores`: `Int`
- `family`: `String`
- `flags`: `[String!]`
- `id`: `PrefixedID!`
- `manufacturer`: `String`
- `model`: `String`
- `packages`: `CpuPackages!`
- `processors`: `Int`
- `revision`: `String`
- `socket`: `String`
- `speed`: `Float`
- `speedmax`: `Float`
- `speedmin`: `Float`
- `stepping`: `Int`
- `threads`: `Int`
- `topology`: `[[[Int!]!]!]!`
- `vendor`: `String`
- `voltage`: `String`

### `InfoDevices` (OBJECT)
- Implements: `Node`
- Fields (5):
- `gpu`: `[InfoGpu!]`
- `id`: `PrefixedID!`
- `network`: `[InfoNetwork!]`
- `pci`: `[InfoPci!]`
- `usb`: `[InfoUsb!]`

### `InfoDisplay` (OBJECT)
- Implements: `Node`
- Fields (16):
- `case`: `InfoDisplayCase!`
- `critical`: `Int!`
- `hot`: `Int!`
- `id`: `PrefixedID!`
- `locale`: `String`
- `max`: `Int`
- `resize`: `Boolean!`
- `scale`: `Boolean!`
- `tabs`: `Boolean!`
- `text`: `Boolean!`
- `theme`: `ThemeName!`
- `total`: `Boolean!`
- `unit`: `Temperature!`
- `usage`: `Boolean!`
- `warning`: `Int!`
- `wwn`: `Boolean!`

### `InfoDisplayCase` (OBJECT)
- Implements: `Node`
- Fields (5):
- `base64`: `String!`
- `error`: `String!`
- `icon`: `String!`
- `id`: `PrefixedID!`
- `url`: `String!`

### `InfoGpu` (OBJECT)
- Implements: `Node`
- Fields (7):
- `blacklisted`: `Boolean!`
- `class`: `String!`
- `id`: `PrefixedID!`
- `productid`: `String!`
- `type`: `String!`
- `typeid`: `String!`
- `vendorname`: `String`

### `InfoMemory` (OBJECT)
- Implements: `Node`
- Fields (2):
- `id`: `PrefixedID!`
- `layout`: `[MemoryLayout!]!`

### `InfoNetwork` (OBJECT)
- Implements: `Node`
- Fields (8):
- `dhcp`: `Boolean`
- `id`: `PrefixedID!`
- `iface`: `String!`
- `mac`: `String`
- `model`: `String`
- `speed`: `String`
- `vendor`: `String`
- `virtual`: `Boolean`

### `InfoNetworkInterface` (OBJECT)
- Implements: `Node`
- Fields (14):
- `description`: `String`
- `gateway`: `String`
- `id`: `PrefixedID!`
- `ipAddress`: `String`
- `ipv6Address`: `String`
- `ipv6Gateway`: `String`
- `ipv6Netmask`: `String`
- `macAddress`: `String`
- `name`: `String!`
- `netmask`: `String`
- `protocol`: `String`
- `status`: `String`
- `useDhcp`: `Boolean`
- `useDhcp6`: `Boolean`

### `InfoOs` (OBJECT)
- Implements: `Node`
- Fields (15):
- `arch`: `String`
- `build`: `String`
- `codename`: `String`
- `distro`: `String`
- `fqdn`: `String`
- `hostname`: `String`
- `id`: `PrefixedID!`
- `kernel`: `String`
- `logofile`: `String`
- `platform`: `String`
- `release`: `String`
- `serial`: `String`
- `servicepack`: `String`
- `uefi`: `Boolean`
- `uptime`: `String`

### `InfoPci` (OBJECT)
- Implements: `Node`
- Fields (9):
- `blacklisted`: `String!`
- `class`: `String!`
- `id`: `PrefixedID!`
- `productid`: `String!`
- `productname`: `String`
- `type`: `String!`
- `typeid`: `String!`
- `vendorid`: `String!`
- `vendorname`: `String`

### `InfoSystem` (OBJECT)
- Implements: `Node`
- Fields (8):
- `id`: `PrefixedID!`
- `manufacturer`: `String`
- `model`: `String`
- `serial`: `String`
- `sku`: `String`
- `uuid`: `String`
- `version`: `String`
- `virtual`: `Boolean`

### `InfoUsb` (OBJECT)
- Implements: `Node`
- Fields (4):
- `bus`: `String`
- `device`: `String`
- `id`: `PrefixedID!`
- `name`: `String!`

### `InfoVersions` (OBJECT)
- Implements: `Node`
- Fields (3):
- `core`: `CoreVersions!`
- `id`: `PrefixedID!`
- `packages`: `PackageVersions`

### `InitiateFlashBackupInput` (INPUT_OBJECT)
- Input fields (4):
- `destinationPath`: `String!`
- `options`: `JSON`
- `remoteName`: `String!`
- `sourcePath`: `String!`

### `InstallPluginInput` (INPUT_OBJECT)
Input payload for installing a plugin

- Input fields (3):
- `forced`: `Boolean`
- `name`: `String`
- `url`: `String!`

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
- `name`: `String!`
- `url`: `String`

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
- `name`: `String!`
- `path`: `String!`
- `size`: `Int!`

### `LogFileContent` (OBJECT)
- Fields (4):
- `content`: `String!`
- `path`: `String!`
- `startLine`: `Int`
- `totalLines`: `Int!`

### `MemoryLayout` (OBJECT)
- Implements: `Node`
- Fields (12):
- `bank`: `String`
- `clockSpeed`: `Int`
- `formFactor`: `String`
- `id`: `PrefixedID!`
- `manufacturer`: `String`
- `partNum`: `String`
- `serialNum`: `String`
- `size`: `BigInt!`
- `type`: `String`
- `voltageConfigured`: `Int`
- `voltageMax`: `Int`
- `voltageMin`: `Int`

### `MemoryUtilization` (OBJECT)
- Implements: `Node`
- Fields (12):
- `active`: `BigInt!`
- `available`: `BigInt!`
- `buffcache`: `BigInt!`
- `free`: `BigInt!`
- `id`: `PrefixedID!`
- `percentSwapTotal`: `Float!`
- `percentTotal`: `Float!`
- `swapFree`: `BigInt!`
- `swapTotal`: `BigInt!`
- `swapUsed`: `BigInt!`
- `total`: `BigInt!`
- `used`: `BigInt!`

### `Metrics` (OBJECT)
System metrics including CPU and memory utilization

- Implements: `Node`
- Fields (4):
- `cpu`: `CpuUtilization`
- `id`: `PrefixedID!`
- `memory`: `MemoryUtilization`
- `temperature`: `TemperatureMetrics`

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
- `apiKey`: `ApiKeyMutations!`
- `archiveAll`: `NotificationOverview!`
- `archiveNotification`: `Notification!`
- `archiveNotifications`: `NotificationOverview!`
- `array`: `ArrayMutations!`
- `configureUps`: `Boolean!`
- `connectSignIn`: `Boolean!`
- `connectSignOut`: `Boolean!`
- `createDockerFolder`: `ResolvedOrganizerV1!`
- `createDockerFolderWithItems`: `ResolvedOrganizerV1!`
- `createNotification`: `Notification!`
- `customization`: `CustomizationMutations!`
- `deleteArchivedNotifications`: `NotificationOverview!`
- `deleteDockerEntries`: `ResolvedOrganizerV1!`
- `deleteNotification`: `NotificationOverview!`
- `docker`: `DockerMutations!`
- `enableDynamicRemoteAccess`: `Boolean!`
- `initiateFlashBackup`: `FlashBackupStatus!`
- `moveDockerEntriesToFolder`: `ResolvedOrganizerV1!`
- `moveDockerItemsToPosition`: `ResolvedOrganizerV1!`
- `notifyIfUnique`: `Notification`
- `onboarding`: `OnboardingMutations!`
- `parityCheck`: `ParityCheckMutations!`
- `rclone`: `RCloneMutations!`
- `recalculateOverview`: `NotificationOverview!`
- `refreshDockerDigests`: `Boolean!`
- `removePlugin`: `Boolean!`
- `renameDockerFolder`: `ResolvedOrganizerV1!`
- `resetDockerTemplateMappings`: `Boolean!`
- `setDockerFolderChildren`: `ResolvedOrganizerV1!`
- `setupRemoteAccess`: `Boolean!`
- `syncDockerTemplatePaths`: `DockerTemplateSyncResult!`
- `unarchiveAll`: `NotificationOverview!`
- `unarchiveNotifications`: `NotificationOverview!`
- `unraidPlugins`: `UnraidPluginsMutations!`
- `unreadNotification`: `Notification!`
- `updateApiSettings`: `ConnectSettingsValues!`
- `updateDockerViewPreferences`: `ResolvedOrganizerV1!`
- `updateServerIdentity`: `Server!`
- `updateSettings`: `UpdateSettingsResponse!`
- `updateSshSettings`: `Vars!`
- `updateSystemTime`: `SystemTime!`
- `updateTemperatureConfig`: `Boolean!`
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
- `title`: `String!`
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
- `overview`: `NotificationOverview!`
- `warningsAndAlerts`: `[Notification!]!`

### `OidcAuthorizationRule` (OBJECT)
- Fields (3):
- `claim`: `String!`
- `operator`: `AuthorizationOperator!`
- `value`: `[String!]!`

### `OidcConfiguration` (OBJECT)
- Fields (2):
- `defaultAllowedOrigins`: `[String!]`
- `providers`: `[OidcProvider!]!`

### `OidcProvider` (OBJECT)
- Fields (15):
- `authorizationEndpoint`: `String`
- `authorizationRuleMode`: `AuthorizationRuleMode`
- `authorizationRules`: `[OidcAuthorizationRule!]`
- `buttonIcon`: `String`
- `buttonStyle`: `String`
- `buttonText`: `String`
- `buttonVariant`: `String`
- `clientId`: `String!`
- `clientSecret`: `String`
- `id`: `PrefixedID!`
- `issuer`: `String`
- `jwksUri`: `String`
- `name`: `String!`
- `scopes`: `[String!]!`
- `tokenEndpoint`: `String`

### `OidcSessionValidation` (OBJECT)
- Fields (2):
- `username`: `String`
- `valid`: `Boolean!`

### `Onboarding` (OBJECT)
Onboarding completion state and context

- Fields (7):
- `activationCode`: `String`
- `completed`: `Boolean!`
- `completedAtVersion`: `String`
- `isPartnerBuild`: `Boolean!`
- `onboardingState`: `OnboardingState!`
- `shouldOpen`: `Boolean!`
- `status`: `OnboardingStatus!`

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
- `clearOnboardingOverride`: `Onboarding!`
- `closeOnboarding`: `Onboarding!`
- `completeOnboarding`: `Onboarding!`
- `createInternalBootPool`: `OnboardingInternalBootResult!`
- `openOnboarding`: `Onboarding!`
- `refreshInternalBootContext`: `OnboardingInternalBootContext!`
- `resetOnboarding`: `Onboarding!`
- `resumeOnboarding`: `Onboarding!`
- `setOnboardingOverride`: `Onboarding!`

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
- `hasActivationCode`: `Boolean!`
- `isFreshInstall`: `Boolean!`
- `isRegistered`: `Boolean!`
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
- `git`: `String`
- `nginx`: `String`
- `node`: `String`
- `npm`: `String`
- `openssl`: `String`
- `php`: `String`
- `pm2`: `String`

### `ParityCheck` (OBJECT)
- Fields (9):
- `correcting`: `Boolean`
- `date`: `DateTime`
- `duration`: `Int`
- `errors`: `Int`
- `paused`: `Boolean`
- `progress`: `Int`
- `running`: `Boolean`
- `speed`: `String`
- `status`: `ParityCheckStatus!`

### `ParityCheckMutations` (OBJECT)
Parity check related mutations, WIP, response types and functionaliy will change

- Fields (4):
- `cancel`: `JSON!`
- `pause`: `JSON!`
- `resume`: `JSON!`
- `start`: `JSON!`

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
- `hardwareSpecsUrl`: `String`
- `manualUrl`: `String`
- `name`: `String`
- `supportUrl`: `String`
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
- `url`: `String!`

### `PartnerLinkInput` (INPUT_OBJECT)
Partner link input for custom links

- Input fields (2):
- `title`: `String!`
- `url`: `String!`

### `Permission` (OBJECT)
- Fields (2):
- `actions`: `[AuthAction!]!`
- `resource`: `Resource!`

### `Plugin` (OBJECT)
- Fields (4):
- `hasApiModule`: `Boolean`
- `hasCliModule`: `Boolean`
- `name`: `String!`
- `version`: `String!`

### `PluginInstallEvent` (OBJECT)
Emitted event representing progress for a plugin installation

- Fields (4):
- `operationId`: `ID!`
- `output`: `[String!]`
- `status`: `PluginInstallStatus!`
- `timestamp`: `DateTime!`

### `PluginInstallOperation` (OBJECT)
Represents a tracked plugin installation operation

- Fields (8):
- `createdAt`: `DateTime!`
- `finishedAt`: `DateTime`
- `id`: `ID!`
- `name`: `String`
- `output`: `[String!]!`
- `status`: `PluginInstallStatus!`
- `updatedAt`: `DateTime`
- `url`: `String!`

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
- `names`: `[String!]!`
- `restart`: `Boolean!`

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
- `apiKeyPossiblePermissions`: `[Permission!]!`
- `apiKeyPossibleRoles`: `[Role!]!`
- `apiKeys`: `[ApiKey!]!`
- `array`: `UnraidArray!`
- `assignableDisks`: `[Disk!]!`
- `cloud`: `Cloud!`
- `config`: `Config!`
- `connect`: `Connect!`
- `customization`: `Customization`
- `disk`: `Disk!`
- `disks`: `[Disk!]!`
- `display`: `InfoDisplay!`
- `docker`: `Docker!`
- `flash`: `Flash!`
- `getApiKeyCreationFormSchema`: `ApiKeyFormSettings!`
- `getAvailableAuthActions`: `[AuthAction!]!`
- `getPermissionsForRoles`: `[Permission!]!`
- `info`: `Info!`
- `installedUnraidPlugins`: `[String!]!`
- `internalBootContext`: `OnboardingInternalBootContext!`
- `isFreshInstall`: `Boolean!`
- `isSSOEnabled`: `Boolean!`
- `logFile`: `LogFileContent!`
- `logFiles`: `[LogFile!]!`
- `me`: `UserAccount!`
- `metrics`: `Metrics!`
- `network`: `Network!`
- `notifications`: `Notifications!`
- `oidcConfiguration`: `OidcConfiguration!`
- `oidcProvider`: `OidcProvider`
- `oidcProviders`: `[OidcProvider!]!`
- `online`: `Boolean!`
- `owner`: `Owner!`
- `parityHistory`: `[ParityCheck!]!`
- `pluginInstallOperation`: `PluginInstallOperation`
- `pluginInstallOperations`: `[PluginInstallOperation!]!`
- `plugins`: `[Plugin!]!`
- `previewEffectivePermissions`: `[Permission!]!`
- `publicOidcProviders`: `[PublicOidcProvider!]!`
- `publicTheme`: `Theme!`
- `rclone`: `RCloneBackupSettings!`
- `registration`: `Registration`
- `remoteAccess`: `RemoteAccess!`
- `server`: `Server`
- `servers`: `[Server!]!`
- `services`: `[Service!]!`
- `settings`: `Settings!`
- `shares`: `[Share!]!`
- `systemTime`: `SystemTime!`
- `timeZoneOptions`: `[TimeZoneOption!]!`
- `upsConfiguration`: `UPSConfiguration!`
- `upsDeviceById`: `UPSDevice`
- `upsDevices`: `[UPSDevice!]!`
- `validateOidcSession`: `OidcSessionValidation!`
- `vars`: `Vars!`
- `vms`: `Vms!`

### `RCloneBackupConfigForm` (OBJECT)
- Fields (3):
- `dataSchema`: `JSON!`
- `id`: `ID!`
- `uiSchema`: `JSON!`

### `RCloneBackupSettings` (OBJECT)
- Fields (3):
- `configForm`: `RCloneBackupConfigForm!`
- `drives`: `[RCloneDrive!]!`
- `remotes`: `[RCloneRemote!]!`

### `RCloneConfigFormInput` (INPUT_OBJECT)
- Input fields (3):
- `parameters`: `JSON`
- `providerType`: `String`
- `showAdvanced`: `Boolean`

### `RCloneDrive` (OBJECT)
- Fields (2):
- `name`: `String!`
- `options`: `JSON!`

### `RCloneMutations` (OBJECT)
RClone related mutations

- Fields (2):
- `createRCloneRemote`: `RCloneRemote!`
- `deleteRCloneRemote`: `Boolean!`

### `RCloneRemote` (OBJECT)
- Fields (4):
- `config`: `JSON!`
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
- `forwardType`: `WAN_FORWARD_TYPE`
- `port`: `Int`

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
- `CONNECT`
- `GUEST`
- `VIEWER`

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
- `guid`: `String!`
- `id`: `PrefixedID!`
- `lanip`: `String!`
- `localurl`: `String!`
- `name`: `String!`
- `owner`: `ProfileModel!`
- `remoteurl`: `String!`
- `status`: `ServerStatus!`
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
- `id`: `PrefixedID!`
- `sso`: `SsoSettings!`
- `unified`: `UnifiedSettings!`

### `SetupRemoteAccessInput` (INPUT_OBJECT)
- Input fields (3):
- `accessType`: `WAN_ACCESS_TYPE!`
- `forwardType`: `WAN_FORWARD_TYPE`
- `port`: `Int`

### `Share` (OBJECT)
- Implements: `Node`
- Fields (16):
- `allocator`: `String`
- `cache`: `Boolean`
- `color`: `String`
- `comment`: `String`
- `cow`: `String`
- `exclude`: `[String!]`
- `floor`: `String`
- `free`: `BigInt`
- `id`: `PrefixedID!`
- `include`: `[String!]`
- `luksStatus`: `String`
- `name`: `String`
- `nameOrig`: `String`
- `size`: `BigInt`
- `splitLevel`: `String`
- `used`: `BigInt`

### `SsoSettings` (OBJECT)
- Implements: `Node`
- Fields (2):
- `id`: `PrefixedID!`
- `oidcProviders`: `[OidcProvider!]!`

### `String` (SCALAR)
The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

- Scalar type

### `Subscription` (OBJECT)
- Fields (16):
- `arraySubscription`: `UnraidArray!`
- `displaySubscription`: `InfoDisplay!`
- `dockerContainerStats`: `DockerContainerStats!`
- `logFile`: `LogFileContent!`
- `notificationAdded`: `Notification!`
- `notificationsOverview`: `NotificationOverview!`
- `notificationsWarningsAndAlerts`: `[Notification!]!`
- `ownerSubscription`: `Owner!`
- `parityHistorySubscription`: `ParityCheck!`
- `pluginInstallUpdates`: `PluginInstallEvent!`
- `serversSubscription`: `Server!`
- `systemMetricsCpu`: `CpuUtilization!`
- `systemMetricsCpuTelemetry`: `CpuPackages!`
- `systemMetricsMemory`: `MemoryUtilization!`
- `systemMetricsTemperature`: `TemperatureMetrics`
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
- `ntpServers`: `[String!]!`
- `timeZone`: `String!`
- `useNtp`: `Boolean!`

### `TailscaleExitNodeStatus` (OBJECT)
Tailscale exit node connection status

- Fields (2):
- `online`: `Boolean!`
- `tailscaleIps`: `[String!]`

### `TailscaleStatus` (OBJECT)
Tailscale status for a Docker container

- Fields (18):
- `authUrl`: `String`
- `backendState`: `String`
- `dnsName`: `String`
- `exitNodeStatus`: `TailscaleExitNodeStatus`
- `hostname`: `String`
- `isExitNode`: `Boolean!`
- `keyExpired`: `Boolean!`
- `keyExpiry`: `DateTime`
- `keyExpiryDays`: `Int`
- `latestVersion`: `String`
- `online`: `Boolean!`
- `primaryRoutes`: `[String!]`
- `relay`: `String`
- `relayName`: `String`
- `tailscaleIps`: `[String!]`
- `updateAvailable`: `Boolean!`
- `version`: `String`
- `webUiUrl`: `String`

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
- `summary`: `TemperatureSummary!`

### `TemperatureReading` (OBJECT)
- Fields (4):
- `status`: `TemperatureStatus!`
- `timestamp`: `DateTime!`
- `unit`: `TemperatureUnit!`
- `value`: `Float!`

### `TemperatureSensor` (OBJECT)
- Implements: `Node`
- Fields (10):
- `critical`: `Float`
- `current`: `TemperatureReading!`
- `history`: `[TemperatureReading!]`
- `id`: `PrefixedID!`
- `location`: `String`
- `max`: `TemperatureReading`
- `min`: `TemperatureReading`
- `name`: `String!`
- `type`: `SensorType!`
- `warning`: `Float`

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
- `coolest`: `TemperatureSensor!`
- `criticalCount`: `Int!`
- `hottest`: `TemperatureSensor!`
- `warningCount`: `Int!`

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
- `headerPrimaryTextColor`: `String`
- `headerSecondaryTextColor`: `String`
- `name`: `ThemeName!`
- `showBannerGradient`: `Boolean!`
- `showBannerImage`: `Boolean!`
- `showHeaderDescription`: `Boolean!`

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
- `value`: `String!`

### `UPSBattery` (OBJECT)
- Fields (3):
- `chargeLevel`: `Int!`
- `estimatedRuntime`: `Int!`
- `health`: `String!`

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
- `customUpsCable`: `String`
- `device`: `String`
- `killUps`: `UPSKillPower`
- `minutes`: `Int`
- `overrideUpsCapacity`: `Int`
- `service`: `UPSServiceState`
- `timeout`: `Int`
- `upsCable`: `UPSCableType`
- `upsType`: `UPSType`

### `UPSConfiguration` (OBJECT)
- Fields (14):
- `batteryLevel`: `Int`
- `customUpsCable`: `String`
- `device`: `String`
- `killUps`: `String`
- `minutes`: `Int`
- `modelName`: `String`
- `netServer`: `String`
- `nisIp`: `String`
- `overrideUpsCapacity`: `Int`
- `service`: `String`
- `timeout`: `Int`
- `upsCable`: `String`
- `upsName`: `String`
- `upsType`: `String`

### `UPSDevice` (OBJECT)
- Fields (6):
- `battery`: `UPSBattery!`
- `id`: `ID!`
- `model`: `String!`
- `name`: `String!`
- `power`: `UPSPower!`
- `status`: `String!`

### `UPSKillPower` (ENUM)
Kill UPS power after shutdown option

- Enum values (2):
- `NO`
- `YES`

### `UPSPower` (OBJECT)
- Fields (5):
- `currentPower`: `Float`
- `inputVoltage`: `Float!`
- `loadPercentage`: `Int!`
- `nominalPower`: `Int`
- `outputVoltage`: `Float!`

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
- `id`: `PrefixedID!`
- `uiSchema`: `JSON!`
- `values`: `JSON!`

### `UnraidArray` (OBJECT)
- Implements: `Node`
- Fields (9):
- `boot`: `ArrayDisk`
- `bootDevices`: `[ArrayDisk!]!`
- `caches`: `[ArrayDisk!]!`
- `capacity`: `ArrayCapacity!`
- `disks`: `[ArrayDisk!]!`
- `id`: `PrefixedID!`
- `parities`: `[ArrayDisk!]!`
- `parityCheckStatus`: `ParityCheck!`
- `state`: `ArrayState!`

### `UnraidPluginsMutations` (OBJECT)
Unraid plugin management mutations

- Fields (2):
- `installLanguage`: `PluginInstallOperation!`
- `installPlugin`: `PluginInstallOperation!`

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
- `values`: `JSON!`
- `warnings`: `[String!]`

### `UpdateSshInput` (INPUT_OBJECT)
- Input fields (2):
- `enabled`: `Boolean!`
- `port`: `Int!`

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
- `ntpServers`: `[String!]`
- `timeZone`: `String`
- `useNtp`: `Boolean`

### `Uptime` (OBJECT)
- Fields (1):
- `timestamp`: `String`

### `UserAccount` (OBJECT)
- Implements: `Node`
- Fields (5):
- `description`: `String!`
- `id`: `PrefixedID!`
- `name`: `String!`
- `permissions`: `[Permission!]`
- `roles`: `[Role!]!`

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
- `fsNumMounted`: `Int`
- `fsNumUnmountable`: `Int`
- `fsProgress`: `String`
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
- `nrRequests`: `Int`
- `nrRequestsDefault`: `Int`
- `nrRequestsStatus`: `String`
- `ntpServer1`: `String`
- `ntpServer2`: `String`
- `ntpServer3`: `String`
- `ntpServer4`: `String`
- `pollAttributes`: `String`
- `pollAttributesDefault`: `String`
- `pollAttributesStatus`: `String`
- `port`: `Int`
- `portssh`: `Int`
- `portssl`: `Int`
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
- `shareAfpEnabled`: `Boolean`
- `shareAvahiAfpModel`: `String`
- `shareAvahiAfpName`: `String`
- `shareAvahiEnabled`: `Boolean`
- `shareAvahiSmbModel`: `String`
- `shareAvahiSmbName`: `String`
- `shareCacheEnabled`: `Boolean`
- `shareCacheFloor`: `String`
- `shareCount`: `Int`
- `shareDisk`: `String`
- `shareInitialGroup`: `String`
- `shareInitialOwner`: `String`
- `shareMoverActive`: `Boolean`
- `shareMoverLogging`: `Boolean`
- `shareMoverSchedule`: `String`
- `shareNfsCount`: `Int`
- `shareNfsEnabled`: `Boolean`
- `shareSmbCount`: `Int`
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
- `useSsh`: `Boolean`
- `useSsl`: `Boolean`
- `useTelnet`: `Boolean`
- `version`: `String`
- `workgroup`: `String`

### `VmDomain` (OBJECT)
- Implements: `Node`
- Fields (4):
- `id`: `PrefixedID!`
- `name`: `String`
- `state`: `VmState!`
- `uuid`: `String`

### `VmMutations` (OBJECT)
- Fields (7):
- `forceStop`: `Boolean!`
- `pause`: `Boolean!`
- `reboot`: `Boolean!`
- `reset`: `Boolean!`
- `resume`: `Boolean!`
- `start`: `Boolean!`
- `stop`: `Boolean!`

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
