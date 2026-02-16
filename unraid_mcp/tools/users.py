"""User account query.

Provides the `unraid_users` tool with 1 action for querying the current authenticated user.
Note: Unraid GraphQL API does not support user management operations (list, add, delete).
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


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
    async def unraid_users(action: USER_ACTIONS = "me") -> dict[str, Any]:
        """Query current authenticated user.

        Actions:
          me - Get current authenticated user info (id, name, description, roles)

        Note: Unraid API does not support user management operations (list, add, delete).
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be: me")

        try:
            logger.info("Executing unraid_users action=me")
            data = await make_graphql_request(QUERIES["me"])
            return data.get("me") or {}

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_users action=me: {e}", exc_info=True)
            raise ToolError(f"Failed to execute users/me: {e!s}") from e

    logger.info("Users tool registered successfully")
