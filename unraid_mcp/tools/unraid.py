"""Single consolidated Unraid tool.

Provides the `unraid` tool with 15 actions, each routing to domain-specific
subactions via the action + subaction pattern.

Actions:
  system       - Server info, metrics, network, UPS (20 subactions)
  health       - Health checks, connection test, diagnostics, setup (4 subactions)
  array        - Parity checks, array state, disk operations (13 subactions)
  disk         - Shares, physical disks, log files (6 subactions)
  docker       - Container lifecycle and network inspection (7 subactions)
  vm           - Virtual machine lifecycle (9 subactions)
  notification - System notifications CRUD (13 subactions)
  key          - API key management (8 subactions)
  plugin       - Plugin management (3 subactions)
  rclone       - Cloud storage remote management (4 subactions)
  setting      - System settings and UPS config (2 subactions)
  customization - Theme and UI customization (5 subactions)
  oidc         - OIDC/SSO provider management (5 subactions)
  user         - Current authenticated user (1 subaction)
  live         - Real-time WebSocket subscription snapshots (11 subactions)
"""

import datetime
import time
from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_and_configure, elicit_reset_confirmation
from ..core.utils import validate_subaction

# Re-exports: domain modules' constants and helpers needed by tests
# Re-export array queries for schema tests
from ._array import (  # noqa: F401
    _ARRAY_DESTRUCTIVE,
    _ARRAY_MUTATIONS,
    _ARRAY_QUERIES,
    _handle_array,
)
from ._customization import (  # noqa: F401
    _CUSTOMIZATION_MUTATIONS,
    _CUSTOMIZATION_QUERIES,
    _handle_customization,
)
from ._disk import _DISK_DESTRUCTIVE, _DISK_MUTATIONS, _DISK_QUERIES, _handle_disk  # noqa: F401
from ._docker import _DOCKER_MUTATIONS, _DOCKER_QUERIES, _handle_docker  # noqa: F401
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
# HEALTH handler — kept here so test patches on unraid_mcp.tools.unraid.*
# intercept elicit_and_configure / elicit_reset_confirmation correctly
# ===========================================================================


async def _handle_health(subaction: str, ctx: Context | None) -> dict[str, Any] | str:
    validate_subaction(subaction, _HEALTH_SUBACTIONS, "health")

    from ..config.settings import (
        CREDENTIALS_ENV_PATH,
        UNRAID_API_URL,
    )
    from ..core.utils import safe_display_url
    from ..subscriptions.utils import _analyze_subscription_status

    if subaction == "setup":
        if CREDENTIALS_ENV_PATH.exists():
            connection_error_type: str | None = None
            try:
                await _client.make_graphql_request(_SYSTEM_QUERIES["online"])
                connection_ok = True
            except Exception as e:
                connection_ok = False
                connection_error_type = type(e).__name__
                logger.debug(f"health/setup connection probe failed: {connection_error_type}: {e}")
            if connection_ok:
                status_note = "and working"
            elif connection_error_type:
                status_note = f"but the connection test failed ({connection_error_type}) — may be a transient outage or misconfiguration"
            else:
                status_note = "but the connection test failed — may be a transient outage"
            reset = await elicit_reset_confirmation(
                ctx,
                f"{safe_display_url(UNRAID_API_URL) or ''} ({status_note})",
            )
            if not reset:
                return (
                    f"✅ Credentials already configured ({status_note}).\n"
                    f"URL: `{safe_display_url(UNRAID_API_URL)}`\n\nNo changes made."
                )
        configured = await elicit_and_configure(ctx)
        if configured:
            return "✅ Credentials configured successfully. You can now use all Unraid MCP tools."
        return (
            f"⚠️ Credentials not configured.\n\n"
            f"Your MCP client may not support elicitation, or setup was cancelled.\n\n"
            f"**Manual setup** — create `{CREDENTIALS_ENV_PATH}` with:\n"
            f"```\nUNRAID_API_URL=https://your-unraid-server:port\nUNRAID_API_KEY=your-api-key\n```\n\n"
            "Then run any Unraid tool to connect."
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
| `array` | `parity_status`, `parity_history`, `parity_start`, `parity_pause`, `parity_resume`, `parity_cancel`, `start_array`, `stop_array`*, `add_disk`, `remove_disk`*, `mount_disk`, `unmount_disk`, `clear_disk_stats`* | |
| `disk` | `shares`, `disks`, `disk_details`, `log_files`, `logs`, `flash_backup`* | |
| `docker` | `list`, `details`, `start`, `stop`, `restart`, `networks`, `network_details` | |
| `vm` | `list`, `details`, `start`, `stop`, `pause`, `resume`, `force_stop`*, `reboot`, `reset`* | |
| `notification` | `overview`, `list`, `create`, `archive`, `mark_unread`, `recalculate`, `archive_all`, `archive_many`, `unarchive_many`, `unarchive_all`, `delete`*, `delete_archived`* | |
| `key` | `list`, `get`, `create`, `update`, `delete`*, `add_role`, `remove_role` | |
| `plugin` | `list`, `add`, `remove`* | |
| `rclone` | `list_remotes`, `config_form`, `create_remote`, `delete_remote`* | |
| `setting` | `update`, `configure_ups`* | |
| `customization` | `theme`, `public_theme`, `is_initial_setup`, `sso_enabled`, `set_theme` | |
| `oidc` | `providers`, `provider`, `configuration`, `public_providers`, `validate_session` | |
| `user` | `me` | |
| `live` | `cpu`, `memory`, `cpu_telemetry`, `array_state`, `parity_progress`, `ups_status`, `notifications_overview`, `owner`, `server_status`, `log_tail` (requires `path=`), `notification_feed` | |

\\* Destructive — requires `confirm=True`

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | str | One of the actions above |
| `subaction` | str | Operation within the action |
| `confirm` | bool | Set `True` for destructive subactions (marked `*`). Interactive clients are prompted via elicitation; agents and one-shot API callers **must** pass `confirm=True` to bypass elicitation. (default: False) |
| `container_id` | str | Docker container ID or name |
| `vm_id` | str | VM identifier |
| `disk_id` | str | Disk identifier |
| `notification_id` | str | Single notification ID |
| `notification_ids` | list[str] | Multiple notification IDs |
| `key_id` | str | API key identifier |
| `name` | str | Name for create/update operations |
| `path` | str | Log file path (for live/log_tail) |
| `collect_for` | float | WebSocket collection duration in seconds (default: 5.0) |
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
unraid(action="array", subaction="stop_array", confirm=True)
```

## Tool: `unraid_help`

Returns this help document.
"""


# ===========================================================================
# TOOL REGISTRATION
# ===========================================================================

UNRAID_ACTIONS = Literal[
    "array",
    "customization",
    "disk",
    "docker",
    "health",
    "key",
    "live",
    "notification",
    "oidc",
    "plugin",
    "rclone",
    "setting",
    "system",
    "user",
    "vm",
]


def register_unraid_tool(mcp: FastMCP) -> None:
    """Register the single `unraid` tool with the FastMCP instance."""

    @mcp.tool(timeout=120)
    async def unraid(
        action: UNRAID_ACTIONS,
        subaction: str,
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
        # plugin
        names: list[str] | None = None,
        bundled: bool = False,
        restart: bool = True,
        # rclone
        provider_type: str | None = None,
        config_data: dict[str, Any] | None = None,
        # setting
        settings_input: dict[str, Any] | None = None,
        ups_config: dict[str, Any] | None = None,
        # customization
        theme_name: str | None = None,
        # oidc
        provider_id: str | None = None,
        token: str | None = None,
        # live
        path: str | None = None,
        collect_for: float = 5.0,
        timeout: float = 10.0,  # noqa: ASYNC109
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
        │ array           │ parity_status, parity_history, parity_start, parity_pause,          │
        │                 │ parity_resume, parity_cancel, start_array, stop_array*,              │
        │                 │ add_disk, remove_disk*, mount_disk, unmount_disk, clear_disk_stats*  │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ disk            │ shares, disks, disk_details, log_files, logs, flash_backup*          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ docker          │ list, details, start, stop, restart, networks, network_details       │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ vm              │ list, details, start, stop, pause, resume,                           │
        │                 │ force_stop*, reboot, reset*                                          │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ notification    │ overview, list, create, archive, mark_unread, recalculate,           │
        │                 │ archive_all, archive_many, unarchive_many, unarchive_all,            │
        │                 │ delete*, delete_archived*                                            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ key             │ list, get, create, update, delete*, add_role, remove_role            │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ plugin          │ list, add, remove*                                                   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ rclone          │ list_remotes, config_form, create_remote, delete_remote*             │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ setting         │ update, configure_ups*                                               │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ customization   │ theme, public_theme, is_initial_setup, sso_enabled, set_theme        │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ oidc            │ providers, provider, configuration, public_providers,                │
        │                 │ validate_session                                                     │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ user            │ me                                                                   │
        ├─────────────────┼──────────────────────────────────────────────────────────────────────┤
        │ live            │ cpu, memory, cpu_telemetry, array_state, parity_progress,            │
        │                 │ ups_status, notifications_overview, owner, server_status,            │
        │                 │ log_tail (requires path=), notification_feed                         │
        └─────────────────┴──────────────────────────────────────────────────────────────────────┘

        * Destructive — interactive clients are prompted for confirmation via
          elicitation. Agents and non-interactive callers must pass confirm=True
          to execute these subactions.
        """
        if action == "system":
            return await _handle_system(subaction, device_id)

        if action == "health":
            return await _handle_health(subaction, ctx)

        if action == "array":
            return await _handle_array(subaction, disk_id, correct, slot, ctx, confirm)

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
            )

        if action == "docker":
            return await _handle_docker(subaction, container_id, network_id)

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
            return await _handle_key(subaction, key_id, name, roles, permissions, ctx, confirm)

        if action == "plugin":
            return await _handle_plugin(subaction, names, bundled, restart, ctx, confirm)

        if action == "rclone":
            return await _handle_rclone(subaction, name, provider_type, config_data, ctx, confirm)

        if action == "setting":
            return await _handle_setting(subaction, settings_input, ups_config, ctx, confirm)

        if action == "customization":
            return await _handle_customization(subaction, theme_name)

        if action == "oidc":
            return await _handle_oidc(subaction, provider_id, token)

        if action == "user":
            return await _handle_user(subaction)

        if action == "live":
            return await _handle_live(subaction, path, collect_for, timeout)

        raise ToolError(
            f"Invalid action '{action}'. Must be one of: {sorted(get_args(UNRAID_ACTIONS))}"
        )

    @mcp.tool()
    async def unraid_help() -> str:
        """Returns markdown help for all Unraid MCP actions and subactions."""
        return _HELP_TEXT

    logger.info("Unraid tool registered successfully")
