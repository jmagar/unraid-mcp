---
description: Manage Unraid API keys for authentication
argument-hint: [action] [key-id]
---

Execute the `unraid_keys` MCP tool with action: `$1`

## Available Actions (5)

**Query Operations:**
- `list` - List all API keys with metadata
- `get` - Get details for a specific API key (requires key_id)

**Management Operations:**
- `create` - Create a new API key (requires name, optional description and expiry)
- `update` - Update an existing API key (requires key_id, name, description)

**⚠️ Destructive:**
- `delete` - Permanently revoke an API key (requires key_id + confirmation)

## Example Usage

```
/unraid-keys list
/unraid-keys get [key-id]
/unraid-keys create "MCP Server Key" "Key for unraid-mcp integration"
/unraid-keys update [key-id] "Updated Name" "Updated description"
```

**Key Format:** PrefixedID (`hex64:suffix`)

**IMPORTANT:**
- Deleted keys are immediately revoked and cannot be recovered
- Store new keys securely - they're only shown once during creation
- Set expiry dates for keys used in automation

Use the tool to execute the requested API key operation and report the results.
