"""API key management.

Provides the `unraid_keys` tool with 5 actions for listing, viewing,
creating, updating, and deleting API keys.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "list": """
        query ListApiKeys {
          apiKeys { id name roles permissions createdAt lastUsed }
        }
    """,
    "get": """
        query GetApiKey($id: PrefixedID!) {
          apiKey(id: $id) { id name roles permissions createdAt lastUsed }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "create": """
        mutation CreateApiKey($input: CreateApiKeyInput!) {
          createApiKey(input: $input) { id name key roles }
        }
    """,
    "update": """
        mutation UpdateApiKey($input: UpdateApiKeyInput!) {
          updateApiKey(input: $input) { id name roles }
        }
    """,
    "delete": """
        mutation DeleteApiKeys($input: DeleteApiKeysInput!) {
          deleteApiKeys(input: $input)
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

KEY_ACTIONS = Literal[
    "list",
    "get",
    "create",
    "update",
    "delete",
]


def register_keys_tool(mcp: FastMCP) -> None:
    """Register the unraid_keys tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_keys(
        action: KEY_ACTIONS,
        confirm: bool = False,
        key_id: str | None = None,
        name: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid API keys.

        Actions:
          list - List all API keys
          get - Get a specific API key (requires key_id)
          create - Create a new API key (requires name; optional roles, permissions)
          update - Update an API key (requires key_id; optional name, roles)
          delete - Delete API keys (requires key_id, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("keys", action, logger):
            logger.info(f"Executing unraid_keys action={action}")

            if action == "list":
                data = await make_graphql_request(QUERIES["list"])
                keys = data.get("apiKeys", [])
                return {"keys": list(keys) if isinstance(keys, list) else []}

            if action == "get":
                if not key_id:
                    raise ToolError("key_id is required for 'get' action")
                data = await make_graphql_request(QUERIES["get"], {"id": key_id})
                return dict(data.get("apiKey") or {})

            if action == "create":
                if not name:
                    raise ToolError("name is required for 'create' action")
                input_data: dict[str, Any] = {"name": name}
                if roles is not None:
                    input_data["roles"] = roles
                if permissions is not None:
                    input_data["permissions"] = permissions
                data = await make_graphql_request(MUTATIONS["create"], {"input": input_data})
                return {
                    "success": True,
                    "key": data.get("createApiKey", {}),
                }

            if action == "update":
                if not key_id:
                    raise ToolError("key_id is required for 'update' action")
                input_data: dict[str, Any] = {"id": key_id}
                if name:
                    input_data["name"] = name
                if roles is not None:
                    input_data["roles"] = roles
                data = await make_graphql_request(MUTATIONS["update"], {"input": input_data})
                return {
                    "success": True,
                    "key": data.get("updateApiKey", {}),
                }

            if action == "delete":
                if not key_id:
                    raise ToolError("key_id is required for 'delete' action")
                data = await make_graphql_request(MUTATIONS["delete"], {"input": {"ids": [key_id]}})
                result = data.get("deleteApiKeys")
                if not result:
                    raise ToolError(
                        f"Failed to delete API key '{key_id}': no confirmation from server"
                    )
                return {
                    "success": True,
                    "message": f"API key '{key_id}' deleted",
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Keys tool registered successfully")
