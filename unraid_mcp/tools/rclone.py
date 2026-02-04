"""RClone cloud storage remote management tools.

This module provides tools for managing RClone remotes including listing existing
remotes, getting configuration forms, creating new remotes, and deleting remotes
for various cloud storage providers (S3, Google Drive, Dropbox, FTP, etc.).
"""

from typing import Any

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError


def register_rclone_tools(mcp: FastMCP) -> None:
    """Register all RClone tools with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register tools with
    """

    @mcp.tool()
    async def list_rclone_remotes() -> list[dict[str, Any]]:
        """Retrieves all configured RClone remotes with their configuration details."""
        try:
            query = """
            query ListRCloneRemotes {
                rclone {
                    remotes {
                        name
                        type
                        parameters
                        config
                    }
                }
            }
            """

            response_data = await make_graphql_request(query)

            rclone_data = response_data.get("rclone")
            # Handle case where rclone field is missing or None
            if not rclone_data:
                return []

            remotes = rclone_data.get("remotes")
            # Handle case where remotes field is missing or None
            if remotes is None:
                return []

            logger.info(f"Retrieved {len(remotes)} RClone remotes")
            return list(remotes) if isinstance(remotes, list) else []

        except Exception as e:
            if isinstance(e, ToolError):
                raise e
            logger.error(f"Failed to list RClone remotes: {str(e)}")
            raise ToolError(f"Failed to list RClone remotes: {str(e)}") from e

    @mcp.tool()
    async def get_rclone_config_form(provider_type: str | None = None) -> dict[str, Any]:
        """
        Get RClone configuration form schema for setting up new remotes.

        Args:
            provider_type: Optional provider type to get specific form (e.g., 's3', 'drive', 'dropbox')
        """
        try:
            query = """
            query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) {
                rclone {
                    configForm(formOptions: $formOptions) {
                        id
                        dataSchema
                        uiSchema
                    }
                }
            }
            """

            variables = {}
            if provider_type:
                # Sanitize provider type to prevent potential path issues
                # The user reported "url must not start with a slash", so we strip slashes just in case
                clean_provider_type = provider_type.strip("/")
                variables["formOptions"] = {"providerType": clean_provider_type}

            response_data = await make_graphql_request(query, variables)

            rclone_data = response_data.get("rclone")
            if not rclone_data:
                raise ToolError("No RClone data received from API")

            form_data = rclone_data.get("configForm")
            if form_data is None:
                raise ToolError("No RClone config form data received")

            logger.info(f"Retrieved RClone config form for {provider_type or 'general'}")
            return dict(form_data) if isinstance(form_data, dict) else {}

        except Exception as e:
            if isinstance(e, ToolError):
                raise e
            logger.error(f"Failed to get RClone config form: {e}")
            raise ToolError(f"Failed to get RClone config form: {e}") from e

    @mcp.tool()
    async def create_rclone_remote(
        name: str, provider_type: str, config_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a new RClone remote with the specified configuration.

        Args:
            name: Name for the new remote
            provider_type: Type of provider (e.g., 's3', 'drive', 'dropbox', 'ftp')
            config_data: Configuration parameters specific to the provider type
        """
        try:
            mutation = """
            mutation CreateRCloneRemote($input: CreateRCloneRemoteInput!) {
                rclone {
                    createRCloneRemote(input: $input) {
                        name
                        type
                        parameters
                    }
                }
            }
            """

            variables = {"input": {"name": name, "type": provider_type, "config": config_data}}

            response_data = await make_graphql_request(mutation, variables)

            if "rclone" in response_data and "createRCloneRemote" in response_data["rclone"]:
                remote_info = response_data["rclone"]["createRCloneRemote"]
                logger.info(f"Successfully created RClone remote: {name}")
                return {
                    "success": True,
                    "message": f"RClone remote '{name}' created successfully",
                    "remote": remote_info,
                }

            raise ToolError("Failed to create RClone remote")

        except Exception as e:
            if isinstance(e, ToolError):
                raise e
            logger.error(f"Failed to create RClone remote {name}: {str(e)}")
            raise ToolError(f"Failed to create RClone remote {name}: {str(e)}") from e

    @mcp.tool()
    async def delete_rclone_remote(name: str) -> dict[str, Any]:
        """
        Delete an existing RClone remote by name.

        Args:
            name: Name of the remote to delete
        """
        try:
            mutation = """
            mutation DeleteRCloneRemote($input: DeleteRCloneRemoteInput!) {
                rclone {
                    deleteRCloneRemote(input: $input)
                }
            }
            """

            variables = {"input": {"name": name}}

            response_data = await make_graphql_request(mutation, variables)

            if "rclone" in response_data and response_data["rclone"]["deleteRCloneRemote"]:
                logger.info(f"Successfully deleted RClone remote: {name}")
                return {"success": True, "message": f"RClone remote '{name}' deleted successfully"}

            raise ToolError(f"Failed to delete RClone remote '{name}'")

        except Exception as e:
            if isinstance(e, ToolError):
                raise e
            logger.error(f"Failed to delete RClone remote {name}: {str(e)}")
            raise ToolError(f"Failed to delete RClone remote {name}: {str(e)}") from e

    logger.info("RClone tools registered successfully")
