"""RClone cloud storage remote management.

Provides the `unraid_rclone` tool with 4 actions for managing
cloud storage remotes (S3, Google Drive, Dropbox, FTP, etc.).
"""

import re
from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "list_remotes": """
        query ListRCloneRemotes {
          rclone { remotes { name type parameters config } }
        }
    """,
    "config_form": """
        query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) {
          rclone { configForm(formOptions: $formOptions) { id dataSchema uiSchema } }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "create_remote": """
        mutation CreateRCloneRemote($input: CreateRCloneRemoteInput!) {
          rclone { createRCloneRemote(input: $input) { name type parameters } }
        }
    """,
    "delete_remote": """
        mutation DeleteRCloneRemote($input: DeleteRCloneRemoteInput!) {
          rclone { deleteRCloneRemote(input: $input) }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete_remote"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

RCLONE_ACTIONS = Literal[
    "list_remotes",
    "config_form",
    "create_remote",
    "delete_remote",
]

# Max config entries to prevent abuse
_MAX_CONFIG_KEYS = 50
# Pattern for suspicious key names (path traversal, shell metacharacters)
_DANGEROUS_KEY_PATTERN = re.compile(r"[.]{2}|[/\\;|`$(){}]")
# Max length for individual config values
_MAX_VALUE_LENGTH = 4096


def _validate_config_data(config_data: dict[str, Any]) -> dict[str, str]:
    """Validate and sanitize rclone config_data before passing to GraphQL.

    Ensures all keys and values are safe strings with no injection vectors.

    Raises:
        ToolError: If config_data contains invalid keys or values
    """
    if len(config_data) > _MAX_CONFIG_KEYS:
        raise ToolError(f"config_data has {len(config_data)} keys (max {_MAX_CONFIG_KEYS})")

    validated: dict[str, str] = {}
    for key, value in config_data.items():
        if not isinstance(key, str) or not key.strip():
            raise ToolError(
                f"config_data keys must be non-empty strings, got: {type(key).__name__}"
            )
        if _DANGEROUS_KEY_PATTERN.search(key):
            raise ToolError(
                f"config_data key '{key}' contains disallowed characters "
                f"(path traversal or shell metacharacters)"
            )
        if not isinstance(value, (str, int, float, bool)):
            raise ToolError(
                f"config_data['{key}'] must be a string, number, or boolean, "
                f"got: {type(value).__name__}"
            )
        str_value = str(value)
        if len(str_value) > _MAX_VALUE_LENGTH:
            raise ToolError(
                f"config_data['{key}'] value exceeds max length "
                f"({len(str_value)} > {_MAX_VALUE_LENGTH})"
            )
        validated[key] = str_value

    return validated


def register_rclone_tool(mcp: FastMCP) -> None:
    """Register the unraid_rclone tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_rclone(
        action: RCLONE_ACTIONS,
        confirm: bool = False,
        name: str | None = None,
        provider_type: str | None = None,
        config_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Manage RClone cloud storage remotes.

        Actions:
          list_remotes - List all configured remotes
          config_form - Get config form schema (optional provider_type for specific provider)
          create_remote - Create a new remote (requires name, provider_type, config_data)
          delete_remote - Delete a remote (requires name, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("rclone", action, logger):
            logger.info(f"Executing unraid_rclone action={action}")

            if action == "list_remotes":
                data = await make_graphql_request(QUERIES["list_remotes"])
                remotes = data.get("rclone", {}).get("remotes", [])
                return {"remotes": list(remotes) if isinstance(remotes, list) else []}

            if action == "config_form":
                variables: dict[str, Any] = {}
                if provider_type:
                    variables["formOptions"] = {"providerType": provider_type}
                data = await make_graphql_request(QUERIES["config_form"], variables or None)
                form = data.get("rclone", {}).get("configForm", {})
                if not form:
                    raise ToolError("No RClone config form data received")
                return dict(form)

            if action == "create_remote":
                if name is None or provider_type is None or config_data is None:
                    raise ToolError("create_remote requires name, provider_type, and config_data")
                validated_config = _validate_config_data(config_data)
                data = await make_graphql_request(
                    MUTATIONS["create_remote"],
                    {"input": {"name": name, "type": provider_type, "config": validated_config}},
                )
                remote = data.get("rclone", {}).get("createRCloneRemote")
                if not remote:
                    raise ToolError(
                        f"Failed to create remote '{name}': no confirmation from server"
                    )
                return {
                    "success": True,
                    "message": f"Remote '{name}' created successfully",
                    "remote": remote,
                }

            if action == "delete_remote":
                if not name:
                    raise ToolError("name is required for 'delete_remote' action")
                data = await make_graphql_request(
                    MUTATIONS["delete_remote"], {"input": {"name": name}}
                )
                success = data.get("rclone", {}).get("deleteRCloneRemote", False)
                if not success:
                    raise ToolError(f"Failed to delete remote '{name}'")
                return {
                    "success": True,
                    "message": f"Remote '{name}' deleted successfully",
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("RClone tool registered successfully")
