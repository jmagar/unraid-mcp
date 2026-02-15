"""User management.

Provides the `unraid_users` tool with 8 actions for managing users,
cloud access, remote access settings, and allowed origins.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError

QUERIES: dict[str, str] = {
    "me": """
        query GetMe {
          me { id name role email }
        }
    """,
    "list": """
        query ListUsers {
          users { id name role email }
        }
    """,
    "get": """
        query GetUser($id: PrefixedID!) {
          user(id: $id) { id name role email }
        }
    """,
    "cloud": """
        query GetCloud {
          cloud { status error }
        }
    """,
    "remote_access": """
        query GetRemoteAccess {
          remoteAccess { enabled url }
        }
    """,
    "origins": """
        query GetAllowedOrigins {
          allowedOrigins
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "add": """
        mutation AddUser($input: AddUserInput!) {
          addUser(input: $input) { id name role }
        }
    """,
    "delete": """
        mutation DeleteUser($id: PrefixedID!) {
          deleteUser(id: $id)
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete"}

USER_ACTIONS = Literal[
    "me", "list", "get", "add", "delete", "cloud", "remote_access", "origins",
]


def register_users_tool(mcp: FastMCP) -> None:
    """Register the unraid_users tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_users(
        action: USER_ACTIONS,
        confirm: bool = False,
        user_id: str | None = None,
        name: str | None = None,
        password: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid users and access settings.

        Actions:
          me - Get current authenticated user info
          list - List all users
          get - Get a specific user (requires user_id)
          add - Add a new user (requires name, password; optional role)
          delete - Delete a user (requires user_id, confirm=True)
          cloud - Get Unraid Connect cloud status
          remote_access - Get remote access settings
          origins - Get allowed origins
        """
        all_actions = set(QUERIES) | set(MUTATIONS)
        if action not in all_actions:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(all_actions)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        try:
            logger.info(f"Executing unraid_users action={action}")

            if action == "me":
                data = await make_graphql_request(QUERIES["me"])
                return dict(data.get("me", {}))

            if action == "list":
                data = await make_graphql_request(QUERIES["list"])
                users = data.get("users", [])
                return {"users": list(users) if isinstance(users, list) else []}

            if action == "get":
                if not user_id:
                    raise ToolError("user_id is required for 'get' action")
                data = await make_graphql_request(QUERIES["get"], {"id": user_id})
                return dict(data.get("user", {}))

            if action == "add":
                if not name or not password:
                    raise ToolError("add requires name and password")
                input_data: dict[str, Any] = {"name": name, "password": password}
                if role:
                    input_data["role"] = role.upper()
                data = await make_graphql_request(
                    MUTATIONS["add"], {"input": input_data}
                )
                return {
                    "success": True,
                    "user": data.get("addUser", {}),
                }

            if action == "delete":
                if not user_id:
                    raise ToolError("user_id is required for 'delete' action")
                data = await make_graphql_request(
                    MUTATIONS["delete"], {"id": user_id}
                )
                return {
                    "success": True,
                    "message": f"User '{user_id}' deleted",
                }

            if action == "cloud":
                data = await make_graphql_request(QUERIES["cloud"])
                return dict(data.get("cloud", {}))

            if action == "remote_access":
                data = await make_graphql_request(QUERIES["remote_access"])
                return dict(data.get("remoteAccess", {}))

            if action == "origins":
                data = await make_graphql_request(QUERIES["origins"])
                origins = data.get("allowedOrigins", [])
                return {"origins": list(origins) if isinstance(origins, list) else []}

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_users action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute users/{action}: {str(e)}") from e

    logger.info("Users tool registered successfully")
