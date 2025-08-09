# Missing Unraid API Features

This document details the comprehensive analysis of Unraid API capabilities that are **NOT** currently implemented in our MCP server, based on investigation of the official Unraid API repository (https://github.com/unraid/api).

## Current Implementation Status

### ✅ What We HAVE Implemented
- Basic system info, array status, physical disks
- Docker container listing/management/details
- VM listing/management/details  
- Basic notification overview/listing
- Log file listing/content retrieval
- User shares information
- Network configuration, registration, and Connect settings
- Unraid variables and system health check

### ❌ What We're MISSING

---

## 1. GraphQL Mutations (Server Control Operations)

### Array Management Mutations
- **`array.setState(input: ArrayStateInput)`** - Start/stop the Unraid array
- **`array.addDiskToArray(input: ArrayDiskInput)`** - Add disk to array
- **`array.removeDiskFromArray(input: ArrayDiskInput)`** - Remove disk from array (requires stopped array)

### Parity Check Mutations
- **`parityCheck.start(correct: boolean)`** - Start parity check with optional correction
- **`parityCheck.pause()`** - Pause ongoing parity check
- **`parityCheck.resume()`** - Resume paused parity check

### Enhanced VM Management Mutations
- **`vm.pause(id: PrefixedID)`** - Pause running VM
- **`vm.resume(id: PrefixedID)`** - Resume paused VM
- *(We have start/stop, missing pause/resume)*

### RClone Remote Management
- **`rclone.createRCloneRemote(input: CreateRCloneRemoteInput)`** - Create new RClone remote
- **`rclone.deleteRCloneRemote(input: DeleteRCloneRemoteInput)`** - Delete RClone remote

### Settings & Configuration Management
- **`updateSettings(input: JSON!)`** - Update server settings with validation
  - **`api`** namespace: `sandbox` (boolean), `ssoSubIds` (string[]), `extraOrigins` (string[])
  - **`connect`** namespace: `accessType` (string), `port` (number|null), `forwardType` (string)
  - **Plugin namespaces**: Dynamic settings from installed plugins
- **`setAdditionalAllowedOrigins(input: AllowedOriginInput!)`** - Configure API allowed origins
- **`setupRemoteAccess(input: SetupRemoteAccessInput!)`** - Configure remote access settings

### Unraid Connect Authentication
- **`connectSignIn(input: ConnectSignInInput!)`** - Sign in to Unraid Connect
- **`connectSignOut()`** - Sign out from Unraid Connect

### Advanced Notification Management
- **`archiveNotification(id: PrefixedID!)`** - Archive specific notification
- **`archiveAllNotifications()`** - Archive all unread notifications
- **`deleteNotification(id: PrefixedID!, type: NotificationType!)`** - Delete specific notification
- **`deleteArchivedNotifications()`** - Delete all archived notifications
- **`recalculateOverview()`** - Recompute notification overview counts

### API Key Management
- **`apiKey.create(input: CreateApiKeyInput!)`** - Create new API key with roles/permissions
- **`apiKey.delete(input: DeleteApiKeyInput!)`** - Delete existing API key

---

## 2. GraphQL Queries (Information Retrieval)

### Enhanced System Information
- **`cloud`** - Cloud connection status, API key validity, allowed origins
- **`servers`** - List of registered multi-server setups via **Unraid Connect**
  - Provides centralized management of multiple Unraid servers through cloud connectivity
  - Returns: server identification, system info, status, configuration data
  - Enables "one-stop shop" server management, monitoring, and maintenance
- **`publicTheme`** - Current theme settings (colors, branding, etc.)
- **`extraAllowedOrigins`** - Additional configured allowed origins
- **`remoteAccess`** - Remote access configuration details
- **`publicPartnerInfo`** - Partner/OEM branding information
- **`customization.activationCode`** - Activation code and customization details
- **`apiKeyPossibleRoles`** and **`apiKeyPossiblePermissions`** - Available API key roles and permissions
- **`settings.unified`** - Unified settings with JSON schema validation

### RClone Configuration
- **`rclone.configForm(formOptions: RCloneConfigFormInput)`** - Get RClone configuration form schema
- **`rclone.remotes`** - List all configured RClone remotes with parameters

### Enhanced Log Management
- Better log file metadata (size, modification timestamps) - we have basic implementation but missing some fields

---

## 3. GraphQL Subscriptions (Real-time Updates)

**We have ZERO subscription capabilities implemented.** All of these provide real-time updates:

### Core Infrastructure Monitoring
- **`arraySubscription`** - Real-time array status changes (critical for storage monitoring)
- **`infoSubscription`** - System information updates (CPU, memory, uptime changes)
- **`parityHistorySubscription`** - Parity check progress and status updates

### Application & Service Monitoring  
- **`logFile(path: String!)`** - Real-time log file content streaming
- **`notificationAdded`** - New notification events
- **`notificationsOverview`** - Live notification count changes

### Advanced System Monitoring
- **`displaySubscription`** - Display-related information updates
- **`ownerSubscription`** - Owner profile/status changes
- **`registrationSubscription`** - Registration status changes (API key updates, etc.)
- **`serversSubscription`** - Multi-server status updates

### Events & General Updates
- **`events`** - General system events including client connections

---

## 4. Priority Implementation Recommendations

### **HIGH PRIORITY** (Critical for Infrastructure Management)
1. **Array Control Mutations** - `setState`, `addDisk`, `removeDisk`
2. **Parity Operations** - `start`, `pause`, `resume` parity checks
3. **Real-time Subscriptions** - `arraySubscription`, `infoSubscription`, `parityHistorySubscription`
4. **Enhanced Notification Management** - Archive, delete operations

### **MEDIUM PRIORITY** (Valuable for Administration)
1. **RClone Management** - Create, delete, list remotes
2. **Settings Management** - Update server configurations
3. **API Key Management** - Create, delete keys
4. **Real-time Log Streaming** - `logFile` subscription

### **LOW PRIORITY** (Nice to Have)
1. **Connect Authentication** - Sign in/out operations
2. **Enhanced System Queries** - Cloud status, themes, partner info
3. **Advanced VM Operations** - Pause/resume VMs
4. **Multi-server Support** - Server listing and management

---

## 5. Implementation Strategy

### Phase 1: Core Operations (Highest Value)
- Implement array control mutations
- Add parity check operations
- Create subscription-to-resource framework for real-time monitoring

### Phase 2: Enhanced Management
- RClone remote management
- Advanced notification operations
- Settings management

### Phase 3: Advanced Features
- API key management
- Connect authentication
- Multi-server capabilities

---

## 6. Technical Notes

### GraphQL Schema Migration Status
According to the Unraid API repository:
- **Docker Resolver**: Still needs migration to code-first approach
- **Disks Resolver**: Still needs migration to code-first approach  
- **API Key Operations**: Mentioned in docs but GraphQL mutations not fully defined in context

### Authentication Requirements
Most mutations require:
- Valid API key in `x-api-key` header
- Appropriate role-based permissions
- Some operations may require `admin` role

### Real-time Capabilities
The Unraid API uses:
- GraphQL subscriptions over WebSocket
- PubSub event system for real-time updates
- Domain event bus architecture

---

## 7. Impact Assessment

Implementing these missing features would:
- **Dramatically increase** our MCP server's capabilities
- **Enable full remote management** of Unraid servers
- **Provide real-time monitoring** through MCP resources
- **Support automation and orchestration** workflows
- **Match feature parity** with the official Unraid API

The subscription-to-resource approach would be particularly powerful, making our MCP server one of the most capable infrastructure monitoring tools available in the MCP ecosystem.