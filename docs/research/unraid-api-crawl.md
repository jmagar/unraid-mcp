# Unraid API Documentation Crawl - Complete Content

**Date:** 2026-02-07
**Source:** Firecrawl deep crawl of official Unraid documentation, blog, and community resources
**Vector DB:** All content auto-embedded to Qdrant (firecrawl collection)

---

## Table of Contents

1. [API Documentation (docs.unraid.net/API/)](#1-api-documentation)
   - [API Overview](#11-api-overview)
   - [How to Use the API](#12-how-to-use-the-api)
   - [CLI Reference](#13-cli-reference)
   - [API Key App Developer Authorization Flow](#14-api-key-app-developer-authorization-flow)
   - [Programmatic API Key Management](#15-programmatic-api-key-management)
   - [OIDC Provider Setup](#16-oidc-provider-setup)
   - [Upcoming Features / Roadmap](#17-upcoming-features--roadmap)
2. [Complete GraphQL Schema](#2-complete-graphql-schema)
   - [Root Types (Query, Mutation, Subscription)](#21-root-types)
   - [Resource Types](#22-resource-types)
   - [Enums and Scalars](#23-enums-and-scalars)
3. [Unraid Connect Documentation](#3-unraid-connect-documentation)
4. [Release Notes (API-Relevant)](#4-release-notes-api-relevant)
5. [Blog Posts](#5-blog-posts)
6. [Community Resources](#6-community-resources)
7. [Source URLs Index](#7-source-urls-index)

---

## 1. API Documentation

### 1.1 API Overview

**Source:** https://docs.unraid.net/API/

Starting with Unraid 7.2, the API comes built into the operating system -- no plugin installation required.

The Unraid API provides a **GraphQL interface** for programmatic interaction with your Unraid server. It enables automation, monitoring, and integration capabilities through a modern, strongly-typed API with:
- Multiple authentication methods (API keys, session cookies, and SSO/OIDC)
- Comprehensive system coverage
- Built-in developer tools

#### Availability

**Native integration (Unraid 7.2+):**
- No plugin installation required
- Automatically available on system startup
- Deep system integration
- Access through **Settings > Management Access > API**

**Plugin installation (Pre-7.2 and Advanced Users):**
1. Install the Unraid Connect plugin from Community Applications
2. Configure the plugin
3. Access API functionality through the GraphQL Sandbox

The Unraid Connect plugin provides the API for pre-7.2 versions. You do NOT need to sign in to Unraid Connect to use the API locally. Installing the plugin on Unraid 7.2+ gives you access to newer API features before they are included in OS releases.

#### Get Started (Unraid 7.2+)
1. The API is already installed and running.
2. Access settings at **Settings > Management Access > API**.
3. Enable the GraphQL Sandbox for development.
4. Create your first API key.
5. Start making GraphQL queries!

#### Get Started (Pre-7.2 Versions)
1. Install the Unraid Connect plugin from Community Applications.
2. No Unraid Connect login required for local API access.
3. Configure the plugin settings.
4. Enable the GraphQL Sandbox.
5. Start exploring the API!

---

### 1.2 How to Use the API

**Source:** https://docs.unraid.net/API/how-to-use-the-api/

The Unraid API provides a GraphQL interface that allows you to interact with your Unraid server. This guide covers authentication, common queries, and usage patterns.

#### Enabling the GraphQL Sandbox

**Live Documentation:**
- View the complete API schema and documentation at [Apollo GraphQL Studio](https://studio.apollographql.com/graph/Unraid-API/variant/current/home)

**WebGUI method (recommended):**
1. Navigate to **Settings > Management Access > Developer Options**
2. Enable the **GraphQL Sandbox** toggle
3. Access the GraphQL playground at: `http://YOUR_SERVER_IP/graphql`

**CLI method:**
```bash
unraid-api developer --sandbox true
```
Or use interactive mode:
```bash
unraid-api developer
```

#### Authentication

Most queries and mutations require authentication. You can authenticate using:
1. **API Keys** -- For programmatic access
2. **Cookies** -- Automatic when signed in to the WebGUI
3. **SSO/OIDC** -- When configured with external providers

**Managing API keys (WebGUI):**
Navigate to **Settings > Management Access > API Keys** to:
- View existing API keys
- Create new API keys
- Manage permissions and roles
- Revoke or regenerate keys

**Managing API keys (CLI):**
```bash
unraid-api apikey --create
```

**Using API keys:**
Include the generated API key in your GraphQL requests as a header:
```json
{
    "x-api-key": "YOUR_API_KEY"
}
```

#### Available Schemas

The API provides access to:
- **System information**: CPU, memory, OS info, system status and health, baseboard and hardware info
- **Array management**: Array status and configuration, start/stop operations, disk status and health, parity checks
- **Docker management**: List and manage Docker containers, monitor container status, manage Docker networks
- **Remote access**: Configure and manage remote access settings, SSO configuration, allowed origins

#### Example Queries

**Check system status:**
```graphql
query {
    info {
        os {
            platform
            distro
            release
            uptime
        }
        cpu {
            manufacturer
            brand
            cores
            threads
        }
    }
}
```

**Monitor array status:**
```graphql
query {
    array {
        state
        capacity {
            disks {
                free
                used
                total
            }
        }
        disks {
            name
            size
            status
            temp
        }
    }
}
```

**List Docker containers:**
```graphql
query {
    dockerContainers {
        id
        names
        state
        status
        autoStart
    }
}
```

#### Schema Types

**Base types:** `Node` (interface for objects with unique IDs), `JSON` (complex JSON data), `DateTime` (timestamp values), `Long` (64-bit integers)

**Resource types:** `Array` (array and disk management), `Docker` (container and network management), `Info` (system information), `Config` (server configuration), `Connect` (remote access settings)

**Available roles:** `admin` (full access), `connect` (remote access features), `guest` (limited read access)

#### Error Handling

The API returns standard GraphQL errors:
```json
{
  "errors": [
    {
      "message": "Error description",
      "locations": [...],
      "path": [...]
    }
  ]
}
```

The API implements rate limiting to prevent abuse.

---

### 1.3 CLI Reference

**Source:** https://docs.unraid.net/API/cli/

All commands follow the pattern: `unraid-api <command> [options]`.

#### Service Management

**Start:**
```bash
unraid-api start [--log-level <level>]
# Levels: trace|debug|info|warn|error|fatal
# Alternative: LOG_LEVEL=trace unraid-api start
```

**Stop:**
```bash
unraid-api stop [--delete]
# --delete: Optional. Delete the PM2 home directory.
```

**Restart:**
```bash
unraid-api restart [--log-level <level>]
```

**Logs:**
```bash
unraid-api logs [-l <lines>]
# -l, --lines: Number of lines to tail (default: 100)
```

#### Configuration Commands

**View config:**
```bash
unraid-api config
```

**Switch environment:**
```bash
unraid-api switch-env [-e <environment>]
# -e: production|staging
```

**Developer mode:**
```bash
unraid-api developer                       # Interactive prompt
unraid-api developer --sandbox true        # Enable GraphQL sandbox
unraid-api developer --sandbox false       # Disable GraphQL sandbox
unraid-api developer --enable-modal        # Enable modal testing tool
unraid-api developer --disable-modal       # Disable modal testing tool
```

Also available via WebGUI: **Settings > Management Access > Developer Options**

#### API Key Management

```bash
unraid-api apikey [options]
```

Options:
- `--name <name>`: Name of the key
- `--create`: Create a new key
- `-r, --roles <roles>`: Comma-separated list of roles
- `-p, --permissions <permissions>`: Comma-separated list of permissions
- `-d, --description <description>`: Description for the key

Also available via WebGUI: **Settings > Management Access > API Keys**

#### SSO (Single Sign-On) Management

```bash
unraid-api sso                    # Base command
unraid-api sso add-user           # Add SSO user (aliases: add, a)
unraid-api sso remove-user        # Remove SSO user (aliases: remove, r)
unraid-api sso list-users         # List SSO users (aliases: list, l)
unraid-api sso validate-token <token>  # Validate SSO token (aliases: validate, v)
```

#### Report Generation

```bash
unraid-api report [-r] [-j]
# -r, --raw: Display raw command output
# -j, --json: Display output in JSON format
```

---

### 1.4 API Key App Developer Authorization Flow

**Source:** https://docs.unraid.net/API/api-key-app-developer-authorization-flow/

Applications can request API access to an Unraid server by redirecting users to a special authorization page where users can review requested permissions and create an API key with one click.

#### Flow

1. **Application initiates request**: The app redirects the user to:
   ```
   https://[unraid-server]/ApiKeyAuthorize?name=MyApp&scopes=docker:read,vm:*&redirect_uri=https://myapp.com/callback&state=abc123
   ```

2. **User authentication**: If not already logged in, the user is redirected to login first (standard Unraid auth).

3. **Consent screen**: User sees:
   - Application name and description
   - Requested permissions (with checkboxes to approve/deny specific scopes)
   - API key name field (pre-filled)
   - Authorize & Cancel buttons

4. **API key creation**: Upon authorization:
   - API key is created with approved scopes.
   - Key is displayed to the user.
   - If `redirect_uri` is provided, user is redirected back with the key.

5. **Callback**: App receives the API key:
   ```
   https://myapp.com/callback?api_key=xxx&state=abc123
   ```

#### Query Parameters

- `name` (required): Name of the requesting application
- `description` (optional): Description of the application
- `scopes` (required): Comma-separated list of requested scopes
- `redirect_uri` (optional): URL to redirect after authorization
- `state` (optional): Opaque value for maintaining state

#### Scope Format

Scopes follow the pattern: `resource:action`.

**Examples:**
- `docker:read` -- read access to Docker
- `vm:*` -- full access to VMs
- `system:update` -- update access to system
- `role:viewer` -- viewer role access
- `role:admin` -- admin role access

**Available resources:** `docker`, `vm`, `system`, `share`, `user`, `network`, `disk`, and others.
**Available actions:** `create`, `read`, `update`, `delete`, or `*` for all.

**Security notes:**
- Redirect URIs must use HTTPS (except localhost for development)
- Users explicitly approve each permission
- The flow uses existing Unraid authentication sessions
- API keys are shown once and must be saved securely

#### Example Integration (JavaScript)

```javascript
const unraidServer = 'tower.local';
const appName = 'My Docker Manager';
const scopes = 'docker:*,system:read';
const redirectUri = 'https://myapp.com/unraid/callback';
const state = generateRandomState();

// Store state for verification
sessionStorage.setItem('oauth_state', state);

// Redirect user to authorization page
window.location.href =
    `https://${unraidServer}/ApiKeyAuthorize?` +
    `name=${encodeURIComponent(appName)}&` +
    `scopes=${encodeURIComponent(scopes)}&` +
    `redirect_uri=${encodeURIComponent(redirectUri)}&` +
    `state=${encodeURIComponent(state)}`;

// Handle callback
const urlParams = new URLSearchParams(window.location.search);
const apiKey = urlParams.get('api_key');
const returnedState = urlParams.get('state');

if (returnedState === sessionStorage.getItem('oauth_state')) {
    // Save API key securely
    saveApiKey(apiKey);
}
```

---

### 1.5 Programmatic API Key Management

**Source:** https://docs.unraid.net/API/programmatic-api-key-management/

Create, use, and delete API keys programmatically for automated workflows, CI/CD pipelines, temporary access provisioning, and infrastructure as code.

#### Creating API Keys

**Basic creation with JSON output:**
```bash
unraid-api apikey --create --name "workflow key" --roles ADMIN --json
```

Output:
```json
{
    "key": "your-generated-api-key-here",
    "name": "workflow key",
    "id": "generated-uuid"
}
```

**Advanced creation with permissions:**
```bash
unraid-api apikey --create \
  --name "limited access key" \
  --permissions "DOCKER:READ_ANY,ARRAY:READ_ANY" \
  --description "Read-only access for monitoring" \
  --json
```

**Handling existing keys (overwrite):**
```bash
unraid-api apikey --create --name "existing key" --roles ADMIN --overwrite --json
```

#### Deleting API Keys

```bash
# Non-interactive deletion by name
unraid-api apikey --delete --name "workflow key"

# JSON output for deletion
unraid-api apikey --delete --name "workflow key" --json
```

#### Available Roles

| Role | Description |
|------|-------------|
| `ADMIN` | Full system access |
| `CONNECT` | Unraid Connect features |
| `VIEWER` | Read-only access |
| `GUEST` | Limited access |

#### Available Resources

`ACTIVATION_CODE`, `API_KEY`, `ARRAY`, `CLOUD`, `CONFIG`, `CONNECT`, `CONNECT__REMOTE_ACCESS`, `CUSTOMIZATIONS`, `DASHBOARD`, `DISK`, `DISPLAY`, `DOCKER`, `FLASH`, `INFO`, `LOGS`, `ME`, `NETWORK`, `NOTIFICATIONS`, `ONLINE`, `OS`, `OWNER`, `PERMISSION`, `REGISTRATION`, `SERVERS`, `SERVICES`, `SHARE`, `VARS`, `VMS`, `WELCOME`

#### Available Actions

`CREATE_ANY`, `CREATE_OWN`, `READ_ANY`, `READ_OWN`, `UPDATE_ANY`, `UPDATE_OWN`, `DELETE_ANY`, `DELETE_OWN`

#### Complete Workflow Example (Temporary Access)

```bash
#!/bin/bash
set -e

# 1. Create temporary API key
echo "Creating temporary API key..."
KEY_DATA=$(unraid-api apikey --create \
  --name "temp deployment key" \
  --roles ADMIN \
  --description "Temporary key for deployment $(date)" \
  --json)

# 2. Extract the API key
API_KEY=$(echo "$KEY_DATA" | jq -r '.key')
echo "API key created successfully"

# 3. Use the key for operations
echo "Configuring services..."
curl -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"provider": "azure", "clientId": "your-client-id"}' \
  http://localhost:3001/graphql

# 4. Clean up (always runs, even on error)
trap 'echo "Cleaning up..."; unraid-api apikey --delete --name "temp deployment key"' EXIT

echo "Deployment completed successfully"
```

---

### 1.6 OIDC Provider Setup

**Source:** https://docs.unraid.net/API/oidc-provider-setup/

OpenID Connect (OIDC) enables Single Sign-On (SSO) for the Unraid API using external identity providers like Google, Microsoft, Authelia, Keycloak, Authentik, and Okta.

#### Quick Start

1. Navigate to **Settings > Management Access > API > OIDC**
2. Click the **+** button to add a new provider
3. Configure the provider settings

#### Required Redirect URI (ALL providers)

```
http://YOUR_UNRAID_IP/graphql/api/auth/oidc/callback
```

#### Authorization Modes

**Simple mode (recommended):**
- Allow specific email domains (e.g., @company.com)
- Allow specific email addresses
- Best for most users

**Advanced mode:**
- Create complex authorization rules based on JWT claims
- Operators: equals, contains, endsWith, startsWith
- Combine conditions with OR/AND logic
- Check group memberships, verify multiple claims

#### Provider-Specific Configuration

**Unraid.net (built-in):**
- Pre-configured, just set authorization rules

**Google:**
- Issuer URL: `https://accounts.google.com`
- Requires valid domain names for OAuth redirect URIs (no local IPs or .local domains)
- Options: Reverse Proxy, Tailscale (.ts.net), Dynamic DNS

**Authelia:**
- Issuer URL: `https://auth.yourdomain.com`
- Client ID: `unraid-api`
- Scopes: `openid`, `profile`, `email`, `groups`

**Microsoft/Azure AD:**
- Issuer URL: `https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0`

**Keycloak:**
- Issuer URL: `https://keycloak.example.com/realms/YOUR_REALM`

**Authentik:**
- Issuer URL: `https://authentik.example.com/application/o/<application_slug>/`

**Okta:**
- Issuer URL: `https://YOUR_DOMAIN.okta.com`

All providers require scopes: `openid`, `profile`, `email`

#### Issuer URL Format

Use the **base URL** (recommended for security):
- Base URL: `https://accounts.google.com` (recommended)
- Full discovery URL: `https://accounts.google.com/.well-known/openid-configuration` (not recommended)

---

### 1.7 Upcoming Features / Roadmap

**Source:** https://docs.unraid.net/API/upcoming-features/

#### Completed Features

| Feature | Available Since |
|---------|----------------|
| API Development Environment Improvements | v4.0.0 |
| Include API in Unraid OS | Unraid v7.2-beta.1 |
| Separate API from Connect Plugin | Unraid v7.2-beta.1 |
| Permissions System Rewrite | v4.0.0 |
| OIDC/SSO Support | Unraid v7.2-beta.1 |
| Array Status Monitoring | v4.0.0 |
| Docker Container Status Monitoring | v4.0.0 |
| Array/Cache Share Status Monitoring | v4.0.0 |
| Notifications System & Interface | v4.0.0 |

#### Upcoming / In Development

| Feature | Target Timeline |
|---------|----------------|
| Make API Open Source | Completed - open-sourced January 2025 (GitHub) |
| Developer Tools for Plugins | Q2 2025 |
| User Interface Component Library | In Development |
| New Settings Pages | Q2 2025 |
| Custom Theme Creator | Q2-Q3 2025 |
| New Connect Settings Interface | Q1 2025 |
| Storage Pool Creation/Status Interface | Q2 2025 |
| New Docker Status Interface Design | Q3 2025 |
| Docker Container Setup Interface | Q3 2025 |
| Docker Compose Support | TBD |
| New Plugins Interface | Q3 2025 |
| Plugin Development Tools | TBD |

#### Under Consideration

- Storage Share Creation & Settings
- Storage Share Management Interface

#### Version Support

| Unraid Version | API Version | Support Status |
|---------------|-------------|----------------|
| Unraid v7.2-beta.1+ | Latest | Active |
| 7.0 - 7.1.x | v4.x via Plugin | Limited |
| 6.12.x | v4.x via Plugin | Limited |
| < 6.12 | Not Supported | EOL |

#### GitHub Repository

- Open source: https://github.com/unraid/api
- Latest release: v4.29.2 (December 19, 2025)
- 102 releases total
- Language: TypeScript 77.4%, Vue 11.8%, PHP 5.6%, Shell 2.3%
- Stars: 95, Forks: 17

---

## 2. Complete GraphQL Schema

**Source:** https://github.com/domalab/unraid-api-client/blob/113c94f1/schema.graphql
**Reference:** https://deepwiki.com/domalab/unraid-api-client/7-graphql-schema-reference

The Unraid GraphQL API follows standard GraphQL conventions with three root types: Query (for fetching data), Mutation (for modifying data), and Subscription (for real-time updates).

### 2.1 Root Types

#### Query Type

```graphql
type Query {
    apiKeys: [ApiKey!]!
    apiKey(id: ID!): ApiKey
    array: Array!
    parityHistory: [ParityCheck]
    online: Boolean
    info: Info
    cloud: Cloud
    config: Config!
    remoteAccess: RemoteAccess!
    extraAllowedOrigins: [String!]!
    connect: Connect!
    disk(id: ID!): Disk
    disks: [Disk]!
    display: Display
    dockerContainers(all: Boolean): [DockerContainer!]!
    docker: Docker!
    dockerNetwork(id: ID!): DockerNetwork!
    dockerNetworks(all: Boolean): [DockerNetwork]!
    flash: Flash
    network: Network
    notifications: Notifications!
    owner: Owner
    registration: Registration
    server: Server
    servers: [Server!]!
    services: [Service!]!
    shares: [Share]
    unassignedDevices: [UnassignedDevice]
    me: Me
    user(id: ID!): User
    users(input: usersInput): [User!]!
    vars: Vars
    vms: Vms
}
```

#### Mutation Type

```graphql
type Mutation {
    createApiKey(input: CreateApiKeyInput!): ApiKeyWithSecret!
    addPermission(input: AddPermissionInput!): Boolean!
    addRoleForUser(input: AddRoleForUserInput!): Boolean!
    addRoleForApiKey(input: AddRoleForApiKeyInput!): Boolean!
    removeRoleFromApiKey(input: RemoveRoleFromApiKeyInput!): Boolean!
    startArray: Array
    stopArray: Array
    addDiskToArray(input: arrayDiskInput): Array
    removeDiskFromArray(input: arrayDiskInput): Array
    mountArrayDisk(id: ID!): Disk
    unmountArrayDisk(id: ID!): Disk
    clearArrayDiskStatistics(id: ID!): JSON
    startParityCheck(correct: Boolean): JSON
    pauseParityCheck: JSON
    resumeParityCheck: JSON
    cancelParityCheck: JSON
    login(username: String!, password: String!): String
    shutdown: String
    reboot: String
    connectSignIn(input: ConnectSignInInput!): Boolean!
    connectSignOut: Boolean!
    enableDynamicRemoteAccess(input: EnableDynamicRemoteAccessInput!): Boolean!
    setAdditionalAllowedOrigins(input: AllowedOriginInput!): [String!]!
    setupRemoteAccess(input: SetupRemoteAccessInput!): Boolean!
    createNotification(input: NotificationData!): Notification!
    deleteNotification(id: String!, type: NotificationType!): NotificationOverview!
    deleteArchivedNotifications: NotificationOverview!
    archiveNotification(id: String!): Notification!
    unreadNotification(id: String!): Notification!
    archiveNotifications(ids: [String!]): NotificationOverview!
    unarchiveNotifications(ids: [String!]): NotificationOverview!
    archiveAll(importance: Importance): NotificationOverview!
    unarchiveAll(importance: Importance): NotificationOverview!
    recalculateOverview: NotificationOverview!
    addUser(input: addUserInput!): User
    deleteUser(input: deleteUserInput!): User
}
```

#### Subscription Type

```graphql
type Subscription {
    array: Array!
    parityHistory: ParityCheck!
    ping: String!
    info: Info!
    online: Boolean!
    config: Config!
    display: Display
    dockerContainer(id: ID!): DockerContainer!
    dockerContainers: [DockerContainer]
    dockerNetwork(id: ID!): DockerNetwork!
    dockerNetworks: [DockerNetwork]!
    flash: Flash!
    notificationAdded: Notification!
    notificationsOverview: NotificationOverview!
    owner: Owner!
    registration: Registration!
    server: Server
    service(name: String!): [Service!]
    share(id: ID!): Share!
    shares: [Share!]
    unassignedDevices: [UnassignedDevice!]
    me: Me
    user(id: ID!): User!
    users: [User]!
    vars: Vars!
    vms: Vms
}
```

### 2.2 Resource Types

#### Permission & API Key Types

```graphql
type Permission {
    resource: Resource!
    actions: [String!]!
}

type ApiKey {
    id: ID!
    name: String!
    description: String
    roles: [Role!]!
    createdAt: DateTime!
    permissions: [Permission!]!
}

type ApiKeyWithSecret {
    id: ID!
    key: String!
    name: String!
    description: String
    roles: [Role!]!
    createdAt: DateTime!
    permissions: [Permission!]!
}

input CreateApiKeyInput {
    name: String!
    description: String
    roles: [Role!]
    permissions: [AddPermissionInput!]
    overwrite: Boolean
}
```

#### Array Type

```graphql
type Array implements Node {
    id: ID!
    previousState: ArrayState
    pendingState: ArrayPendingState
    state: ArrayState!
    capacity: ArrayCapacity!
    boot: ArrayDisk
    parities: [ArrayDisk!]!
    disks: [ArrayDisk!]!
    caches: [ArrayDisk!]!
}

type ArrayDisk {
    id: ID!
    idx: Int!
    name: String
    device: String
    size: Long!
    status: ArrayDiskStatus
    rotational: Boolean
    temp: Int
    numReads: Long!
    numWrites: Long!
    numErrors: Long!
    fsSize: Long
    fsFree: Long
    fsUsed: Long
    exportable: Boolean
    type: ArrayDiskType!
    warning: Int
    critical: Int
    fsType: String
    comment: String
    format: String
    transport: String
}

type ArrayCapacity {
    kilobytes: Capacity!
    disks: Capacity!
}

type Capacity {
    free: String!
    used: String!
    total: String!
}
```

#### Docker Types

```graphql
type DockerContainer {
    id: ID!
    names: [String!]
    image: String!
    imageId: String!
    command: String!
    created: Int!
    ports: [ContainerPort!]!
    sizeRootFs: Long
    labels: JSON
    state: ContainerState!
    status: String!
    hostConfig: ContainerHostConfig
    networkSettings: JSON
    mounts: [JSON]
    autoStart: Boolean!
}

type Docker implements Node {
    id: ID!
    containers: [DockerContainer!]
    networks: [DockerNetwork!]
}

type DockerNetwork {
    name: String
    id: ID
    created: String
    scope: String
    driver: String
    enableIPv6: Boolean!
    ipam: JSON
    internal: Boolean!
    attachable: Boolean!
    ingress: Boolean!
    configFrom: JSON
    configOnly: Boolean!
    containers: JSON
    options: JSON
    labels: JSON
}
```

#### Info (System Information) Type

```graphql
type Info implements Node {
    apps: InfoApps
    baseboard: Baseboard
    cpu: InfoCpu
    devices: Devices
    display: Display
    id: ID!
    machineId: ID
    memory: InfoMemory
    os: Os
    system: System
    time: DateTime!
    versions: Versions
}

type InfoCpu {
    manufacturer: String!
    brand: String!
    vendor: String!
    family: String!
    model: String!
    stepping: Int!
    revision: String!
    voltage: String
    speed: Float!
    speedmin: Float!
    speedmax: Float!
    threads: Int!
    cores: Int!
    processors: Long!
    socket: String!
    cache: JSON!
    flags: [String!]
}

type InfoMemory {
    max: Long!
    total: Long!
    free: Long!
    used: Long!
    active: Long!
    available: Long!
    buffcache: Long!
    swaptotal: Long!
    swapused: Long!
    swapfree: Long!
    layout: [MemoryLayout!]
}

type Os {
    platform: String
    distro: String
    release: String
    codename: String
    kernel: String
    arch: String
    hostname: String
    codepage: String
    logofile: String
    serial: String
    build: String
    uptime: DateTime
}
```

#### VM Types

```graphql
type Vms {
    id: ID!
    domain: [VmDomain!]
}

type VmDomain {
    uuid: ID!
    name: String
    state: VmState!
}
```

#### Network Type

```graphql
type Network implements Node {
    iface: String
    ifaceName: String
    ipv4: String
    ipv6: String
    mac: String
    internal: String
    operstate: String
    type: String
    duplex: String
    mtu: String
    speed: String
    carrierChanges: String
    id: ID!
    accessUrls: [AccessUrl!]
}
```

#### Share Type

```graphql
type Share {
    name: String
    free: Long
    used: Long
    size: Long
    include: [String]
    exclude: [String]
    cache: Boolean
    nameOrig: String
    comment: String
    allocator: String
    splitLevel: String
    floor: String
    cow: String
    color: String
    luksStatus: String
}
```

#### User Types

```graphql
interface UserAccount {
    id: ID!
    name: String!
    description: String!
    roles: [Role!]!
    permissions: [Permission!]
}

type Me implements UserAccount {
    id: ID!
    name: String!
    description: String!
    roles: [Role!]!
    permissions: [Permission!]
}

type User implements UserAccount {
    id: ID!
    name: String!
    description: String!
    roles: [Role!]!
    password: Boolean
    permissions: [Permission!]
}
```

#### Notification Types

```graphql
type Notifications implements Node {
    id: ID!
    overview: NotificationOverview!
    list(filter: NotificationFilter!): [Notification!]!
}

type Notification implements Node {
    id: ID!
    title: String!
    subject: String!
    description: String!
    importance: Importance!
    link: String
    type: NotificationType!
    timestamp: String
    formattedTimestamp: String
}

type NotificationOverview {
    unread: NotificationCounts!
    archive: NotificationCounts!
}

type NotificationCounts {
    info: Int!
    warning: Int!
    alert: Int!
    total: Int!
}
```

#### Vars Type (Server Configuration)

```graphql
type Vars implements Node {
    id: ID!
    version: String          # Unraid version
    maxArraysz: Int
    maxCachesz: Int
    name: String             # Machine hostname
    timeZone: String
    comment: String
    security: String
    workgroup: String
    domain: String
    useNtp: Boolean
    ntpServer1: String
    ntpServer2: String
    ntpServer3: String
    ntpServer4: String
    useSsl: Boolean
    port: Int                # WebUI HTTP port
    portssl: Int             # WebUI HTTPS port
    useTelnet: Boolean
    useSsh: Boolean
    portssh: Int
    startPage: String
    startArray: Boolean
    spindownDelay: String
    defaultFormat: String
    defaultFsType: String
    shutdownTimeout: Int
    shareDisk: String
    shareUser: String
    shareSmbEnabled: Boolean
    shareNfsEnabled: Boolean
    shareAfpEnabled: Boolean
    shareCacheEnabled: Boolean
    shareMoverSchedule: String
    shareMoverLogging: Boolean
    safeMode: Boolean
    configValid: Boolean
    configError: ConfigErrorState
    deviceCount: Int
    flashGuid: String
    flashProduct: String
    flashVendor: String
    regState: RegistrationState
    regTo: String            # Registration owner
    mdState: String
    mdNumDisks: Int
    mdNumDisabled: Int
    mdNumInvalid: Int
    mdNumMissing: Int
    mdResync: Int
    mdResyncAction: String
    fsState: String
    fsProgress: String       # Human friendly array events string
    fsCopyPrcnt: Int         # 0-100 for disk upgrade/swap
    shareCount: Int
    shareSmbCount: Int
    shareNfsCount: Int
    csrfToken: String
    # ... and many more fields
}
```

#### Cloud/Connect Types

```graphql
type Cloud {
    error: String
    apiKey: ApiKeyResponse!
    relay: RelayResponse
    minigraphql: MinigraphqlResponse!
    cloud: CloudResponse!
    allowedOrigins: [String!]!
}

type Connect implements Node {
    id: ID!
    dynamicRemoteAccess: DynamicRemoteAccessStatus!
}

type RemoteAccess {
    accessType: WAN_ACCESS_TYPE!
    forwardType: WAN_FORWARD_TYPE
    port: Port
}
```

#### Disk Type (Physical Disk)

```graphql
type Disk {
    device: String!
    type: String!
    name: String!
    vendor: String!
    size: Long!
    bytesPerSector: Long!
    totalCylinders: Long!
    totalHeads: Long!
    totalSectors: Long!
    totalTracks: Long!
    tracksPerCylinder: Long!
    sectorsPerTrack: Long!
    firmwareRevision: String!
    serialNum: String!
    interfaceType: DiskInterfaceType!
    smartStatus: DiskSmartStatus!
    temperature: Long!
    partitions: [DiskPartition!]
}
```

### 2.3 Enums and Scalars

#### Scalar Types

| Scalar | Description |
|--------|-------------|
| `JSON` | Complex JSON data structures |
| `Long` | 52-bit integers |
| `UUID` | Universally Unique Identifier |
| `DateTime` | RFC 3339 date-time string |
| `Port` | Valid TCP port (0-65535) |
| `URL` | Standard URL format |

#### Key Enums

**Resource (for permissions):**
`api_key`, `array`, `cloud`, `config`, `connect`, `connect__remote_access`, `customizations`, `dashboard`, `disk`, `display`, `docker`, `flash`, `info`, `logs`, `me`, `network`, `notifications`, `online`, `os`, `owner`, `permission`, `registration`, `servers`, `services`, `share`, `vars`, `vms`, `welcome`

**Role:**
`admin`, `connect`, `guest`

**ArrayState:**
`STARTED`, `STOPPED`, `NEW_ARRAY`, `RECON_DISK`, `DISABLE_DISK`, `SWAP_DSBL`, `INVALID_EXPANSION`, `PARITY_NOT_BIGGEST`, `TOO_MANY_MISSING_DISKS`, `NEW_DISK_TOO_SMALL`, `NO_DATA_DISKS`

**ArrayDiskStatus:**
`DISK_NP`, `DISK_OK`, `DISK_NP_MISSING`, `DISK_INVALID`, `DISK_WRONG`, `DISK_DSBL`, `DISK_NP_DSBL`, `DISK_DSBL_NEW`, `DISK_NEW`

**ArrayDiskType:**
`Data`, `Parity`, `Flash`, `Cache`

**ContainerState:**
`RUNNING`, `EXITED`

**VmState:**
`NOSTATE`, `RUNNING`, `IDLE`, `PAUSED`, `SHUTDOWN`, `SHUTOFF`, `CRASHED`, `PMSUSPENDED`

**DiskInterfaceType:**
`SAS`, `SATA`, `USB`, `PCIe`, `UNKNOWN`

**DiskFsType:**
`xfs`, `btrfs`, `vfat`, `zfs`

**Importance (Notifications):**
`ALERT`, `INFO`, `WARNING`

**NotificationType:**
`UNREAD`, `ARCHIVE`

**WAN_ACCESS_TYPE:**
`DYNAMIC`, `ALWAYS`, `DISABLED`

**RegistrationState:**
`TRIAL`, `BASIC`, `PLUS`, `PRO`, `STARTER`, `UNLEASHED`, `LIFETIME`, `EEXPIRED`, `EGUID`, `EGUID1`, `ETRIAL`, `ENOKEYFILE`, `ENOFLASH`, `EBLACKLISTED`, `ENOCONN`

---

## 3. Unraid Connect Documentation

**Source:** https://docs.unraid.net/unraid-connect/overview-and-setup
**Source:** https://docs.unraid.net/unraid-connect/remote-access
**Source:** https://docs.unraid.net/unraid-connect/automated-flash-backup

Unraid Connect is the cloud management layer that provides:
- Remote access to your Unraid server from anywhere
- Automated flash backup to the cloud
- Server dashboard and monitoring from unraid.net
- The API plugin for pre-7.2 Unraid versions

Key points:
- Unraid Connect plugin is completely optional on 7.2+
- The API functionality was separated from Connect in 7.2
- You do NOT need to sign in to Unraid Connect to use the API locally
- Connect adds cloud communication features (remote access, dashboard, flash backup)
- Remote access uses WireGuard VPN or Dynamic DNS

---

## 4. Release Notes (API-Relevant)

### Unraid 7.2.0 (October 29, 2025)

**Source:** https://docs.unraid.net/unraid-os/release-notes/7.2.0

**Major API changes:**
- The Unraid API is now built into Unraid OS (no plugin required)
- The new Notifications panel is the first major feature built on the API
- Dashboard now gets CPU usage stats from the Unraid API
- Over time, the entire webGUI will transition to use the API
- Fully open source: https://github.com/unraid/api
- SSO/OIDC login support for the webGUI
- API version: dynamix.unraid.net 4.25.3

**Other key 7.2.0 changes:**
- Responsive CSS (mobile-friendly webGUI)
- ZFS RAIDZ expansion
- Ext2/3/4, NTFS, exFAT support
- IPv6 Docker custom networks with ULA support
- Welcome screen for new systems

### Unraid 7.1.0 (May 2025)

**Source:** https://docs.unraid.net/unraid-os/release-notes/7.1.0

- API available via Unraid Connect plugin
- Focus on ZFS improvements, Docker enhancements, and VM updates

### Unraid 7.0.0 (February 2025)

**Source:** https://docs.unraid.net/unraid-os/release-notes/7.0.0

- Major release introducing ZFS support
- API available via Unraid Connect plugin
- Modernized PHP stack and security improvements

---

## 5. Blog Posts

### API Feature Bounty Program (September 5, 2025)

**Source:** https://unraid.net/blog/api-feature-bounty-program

Unraid launched a Feature Bounty Program for developers to contribute to the API roadmap:
- Feature requests become bounties
- Developers build and claim bounties for monetary rewards
- Community-driven growth

**Live bounty board:** https://github.com/orgs/unraid/projects/3/views/1
**Feature bounty info:** https://unraid.net/feature-bounty

**Community API projects highlighted:**
- Unraid Mobile App (by S3ppo) - https://forums.unraid.net/topic/189522-unraid-mobile-app/
- Homepage Dashboard Widget (by surf108)
- Home Assistant Integration (by domalab) - https://github.com/domalab/ha-unraid-connect
- Unloggarr AI-powered log analysis (by jmagar) - https://github.com/jmagar/unloggarr
- nzb360 Mobile App (Android) - https://play.google.com/store/apps/details?id=com.kevinforeman.nzb360
- API Show and Tell Discord channel

### Unraid 7.2.0 Stable Release Blog (October 29, 2025)

**Source:** https://unraid.net/blog/unraid-7-2-0

Highlights the API as now integrated directly into Unraid OS:
- "The Unraid API is now integrated directly into Unraid OS, giving developers and power users new ways to interact with their systems."
- New Notifications panel is the first major feature built on the API
- Over time, more of the webGUI will transition to use the API
- Fully open source at https://github.com/unraid/api
- Supports external authentication (OIDC) for secure, scalable access

---

## 6. Community Resources

### Third-Party API Client

**Source:** https://deepwiki.com/domalab/unraid-api-client/

The `domalab/unraid-api-client` repository provides:
- Python client for the Unraid GraphQL API
- Shell script client for bash-based automation
- Complete GraphQL schema file (schema.graphql)
- Example queries for all major resource types
- Authentication examples
- Error handling patterns

GitHub: https://github.com/domalab/unraid-api-client

### Official Unraid API GitHub

**Source:** https://github.com/unraid/api

- Monorepo: Unraid API / Connect / UI
- TypeScript (77.4%), Vue (11.8%), PHP (5.6%)
- 95 stars, 17 forks
- 102 releases (latest v4.29.2)
- Open source since January 2025
- Topics: api, unraid, unraid-api, unraid-connect, unraid-ui

### Community Forums

- Unraid API / Unraid Connect forum: https://forums.unraid.net/forum/93-unraid-api-unraid-connect/
- 68 posts in the API subforum
- Topics include API key issues, plugin updates, and integration questions

---

## 7. Source URLs Index

### Official API Documentation (Primary Sources)
| URL | Description |
|-----|-------------|
| https://docs.unraid.net/API/ | API overview and getting started |
| https://docs.unraid.net/API/how-to-use-the-api/ | Authentication, queries, and usage |
| https://docs.unraid.net/API/cli/ | CLI command reference |
| https://docs.unraid.net/API/api-key-app-developer-authorization-flow/ | App developer auth flow |
| https://docs.unraid.net/API/programmatic-api-key-management/ | Programmatic key management |
| https://docs.unraid.net/API/oidc-provider-setup/ | OIDC/SSO provider configuration |
| https://docs.unraid.net/API/upcoming-features/ | Roadmap and feature status |

### GraphQL Schema (Primary Sources)
| URL | Description |
|-----|-------------|
| https://github.com/domalab/unraid-api-client/blob/113c94f1/schema.graphql | Complete GraphQL schema file |
| https://deepwiki.com/domalab/unraid-api-client/7-graphql-schema-reference | Schema reference documentation |
| https://studio.apollographql.com/graph/Unraid-API/variant/current/home | Apollo Studio (requires auth) |

### Unraid Connect Documentation
| URL | Description |
|-----|-------------|
| https://docs.unraid.net/unraid-connect/overview-and-setup | Connect overview |
| https://docs.unraid.net/unraid-connect/remote-access | Remote access configuration |
| https://docs.unraid.net/unraid-connect/automated-flash-backup | Automated flash backup |

### Release Notes
| URL | Description |
|-----|-------------|
| https://docs.unraid.net/unraid-os/release-notes/7.2.0 | Unraid 7.2.0 (API built-in) |
| https://docs.unraid.net/unraid-os/release-notes/7.1.0 | Unraid 7.1.0 |
| https://docs.unraid.net/unraid-os/release-notes/7.0.0 | Unraid 7.0.0 |
| https://docs.unraid.net/unraid-os/release-notes/7.0.1 | Unraid 7.0.1 |
| https://docs.unraid.net/unraid-os/release-notes/7.2.1 | Unraid 7.2.1 |
| https://docs.unraid.net/unraid-os/release-notes/7.2.2 | Unraid 7.2.2 |
| https://docs.unraid.net/unraid-os/release-notes/7.2.3 | Unraid 7.2.3 |

### Blog Posts
| URL | Description |
|-----|-------------|
| https://unraid.net/blog/unraid-7-2-0 | 7.2.0 stable release announcement |
| https://unraid.net/blog/api-feature-bounty-program | API Feature Bounty Program |
| https://unraid.net/blog/unraid-7 | Unraid 7.0 announcement |
| https://unraid.net/blog/unraid-7-1 | Unraid 7.1 announcement |
| https://unraid.net/blog/unraid-7-2-0-beta.1 | 7.2.0 beta.1 |
| https://unraid.net/blog/unraid-7-2-0-beta.2 | 7.2.0 beta.2 |
| https://unraid.net/blog/unraid-7-2-0-beta.3 | 7.2.0 beta.3 |
| https://unraid.net/blog/unraid-7-2-0-rc-1 | 7.2.0 RC 1 |
| https://unraid.net/blog/unraid-7-2-0-rc-2 | 7.2.0 RC 2 |

### GitHub Repositories
| URL | Description |
|-----|-------------|
| https://github.com/unraid/api | Official Unraid API monorepo |
| https://github.com/unraid/api/releases | API releases (102 total) |
| https://github.com/domalab/unraid-api-client | Third-party API client (Python/Shell) |
| https://github.com/domalab/ha-unraid-connect | Home Assistant integration |
| https://github.com/jmagar/unloggarr | AI-powered log analysis |
| https://github.com/orgs/unraid/projects/3/views/1 | Feature bounty board |

### Community
| URL | Description |
|-----|-------------|
| https://forums.unraid.net/forum/93-unraid-api-unraid-connect/ | API/Connect forum |
| https://unraid.net/feature-bounty | Feature bounty program info |

---

## Data Collection Summary

- **Sites mapped:** 4 (docs.unraid.net/API/, docs.unraid.net/connect/, docs.unraid.net/unraid-os/release-notes/, unraid.net/blog/)
- **Pages crawled:** 7 API docs + 19 Connect + 7 release notes + 12 blog posts + 10 deepwiki pages + misc = ~60 pages
- **Vector DB chunks:** 351 from docs.unraid.net, 575 from unraid.net, plus deepwiki, forums, and GitHub
- **Raw files saved:** 6 files in docs/research/raw/
- **GraphQL schema:** Complete schema.graphql extracted (1,600+ lines)
