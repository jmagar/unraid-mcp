"""Setting domain handler for the Unraid MCP tool.

Covers: update, configure_ups* (2 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


# ===========================================================================
# SETTING
# ===========================================================================

_SETTING_MUTATIONS: dict[str, str] = {
    "update": "mutation UpdateSettings($input: JSON!) { updateSettings(input: $input) { restartRequired values warnings } }",
    "configure_ups": "mutation ConfigureUps($config: UPSConfigInput!) { configureUps(config: $config) }",
}

_SETTING_SUBACTIONS: set[str] = set(_SETTING_MUTATIONS)
_SETTING_DESTRUCTIVE: set[str] = {"configure_ups"}


async def _handle_setting(
    subaction: str,
    settings_input: dict[str, Any] | None,
    ups_config: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _SETTING_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for setting. Must be one of: {sorted(_SETTING_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _SETTING_DESTRUCTIVE,
        confirm,
        "Configure UPS monitoring. This will overwrite the current UPS daemon settings.",
    )

    with tool_error_handler("setting", subaction, logger):
        logger.info(f"Executing unraid action=setting subaction={subaction}")

        if subaction == "update":
            if settings_input is None:
                raise ToolError("settings_input is required for setting/update")
            data = await _client.make_graphql_request(
                _SETTING_MUTATIONS["update"], {"input": settings_input}
            )
            return {"success": True, "subaction": "update", "data": data.get("updateSettings")}

        if subaction == "configure_ups":
            if ups_config is None:
                raise ToolError("ups_config is required for setting/configure_ups")
            data = await _client.make_graphql_request(
                _SETTING_MUTATIONS["configure_ups"], {"config": ups_config}
            )
            return {
                "success": True,
                "subaction": "configure_ups",
                "result": data.get("configureUps"),
            }

        raise ToolError(f"Unhandled setting subaction '{subaction}' — this is a bug")
