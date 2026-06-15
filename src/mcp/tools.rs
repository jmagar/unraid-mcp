mod arg_helpers;
mod paginate;

use std::sync::LazyLock;

use serde_json::{json, Value};

use crate::token_limit::truncate_if_needed;

use self::arg_helpers::{i64_arg, string_arg, usize_arg};
use self::paginate::paginate_array;
use super::schemas::ACTIONS;
use super::AppState;

/// All valid action names — used in error messages. Derived from the canonical
/// [`ACTIONS`] list so it can never drift from the schema enum or scope source.
static VALID_ACTIONS: LazyLock<String> = LazyLock::new(|| {
    ACTIONS
        .iter()
        .map(|a| a.name)
        .collect::<Vec<_>>()
        .join(", ")
});

// ── public entry point ────────────────────────────────────────────────────────

/// Dispatch a named MCP tool. Returns `Ok(Value)` always; errors are encoded in
/// the returned value so the MCP protocol layer does not treat them as fatal.
///
/// Exposed at `pub(crate)` so in-crate test-support helpers (gated behind
/// `#[cfg(any(test, feature = "test-support"))]`, see [`crate::testing`]) can
/// drive a tool by name + args without going through the HTTP/stdio transports.
pub(crate) async fn execute_tool(
    state: &AppState,
    name: &str,
    args: Value,
) -> anyhow::Result<Value> {
    match name {
        "unraid" => dispatch(state, args).await,
        _ => Err(anyhow::anyhow!(
            "unknown tool: {name}\n\
             Hint: the only supported tool is \"unraid\".\n\
             Use action=help for documentation."
        )),
    }
}

/// Serialize `value` to pretty JSON and apply the 40 KB token-cap truncation.
pub(super) fn serialize_response(value: Value) -> anyhow::Result<String> {
    let text = serde_json::to_string_pretty(&value)?;
    Ok(truncate_if_needed(text))
}

// ── dispatch ──────────────────────────────────────────────────────────────────

async fn dispatch(state: &AppState, args: Value) -> anyhow::Result<Value> {
    let action = match string_arg(&args, "action") {
        Some(a) => a,
        None => {
            let valid = &*VALID_ACTIONS;
            return Err(anyhow::anyhow!(
                "\"action\" is required.\n\
                 Valid actions: {valid}\n\
                 Example: {{\"action\": \"docker\"}}\n\
                 See: action=help for full documentation."
            ));
        }
    };

    state.counters.inc_requests();

    let result = dispatch_action(state, &action, &args).await;

    match result {
        Ok(v) => Ok(v),
        Err(e) => {
            state.counters.inc_errors();
            Err(annotate_upstream_error(e, &action))
        }
    }
}

async fn dispatch_action(state: &AppState, action: &str, args: &Value) -> anyhow::Result<Value> {
    match action {
        "array" => state.service.array().await,
        "disks" => state.service.disks().await,

        "docker" => {
            let filter = string_arg(args, "state");
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .docker()
                .await
                .map(|v| paginate_array(v, &["docker", "containers"], limit, offset, filter))
        }

        "docker_logs" => {
            let id = string_arg(args, "id").ok_or_else(|| {
                anyhow::anyhow!(
                    "\"id\" is required for action=docker_logs.\n\
                     Hint: call action=docker first to list available container IDs.\n\
                     Example: {{\"action\": \"docker_logs\", \"id\": \"<container_id>\", \"tail\": 100}}"
                )
            })?;
            state.service.docker_logs(&id, i64_arg(args, "tail")?).await
        }

        "vms" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .vms()
                .await
                .map(|v| paginate_array(v, &["vms", "domains"], limit, offset, None))
        }

        "server" => state.service.server().await,
        "info" => state.service.info().await,

        "shares" => {
            let filter = string_arg(args, "name");
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .shares()
                .await
                .map(|v| paginate_array(v, &["shares"], limit, offset, filter))
        }

        "notifications" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state.service.notifications().await.map(|v| {
                paginate_array(
                    v,
                    &["notifications", "warningsAndAlerts"],
                    limit,
                    offset,
                    None,
                )
            })
        }

        "log_files" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .log_files()
                .await
                .map(|v| paginate_array(v, &["logFiles"], limit, offset, None))
        }

        "log_file" => {
            let path = string_arg(args, "path").ok_or_else(|| {
                anyhow::anyhow!(
                    "\"path\" is required for action=log_file.\n\
                     Hint: call action=log_files first to list available log file paths.\n\
                     Example: {{\"action\": \"log_file\", \"path\": \"/var/log/syslog\", \"lines\": 100}}"
                )
            })?;
            state
                .service
                .log_file(&path, i64_arg(args, "lines")?, i64_arg(args, "start_line")?)
                .await
        }

        "services" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .services()
                .await
                .map(|v| paginate_array(v, &["services"], limit, offset, None))
        }

        "network" => state.service.network().await,

        "ups" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .ups()
                .await
                .map(|v| paginate_array(v, &["upsDevices"], limit, offset, None))
        }

        "ups_config" => state.service.ups_config().await,
        "metrics" => state.service.metrics().await,

        "plugins" => {
            let filter = string_arg(args, "name");
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .plugins()
                .await
                .map(|v| paginate_array(v, &["plugins"], limit, offset, filter))
        }

        "parity_history" => {
            let limit = usize_arg(args, "limit")?.unwrap_or(50).min(200);
            let offset = usize_arg(args, "offset")?.unwrap_or(0);
            state
                .service
                .parity_history()
                .await
                .map(|v| paginate_array(v, &["parityHistory"], limit, offset, None))
        }

        "vars" => state.service.vars().await,
        "registration" => state.service.registration().await,
        "flash" => state.service.flash().await,
        "rclone" => state.service.rclone().await,
        "remote_access" => state.service.remote_access().await,
        "connect" => state.service.connect().await,

        "status" => {
            let snap = state.counters.snapshot();
            Ok(json!({
                "status": "ok",
                "server": {
                    "version": env!("CARGO_PKG_VERSION"),
                    "pid": std::process::id(),
                },
                "counters": snap,
            }))
        }

        "help" => Ok(json!({ "help": HELP_TEXT })),

        other => {
            let valid = &*VALID_ACTIONS;
            Err(anyhow::anyhow!(
                "unknown unraid action: \"{other}\"\n\
                 Valid actions: {valid}\n\
                 See: action=help for full documentation."
            ))
        }
    }
}

// ── upstream error annotation ─────────────────────────────────────────────────

fn annotate_upstream_error(err: anyhow::Error, action: &str) -> anyhow::Error {
    let msg = err.to_string();
    if msg.contains("connection refused")
        || msg.contains("failed to connect")
        || msg.contains("No connection could be made")
        || msg.contains("os error")
    {
        anyhow::anyhow!(
            "ERROR: {action} failed — upstream unreachable\n\
             Reason: {msg}\n\
             Hint: check that UNRAID_API_URL is reachable and UNRAID_API_KEY is valid.\n\
             Use action=status to check server health."
        )
    } else if msg.contains("API key") || msg.contains("401") || msg.contains("Unauthorized") {
        anyhow::anyhow!(
            "ERROR: {action} failed — API key rejected\n\
             Reason: {msg}\n\
             Hint: check that UNRAID_API_KEY is correct and has not expired."
        )
    } else {
        anyhow::anyhow!(
            "ERROR: {action} failed\n\
             Reason: {msg}\n\
             Hint: check UNRAID_API_URL and UNRAID_API_KEY. \
             Use action=status to check server health."
        )
    }
}

// ── help text ─────────────────────────────────────────────────────────────────

const HELP_TEXT: &str = r#"# unraid MCP Tool

Read-only access to the Unraid server via its GraphQL API.
Set the required `action` argument to select the operation.

## Core
- `array`          — Array state, disk health, parity, capacity
- `disks`          — Physical disks with SMART status and temps
- `docker`         — All Docker containers (supports limit, offset, state filter)
- `docker_logs`    — Container logs (requires `id`, optional `tail`)
                     Hint: call action=docker first to get a container id.
- `vms`            — Virtual machines and state (supports limit, offset)
- `server`         — Server identity, IPs, online status
- `info`           — OS, CPU, memory, Unraid/kernel versions
- `shares`         — User shares with sizes and cache settings (supports limit, offset, name filter)
- `notifications`  — Active warnings/alerts and overview counts (supports limit, offset)

## System
- `services`       — Running system services and uptime (supports limit, offset)
- `network`        — Network access URLs
- `metrics`        — Live CPU, memory, and temperature readings
- `vars`           — System configuration variables
- `registration`   — License registration state and expiry
- `flash`          — USB flash drive info

## Logs
- `log_files`      — List available log files with sizes (supports limit, offset)
                     Hint: call this first to get valid paths for action=log_file.
- `log_file`       — Read a log file (requires `path`, optional `lines`, `start_line`)

## Storage
- `parity_history` — All past parity check results (supports limit, offset)
- `rclone`         — Backup remote configurations

## UPS
- `ups`            — UPS devices: battery, power, status (supports limit, offset)
- `ups_config`     — UPS monitoring configuration

## Remote access
- `remote_access`  — WAN access type, port forwarding config
- `connect`        — Unraid Connect dynamic remote access status

## Plugins
- `plugins`        — Installed community plugins with versions (supports limit, offset, name filter)

## Observability
- `status`         — Server runtime state, request counters, pid

## Pagination (for list actions)
Pass `limit` (default 50, max 200) and `offset` (default 0) to page through results.
Response shape: {items, total, limit, offset, has_more, next_offset}

## Meta
- `help`           — This documentation
"#;
