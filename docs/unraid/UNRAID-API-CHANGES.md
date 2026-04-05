# Unraid API Schema Changes

> Generated on 2026-04-05T12:03:27+00:00
> Source: https://10-1-0-2.95d289568cc4a4bdc8e0d50284d6f455ec0eae5f.myunraid.net:31337/graphql

## Query fields

- Added: 13
  - `assignableDisks`
  - `cloud`
  - `connect`
  - `display`
  - `installedUnraidPlugins`
  - `internalBootContext`
  - `isFreshInstall`
  - `network`
  - `pluginInstallOperation`
  - `pluginInstallOperations`
  - `remoteAccess`
  - `systemTime`
  - `timeZoneOptions`
- Removed: 2
  - `isInitialSetup`
  - `publicPartnerInfo`

## Mutation fields

- Added: 23
  - `connectSignIn`
  - `connectSignOut`
  - `createDockerFolder`
  - `createDockerFolderWithItems`
  - `deleteDockerEntries`
  - `enableDynamicRemoteAccess`
  - `moveDockerEntriesToFolder`
  - `moveDockerItemsToPosition`
  - `notifyIfUnique`
  - `onboarding`
  - `refreshDockerDigests`
  - `renameDockerFolder`
  - `resetDockerTemplateMappings`
  - `setDockerFolderChildren`
  - `setupRemoteAccess`
  - `syncDockerTemplatePaths`
  - `unraidPlugins`
  - `updateApiSettings`
  - `updateDockerViewPreferences`
  - `updateServerIdentity`
  - `updateSshSettings`
  - `updateSystemTime`
  - `updateTemperatureConfig`
- Removed: 0

## Subscription fields

- Added: 5
  - `displaySubscription`
  - `dockerContainerStats`
  - `notificationsWarningsAndAlerts`
  - `pluginInstallUpdates`
  - `systemMetricsTemperature`
- Removed: 0

## Type Changes

### ENUM

- Added: 10
  - `DynamicRemoteAccessType`
  - `MinigraphStatus`
  - `OnboardingStatus`
  - `PluginInstallStatus`
  - `SensorType`
  - `TemperatureStatus`
  - `TemperatureUnit`
  - `URL_TYPE`
  - `WAN_ACCESS_TYPE`
  - `WAN_FORWARD_TYPE`
- Removed: 0

### INPUT_OBJECT

- Added: 27
  - `AccessUrlInput`
  - `AccessUrlObjectInput`
  - `ActivationCodeOverrideInput`
  - `BrandingConfigInput`
  - `ConnectSettingsInput`
  - `ConnectSignInInput`
  - `ConnectUserInfoInput`
  - `CreateInternalBootPoolInput`
  - `DockerAutostartEntryInput`
  - `EnableDynamicRemoteAccessInput`
  - `InstallPluginInput`
  - `IpmiConfigInput`
  - `LmSensorsConfigInput`
  - `OnboardingOverrideCompletionInput`
  - `OnboardingOverrideInput`
  - `PartnerConfigInput`
  - `PartnerInfoOverrideInput`
  - `PartnerLinkInput`
  - `SensorConfigInput`
  - `SetupRemoteAccessInput`
  - `SystemConfigInput`
  - `TemperatureConfigInput`
  - `TemperatureHistoryConfigInput`
  - `TemperatureSensorsConfigInput`
  - `TemperatureThresholdsConfigInput`
  - `UpdateSshInput`
  - `UpdateSystemTimeInput`
- Removed: 0

### OBJECT

- Added: 50
  - `AccessUrl`
  - `AccessUrlObject`
  - `ApiKeyResponse`
  - `BrandingConfig`
  - `Cloud`
  - `CloudResponse`
  - `Connect`
  - `ConnectSettings`
  - `ConnectSettingsValues`
  - `DockerContainerLogLine`
  - `DockerContainerLogs`
  - `DockerContainerPortConflict`
  - `DockerContainerStats`
  - `DockerLanPortConflict`
  - `DockerPortConflictContainer`
  - `DockerPortConflicts`
  - `DockerTemplateSyncResult`
  - `DynamicRemoteAccessStatus`
  - `FlatOrganizerEntry`
  - `InfoNetworkInterface`
  - `IpmiConfig`
  - `Language`
  - `LmSensorsConfig`
  - `MinigraphqlResponse`
  - `Network`
  - `Onboarding`
  - `OnboardingInternalBootContext`
  - `OnboardingInternalBootResult`
  - `OnboardingMutations`
  - `OnboardingState`
  - `PartnerConfig`
  - `PartnerLink`
  - `PluginInstallEvent`
  - `PluginInstallOperation`
  - `RelayResponse`
  - `RemoteAccess`
  - `SensorConfig`
  - `SystemConfig`
  - `SystemTime`
  - `TailscaleExitNodeStatus`
  - `TailscaleStatus`
  - `TemperatureHistoryConfig`
  - `TemperatureMetrics`
  - `TemperatureReading`
  - `TemperatureSensor`
  - `TemperatureSensorsConfig`
  - `TemperatureSummary`
  - `TemperatureThresholdsConfig`
  - `TimeZoneOption`
  - `UnraidPluginsMutations`
- Removed: 4
  - `OrganizerContainerResource`
  - `OrganizerResource`
  - `PublicPartnerInfo`
  - `ResolvedOrganizerFolder`

### SCALAR

- Added: 1
  - `URL`
- Removed: 0

### UNION

- Added: 0
- Removed: 1
  - `ResolvedOrganizerEntry`

## Type Signature Changes

### `ActivationCode` (OBJECT)

- Added members: 3
  - `branding(): BrandingConfig`
  - `partner(): PartnerConfig`
  - `system(): SystemConfig`
- Removed members: 10
  - `background(): String`
  - `comment(): String`
  - `header(): String`
  - `headermetacolor(): String`
  - `partnerName(): String`
  - `partnerUrl(): String`
  - `serverName(): String`
  - `showBannerGradient(): Boolean`
  - `sysModel(): String`
  - `theme(): String`

### `ArrayDiskType` (ENUM)

- Added members: 1
  - `BOOT`
- Removed members: 0

### `ArrayStateInput` (INPUT_OBJECT)

- Added members: 2
  - `decryptionKeyfile: String`
  - `decryptionPassword: String`
- Removed members: 0

### `ContainerState` (ENUM)

- Added members: 1
  - `PAUSED`
- Removed members: 0

### `Customization` (OBJECT)

- Added members: 2
  - `availableLanguages(): [Language!]`
  - `onboarding(): Onboarding!`
- Removed members: 2
  - `partnerInfo(): PublicPartnerInfo`
  - `theme(): Theme!`

### `CustomizationMutations` (OBJECT)

- Added members: 1
  - `setLocale(locale: String!): String!`
- Removed members: 0

### `Docker` (OBJECT)

- Added members: 7
  - `container(id: PrefixedID!): DockerContainer`
  - `containerUpdateStatuses(): [ExplicitStatusItem!]!`
  - `containers(): [DockerContainer!]!`
  - `logs(id: PrefixedID!, since: DateTime, tail: Int): DockerContainerLogs!`
  - `networks(): [DockerNetwork!]!`
  - `organizer(): ResolvedOrganizerV1!`
  - `portConflicts(): DockerPortConflicts!`
- Removed members: 2
  - `containers(skipCache: Boolean! = false): [DockerContainer!]!`
  - `networks(skipCache: Boolean! = false): [DockerNetwork!]!`

### `DockerContainer` (OBJECT)

- Added members: 18
  - `autoStartOrder(): Int`
  - `autoStartWait(): Int`
  - `iconUrl(): String`
  - `isOrphaned(): Boolean!`
  - `isRebuildReady(): Boolean`
  - `isUpdateAvailable(): Boolean`
  - `lanIpPorts(): [String!]`
  - `projectUrl(): String`
  - `registryUrl(): String`
  - `shell(): String`
  - `sizeLog(): BigInt`
  - `sizeRw(): BigInt`
  - `supportUrl(): String`
  - `tailscaleEnabled(): Boolean!`
  - `tailscaleStatus(forceRefresh: Boolean = false): TailscaleStatus`
  - `templatePath(): String`
  - `templatePorts(): [ContainerPort!]`
  - `webUiUrl(): String`
- Removed members: 0

### `DockerMutations` (OBJECT)

- Added members: 7
  - `pause(id: PrefixedID!): DockerContainer!`
  - `removeContainer(id: PrefixedID!, withImage: Boolean): Boolean!`
  - `unpause(id: PrefixedID!): DockerContainer!`
  - `updateAllContainers(): [DockerContainer!]!`
  - `updateAutostartConfiguration(entries: [DockerAutostartEntryInput!]!, persistUserPreferences: Boolean): Boolean!`
  - `updateContainer(id: PrefixedID!): DockerContainer!`
  - `updateContainers(ids: [PrefixedID!]!): [DockerContainer!]!`
- Removed members: 0

### `Info` (OBJECT)

- Added members: 2
  - `networkInterfaces(): [InfoNetworkInterface!]!`
  - `primaryNetwork(): InfoNetworkInterface`
- Removed members: 0

### `Metrics` (OBJECT)

- Added members: 1
  - `temperature(): TemperatureMetrics`
- Removed members: 0

### `Mutation` (OBJECT)

- Added members: 23
  - `connectSignIn(input: ConnectSignInInput!): Boolean!`
  - `connectSignOut(): Boolean!`
  - `createDockerFolder(childrenIds: [String!], name: String!, parentId: String): ResolvedOrganizerV1!`
  - `createDockerFolderWithItems(name: String!, parentId: String, position: Float, sourceEntryIds: [String!]): ResolvedOrganizerV1!`
  - `deleteDockerEntries(entryIds: [String!]!): ResolvedOrganizerV1!`
  - `enableDynamicRemoteAccess(input: EnableDynamicRemoteAccessInput!): Boolean!`
  - `moveDockerEntriesToFolder(destinationFolderId: String!, sourceEntryIds: [String!]!): ResolvedOrganizerV1!`
  - `moveDockerItemsToPosition(destinationFolderId: String!, position: Float!, sourceEntryIds: [String!]!): ResolvedOrganizerV1!`
  - `notifyIfUnique(input: NotificationData!): Notification`
  - `onboarding(): OnboardingMutations!`
  - `refreshDockerDigests(): Boolean!`
  - `renameDockerFolder(folderId: String!, newName: String!): ResolvedOrganizerV1!`
  - `resetDockerTemplateMappings(): Boolean!`
  - `setDockerFolderChildren(childrenIds: [String!]!, folderId: String): ResolvedOrganizerV1!`
  - `setupRemoteAccess(input: SetupRemoteAccessInput!): Boolean!`
  - `syncDockerTemplatePaths(): DockerTemplateSyncResult!`
  - `unraidPlugins(): UnraidPluginsMutations!`
  - `updateApiSettings(input: ConnectSettingsInput!): ConnectSettingsValues!`
  - `updateDockerViewPreferences(prefs: JSON!, viewId: String = "default"): ResolvedOrganizerV1!`
  - `updateServerIdentity(comment: String, name: String!, sysModel: String): Server!`
  - `updateSshSettings(input: UpdateSshInput!): Vars!`
  - `updateSystemTime(input: UpdateSystemTimeInput!): SystemTime!`
  - `updateTemperatureConfig(input: TemperatureConfigInput!): Boolean!`
- Removed members: 0

### `Notifications` (OBJECT)

- Added members: 1
  - `warningsAndAlerts(): [Notification!]!`
- Removed members: 0

### `Query` (OBJECT)

- Added members: 13
  - `assignableDisks(): [Disk!]!`
  - `cloud(): Cloud!`
  - `connect(): Connect!`
  - `display(): InfoDisplay!`
  - `installedUnraidPlugins(): [String!]!`
  - `internalBootContext(): OnboardingInternalBootContext!`
  - `isFreshInstall(): Boolean!`
  - `network(): Network!`
  - `pluginInstallOperation(operationId: ID!): PluginInstallOperation`
  - `pluginInstallOperations(): [PluginInstallOperation!]!`
  - `remoteAccess(): RemoteAccess!`
  - `systemTime(): SystemTime!`
  - `timeZoneOptions(): [TimeZoneOption!]!`
- Removed members: 2
  - `isInitialSetup(): Boolean!`
  - `publicPartnerInfo(): PublicPartnerInfo`

### `ResolvedOrganizerView` (OBJECT)

- Added members: 2
  - `flatEntries(): [FlatOrganizerEntry!]!`
  - `rootId(): String!`
- Removed members: 1
  - `root(): ResolvedOrganizerEntry!`

### `Server` (OBJECT)

- Added members: 1
  - `comment(): String`
- Removed members: 0

### `Subscription` (OBJECT)

- Added members: 5
  - `displaySubscription(): InfoDisplay!`
  - `dockerContainerStats(): DockerContainerStats!`
  - `notificationsWarningsAndAlerts(): [Notification!]!`
  - `pluginInstallUpdates(operationId: ID!): PluginInstallEvent!`
  - `systemMetricsTemperature(): TemperatureMetrics`
- Removed members: 0

### `UPSPower` (OBJECT)

- Added members: 2
  - `currentPower(): Float`
  - `nominalPower(): Int`
- Removed members: 0

### `UnraidArray` (OBJECT)

- Added members: 1
  - `bootDevices(): [ArrayDisk!]!`
- Removed members: 0

### `Vars` (OBJECT)

- Added members: 5
  - `bootEligible(): Boolean`
  - `bootedFromFlashWithInternalBootSetup(): Boolean`
  - `enableBootTransfer(): String`
  - `reservedNames(): String`
  - `tpmGuid(): String`
- Removed members: 0
