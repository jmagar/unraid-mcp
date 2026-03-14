"""User account query.

Provides the `unraid_users` tool with 1 action for querying the current authenticated user.
Note: Unraid GraphQL API does not support user management operations (list, add, delete).
"""

from typing import Any, Literal

from fastmcp import Context as _Context
from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import CredentialsNotConfiguredError as _CredErr
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_and_configure as _elicit


# Re-export at module scope so tests can patch "unraid_mcp.tools.users.elicit_and_configure"
# and "unraid_mcp.tools.users.CredentialsNotConfiguredError"
elicit_and_configure = _elicit
CredentialsNotConfiguredError = _CredErr
Context = _Context


QUERIES: dict[str, str] = {
    "me": """
        query GetMe {
          me { id name description roles }
        }
    """,
}

ALL_ACTIONS = set(QUERIES)

USER_ACTIONS = Literal["me"]


def register_users_tool(mcp: FastMCP) -> None:
    """Register the unraid_users tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_users(
        action: USER_ACTIONS = "me",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Query current authenticated user.

        Actions:
          me - Get current authenticated user info (id, name, description, roles)

        Note: Unraid API does not support user management operations (list, add, delete).
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        with tool_error_handler("users", action, logger):
            logger.info("Executing unraid_users action=me")
            try:
                data = await make_graphql_request(QUERIES["me"])
            except CredentialsNotConfiguredError:
                configured = await elicit_and_configure(ctx)
                if not configured:
                    raise ToolError(
                        "Credentials required. Run `unraid_health action=setup` to configure."
                    )
                data = await make_graphql_request(QUERIES["me"])
            return data.get("me") or {}

    logger.info("Users tool registered successfully")
