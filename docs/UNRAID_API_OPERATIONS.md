# Unraid GraphQL API Operations

Generated via live introspection at `2026-02-15 23:45:50Z`.

## Schema Summary
- Query root: `Query`
- Mutation root: `Mutation`
- Subscription root: `Subscription`
- Total types: **164**
- Total directives: **6**
- Type kinds:
- `ENUM`: 32
- `INPUT_OBJECT`: 16
- `INTERFACE`: 2
- `OBJECT`: 103
- `SCALAR`: 10
- `UNION`: 1

## Queries
Total: **46**

### `apiKey(id: PrefixedID!): ApiKey`
#### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**

Arguments:
- `id`: `PrefixedID!`

### `apiKeyPossiblePermissions(): [Permission!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible permissions for API keys

### `apiKeyPossibleRoles(): [Role!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: All possible roles for API keys

### `apiKeys(): [ApiKey!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY**

### `array(): UnraidArray!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**

### `config(): Config!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG**

### `customization(): Customization`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CUSTOMIZATIONS**

### `disk(id: PrefixedID!): Disk!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**

Arguments:
- `id`: `PrefixedID!`

### `disks(): [Disk!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **DISK**

### `docker(): Docker!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **DOCKER**

### `flash(): Flash!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**

### `getApiKeyCreationFormSchema(): ApiKeyFormSettings!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **API_KEY** #### Description: Get JSON Schema for API key creation form

### `getAvailableAuthActions(): [AuthAction!]!`
Get all available authentication actions with possession

### `getPermissionsForRoles(roles: [Role!]!): [Permission!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Get the actual permissions that would be granted by a set of roles

Arguments:
- `roles`: `[Role!]!`

### `info(): Info!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**

### `isInitialSetup(): Boolean!`
### `isSSOEnabled(): Boolean!`
### `logFile(lines: Int, path: String!, startLine: Int): LogFileContent!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**

Arguments:
- `lines`: `Int`
- `path`: `String!`
- `startLine`: `Int`

### `logFiles(): [LogFile!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**

### `me(): UserAccount!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ME**

### `metrics(): Metrics!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**

### `notifications(): Notifications!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS** #### Description: Get all notifications

### `oidcConfiguration(): OidcConfiguration!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get the full OIDC configuration (admin only)

### `oidcProvider(id: PrefixedID!): OidcProvider`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get a specific OIDC provider by ID

Arguments:
- `id`: `PrefixedID!`

### `oidcProviders(): [OidcProvider!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Get all configured OIDC providers (admin only)

### `online(): Boolean!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ONLINE**

### `owner(): Owner!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**

### `parityHistory(): [ParityCheck!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**

### `plugins(): [Plugin!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: List all installed plugins with their metadata

### `previewEffectivePermissions(permissions: [AddPermissionInput!], roles: [Role!]): [Permission!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **PERMISSION** #### Description: Preview the effective permissions for a combination of roles and explicit permissions

Arguments:
- `permissions`: `[AddPermissionInput!]`
- `roles`: `[Role!]`

### `publicOidcProviders(): [PublicOidcProvider!]!`
Get public OIDC provider information for login buttons

### `publicPartnerInfo(): PublicPartnerInfo`
### `publicTheme(): Theme!`
### `rclone(): RCloneBackupSettings!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **FLASH**

### `registration(): Registration`
#### Required Permissions: - Action: **READ_ANY** - Resource: **REGISTRATION**

### `server(): Server`
#### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**

### `servers(): [Server!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**

### `services(): [Service!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **SERVICES**

### `settings(): Settings!`
### `shares(): [Share!]!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **SHARE**

### `upsConfiguration(): UPSConfiguration!`
### `upsDeviceById(id: String!): UPSDevice`
Arguments:
- `id`: `String!`

### `upsDevices(): [UPSDevice!]!`
### `validateOidcSession(token: String!): OidcSessionValidation!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **CONFIG** #### Description: Validate an OIDC session token (internal use for CLI validation)

Arguments:
- `token`: `String!`

### `vars(): Vars!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **VARS**

### `vms(): Vms!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **VMS** #### Description: Get information about all VMs on the system

## Mutations
Total: **22**

### `addPlugin(input: PluginManagementInput!): Boolean!`
#### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG** #### Description: Add one or more plugins to the API. Returns false if restart was triggered automatically, true if manual restart is required.

Arguments:
- `input`: `PluginManagementInput!`

### `apiKey(): ApiKeyMutations!`
### `archiveAll(importance: NotificationImportance): NotificationOverview!`
Arguments:
- `importance`: `NotificationImportance`

### `archiveNotification(id: PrefixedID!): Notification!`
Marks a notification as archived.

Arguments:
- `id`: `PrefixedID!`

### `archiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
Arguments:
- `ids`: `[PrefixedID!]!`

### `array(): ArrayMutations!`
### `configureUps(config: UPSConfigInput!): Boolean!`
Arguments:
- `config`: `UPSConfigInput!`

### `createNotification(input: NotificationData!): Notification!`
Creates a new notification record

Arguments:
- `input`: `NotificationData!`

### `customization(): CustomizationMutations!`
### `deleteArchivedNotifications(): NotificationOverview!`
Deletes all archived notifications on server.

### `deleteNotification(id: PrefixedID!, type: NotificationType!): NotificationOverview!`
Arguments:
- `id`: `PrefixedID!`
- `type`: `NotificationType!`

### `docker(): DockerMutations!`
### `initiateFlashBackup(input: InitiateFlashBackupInput!): FlashBackupStatus!`
Initiates a flash drive backup using a configured remote.

Arguments:
- `input`: `InitiateFlashBackupInput!`

### `parityCheck(): ParityCheckMutations!`
### `rclone(): RCloneMutations!`
### `recalculateOverview(): NotificationOverview!`
Reads each notification to recompute & update the overview.

### `removePlugin(input: PluginManagementInput!): Boolean!`
#### Required Permissions: - Action: **DELETE_ANY** - Resource: **CONFIG** #### Description: Remove one or more plugins from the API. Returns false if restart was triggered automatically, true if manual restart is required.

Arguments:
- `input`: `PluginManagementInput!`

### `unarchiveAll(importance: NotificationImportance): NotificationOverview!`
Arguments:
- `importance`: `NotificationImportance`

### `unarchiveNotifications(ids: [PrefixedID!]!): NotificationOverview!`
Arguments:
- `ids`: `[PrefixedID!]!`

### `unreadNotification(id: PrefixedID!): Notification!`
Marks a notification as unread.

Arguments:
- `id`: `PrefixedID!`

### `updateSettings(input: JSON!): UpdateSettingsResponse!`
#### Required Permissions: - Action: **UPDATE_ANY** - Resource: **CONFIG**

Arguments:
- `input`: `JSON!`

### `vm(): VmMutations!`
## Subscriptions
Total: **11**

### `arraySubscription(): UnraidArray!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**

### `logFile(path: String!): LogFileContent!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **LOGS**

Arguments:
- `path`: `String!`

### `notificationAdded(): Notification!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**

### `notificationsOverview(): NotificationOverview!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **NOTIFICATIONS**

### `ownerSubscription(): Owner!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **OWNER**

### `parityHistorySubscription(): ParityCheck!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **ARRAY**

### `serversSubscription(): Server!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **SERVERS**

### `systemMetricsCpu(): CpuUtilization!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**

### `systemMetricsCpuTelemetry(): CpuPackages!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**

### `systemMetricsMemory(): MemoryUtilization!`
#### Required Permissions: - Action: **READ_ANY** - Resource: **INFO**

### `upsUpdates(): UPSDevice!`
