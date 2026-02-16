---
description: Query current authenticated Unraid user
argument-hint: [action]
---

Execute the `unraid_users` MCP tool with action: `$1`

## Available Actions (1)

**Query Operation:**
- `me` - Get current authenticated user info (id, name, description, roles)

## Example Usage

```
/users me
```

## API Limitation

⚠️ **Note:** The Unraid GraphQL API does not support user management operations. Only the `me` query is available, which returns information about the currently authenticated user (the API key holder).

**Not supported:**
- Listing all users
- Getting other user details
- Adding/deleting users
- Cloud/remote access queries

For user management, use the Unraid web UI.

Use the tool to query the current authenticated user and report the results.
