use serde_json::{json, Value};

pub(super) const UNRAID_ACTIONS: &[&str] = &[
    "array",
    "disks",
    "docker",
    "docker_logs",
    "vms",
    "server",
    "info",
    "shares",
    "notifications",
    "log_files",
    "log_file",
    "services",
    "network",
    "ups",
    "ups_config",
    "metrics",
    "plugins",
    "parity_history",
    "vars",
    "registration",
    "flash",
    "rclone",
    "remote_access",
    "connect",
    "status",
    "help",
];

pub(super) fn tool_definitions() -> Vec<Value> {
    vec![json!({
        "name": "unraid",
        "description": "Query the Unraid server via its GraphQL API (read-only). Use action=help for documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Operation to perform.",
                    "enum": UNRAID_ACTIONS
                },
                "id": {
                    "type": "string",
                    "description": "Container ID (docker_logs) or UPS ID (ups_device)."
                },
                "path": {
                    "type": "string",
                    "description": "Log file path — required for action=log_file."
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of lines to read (log_file)."
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number, 1-indexed (log_file)."
                },
                "tail": {
                    "type": "integer",
                    "description": "Number of log lines to return (docker_logs, default 100)."
                },
                "limit": {
                    "type": "integer",
                    "description": "Max items to return for list actions (default 50, max 200)."
                },
                "offset": {
                    "type": "integer",
                    "description": "Zero-based offset for pagination of list actions (default 0)."
                },
                "state": {
                    "type": "string",
                    "description": "Filter docker containers by state substring (e.g. \"running\", \"stopped\")."
                },
                "name": {
                    "type": "string",
                    "description": "Filter shares or plugins by name substring (case-insensitive)."
                }
            },
            "required": ["action"]
        }
    })]
}
