---
description: Manage Docker containers on Unraid
argument-hint: [action] [additional-args]
---

Execute the `unraid_docker` MCP tool with action: `$1`

## Available Actions (15)

**Query Operations:**
- `list` - List all Docker containers with status
- `details` - Get detailed info for a container (requires container identifier)
- `logs` - Get container logs (requires container identifier)
- `check_updates` - Check for available container updates
- `port_conflicts` - Identify port conflicts
- `networks` - List Docker networks
- `network_details` - Get network details (requires network identifier)

**Container Lifecycle:**
- `start` - Start a stopped container (requires container identifier)
- `stop` - Stop a running container (requires container identifier)
- `restart` - Restart a container (requires container identifier)
- `pause` - Pause a running container (requires container identifier)
- `unpause` - Unpause a paused container (requires container identifier)

**Updates & Management:**
- `update` - Update a specific container (requires container identifier)
- `update_all` - Update all containers with available updates

**⚠️ Destructive:**
- `remove` - Permanently delete a container (requires container identifier + confirmation)

## Example Usage

```
/unraid-docker list
/unraid-docker details plex
/unraid-docker logs plex
/unraid-docker start nginx
/unraid-docker restart sonarr
/unraid-docker check_updates
/unraid-docker update plex
/unraid-docker port_conflicts
```

**Container Identification:** Use container name, ID, or partial match (fuzzy search supported)

Use the tool to execute the requested Docker operation and report the results.
