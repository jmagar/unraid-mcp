"""API key management.

Provides the `unraid_keys` tool with 5 actions for listing, viewing,
creating, updating, and deleting API keys.
"""

from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_destructive_confirmation


QUERIES: dict[str, str] = {
    "list": """
        query ListApiKeys {
          apiKeys { id name roles permissions { resource actions } createdAt }
        }
    """,
    "get": """
        query GetApiKey($id: PrefixedID!) {
          apiKey(id: $id) { id name roles permissions { resource actions } createdAt }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "create": """
        mutation CreateApiKey($input: CreateApiKeyInput!) {
          apiKey { create(input: $input) { id name key roles } }
        }
    """,
    "update": """
        mutation UpdateApiKey($input: UpdateApiKeyInput!) {
          apiKey { update(input: $input) { id name roles } }
        }
    """,
    "delete": """
        mutation DeleteApiKey($input: DeleteApiKeyInput!) {
          apiKey { delete(input: $input) }
        }
    """,
    "add_role": """
        mutation AddRole($input: AddRoleForApiKeyInput!) {
          apiKey { addRole(input: $input) }
        }
    """,
    "remove_role": """
        mutation RemoveRole($input: RemoveRoleFromApiKeyInput!) {
          apiKey { removeRole(input: $input) }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

KEY_ACTIONS = Literal[
    "add_role",
    "create",
    "delete",
    "get",
    "list",
    "remove_role",
    "update",
]

if set(get_args(KEY_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(KEY_ACTIONS))
    _extra = set(get_args(KEY_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"KEY_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_keys_tool(mcp: FastMCP) -> None:
    """Register the unraid_keys tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_keys(
        action: KEY_ACTIONS,
        ctx: Context | None = None,
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
          add_role - Add a role to an API key (requires key_id and roles)
          remove_role - Remove a role from an API key (requires key_id and roles)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            _desc = f"Delete API key **{key_id}**. Any clients using this key will lose access."
            confirmed = await elicit_destructive_confirmation(ctx, action, _desc)
            if not confirmed:
                raise ToolError(
                    f"Action '{action}' was not confirmed. "
                    "Re-run with confirm=True to bypass elicitation."
                )

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
                created_key = (data.get("apiKey") or {}).get("create")
                if not created_key:
                    raise ToolError("Failed to create API key: no data returned from server")
                return {"success": True, "key": created_key}

            if action == "update":
                if not key_id:
                    raise ToolError("key_id is required for 'update' action")
                input_data: dict[str, Any] = {"id": key_id}
                if name:
                    input_data["name"] = name
                if roles is not None:
                    input_data["roles"] = roles
                data = await make_graphql_request(MUTATIONS["update"], {"input": input_data})
                updated_key = (data.get("apiKey") or {}).get("update")
                if not updated_key:
                    raise ToolError("Failed to update API key: no data returned from server")
                return {"success": True, "key": updated_key}

            if action == "delete":
                if not key_id:
                    raise ToolError("key_id is required for 'delete' action")
                data = await make_graphql_request(MUTATIONS["delete"], {"input": {"ids": [key_id]}})
                result = (data.get("apiKey") or {}).get("delete")
                if not result:
                    raise ToolError(
                        f"Failed to delete API key '{key_id}': no confirmation from server"
                    )
                return {
                    "success": True,
                    "message": f"API key '{key_id}' deleted",
                }

            if action == "add_role":
                if not key_id:
                    raise ToolError("key_id is required for 'add_role' action")
                if not roles or len(roles) == 0:
                    raise ToolError(
                        "role is required for 'add_role' action (pass as roles=['ROLE_NAME'])"
                    )
                data = await make_graphql_request(
                    MUTATIONS["add_role"],
                    {"input": {"apiKeyId": key_id, "role": roles[0]}},
                )
                return {"success": True, "message": f"Role '{roles[0]}' added to key '{key_id}'"}

            if action == "remove_role":
                if not key_id:
                    raise ToolError("key_id is required for 'remove_role' action")
                if not roles or len(roles) == 0:
                    raise ToolError(
                        "role is required for 'remove_role' action (pass as roles=['ROLE_NAME'])"
                    )
                data = await make_graphql_request(
                    MUTATIONS["remove_role"],
                    {"input": {"apiKeyId": key_id, "role": roles[0]}},
                )
                return {
                    "success": True,
                    "message": f"Role '{roles[0]}' removed from key '{key_id}'",
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Keys tool registered successfully")
