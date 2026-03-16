"""System settings and UPS mutations.

Provides the `unraid_settings` tool with 2 actions for updating system
configuration and UPS monitoring.
"""

from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


MUTATIONS: dict[str, str] = {
    "update": """
        mutation UpdateSettings($input: JSON!) {
          updateSettings(input: $input) { restartRequired values warnings }
        }
    """,
    "configure_ups": """
        mutation ConfigureUps($config: UPSConfigInput!) {
          configureUps(config: $config)
        }
    """,
}

DESTRUCTIVE_ACTIONS = {
    "configure_ups",
}
ALL_ACTIONS = set(MUTATIONS)

SETTINGS_ACTIONS = Literal[
    "configure_ups",
    "update",
]

if set(get_args(SETTINGS_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(SETTINGS_ACTIONS))
    _extra = set(get_args(SETTINGS_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"SETTINGS_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_settings_tool(mcp: FastMCP) -> None:
    """Register the unraid_settings tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_settings(
        action: SETTINGS_ACTIONS,
        ctx: Context | None = None,
        confirm: bool = False,
        settings_input: dict[str, Any] | None = None,
        ups_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update Unraid system settings and UPS configuration.

        Actions:
          update - Update system settings (requires settings_input dict)
          configure_ups - Configure UPS monitoring (requires ups_config dict, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        await gate_destructive_action(
            ctx,
            action,
            DESTRUCTIVE_ACTIONS,
            confirm,
            "Configure UPS monitoring. This will overwrite the current UPS daemon settings.",
        )

        with tool_error_handler("settings", action, logger):
            logger.info(f"Executing unraid_settings action={action}")

            if action == "update":
                if settings_input is None:
                    raise ToolError("settings_input is required for 'update' action")
                data = await make_graphql_request(MUTATIONS["update"], {"input": settings_input})
                return {"success": True, "action": "update", "data": data.get("updateSettings")}

            if action == "configure_ups":
                if ups_config is None:
                    raise ToolError("ups_config is required for 'configure_ups' action")
                data = await make_graphql_request(
                    MUTATIONS["configure_ups"], {"config": ups_config}
                )
                return {
                    "success": True,
                    "action": "configure_ups",
                    "result": data.get("configureUps"),
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Settings tool registered successfully")
