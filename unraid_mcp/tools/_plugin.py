"""Plugin domain handler for the Unraid MCP tool.

Covers: list, installed_unraid, install_operations, install_operation, add,
remove*, install, install_language (8 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action
from ..core.pagination import cap_list
from ..core.utils import coerce_list, validate_subaction


# ===========================================================================
# PLUGIN
# ===========================================================================

_PLUGIN_QUERIES: dict[str, str] = {
    "list": "query ListPlugins { plugins { name version hasApiModule hasCliModule } }",
    # Raw installed .plg filenames — distinct from the structured `plugins` list.
    "installed_unraid": "query InstalledUnraidPlugins { installedUnraidPlugins }",
    "install_operations": "query PluginInstallOperations { pluginInstallOperations { id url name status createdAt updatedAt finishedAt } }",
    "install_operation": "query PluginInstallOperation($operationId: ID!) { pluginInstallOperation(operationId: $operationId) { id url name status createdAt updatedAt finishedAt output } }",
}

_PLUGIN_MUTATIONS: dict[str, str] = {
    "add": "mutation AddPlugin($input: PluginManagementInput!) { addPlugin(input: $input) }",
    "remove": "mutation RemovePlugin($input: PluginManagementInput!) { removePlugin(input: $input) }",
    # Async .plg install group (returns an operation to poll via install_operation).
    "install": "mutation InstallPlugin($input: InstallPluginInput!) { unraidPlugins { installPlugin(input: $input) { id url name status createdAt } } }",
    "install_language": "mutation InstallLanguage($input: InstallPluginInput!) { unraidPlugins { installLanguage(input: $input) { id url name status createdAt } } }",
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
    limit: int = 20,
    url: str | None = None,
    plugin_name: str | None = None,
    forced: bool = False,
    operation_id: str | None = None,
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
            capped, page = cap_list(coerce_list(data.get("plugins")), limit)
            return {
                "success": True,
                "subaction": subaction,
                "plugins": capped,
                "page": page,
            }

        if subaction == "installed_unraid":
            data = await _client.make_graphql_request(_PLUGIN_QUERIES["installed_unraid"])
            capped, page = cap_list(coerce_list(data.get("installedUnraidPlugins")), limit)
            return {
                "success": True,
                "subaction": subaction,
                "plugins": capped,
                "page": page,
            }

        if subaction == "install_operations":
            data = await _client.make_graphql_request(_PLUGIN_QUERIES["install_operations"])
            capped, page = cap_list(coerce_list(data.get("pluginInstallOperations")), limit)
            return {
                "success": True,
                "subaction": subaction,
                "operations": capped,
                "page": page,
            }

        if subaction == "install_operation":
            if not operation_id:
                raise ToolError("operation_id is required for plugin/install_operation")
            data = await _client.make_graphql_request(
                _PLUGIN_QUERIES["install_operation"], {"operationId": operation_id}
            )
            return {
                "success": True,
                "subaction": subaction,
                "operation": data.get("pluginInstallOperation"),
            }

        if subaction in ("install", "install_language"):
            if not url:
                raise ToolError(f"url is required for plugin/{subaction}")
            input_data: dict[str, Any] = {"url": url, "forced": forced}
            if plugin_name:
                input_data["name"] = plugin_name
            data = await _client.make_graphql_request(
                _PLUGIN_MUTATIONS[subaction], {"input": input_data}
            )
            result_key = "installPlugin" if subaction == "install" else "installLanguage"
            return {
                "success": True,
                "subaction": subaction,
                "operation": (data.get("unraidPlugins") or {}).get(result_key),
            }

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
