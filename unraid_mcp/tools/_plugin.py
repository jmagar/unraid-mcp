"""Plugin domain handler for the Unraid MCP tool.

Covers: list, add, remove* (3 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import validate_subaction
from ..core.guards import gate_destructive_action


# ===========================================================================
# PLUGIN
# ===========================================================================

_PLUGIN_QUERIES: dict[str, str] = {
    "list": "query ListPlugins { plugins { name version hasApiModule hasCliModule } }",
}

_PLUGIN_MUTATIONS: dict[str, str] = {
    "add": "mutation AddPlugin($input: PluginManagementInput!) { addPlugin(input: $input) }",
    "remove": "mutation RemovePlugin($input: PluginManagementInput!) { removePlugin(input: $input) }",
}

_PLUGIN_SUBACTIONS: set[str] = set(_PLUGIN_QUERIES) | set(_PLUGIN_MUTATIONS)
_PLUGIN_DESTRUCTIVE: set[str] = {"remove"}


async def _handle_plugin(
    subaction: str,
    names: list[str] | None,
    bundled: bool,
    restart: bool,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    validate_subaction(subaction, _PLUGIN_SUBACTIONS, "plugin")

    await gate_destructive_action(
        ctx,
        subaction,
        _PLUGIN_DESTRUCTIVE,
        confirm,
        f"Remove plugin(s) **{names}** from the Unraid API. This cannot be undone without re-installing.",
    )

    with tool_error_handler("plugin", subaction, logger):
        logger.info(f"Executing unraid action=plugin subaction={subaction}")

        if subaction == "list":
            data = await _client.make_graphql_request(_PLUGIN_QUERIES["list"])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in ("add", "remove"):
            if not names:
                raise ToolError(f"names is required for plugin/{subaction}")
            data = await _client.make_graphql_request(
                _PLUGIN_MUTATIONS[subaction],
                {"input": {"names": names, "bundled": bundled, "restart": restart}},
            )
            result_key = "addPlugin" if subaction == "add" else "removePlugin"
            return {
                "success": True,
                "subaction": subaction,
                "names": names,
                "manual_restart_required": data.get(result_key),
            }

        raise ToolError(f"Unhandled plugin subaction '{subaction}' — this is a bug")
