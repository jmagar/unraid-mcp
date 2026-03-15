"""UI customization and system state queries.

Provides the `unraid_customization` tool with 5 actions covering
theme/customization data, public UI config, initial setup state, and
theme mutation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, get_args


if TYPE_CHECKING:
    from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "theme": """
        query GetCustomization {
          customization {
            theme { name showBannerImage showBannerGradient showHeaderDescription
                    headerBackgroundColor headerPrimaryTextColor headerSecondaryTextColor }
            partnerInfo { partnerName hasPartnerLogo partnerUrl partnerLogoUrl }
            activationCode { code partnerName serverName sysModel comment header theme }
          }
        }
    """,
    "public_theme": """
        query GetPublicTheme {
          publicTheme { name showBannerImage showBannerGradient showHeaderDescription
                        headerBackgroundColor headerPrimaryTextColor headerSecondaryTextColor }
          publicPartnerInfo { partnerName hasPartnerLogo partnerUrl partnerLogoUrl }
        }
    """,
    "is_initial_setup": """
        query IsInitialSetup {
          isInitialSetup
        }
    """,
    "sso_enabled": """
        query IsSSOEnabled {
          isSSOEnabled
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "set_theme": """
        mutation SetTheme($theme: ThemeName!) {
          customization { setTheme(theme: $theme) {
            name showBannerImage showBannerGradient showHeaderDescription
          }}
        }
    """,
}

ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

CUSTOMIZATION_ACTIONS = Literal[
    "is_initial_setup",
    "public_theme",
    "set_theme",
    "sso_enabled",
    "theme",
]

if set(get_args(CUSTOMIZATION_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(CUSTOMIZATION_ACTIONS))
    _extra = set(get_args(CUSTOMIZATION_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"CUSTOMIZATION_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing: {_missing or 'none'}. Extra: {_extra or 'none'}"
    )


def register_customization_tool(mcp: FastMCP) -> None:
    """Register the unraid_customization tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_customization(
        action: CUSTOMIZATION_ACTIONS,
        theme_name: str | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid UI customization and system state.

        Actions:
          theme            - Get full customization (theme, partner info, activation code)
          public_theme     - Get public theme and partner info (no auth required)
          is_initial_setup - Check if server is in initial setup mode
          sso_enabled      - Check if SSO is enabled
          set_theme        - Change the UI theme (requires theme_name: azure/black/gray/white)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action == "set_theme" and not theme_name:
            raise ToolError(
                "theme_name is required for 'set_theme' action "
                "(valid values: azure, black, gray, white)"
            )

        with tool_error_handler("customization", action, logger):
            logger.info(f"Executing unraid_customization action={action}")

            if action in QUERIES:
                data = await make_graphql_request(QUERIES[action])
                return {"success": True, "action": action, "data": data}

            if action == "set_theme":
                data = await make_graphql_request(MUTATIONS[action], {"theme": theme_name})
                return {"success": True, "action": action, "data": data}

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Customization tool registered successfully")
