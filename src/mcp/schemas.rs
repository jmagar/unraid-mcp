use std::sync::LazyLock;

use serde_json::{json, Value};

/// Canonical specification for one `unraid` tool action.
///
/// This is the SINGLE source of truth for the set of valid actions and their
/// scope requirements. Everything else — the JSON Schema enum, the error-message
/// action list, and the MCP scope gating — is derived from [`ACTIONS`]. To add
/// or remove an action, edit this slice only.
pub(super) struct ActionSpec {
    /// The action name as passed in the `action` argument.
    pub name: &'static str,
    /// Whether the action requires the `unraid:read` scope.
    ///
    /// `true` for all data actions and `status` (need `unraid:read`).
    /// `false` only for `help`, which requires no scope.
    pub read_only: bool,
}

/// The canonical action list. Order is preserved in the JSON Schema enum and the
/// error-message list, so it doubles as the documented action ordering.
pub(super) const ACTIONS: &[ActionSpec] = &[
    ActionSpec { name: "array", read_only: true },
    ActionSpec { name: "disks", read_only: true },
    ActionSpec { name: "docker", read_only: true },
    ActionSpec { name: "docker_logs", read_only: true },
    ActionSpec { name: "vms", read_only: true },
    ActionSpec { name: "server", read_only: true },
    ActionSpec { name: "info", read_only: true },
    ActionSpec { name: "shares", read_only: true },
    ActionSpec { name: "notifications", read_only: true },
    ActionSpec { name: "log_files", read_only: true },
    ActionSpec { name: "log_file", read_only: true },
    ActionSpec { name: "services", read_only: true },
    ActionSpec { name: "network", read_only: true },
    ActionSpec { name: "ups", read_only: true },
    ActionSpec { name: "ups_config", read_only: true },
    ActionSpec { name: "metrics", read_only: true },
    ActionSpec { name: "plugins", read_only: true },
    ActionSpec { name: "parity_history", read_only: true },
    ActionSpec { name: "vars", read_only: true },
    ActionSpec { name: "registration", read_only: true },
    ActionSpec { name: "flash", read_only: true },
    ActionSpec { name: "rclone", read_only: true },
    ActionSpec { name: "remote_access", read_only: true },
    ActionSpec { name: "connect", read_only: true },
    ActionSpec { name: "status", read_only: true },
    // `help` is the only action that requires no scope.
    ActionSpec { name: "help", read_only: false },
];

/// All valid action names, derived from [`ACTIONS`]. Used for the JSON Schema enum.
pub(super) static UNRAID_ACTIONS: LazyLock<Vec<&'static str>> =
    LazyLock::new(|| ACTIONS.iter().map(|a| a.name).collect());

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
                    "enum": *UNRAID_ACTIONS
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

#[cfg(test)]
mod tests {
    use super::*;

    /// `help` is the only action that requires no scope; every other action is
    /// read-scoped. This guards against silently flipping the scope flag.
    #[test]
    fn only_help_is_unscoped() {
        for spec in ACTIONS {
            if spec.name == "help" {
                assert!(!spec.read_only, "help must require no scope");
            } else {
                assert!(spec.read_only, "{} must be read-scoped", spec.name);
            }
        }
    }

    /// The derived schema-enum name list must agree with the canonical specs,
    /// in the same order — this is the list the JSON Schema `enum` is built from.
    #[test]
    fn schema_enum_matches_canonical() {
        let derived: Vec<&str> = ACTIONS.iter().map(|a| a.name).collect();
        assert_eq!(*UNRAID_ACTIONS, derived);
    }

    /// `help` must be present in the canonical list (it is reachable with no scope).
    #[test]
    fn help_is_present() {
        assert!(ACTIONS.iter().any(|a| a.name == "help"));
    }
}
