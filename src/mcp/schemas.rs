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
    /// The OAuth/JWT scope this action requires.
    pub scope: Scope,
}

/// Scope an action requires. `unraid:admin` satisfies `unraid:read`, so a
/// read-scoped token cannot reach a [`Scope::Write`] (mutating) action.
#[derive(Clone, Copy, PartialEq, Eq)]
pub(super) enum Scope {
    /// No scope required (the `help` meta action).
    None,
    /// `unraid:read` — every data *query* action, plus `status`.
    Read,
    /// `unraid:admin` — mutating actions that change server state.
    Write,
}

/// The canonical action list. Order is preserved in the JSON Schema enum and the
/// error-message list, so it doubles as the documented action ordering.
pub(super) const ACTIONS: &[ActionSpec] = &[
    ActionSpec {
        name: "array",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "disks",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "docker",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "docker_logs",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "vms",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "server",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "info",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "shares",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "notifications",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "log_files",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "log_file",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "services",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "network",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "ups",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "ups_config",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "metrics",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "plugins",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "parity_history",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "vars",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "registration",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "flash",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "rclone",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "remote_access",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "connect",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "online",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "system_time",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "installed_unraid_plugins",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "is_sso_enabled",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "public_oidc_providers",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "oidc_providers",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "oidc_configuration",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "api_keys",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "api_key_possible_roles",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "api_key_possible_permissions",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "get_available_auth_actions",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "get_api_key_creation_form_schema",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "config",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "settings",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "display",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "customization",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "internal_boot_context",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "me",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "owner",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "servers",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "is_fresh_install",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "public_theme",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "network_interfaces",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "time_zone_options",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "assignable_disks",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "plugin_install_operations",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "cloud",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "api_key",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "disk",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "oidc_provider",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "ups_device_by_id",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "plugin_install_operation",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "validate_oidc_session",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "get_permissions_for_roles",
        scope: Scope::Read,
    },
    ActionSpec {
        name: "recalculate_overview",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "delete_archived_notifications",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "archive_notification",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "create_notification",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_start",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_stop",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_pause",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_resume",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_force_stop",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_reboot",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "vm_reset",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_start",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_stop",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_pause",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_unpause",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_update_container",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_remove_container",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_update_containers",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "docker_update_all_containers",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_set_state",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_add_disk_to_array",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_remove_disk_from_array",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_mount_array_disk",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_unmount_array_disk",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "array_clear_array_disk_statistics",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "parity_check_start",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "parity_check_pause",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "parity_check_resume",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "parity_check_cancel",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "api_key_create",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "api_key_add_role",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "api_key_remove_role",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "api_key_delete",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "api_key_update",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "rclone_create_r_clone_remote",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "rclone_delete_r_clone_remote",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "unraid_plugins_install_plugin",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "unraid_plugins_install_language",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "onboarding_complete_onboarding",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "onboarding_reset_onboarding",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "archive_notifications",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "unarchive_notifications",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "unread_notification",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "archive_all",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "unarchive_all",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "update_server_identity",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "configure_ups",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "update_system_time",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "update_temperature_config",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "add_plugin",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "remove_plugin",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "connect_sign_out",
        scope: Scope::Write,
    },
    ActionSpec {
        name: "status",
        scope: Scope::Read,
    },
    // `help` is the only action that requires no scope.
    ActionSpec {
        name: "help",
        scope: Scope::None,
    },
];

/// All valid action names, derived from [`ACTIONS`]. Used for the JSON Schema enum.
pub(super) static UNRAID_ACTIONS: LazyLock<Vec<&'static str>> =
    LazyLock::new(|| ACTIONS.iter().map(|a| a.name).collect());

/// The upstream-GraphQL-backed data actions (every read-only action except
/// `status`, which is local observability with no query/fixture). Re-exported so
/// the scenario + schema-contract integration tests cover every action
/// automatically — adding an entry to [`ACTIONS`] is enough.
pub fn data_action_names() -> Vec<&'static str> {
    ACTIONS
        .iter()
        .filter(|a| a.scope == Scope::Read && a.name != "status")
        .map(|a| a.name)
        .collect()
}

/// The mutating (write-scoped) actions. Re-exported for the same reason as
/// [`data_action_names`] — so the contract/scenario tests cover mutations too.
pub fn write_action_names() -> Vec<&'static str> {
    ACTIONS
        .iter()
        .filter(|a| a.scope == Scope::Write)
        .map(|a| a.name)
        .collect()
}

pub(super) fn tool_definitions() -> Vec<Value> {
    vec![json!({
        "name": "unraid",
        "description": "Query and manage the Unraid server via its GraphQL API. Read actions need scope unraid:read; mutating actions need unraid:admin. Use action=help for documentation.",
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
                },
                "token": {
                    "type": "string",
                    "description": "Session token — required for action=validate_oidc_session."
                },
                "roles": {
                    "type": "array",
                    "items": { "type": "string" },
                    "description": "Role names — required for action=get_permissions_for_roles."
                },
                "title": { "type": "string", "description": "Notification title (create_notification)." },
                "subject": { "type": "string", "description": "Notification subject (create_notification)." },
                "description": { "type": "string", "description": "Notification body (create_notification)." },
                "importance": { "type": "string", "enum": ["ALERT", "INFO", "WARNING"], "description": "Notification importance (create_notification)." },
                "link": { "type": "string", "description": "Optional notification link (create_notification)." },
                "desired_state": { "type": "string", "enum": ["START", "STOP"], "description": "Array target state (array_set_state)." },
                "slot": { "type": "integer", "description": "Array disk slot (array_add/remove_disk_from_array)." },
                "correct": { "type": "boolean", "description": "Whether the parity check should write corrections (parity_check_start)." },
                "with_image": { "type": "boolean", "description": "Also remove the image (docker_remove_container)." },
                "ids": { "type": "array", "items": { "type": "string" }, "description": "Container IDs (docker_update_containers) / API key IDs (api_key_delete)." },
                "api_key_id": { "type": "string", "description": "API key ID (api_key_add_role/remove_role)." },
                "role": { "type": "string", "description": "Role name (api_key_add_role/remove_role)." },
                "permissions": { "type": "array", "items": { "type": "object" }, "description": "Permissions [{resource, actions}] (api_key_create/update)." },
                "overwrite": { "type": "boolean", "description": "Overwrite existing key (api_key_create)." },
                "url": { "type": "string", "description": "Plugin .plg URL (unraid_plugins_install_*)." },
                "forced": { "type": "boolean", "description": "Force install (unraid_plugins_install_*)." },
                "type": { "type": "string", "description": "RClone remote type (rclone_create_r_clone_remote)." },
                "parameters": { "type": "object", "description": "RClone remote parameters JSON (rclone_create_r_clone_remote)." },
                "comment": { "type": "string", "description": "Server comment (update_server_identity)." },
                "sys_model": { "type": "string", "description": "Server model (update_server_identity)." },
                "config": { "type": "object", "description": "UPS config object (configure_ups)." },
                "input": { "type": "object", "description": "Input object for update_system_time / update_temperature_config / add_plugin / remove_plugin." }
            },
            "required": ["action"]
        }
    })]
}

#[cfg(test)]
mod tests {
    use super::*;

    /// `help` is the only unscoped action; query actions are read-scoped and
    /// mutating actions are write-scoped. Guards against silently flipping scope.
    #[test]
    fn only_help_is_unscoped() {
        for spec in ACTIONS {
            match spec.name {
                "help" => assert!(spec.scope == Scope::None, "help must be unscoped"),
                _ => assert!(
                    spec.scope == Scope::Read || spec.scope == Scope::Write,
                    "{} must be read- or write-scoped",
                    spec.name
                ),
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
