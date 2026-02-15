"""RClone cloud storage remote management.

Provides the `unraid_rclone` tool with 4 actions for managing
cloud storage remotes (S3, Google Drive, Dropbox, FTP, etc.).
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


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
    "list_remotes", "config_form", "create_remote", "delete_remote",
]


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

        try:
            logger.info(f"Executing unraid_rclone action={action}")

            if action == "list_remotes":
                data = await make_graphql_request(QUERIES["list_remotes"])
                remotes = data.get("rclone", {}).get("remotes", [])
                return {"remotes": list(remotes) if isinstance(remotes, list) else []}

            if action == "config_form":
                variables: dict[str, Any] = {}
                if provider_type:
                    variables["formOptions"] = {"providerType": provider_type}
                data = await make_graphql_request(
                    QUERIES["config_form"], variables or None
                )
                form = data.get("rclone", {}).get("configForm", {})
                if not form:
                    raise ToolError("No RClone config form data received")
                return dict(form)

            if action == "create_remote":
                if name is None or provider_type is None or config_data is None:
                    raise ToolError(
                        "create_remote requires name, provider_type, and config_data"
                    )
                data = await make_graphql_request(
                    MUTATIONS["create_remote"],
                    {"input": {"name": name, "type": provider_type, "config": config_data}},
                )
                remote = data.get("rclone", {}).get("createRCloneRemote")
                if not remote:
                    raise ToolError(f"Failed to create remote '{name}': no confirmation from server")
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

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_rclone action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute rclone/{action}: {e!s}") from e

    logger.info("RClone tool registered successfully")
