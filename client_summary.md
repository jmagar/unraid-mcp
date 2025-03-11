# Unraid API Client Summary

## Authentication

The Unraid API uses the `x-api-key` header for authentication, not Bearer tokens. The API key can be generated using the `unraid-api apikey --create` command on the Unraid server.

## CORS Handling

The Unraid API has CORS protection enabled. To successfully connect, the client must include an `Origin` header that matches the server's URL. For example, if the API URL is `http://192.168.1.68:6969/graphql`, the Origin header should be `http://192.168.1.68:6969`.

## Working Queries

The following queries have been tested and confirmed to work:

### System Information

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

### Array Status

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

### Docker Containers

```graphql
query {
  docker {
    containers {
      names
      state
      id
    }
  }
}
```

## Client Implementation

The UnraidClient class has been updated to:

1. Use the correct `x-api-key` header for authentication
2. Include the proper `Origin` header to handle CORS
3. Handle errors and provide detailed logging

## Next Steps

1. Implement additional queries for VMs, shares, and other resources
2. Add support for mutations (e.g., starting/stopping containers)
3. Create helper methods for common operations
4. Implement caching for improved performance 