---
description: Manage Rclone cloud storage remotes on Unraid
argument-hint: [action] [remote-name]
---

Execute the `unraid_rclone` MCP tool with action: `$1`

## Available Actions (4)

**Query Operations:**
- `list_remotes` - List all configured Rclone remotes
- `config_form` - Get configuration form for a remote type (requires remote_type)

**Management Operations:**
- `create_remote` - Create a new Rclone remote (requires remote_name, remote_type, config)

**⚠️ Destructive:**
- `delete_remote` - Permanently delete a remote (requires remote_name + confirmation)

## Example Usage

```
/unraid-rclone list_remotes
/unraid-rclone config_form s3
/unraid-rclone create_remote mybackup s3 {"access_key":"...","secret_key":"..."}
```

**Supported Remote Types:** s3, dropbox, google-drive, onedrive, backblaze, ftp, sftp, webdav, etc.

**IMPORTANT:** Deleting a remote does NOT delete cloud data, only the local configuration.

Use the tool to execute the requested Rclone operation and report the results.
