"""Single consolidated Unraid tool.

Provides the `unraid` tool with 19 actions, each routing to domain-specific
subactions via the action + subaction pattern.

Actions:
  system       - Server info, metrics, network, UPS (18 subactions)
  health       - Health checks, connection test, diagnostics, setup (4 subactions)
  array        - Parity checks, array state, disk operations (14 subactions)
  disk         - Shares, physical disks, log files (6 subactions)
  docker       - Container lifecycle, updates, organizer, networks (25 subactions)
  vm           - Virtual machine lifecycle (9 subactions)
  notification - System notifications CRUD (12 subactions)
  key          - API key & permission management (13 subactions)
  plugin       - Plugin management and async installs (8 subactions)
  rclone       - Cloud storage remote management (4 subactions)
  setting      - System settings, UPS, SSH, time, identity (6 subactions)
  connect      - Unraid Connect / remote access (7 subactions)
  customization - Theme, locale and UI customization (5 subactions)
  oidc         - OIDC/SSO provider management (5 subactions)
  onboarding   - First-boot/onboarding state (11 subactions)
  user         - Current authenticated user (1 subaction)
  live         - Real-time WebSocket subscription snapshots (16 subactions)
  subscriptions - WebSocket subscription diagnostics (2 subactions)
  help         - Return the full Markdown action/subaction reference (no subaction)
"""

import datetime
import time
from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import validate_subaction

# Re-exports: domain modules' constants and helpers needed by tests
# Re-export array queries for schema tests
from ._array import (  # noqa: F401
    _ARRAY_DESTRUCTIVE,
    _ARRAY_MUTATIONS,
    _ARRAY_QUERIES,
    _handle_array,
)
from ._connect import (  # noqa: F401
    _CONNECT_DESTRUCTIVE,
    _CONNECT_MUTATIONS,
    _CONNECT_QUERIES,
    _handle_connect,
)
from ._customization import (  # noqa: F401
    _CUSTOMIZATION_MUTATIONS,
    _CUSTOMIZATION_QUERIES,
    _handle_customization,
)
from ._disk import _DISK_DESTRUCTIVE, _DISK_MUTATIONS, _DISK_QUERIES, _handle_disk  # noqa: F401
from ._docker import (  # noqa: F401
    _DOCKER_BULK_MUTATIONS,
    _DOCKER_DESTRUCTIVE,
    _DOCKER_MUTATIONS,
    _DOCKER_ORGANIZER,
    _DOCKER_QUERIES,
    _DOCKER_ROOT_MUTATIONS,
    _handle_docker,
)
from ._health import (  # noqa: F401
    _HEALTH_QUERIES,
    _HEALTH_SUBACTIONS,
    _SEVERITY,
    _comprehensive_health_check,
)
from ._key import _KEY_DESTRUCTIVE, _KEY_MUTATIONS, _KEY_QUERIES, _handle_key  # noqa: F401
from ._live import _handle_live
from ._notification import (  # noqa: F401
    _NOTIFICATION_DESTRUCTIVE,
    _NOTIFICATION_MUTATIONS,
    _NOTIFICATION_QUERIES,
    _handle_notification,
)
from ._oidc import _OIDC_QUERIES, _handle_oidc  # noqa: F401
from ._onboarding import (  # noqa: F401
    _ONBOARDING_DESTRUCTIVE,
    _ONBOARDING_INPUT_MUTATIONS,
    _ONBOARDING_QUERIES,
    _ONBOARDING_SIMPLE_MUTATIONS,
    _handle_onboarding,
)
from ._plugin import (  # noqa: F401
    _PLUGIN_DESTRUCTIVE,
    _PLUGIN_MUTATIONS,
    _PLUGIN_QUERIES,
    _handle_plugin,
)
from ._rclone import (  # noqa: F401
    _RCLONE_DESTRUCTIVE,
    _RCLONE_MUTATIONS,
    _RCLONE_QUERIES,
    _handle_rclone,
)
from ._setting import _SETTING_DESTRUCTIVE, _SETTING_MUTATIONS, _handle_setting  # noqa: F401
from ._system import (  # noqa: F401
    _SYSTEM_QUERIES,
    _analyze_disk_health,
    _handle_system,
)
from ._user import _USER_QUERIES, _handle_user  # noqa: F401
from ._vm import _VM_DESTRUCTIVE, _VM_MUTATIONS, _VM_QUERIES, _handle_vm  # noqa: F401


# ===========================================================================
# HEALTH handler
# ===========================================================================


async def _handle_health(subaction: str, ctx: Context | None) -> dict[str, Any] | str:
    validate_subaction(subaction, _HEALTH_SUBACTIONS, "health")

    from ..config.settings import (
        CREDENTIALS_ENV_PATH,
        UNRAID_API_URL,
        is_configured,
    )
    from ..core.utils import safe_display_url
    from ..subscriptions.utils import _analyze_subscription_status

    if subaction == "setup":
        if is_configured():
            try:
                await _client.make_graphql_request(_SYSTEM_QUERIES["online"])
                status = "and the connection test succeeded"
            except Exception as e:
                logger.debug("health/setup connection probe failed: %s: %s", type(e).__name__, e)
                status = (
                    f"but the connection test failed ({type(e).__name__}) — "
                    "this may be a transient outage or a misconfiguration"
                )
            return (
                f"✅ Credentials are configured ({status}).\n"
                f"URL: `{safe_display_url(UNRAID_API_URL)}`\n"
                f"File: `{CREDENTIALS_ENV_PATH}`\n\n"
                "To change them, update the plugin's userConfig form "
                "(Unraid GraphQL API URL / Unraid API Key) or edit that file, "
                "then restart the server."
            )
        # Not loaded in this session. Credentials load once at startup, so a .env that
        # exists on disk (e.g. just written by the ConfigChange hook) is not active until
        # the next restart — report that distinctly from a genuinely-missing config.
        if CREDENTIALS_ENV_PATH.exists():
            return (
                f"⚠️ A credentials file exists (`{CREDENTIALS_ENV_PATH}`) but is not loaded "
                "in this session — credentials are read once at startup.\n\n"
                "Restart the server (or your MCP client), then run "
                '`unraid(action="health", subaction="test_connection")` to verify. '
                "If it still fails, check that the file contains non-empty "
                "`UNRAID_API_URL` and `UNRAID_API_KEY` values."
            )
        return (
            "⚠️ Credentials are not configured.\n\n"
            "**Claude Code plugin:** set *Unraid GraphQL API URL* and *Unraid API Key* "
            "in the plugin's configuration form — they are applied automatically on the "
            "next session and persisted to disk.\n\n"
            f"**Manual / Docker:** create `{CREDENTIALS_ENV_PATH}` with:\n"
            "```\nUNRAID_API_URL=https://your-unraid-server:port\n"
            "UNRAID_API_KEY=your-api-key\n```\n\n"
            "Then restart the server and run "
            '`unraid(action="health", subaction="test_connection")` to verify.'
        )

    with tool_error_handler("health", subaction, logger):
        logger.info(f"Executing unraid action=health subaction={subaction}")

        if subaction == "test_connection":
            start = time.time()
            data = await _client.make_graphql_request(_SYSTEM_QUERIES["online"])
            latency = round((time.time() - start) * 1000, 2)
            return {"status": "connected", "online": data.get("online"), "latency_ms": latency}

        if subaction == "check":
            return await _comprehensive_health_check()

        if subaction == "diagnose":
            # Import from middleware_refs (not server) to avoid the circular
            # dependency: server.py imports tools/unraid.py at module level.
            from ..core.middleware_refs import error_middleware
            from ..subscriptions.manager import subscription_manager
            from ..subscriptions.resources import ensure_subscriptions_started

            await ensure_subscriptions_started()
            status = await subscription_manager.get_subscription_status()
            error_count, connection_issues = _analyze_subscription_status(status)
            return {
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "environment": {
                    "auto_start_enabled": subscription_manager.auto_start_enabled,
                    "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                    "api_url_configured": bool(UNRAID_API_URL),
                },
                "subscriptions": status,
                "summary": {
                    "total_configured": len(subscription_manager.subscription_configs),
                    "active_count": len(subscription_manager.active_subscriptions),
                    "with_data": len(subscription_manager.resource_data),
                    "in_error_state": error_count,
                    "connection_issues": connection_issues,
                },
                # cache section removed: ResponseCachingMiddleware was removed because
                # all caching was disabled (the consolidated `unraid` tool mixes reads
                # and mutations, making safe per-subaction exclusion impossible).
                "cache": {"note": "caching disabled — tool mixes reads and mutations"},
                "errors": error_middleware.get_error_stats()
                if error_middleware is not None
                else {},
            }

        raise ToolError(f"Unhandled health subaction '{subaction}' — this is a bug")


_HELP_TEXT = """# Unraid MCP Server

Interact with an Unraid server's GraphQL API.

## Tool: `unraid`

Single entry point for all operations. Use `action` + `subaction` to select an operation.

### Actions and Subactions

| Action | Subactions | Notes |
|--------|-----------|-------|
| `system` | `overview`, `array`, `network`, `registration`, `variables`, `metrics`, `services`, `display`, `config`, `online`, `owner`, `settings`, `server`, `servers`, `flash`, `ups_devices`, `ups_device`, `ups_config` | |
| `health` | `check`, `test_connection`, `diagnose`, `setup` | |
| `array` | `parity_status`, `parity_history`, `assignable_disks`, `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`, `start_array`, `stop_array`*, `add_disk`, `remove_disk`*, `mount_disk`, `unmount_disk`, `clear_disk_stats`* | |
| `disk` | `shares`, `disks`, `disk_details`, `log_files`, `logs`, `flash_backup`* | |
| `docker` | `list`, `details`, `ports`, `start`, `stop`, `restart`, `unpause`, `networks`, `network_details`, `remove_container`*, `update_container`, `update_containers`, `update_all_containers`, `update_autostart`, `refresh_digests`, `sync_template_paths`, `reset_template_mappings`*, `create_folder`, `create_folder_with_items`, `rename_folder`, `set_folder_children`, `delete_entries`*, `move_entries_to_folder`, `move_items_to_position`, `update_view_preferences` | organizer ops use `organizer_input` |
| `vm` | `list`, `details`, `start`, `stop`, `pause`, `resume`, `force_stop`*, `reboot`, `reset`* | |
| `notification` | `overview`, `list`, `create`, `archive`, `mark_unread`, `recalculate`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`*, `delete_archived`* | |
| `key` | `list`, `get`, `possible_roles`, `possible_permissions`, `permissions_for_roles`, `preview_permissions`, `auth_actions`, `creation_form_schema`, `create`, `update`, `delete`*, `add_role`, `remove_role` | |
| `plugin` | `list`, `installed_unraid`, `install_operations`, `install_operation`, `add`, `remove`*, `install`*, `install_language`* | install runs a .plg as root |
| `rclone` | `list_remotes`, `config_form`, `create_remote`, `delete_remote`* | |
| `setting` | `update`, `configure_ups`*, `update_ssh`*, `update_temperature`, `update_system_time`*, `update_server_identity` | |
| `connect` | `remote_access`, `cloud`, `update_api_settings`*, `sign_in`*, `sign_out`*, `setup_remote_access`*, `enable_dynamic_remote_access`* | Unraid Connect; all mutations destructive; inputs via `connect_input` |
| `customization` | `public_theme`, `is_initial_setup`, `sso_enabled`, `set_theme`, `set_locale` | |
| `oidc` | `providers`, `provider`, `configuration`, `public_providers`, `validate_session` | |
| `onboarding` | `internal_boot_context`, `complete`, `open`, `close`, `resume`, `bypass`, `reset`*, `set_override`, `clear_override`, `refresh_internal_boot_context`, `create_internal_boot_pool`* | inputs via `onboarding_input` |
| `user` | `me` | |
| `live` | `cpu`, `memory`, `cpu_telemetry`, `array_state`, `parity_progress`, `ups_status`, `notifications_overview`, `notifications_warnings`, `owner`, `server_status`, `display`, `docker_container_stats`, `temperature`, `log_tail` (requires `path=`), `notification_feed`, `plugin_install_updates` | |
| `subscriptions` | `diagnose`, `test_query` (requires `subscription_query=`) | WebSocket subscription diagnostics |
| `help` | _(no subaction)_ | Returns this reference |

\\* Destructive — requires `confirm=True`

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | str | One of the actions above |
| `subaction` | str | Operation within the action |
| `confirm` | bool | Set `True` for destructive subactions (marked `*`). Interactive clients are prompted via elicitation; agents and one-shot API callers **must** pass `confirm=True` to bypass elicitation. (default: False) |
| `container_id` | str | Docker container ID or name |
| `container_ids` | list[str] | Multiple container IDs/names (docker/update_containers) |
| `with_image` | bool | Also remove the image (docker/remove_container) |
| `autostart_entries` | list[dict] | Autostart config: `[{id, autoStart, wait?}]` (docker/update_autostart) |
| `organizer_input` | dict | Docker organizer/folder mutation fields (docker/*_folder, *_entries, etc.) |
| `vm_id` | str | VM identifier |
| `disk_id` | str | Disk identifier |
| `notification_id` | str | Single notification ID |
| `notification_ids` | list[str] | Multiple notification IDs |
| `key_id` | str | API key identifier |
| `name` | str | Name for create/update operations (also server name for setting/update_server_identity) |
| `roles` | list[str] | Roles (key ops, key/permissions_for_roles, key/preview_permissions) |
| `permissions_input` | list[dict] | Structured permissions `[{resource, actions}]` (key/preview_permissions) |
| `url` | str | Plugin .plg URL (plugin/install, plugin/install_language) |
| `plugin_name` | str | Optional plugin name (plugin/install) |
| `forced` | bool | Force plugin install (plugin/install) |
| `operation_id` | str | Plugin install operation ID (plugin/install_operation, live/plugin_install_updates) |
| `config_input` | dict | Input object for setting/update_ssh, update_temperature, update_system_time |
| `comment` | str | Server comment (setting/update_server_identity) |
| `sys_model` | str | Server model string (setting/update_server_identity) |
| `connect_input` | dict | Input object for connect mutations (sign_in, setup_remote_access, etc.) |
| `onboarding_input` | dict | Input object for onboarding/set_override, create_internal_boot_pool |
| `theme_name` | str | Theme name (customization/set_theme) |
| `locale` | str | Locale string (customization/set_locale) |
| `path` | str | Log file path (for live/log_tail) |
| `subscription_query` | str | Raw GraphQL subscription string (for `subscriptions/test_query`) |
| `collect_for` | float | WebSocket collection duration in seconds (default: 5.0) |
| `level` | str | Filter logs to this severity and above: one of debug, info, notice, warning, error, critical (for `disk/logs` and `live/log_tail`). Omit for no filtering. |
| `context` | int | Lines of context kept before/after each matching log line (default: 2). Non-contiguous matches are separated by `---`. |
| `limit` | int | Max items to return (default: 20) |
| `offset` | int | Pagination offset (default: 0) |

### Examples

```
unraid(action="system", subaction="overview")
unraid(action="health", subaction="check")
unraid(action="health", subaction="test_connection")
unraid(action="docker", subaction="list")
unraid(action="docker", subaction="start", container_id="my-container")
unraid(action="vm", subaction="list")
unraid(action="array", subaction="parity_status")
unraid(action="notification", subaction="list", limit=10, list_type="UNREAD")
unraid(action="disk", subaction="disks")
unraid(action="live", subaction="cpu", collect_for=3.0)
unraid(action="live", subaction="log_tail", path="/var/log/syslog", collect_for=5.0)
unraid(action="live", subaction="log_tail", path="/var/log/syslog", level="warning", context=3)
unraid(action="disk", subaction="logs", log_path="/var/log/syslog", level="error", context=2)
unraid(action="array", subaction="stop_array", confirm=True)
unraid(action="subscriptions", subaction="diagnose")
unraid(action="subscriptions", subaction="test_query", subscription_query="subscription { cpu { used idle system } }")
unraid(action="help")
```

## `subscriptions` action

- `diagnose` — full diagnostic dump of the WebSocket subscription system
  (connection states, error counts, reconnect status, troubleshooting hints).
- `test_query` — send a raw GraphQL subscription string directly over the
  WebSocket to debug schema/field issues. Requires `subscription_query=`. Only
  whitelisted subscription fields are permitted; mutation/query keywords are
  rejected.

## `help` action

`unraid(action="help")` returns this document.
"""


# ===========================================================================
# TOOL REGISTRATION
# ===========================================================================

UNRAID_ACTIONS = Literal[
    "array",
    "connect",
    "customization",
    "disk",
    "docker",
    "health",
    "help",
    "key",
    "live",
    "notification",
    "oidc",
    "onboarding",
    "plugin",
    "rclone",
    "setting",
    "subscriptions",
    "system",
    "user",
    "vm",
]


def register_unraid_tool(mcp: FastMCP) -> None:
    """Register the single `unraid` tool with the FastMCP instance."""

    @mcp.tool(timeout=120)
    async def unraid(
        action: UNRAID_ACTIONS,
        subaction: str = "",
        ctx: Context | None = None,
        confirm: bool = False,
        # system
        device_id: str | None = None,
        # array + disk
        disk_id: str | None = None,
        correct: bool | None = None,
        slot: int | None = None,
        # disk
        log_path: str | None = None,
        tail_lines: int = 100,
        remote_name: str | None = None,
        source_path: str | None = None,
        destination_path: str | None = None,
        backup_options: dict[str, Any] | None = None,
        # docker
        container_id: str | None = None,
        network_id: str | None = None,
        container_ids: list[str] | None = None,
        with_image: bool = False,
        autostart_entries: list[dict[str, Any]] | None = None,
        organizer_input: dict[str, Any] | None = None,
        # vm
        vm_id: str | None = None,
        # notification
        notification_id: str | None = None,
        notification_ids: list[str] | None = None,
        notification_type: str | None = None,
        importance: str | None = None,
        offset: int = 0,
        limit: int = 20,
        list_type: str = "UNREAD",
        title: str | None = None,
        subject: str | None = None,
        description: str | None = None,
        # key
        key_id: str | None = None,
        name: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        permissions_input: list[dict[str, Any]] | None = None,
        # plugin
        names: list[str] | None = None,
        bundled: bool = False,
        restart: bool = True,
        url: str | None = None,
        plugin_name: str | None = None,
        forced: bool = False,
        operation_id: str | None = None,
        # rclone
        provider_type: str | None = None,
        config_data: dict[str, Any] | None = None,
        # setting
        settings_input: dict[str, Any] | None = None,
        ups_config: dict[str, Any] | None = None,
        config_input: dict[str, Any] | None = None,
        comment: str | None = None,
        sys_model: str | None = None,
        # connect
        connect_input: dict[str, Any] | None = None,
        # onboarding
        onboarding_input: dict[str, Any] | None = None,
        # customization
        theme_name: str | None = None,
        locale: str | None = None,
        # oidc
        provider_id: str | None = None,
        token: str | None = None,
        # subscriptions
        subscription_query: str | None = None,
        # live
        path: str | None = None,
        collect_for: float = 5.0,
        timeout: float = 10.0,  # noqa: ASYNC109
        # log filtering (disk/logs + live/log_tail)
        level: str | None = None,
        context: int = 2,
    ) -> dict[str, Any] | str:
        """Interact with an Unraid server's GraphQL API.

        Use action + subaction to select an operation. All params are optional
        except those required by the specific subaction.

        ┌─────────────────┬──────────────────────────────────────────────────────────────────────┐
        │ action          │ subactions                                                           │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ system          │ overview, array, network, registration, variables, metrics,          │
        │                 │ services, display, config, online, owner, settings, server,          │
        │                 │ servers, flash, ups_devices, ups_device, ups_config                  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ health          │ check, test_connection, diagnose, setup                              │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ array           │ parity_status, parity_history, assignable_disks,                     │
        │                 │ parity_start, parity_pause, parity_resume, parity_cancel,            │
        │                 │ start_array, stop_array*, add_disk, remove_disk*, mount_disk,         │
        │                 │ unmount_disk, clear_disk_stats*                                      │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ disk            │ shares, disks, disk_details, log_files, logs, flash_backup*          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ docker          │ list, details, ports, start, stop, restart, unpause, networks,       │
        │                 │ network_details, remove_container*, update_container,                │
        │                 │ update_containers, update_all_containers, update_autostart,          │
        │                 │ refresh_digests, sync_template_paths, reset_template_mappings*,       │
        │                 │ create_folder, create_folder_with_items, rename_folder,              │
        │                 │ set_folder_children, delete_entries*, move_entries_to_folder,         │
        │                 │ move_items_to_position, update_view_preferences                      │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ vm              │ list, details, start, stop, pause, resume,                           │
        │                 │ force_stop*, reboot, reset*                                          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ notification    │ overview, list, create, archive, mark_unread, recalculate,           │
        │                 │ archive_all, archive_many, unarchive_many, unarchive_all,            │
        │                 │ delete*, delete_archived*                                            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ key             │ list, get, possible_roles, possible_permissions,                     │
        │                 │ permissions_for_roles, preview_permissions, auth_actions,            │
        │                 │ creation_form_schema, create, update, delete*, add_role, remove_role │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ plugin          │ list, installed_unraid, install_operations, install_operation,       │
        │                 │ add, remove*, install*, install_language*                            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ rclone          │ list_remotes, config_form, create_remote, delete_remote*             │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ setting         │ update, configure_ups*, update_ssh*, update_temperature,             │
        │                 │ update_system_time*, update_server_identity                         │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ connect         │ remote_access, cloud, update_api_settings*, sign_in*, sign_out*,      │
        │                 │ setup_remote_access*, enable_dynamic_remote_access*                  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ customization   │ public_theme, is_initial_setup, sso_enabled, set_theme, set_locale   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ oidc            │ providers, provider, configuration, public_providers,                │
        │                 │ validate_session                                                     │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ onboarding      │ internal_boot_context, complete, open, close, resume, bypass,        │
        │                 │ reset*, set_override, clear_override,                                │
        │                 │ refresh_internal_boot_context, create_internal_boot_pool*           │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ user            │ me                                                                   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ live            │ cpu, memory, cpu_telemetry, array_state, parity_progress,            │
        │                 │ ups_status, notifications_overview, notifications_warnings,          │
        │                 │ owner, server_status, display, docker_container_stats,               │
        │                 │ temperature, log_tail (requires path=), notification_feed,           │
        │                 │ plugin_install_updates                                              │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ subscriptions   │ diagnose, test_query (requires subscription_query=)                  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ help            │ (no subaction — returns the full Markdown reference)                 │
        └─────────────────┴──────────────────────────────────────────────────────────────────────┘

        * Destructive — interactive clients are prompted for confirmation via
          elicitation. Agents and non-interactive callers must pass confirm=True
          to execute these subactions.

        Log filtering (disk/logs, live/log_tail): pass level= to keep only lines
        at-or-above a severity (debug|info|notice|warning|error|critical) and
        context= (default 2) for lines of surrounding context around each match.
        Non-contiguous matches are separated by a '---' marker. Omit level for
        unchanged output.
        """
        if action == "help":
            return _HELP_TEXT

        if action == "system":
            return await _handle_system(subaction, device_id, limit)

        if action == "health":
            return await _handle_health(subaction, ctx)

        if action == "array":
            return await _handle_array(subaction, disk_id, correct, slot, ctx, confirm, limit)

        if action == "disk":
            return await _handle_disk(
                subaction,
                disk_id,
                log_path,
                tail_lines,
                remote_name,
                source_path,
                destination_path,
                backup_options,
                ctx,
                confirm,
                level,
                context,
                limit,
            )

        if action == "docker":
            return await _handle_docker(
                subaction,
                container_id,
                network_id,
                limit,
                ctx,
                confirm,
                container_ids,
                with_image,
                autostart_entries,
                organizer_input,
            )

        if action == "vm":
            return await _handle_vm(subaction, vm_id, ctx, confirm)

        if action == "notification":
            return await _handle_notification(
                subaction,
                ctx,
                confirm,
                notification_id,
                notification_ids,
                notification_type,
                importance,
                offset,
                limit,
                list_type,
                title,
                subject,
                description,
            )

        if action == "key":
            return await _handle_key(
                subaction,
                key_id,
                name,
                roles,
                permissions,
                ctx,
                confirm,
                limit,
                permissions_input,
            )

        if action == "plugin":
            return await _handle_plugin(
                subaction,
                names,
                bundled,
                restart,
                ctx,
                confirm,
                limit,
                url,
                plugin_name,
                forced,
                operation_id,
            )

        if action == "rclone":
            return await _handle_rclone(
                subaction, name, provider_type, config_data, ctx, confirm, limit
            )

        if action == "setting":
            return await _handle_setting(
                subaction,
                settings_input,
                ups_config,
                ctx,
                confirm,
                config_input,
                name,
                comment,
                sys_model,
            )

        if action == "connect":
            return await _handle_connect(subaction, ctx, confirm, connect_input)

        if action == "onboarding":
            return await _handle_onboarding(subaction, ctx, confirm, onboarding_input)

        if action == "customization":
            return await _handle_customization(subaction, theme_name, locale)

        if action == "oidc":
            return await _handle_oidc(subaction, provider_id, token, limit)

        if action == "user":
            return await _handle_user(subaction)

        if action == "live":
            return await _handle_live(
                subaction, path, collect_for, timeout, level, context, limit, operation_id
            )

        if action == "subscriptions":
            # Lazy import to keep tool import-time free of the subscription stack
            # (mirrors the health/diagnose pattern above).
            from ..subscriptions.diagnostics import _handle_subscriptions

            return await _handle_subscriptions(subaction, subscription_query)

        raise ToolError(
            f"Invalid action '{action}'. Must be one of: {sorted(get_args(UNRAID_ACTIONS))}"
        )

    logger.info("Unraid tool registered successfully")
