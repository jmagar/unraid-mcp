"""Plugin management for the Unraid API.

Provides the `unraid_plugins` tool with 3 actions: list, add, remove.
"""

from __future__ import annotations

from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_destructive_confirmation


QUERIES: dict[str, str] = {
    "list": """
        query ListPlugins {
          plugins { name version hasApiModule hasCliModule }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "add": """
        mutation AddPlugin($input: PluginManagementInput!) {
          addPlugin(input: $input)
        }
    """,
    "remove": """
        mutation RemovePlugin($input: PluginManagementInput!) {
          removePlugin(input: $input)
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"remove"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

PLUGIN_ACTIONS = Literal["add", "list", "remove"]

if set(get_args(PLUGIN_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(PLUGIN_ACTIONS))
    _extra = set(get_args(PLUGIN_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"PLUGIN_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing: {_missing or 'none'}. Extra: {_extra or 'none'}"
    )


def register_plugins_tool(mcp: FastMCP) -> None:
    """Register the unraid_plugins tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_plugins(
        action: PLUGIN_ACTIONS,
        ctx: Context | None = None,
        confirm: bool = False,
        names: list[str] | None = None,
        bundled: bool = False,
        restart: bool = True,
    ) -> dict[str, Any]:
        """Manage Unraid API plugins.

        Actions:
          list   - List all installed plugins with version and module info
          add    - Install one or more plugins (requires names: list of package names)
          remove - Remove one or more plugins (requires names, confirm=True)

        Parameters:
          names   - List of plugin package names (required for add/remove)
          bundled - Whether plugins are bundled (default: False)
          restart - Whether to auto-restart API after operation (default: True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            _desc = f"Remove plugin(s) **{names}** from the Unraid API. This cannot be undone without re-installing."
            confirmed = await elicit_destructive_confirmation(ctx, action, _desc)
            if not confirmed:
                raise ToolError(
                    f"Action '{action}' was not confirmed. "
                    "Re-run with confirm=True to bypass elicitation."
                )

        with tool_error_handler("plugins", action, logger):
            logger.info(f"Executing unraid_plugins action={action}")

            if action == "list":
                data = await make_graphql_request(QUERIES["list"])
                return {"success": True, "action": action, "data": data}

            if action in ("add", "remove"):
                if not names:
                    raise ToolError(f"names is required for '{action}' action")
                input_data = {"names": names, "bundled": bundled, "restart": restart}
                mutation_key = "add" if action == "add" else "remove"
                data = await make_graphql_request(MUTATIONS[mutation_key], {"input": input_data})
                result_key = "addPlugin" if action == "add" else "removePlugin"
                restart_required = data.get(result_key)
                return {
                    "success": True,
                    "action": action,
                    "names": names,
                    "manual_restart_required": restart_required,
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Plugins tool registered successfully")
