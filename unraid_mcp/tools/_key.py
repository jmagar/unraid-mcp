"""Key domain handler for the Unraid MCP tool.

Covers: list, get, possible_roles, create, update, delete*, add_role, remove_role (8 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action
from ..core.utils import safe_get, validate_subaction


# ===========================================================================
# KEY (API keys)
# ===========================================================================

_KEY_QUERIES: dict[str, str] = {
    "list": "query ListApiKeys { apiKeys { id name roles permissions { resource actions } createdAt } }",
    "get": "query GetApiKey($id: PrefixedID!) { apiKey(id: $id) { id name roles permissions { resource actions } createdAt } }",
    "possible_roles": "query GetPossibleRoles { apiKeyPossibleRoles }",
}

_KEY_MUTATIONS: dict[str, str] = {
    "create": "mutation CreateApiKey($input: CreateApiKeyInput!) { apiKey { create(input: $input) { id name key roles } } }",
    "update": "mutation UpdateApiKey($input: UpdateApiKeyInput!) { apiKey { update(input: $input) { id name roles } } }",
    "delete": "mutation DeleteApiKey($input: DeleteApiKeyInput!) { apiKey { delete(input: $input) } }",
    "add_role": "mutation AddRole($input: AddRoleForApiKeyInput!) { apiKey { addRole(input: $input) } }",
    "remove_role": "mutation RemoveRole($input: RemoveRoleFromApiKeyInput!) { apiKey { removeRole(input: $input) } }",
}

_KEY_SUBACTIONS: set[str] = set(_KEY_QUERIES) | set(_KEY_MUTATIONS)
_KEY_DESTRUCTIVE: set[str] = {"delete"}


async def _handle_key(
    subaction: str,
    key_id: str | None,
    name: str | None,
    roles: list[str] | None,
    permissions: list[str] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    validate_subaction(subaction, _KEY_SUBACTIONS, "key")

    await gate_destructive_action(
        ctx,
        subaction,
        _KEY_DESTRUCTIVE,
        confirm,
        f"Delete API key **{key_id}**. Any clients using this key will lose access.",
    )

    with tool_error_handler("key", subaction, logger):
        logger.info(f"Executing unraid action=key subaction={subaction}")

        if subaction == "list":
            data = await _client.make_graphql_request(_KEY_QUERIES["list"])
            keys = data.get("apiKeys", [])
            return {"keys": list(keys) if isinstance(keys, list) else []}

        if subaction == "possible_roles":
            data = await _client.make_graphql_request(_KEY_QUERIES["possible_roles"])
            roles_list = data.get("apiKeyPossibleRoles", [])
            return {"roles": list(roles_list) if isinstance(roles_list, list) else []}

        if subaction == "get":
            if not key_id:
                raise ToolError("key_id is required for key/get")
            data = await _client.make_graphql_request(_KEY_QUERIES["get"], {"id": key_id})
            return dict(data.get("apiKey") or {})

        if subaction == "create":
            if not name:
                raise ToolError("name is required for key/create")
            input_data: dict[str, Any] = {"name": name}
            if roles is not None:
                input_data["roles"] = roles
            if permissions is not None:
                input_data["permissions"] = permissions
            data = await _client.make_graphql_request(
                _KEY_MUTATIONS["create"], {"input": input_data}
            )
            created_key = safe_get(data, "apiKey", "create")
            if not created_key:
                raise ToolError("Failed to create API key: no data returned from server")
            return {"success": True, "key": created_key}

        if subaction == "update":
            if not key_id:
                raise ToolError("key_id is required for key/update")
            input_data: dict[str, Any] = {"id": key_id}
            if name:
                input_data["name"] = name
            if roles is not None:
                input_data["roles"] = roles
            if permissions is not None:
                input_data["permissions"] = permissions
            data = await _client.make_graphql_request(
                _KEY_MUTATIONS["update"], {"input": input_data}
            )
            updated_key = safe_get(data, "apiKey", "update")
            if not updated_key:
                raise ToolError("Failed to update API key: no data returned from server")
            return {"success": True, "key": updated_key}

        if subaction == "delete":
            if not key_id:
                raise ToolError("key_id is required for key/delete")
            data = await _client.make_graphql_request(
                _KEY_MUTATIONS["delete"], {"input": {"ids": [key_id]}}
            )
            if not safe_get(data, "apiKey", "delete"):
                raise ToolError(f"Failed to delete API key '{key_id}': no confirmation from server")
            return {"success": True, "message": f"API key '{key_id}' deleted"}

        if subaction in ("add_role", "remove_role"):
            if not key_id:
                raise ToolError(f"key_id is required for key/{subaction}")
            if not roles:
                raise ToolError(
                    f"roles is required for key/{subaction} (pass as roles=['ROLE_NAME'])"
                )
            data = await _client.make_graphql_request(
                _KEY_MUTATIONS[subaction], {"input": {"apiKeyId": key_id, "role": roles[0]}}
            )
            verb = "added to" if subaction == "add_role" else "removed from"
            return {"success": True, "message": f"Role '{roles[0]}' {verb} key '{key_id}'"}

        raise ToolError(f"Unhandled key subaction '{subaction}' — this is a bug")
