# Unraid API Documentation

## Overview

This document provides a comprehensive guide to the Unraid GraphQL API. The API allows developers to interact with various components of an Unraid server, including array management, disk operations, user administration, Docker containers, virtual machines, and more.

## Table of Contents

- [Authentication](#authentication)
- [Core Resources](#core-resources)
  - [Array Management](#array-management)
  - [Disk Operations](#disk-operations)
  - [User Management](#user-management)
  - [Docker Management](#docker-management)
  - [Virtual Machines](#virtual-machines)
  - [Remote Access](#remote-access)
  - [Notifications](#notifications)
- [API Reference](#api-reference)
  - [Queries](#queries)
  - [Mutations](#mutations)
  - [Subscriptions](#subscriptions)
- [Custom Types](#custom-types)
- [Enumerations](#enumerations)

## Authentication

The API uses API keys for authentication. You can create an API key using the `createApiKey` mutation:

```graphql
mutation {
  createApiKey(input: {
    name: "My API Key",
    description: "API key for my application",
    roles: [admin]
  }) {
    id
    key
    name
    roles
  }
}
```

## Core Resources

### Array Management

The Unraid array is the core storage component of the system. The API provides operations to:

- Start and stop the array
- Add and remove disks
- Monitor array status
- Perform parity checks

Example query to get array information:

```graphql
query {
  array {
    state
    capacity {
      kilobytes {
        free
        used
        total
      }
    }
    parities {
      id
      name
      size
    }
    disks {
      id
      name
      size
      status
    }
  }
}
```

### Disk Operations

The API allows detailed access to disk information and operations:

- View detailed disk information (size, temperature, status)
- Mount and unmount disks
- Monitor disk statistics

Example query to get all disks:

```graphql
query {
  disks {
    device
    name
    size
    temperature
    smartStatus
    interfaceType
  }
}
```

### User Management

Manage users and their permissions:

- Add and delete users
- Assign roles and permissions
- Manage API keys

Example to create a new user:

```graphql
mutation {
  addUser(input: {
    name: "john",
    password: "securepassword",
    description: "John Doe"
  }) {
    id
    name
    roles
  }
}
```

### Docker Management

Interact with Docker containers:

- View container information
- Manage Docker networks

Example to get all Docker containers:

```graphql
query {
  dockerContainers {
    id
    names
    image
    state
    status
    ports {
      ip
      privatePort
      publicPort
      type
    }
  }
}
```

### Virtual Machines

Manage virtual machines running on Unraid:

- View VM information
- Check VM status

Example to get all VMs:

```graphql
query {
  vms {
    domain {
      uuid
      name
      state
    }
  }
}
```

### Remote Access

Configure remote access to the Unraid server:

- Set up dynamic remote access
- Configure access URLs
- Manage allowed origins

### Notifications

The API provides a comprehensive notification system:

- Create and manage notifications
- Filter notifications by importance
- Archive and unarchive notifications

Example to create a notification:

```graphql
mutation {
  createNotification(input: {
    title: "Disk Warning",
    subject: "High Temperature",
    description: "Disk temperature is above threshold",
    importance: WARNING
  }) {
    id
    title
    importance
  }
}
```

## API Reference

### Queries

The API provides the following top-level queries:

| Query | Description |
|-------|-------------|
| `apiKeys` | List all API keys |
| `apiKey(id: ID!)` | Get a specific API key |
| `array` | Get information about the Unraid array |
| `parityHistory` | Get historical parity check data |
| `disk(id: ID!)` | Get information about a specific disk |
| `disks` | Get information about all disks |
| `dockerContainers(all: Boolean)` | Get Docker containers |
| `dockerNetworks(all: Boolean)` | Get Docker networks |
| `info` | Get system information |
| `me` | Get current user information |
| `notifications` | Get system notifications |
| `shares` | Get network shares |
| `unassignedDevices` | Get unassigned devices |
| `users(input: usersInput)` | Get all users |
| `vms` | Get virtual machines |

### Mutations

The API provides the following top-level mutations:

| Mutation | Description |
|----------|-------------|
| `createApiKey(input: CreateApiKeyInput!)` | Create a new API key |
| `addPermission(input: AddPermissionInput!)` | Add a permission |
| `addRoleForUser(input: AddRoleForUserInput!)` | Add a role to a user |
| `addRoleForApiKey(input: AddRoleForApiKeyInput!)` | Add a role to an API key |
| `startArray` | Start the array |
| `stopArray` | Stop the array |
| `addDiskToArray(input: arrayDiskInput)` | Add a disk to the array |
| `removeDiskFromArray(input: arrayDiskInput)` | Remove a disk from the array |
| `startParityCheck(correct: Boolean)` | Start a parity check |
| `pauseParityCheck` | Pause a running parity check |
| `resumeParityCheck` | Resume a paused parity check |
| `cancelParityCheck` | Cancel a running parity check |
| `addUser(input: addUserInput!)` | Add a new user |
| `deleteUser(input: deleteUserInput!)` | Delete a user |
| `createNotification(input: NotificationData!)` | Create a notification |
| `archiveNotification(id: String!)` | Archive a notification |

### Subscriptions

The API provides real-time updates via subscriptions:

| Subscription | Description |
|--------------|-------------|
| `array` | Get real-time updates about the array |
| `parityHistory` | Get real-time updates about parity check progress |
| `dockerContainer(id: ID!)` | Get real-time updates about a specific Docker container |
| `dockerContainers` | Get real-time updates about all Docker containers |
| `notificationAdded` | Get notified when a new notification is added |
| `user(id: ID!)` | Get real-time updates about a specific user |
| `users` | Get real-time updates about all users |

## Custom Types

The API uses several custom types:

| Type | Description |
|------|-------------|
| `JSON` | Represents JSON values |
| `Long` | Represents 52-bit integers |
| `UUID` | Represents a Universally Unique Identifier |
| `DateTime` | Represents a date-time string at UTC |
| `Port` | Represents a valid TCP port (0-65535) |
| `URL` | Represents a standard URL format |

## Enumerations

Key enumerations used in the API:

| Enumeration | Description |
|-------------|-------------|
| `Resource` | Available resources for permissions (e.g., `api_key`, `array`, `disk`) |
| `Role` | Available roles for API keys and users (`admin`, `connect`, `guest`) |
| `ArrayState` | Possible states of the array (e.g., `STARTED`, `STOPPED`) |
| `ArrayDiskStatus` | Possible statuses for disks in the array |
| `DiskInterfaceType` | Types of disk interfaces (`SAS`, `SATA`, `USB`, etc.) |
| `ContainerState` | Possible states for Docker containers (`RUNNING`, `EXITED`) |
| `VmState` | Possible states for virtual machines |
| `Importance` | Importance levels for notifications (`ALERT`, `INFO`, `WARNING`) |

## Common Use Cases and Examples

### System Monitoring

#### CPU, RAM and System Information

Monitor CPU usage, RAM usage, and general system information:

```graphql
query {
  info {
    cpu {
      manufacturer
      brand
      cores
      threads
      speed
      speedmax
    }
    memory {
      total
      free
      used
      active
      available
      swaptotal
      swapused
      swapfree
    }
    system {
      manufacturer
      model
      serial
    }
    os {
      uptime
      distro
      release
      kernel
    }
  }
}
```

#### CPU and Motherboard Temperature

The schema doesn't have direct temperature sensors for CPU and motherboard, but you can access device information which might contain this data:

```graphql
query {
  info {
    devices {
      pci {
        id
        vendorname
        productname
      }
    }
    cpu {
      manufacturer
      brand
      cores
      temperature # Note: This field may not be directly available
    }
  }
}
```

#### Array Usage and Disk Information

Monitor array usage, disk health, and status:

```graphql
query {
  array {
    state
    capacity {
      kilobytes {
        free
        used
        total
      }
    }
    parities {
      id
      name
      size
      temp
      numErrors
    }
    disks {
      id
      name
      size
      temp
      numErrors
      fsUsed
      fsFree
      fsSize
      status
    }
    caches {
      id
      name
      size
      temp
      numErrors
    }
  }
}
```

#### Individual Disk Information

Get detailed information about a specific disk:

```graphql
query {
  disk(id: "yourDiskId") {
    device
    name
    size
    temperature
    smartStatus
    partitions {
      name
      fsType
      size
    }
  }
}
```

#### Monitor Parity Check Status

Get information about parity checks:

```graphql
query {
  parityHistory {
    date
    duration
    speed
    status
    errors
  }
  
  # For active parity check status, use the array subscription
  # subscription {
  #   array {
  #     state
  #     # Additional fields related to parity check status
  #   }
  # }
}
```

#### Real-time System Monitoring with Subscriptions

Use subscriptions for real-time monitoring:

```graphql
subscription {
  info {
    cpu {
      cores
      threads
      speed
    }
    memory {
      total
      used
      free
    }
  }
  
  array {
    state
    capacity {
      kilobytes {
        used
        free
      }
    }
  }
}
```

### Container and VM Management

#### Docker Container Control

List and control Docker containers:

```graphql
query {
  dockerContainers {
    id
    names
    image
    state
    status
    ports {
      ip
      privatePort
      publicPort
    }
    autoStart
  }
}

# To control containers, you would need appropriate mutations
# Note: The schema doesn't show specific container start/stop mutations
# but you can use Docker-related mutations that might be available
```

#### Virtual Machine Control

Monitor virtual machines:

```graphql
query {
  vms {
    domain {
      uuid
      name
      state
    }
  }
}

# To control VMs, you would need appropriate mutations
# Note: The schema doesn't show specific VM start/stop mutations
```

#### Docker Networks

Examine Docker networks:

```graphql
query {
  dockerNetworks {
    id
    name
    driver
    scope
    internal
    attachable
  }
}
```

### Notification Management

Create and manage notifications:

```graphql
mutation {
  createNotification(input: {
    title: "Disk Warning",
    subject: "High Temperature",
    description: "Disk temperature is above threshold",
    importance: WARNING
  }) {
    id
    title
    importance
  }
}

query {
  notifications {
    overview {
      unread {
        info
        warning
        alert
        total
      }
    }
    list(filter: {
      importance: WARNING,
      type: UNREAD,
      offset: 0,
      limit: 10
    }) {
      id
      title
      subject
      description
      timestamp
    }
  }
}
```

### User Management

```graphql
query {
  users {
    id
    name
    description
    roles
  }
}

mutation {
  addUser(input: {
    name: "newuser",
    password: "securepassword",
    description: "New operator"
  }) {
    id
    name
    roles
  }
}
```

### Other Common Operations

#### Start/Stop Array

```graphql
mutation {
  startArray
}

mutation {
  stopArray
}
```

#### Parity Check Control

```graphql
mutation {
  # Start a parity check
  startParityCheck(correct: false) # Set to true to correct errors
  
  # Pause a running parity check
  # pauseParityCheck
  
  # Resume a paused parity check
  # resumeParityCheck
  
  # Cancel a running parity check
  # cancelParityCheck
}
```

## Best Practices

1. **Rate Limiting**: Be mindful of the rate at which you make API requests to avoid performance impacts.
2. **Error Handling**: Always handle potential errors in your API responses.
3. **Permissions**: Only assign the minimum permissions required for your application.
4. **Subscriptions**: Use subscriptions for real-time data instead of polling with queries.
5. **API Keys**: Keep your API keys secure and rotate them periodically.

## Additional Resources

For more information about GraphQL and how to use it effectively, refer to the following resources:

- [Official GraphQL Documentation](https://graphql.org/learn/)
- [Unraid Documentation](https://docs.unraid.net/)
- [GraphQL Clients](https://graphql.org/code/#graphql-clients)
