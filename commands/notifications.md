---
description: Manage Unraid system notifications and alerts
argument-hint: [action] [additional-args]
---

Execute the `unraid_notifications` MCP tool with action: `$1`

## Available Actions (9)

**Query Operations:**
- `overview` - Summary of notification counts by category
- `list` - List all notifications with details
- `warnings` - List only warning/error notifications
- `unread` - List unread notifications only

**Management Operations:**
- `create` - Create a new notification (requires title, message, severity)
- `archive` - Archive a specific notification (requires notification_id)
- `archive_all` - Archive all current notifications

**⚠️ Destructive Operations:**
- `delete` - Permanently delete a notification (requires notification_id + confirmation)
- `delete_archived` - Permanently delete all archived notifications (requires confirmation)

## Example Usage

```
/unraid-notifications overview
/unraid-notifications list
/unraid-notifications warnings
/unraid-notifications unread
/unraid-notifications create "Test Alert" "This is a test" normal
/unraid-notifications archive [notification-id]
/unraid-notifications archive_all
```

**Severity Levels:** `normal`, `warning`, `alert`, `critical`

**IMPORTANT:** Delete operations are permanent and cannot be undone.

Use the tool to execute the requested notification operation and present results clearly.
