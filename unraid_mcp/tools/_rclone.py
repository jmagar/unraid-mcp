"""Rclone domain handler for the Unraid MCP tool.

Covers: list_remotes, config_form, create_remote, delete_remote* (4 subactions).
"""

import re
from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


# ===========================================================================
# RCLONE
# ===========================================================================

_RCLONE_QUERIES: dict[str, str] = {
    "list_remotes": "query ListRCloneRemotes { rclone { remotes { name type parameters config } } }",
    "config_form": "query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) { rclone { configForm(formOptions: $formOptions) { id dataSchema uiSchema } } }",
}

_RCLONE_MUTATIONS: dict[str, str] = {
    "create_remote": "mutation CreateRCloneRemote($input: CreateRCloneRemoteInput!) { rclone { createRCloneRemote(input: $input) { name type parameters } } }",
    "delete_remote": "mutation DeleteRCloneRemote($input: DeleteRCloneRemoteInput!) { rclone { deleteRCloneRemote(input: $input) } }",
}

_RCLONE_SUBACTIONS: set[str] = set(_RCLONE_QUERIES) | set(_RCLONE_MUTATIONS)
_RCLONE_DESTRUCTIVE: set[str] = {"delete_remote"}
_MAX_CONFIG_KEYS = 50
_DANGEROUS_KEY_PATTERN = re.compile(r"\.\.|[/\\;|`$(){}]")
_MAX_VALUE_LENGTH = 4096


def _validate_rclone_config(config_data: dict[str, Any]) -> dict[str, str]:
    if len(config_data) > _MAX_CONFIG_KEYS:
        raise ToolError(f"config_data has {len(config_data)} keys (max {_MAX_CONFIG_KEYS})")
    validated: dict[str, str] = {}
    for key, value in config_data.items():
        if not isinstance(key, str) or not key.strip():
            raise ToolError(
                f"config_data keys must be non-empty strings, got: {type(key).__name__}"
            )
        if _DANGEROUS_KEY_PATTERN.search(key):
            raise ToolError(f"config_data key '{key}' contains disallowed characters")
        if not isinstance(value, (str, int, float, bool)):
            raise ToolError(f"config_data['{key}'] must be a string, number, or boolean")
        str_value = str(value)
        if len(str_value) > _MAX_VALUE_LENGTH:
            raise ToolError(
                f"config_data['{key}'] value exceeds max length ({len(str_value)} > {_MAX_VALUE_LENGTH})"
            )
        validated[key] = str_value
    return validated


async def _handle_rclone(
    subaction: str,
    name: str | None,
    provider_type: str | None,
    config_data: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _RCLONE_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for rclone. Must be one of: {sorted(_RCLONE_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _RCLONE_DESTRUCTIVE,
        confirm,
        f"Delete rclone remote **{name}**. This cannot be undone.",
    )

    with tool_error_handler("rclone", subaction, logger):
        logger.info(f"Executing unraid action=rclone subaction={subaction}")

        if subaction == "list_remotes":
            data = await _client.make_graphql_request(_RCLONE_QUERIES["list_remotes"])
            remotes = data.get("rclone", {}).get("remotes", [])
            return {"remotes": list(remotes) if isinstance(remotes, list) else []}

        if subaction == "config_form":
            variables: dict[str, Any] = {}
            if provider_type:
                variables["formOptions"] = {"providerType": provider_type}
            data = await _client.make_graphql_request(
                _RCLONE_QUERIES["config_form"], variables or None
            )
            form = (data.get("rclone") or {}).get("configForm", {})
            if not form:
                raise ToolError("No RClone config form data received")
            return dict(form)

        if subaction == "create_remote":
            if name is None or provider_type is None or config_data is None:
                raise ToolError("create_remote requires name, provider_type, and config_data")
            validated = _validate_rclone_config(config_data)
            data = await _client.make_graphql_request(
                _RCLONE_MUTATIONS["create_remote"],
                {"input": {"name": name, "type": provider_type, "parameters": validated}},
            )
            remote = (data.get("rclone") or {}).get("createRCloneRemote")
            if not remote:
                raise ToolError(f"Failed to create remote '{name}': no confirmation from server")
            return {
                "success": True,
                "message": f"Remote '{name}' created successfully",
                "remote": remote,
            }

        if subaction == "delete_remote":
            if not name:
                raise ToolError("name is required for rclone/delete_remote")
            data = await _client.make_graphql_request(
                _RCLONE_MUTATIONS["delete_remote"], {"input": {"name": name}}
            )
            if not (data.get("rclone") or {}).get("deleteRCloneRemote", False):
                raise ToolError(f"Failed to delete remote '{name}'")
            return {"success": True, "message": f"Remote '{name}' deleted successfully"}

        raise ToolError(f"Unhandled rclone subaction '{subaction}' — this is a bug")
