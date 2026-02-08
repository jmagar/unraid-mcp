"""Docker container management.

Provides the `unraid_docker` tool with 15 actions for container lifecycle,
logs, networks, and update management.
"""

import re
from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError

QUERIES: dict[str, str] = {
    "list": """
        query ListDockerContainers {
          docker { containers(skipCache: false) {
            id names image state status autoStart
          } }
        }
    """,
    "details": """
        query GetContainerDetails {
          docker { containers(skipCache: false) {
            id names image imageId command created
            ports { ip privatePort publicPort type }
            sizeRootFs labels state status
            hostConfig { networkMode }
            networkSettings mounts autoStart
          } }
        }
    """,
    "logs": """
        query GetContainerLogs($id: PrefixedID!, $tail: Int) {
          docker { logs(id: $id, tail: $tail) }
        }
    """,
    "networks": """
        query GetDockerNetworks {
          dockerNetworks { id name driver scope }
        }
    """,
    "network_details": """
        query GetDockerNetwork($id: PrefixedID!) {
          dockerNetwork(id: $id) { id name driver scope containers }
        }
    """,
    "port_conflicts": """
        query GetPortConflicts {
          docker { portConflicts { containerName port conflictsWith } }
        }
    """,
    "check_updates": """
        query CheckContainerUpdates {
          docker { containerUpdateStatuses { id name updateAvailable currentVersion latestVersion } }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "start": """
        mutation StartContainer($id: PrefixedID!) {
          docker { start(id: $id) { id names state status } }
        }
    """,
    "stop": """
        mutation StopContainer($id: PrefixedID!) {
          docker { stop(id: $id) { id names state status } }
        }
    """,
    "pause": """
        mutation PauseContainer($id: PrefixedID!) {
          docker { pause(id: $id) { id names state status } }
        }
    """,
    "unpause": """
        mutation UnpauseContainer($id: PrefixedID!) {
          docker { unpause(id: $id) { id names state status } }
        }
    """,
    "remove": """
        mutation RemoveContainer($id: PrefixedID!) {
          docker { removeContainer(id: $id) }
        }
    """,
    "update": """
        mutation UpdateContainer($id: PrefixedID!) {
          docker { updateContainer(id: $id) { id names state status } }
        }
    """,
    "update_all": """
        mutation UpdateAllContainers {
          docker { updateAllContainers { id names state status } }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"remove"}
CONTAINER_ACTIONS = {"start", "stop", "restart", "pause", "unpause", "remove", "update", "details", "logs"}

DOCKER_ACTIONS = Literal[
    "list", "details", "start", "stop", "restart", "pause", "unpause",
    "remove", "update", "update_all", "logs",
    "networks", "network_details", "port_conflicts", "check_updates",
]

# Docker container IDs: 64 hex chars + optional suffix (e.g., ":local")
_DOCKER_ID_PATTERN = re.compile(r"^[a-f0-9]{64}(:[a-z0-9]+)?$", re.IGNORECASE)


def find_container_by_identifier(
    identifier: str, containers: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Find a container by ID or name with fuzzy matching."""
    if not containers:
        return None

    for c in containers:
        if c.get("id") == identifier:
            return c
        if identifier in c.get("names", []):
            return c

    id_lower = identifier.lower()
    for c in containers:
        for name in c.get("names", []):
            if id_lower in name.lower() or name.lower() in id_lower:
                logger.info(f"Fuzzy match: '{identifier}' -> '{name}'")
                return c

    return None


def get_available_container_names(containers: list[dict[str, Any]]) -> list[str]:
    """Extract all container names for error messages."""
    names: list[str] = []
    for c in containers:
        names.extend(c.get("names", []))
    return names


async def _resolve_container_id(container_id: str) -> str:
    """Resolve a container name/identifier to its actual PrefixedID."""
    if _DOCKER_ID_PATTERN.match(container_id):
        return container_id

    logger.info(f"Resolving container identifier '{container_id}'")
    list_query = """
        query ResolveContainerID {
          docker { containers(skipCache: true) { id names } }
        }
    """
    data = await make_graphql_request(list_query)
    containers = data.get("docker", {}).get("containers", [])
    resolved = find_container_by_identifier(container_id, containers)
    if resolved:
        actual_id = str(resolved.get("id", ""))
        logger.info(f"Resolved '{container_id}' -> '{actual_id}'")
        return actual_id

    available = get_available_container_names(containers)
    msg = f"Container '{container_id}' not found."
    if available:
        msg += f" Available: {', '.join(available[:10])}"
    raise ToolError(msg)


def register_docker_tool(mcp: FastMCP) -> None:
    """Register the unraid_docker tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_docker(
        action: DOCKER_ACTIONS,
        container_id: str | None = None,
        network_id: str | None = None,
        confirm: bool = False,
        tail_lines: int = 100,
    ) -> dict[str, Any]:
        """Manage Docker containers, networks, and updates.

        Actions:
          list - List all containers
          details - Detailed info for a container (requires container_id)
          start - Start a container (requires container_id)
          stop - Stop a container (requires container_id)
          restart - Stop then start a container (requires container_id)
          pause - Pause a container (requires container_id)
          unpause - Unpause a container (requires container_id)
          remove - Remove a container (requires container_id, confirm=True)
          update - Update a container to latest image (requires container_id)
          update_all - Update all containers with available updates
          logs - Get container logs (requires container_id, optional tail_lines)
          networks - List Docker networks
          network_details - Details of a network (requires network_id)
          port_conflicts - Check for port conflicts
          check_updates - Check which containers have updates available
        """
        all_actions = set(QUERIES) | set(MUTATIONS) | {"restart"}
        if action not in all_actions:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(all_actions)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        if action in CONTAINER_ACTIONS and not container_id:
            raise ToolError(f"container_id is required for '{action}' action")

        if action == "network_details" and not network_id:
            raise ToolError("network_id is required for 'network_details' action")

        try:
            logger.info(f"Executing unraid_docker action={action}")

            # --- Read-only queries ---
            if action == "list":
                data = await make_graphql_request(QUERIES["list"])
                containers = data.get("docker", {}).get("containers", [])
                return {"containers": list(containers) if isinstance(containers, list) else []}

            if action == "details":
                data = await make_graphql_request(QUERIES["details"])
                containers = data.get("docker", {}).get("containers", [])
                container = find_container_by_identifier(container_id or "", containers)
                if container:
                    return container
                available = get_available_container_names(containers)
                msg = f"Container '{container_id}' not found."
                if available:
                    msg += f" Available: {', '.join(available[:10])}"
                raise ToolError(msg)

            if action == "logs":
                actual_id = await _resolve_container_id(container_id or "")
                data = await make_graphql_request(
                    QUERIES["logs"], {"id": actual_id, "tail": tail_lines}
                )
                return {"logs": data.get("docker", {}).get("logs")}

            if action == "networks":
                data = await make_graphql_request(QUERIES["networks"])
                networks = data.get("dockerNetworks", [])
                return {"networks": list(networks) if isinstance(networks, list) else []}

            if action == "network_details":
                data = await make_graphql_request(
                    QUERIES["network_details"], {"id": network_id}
                )
                return dict(data.get("dockerNetwork", {}))

            if action == "port_conflicts":
                data = await make_graphql_request(QUERIES["port_conflicts"])
                conflicts = data.get("docker", {}).get("portConflicts", [])
                return {"port_conflicts": list(conflicts) if isinstance(conflicts, list) else []}

            if action == "check_updates":
                data = await make_graphql_request(QUERIES["check_updates"])
                statuses = data.get("docker", {}).get("containerUpdateStatuses", [])
                return {"update_statuses": list(statuses) if isinstance(statuses, list) else []}

            # --- Mutations ---
            if action == "restart":
                actual_id = await _resolve_container_id(container_id or "")
                # Stop (idempotent: treat "already stopped" as success)
                stop_data = await make_graphql_request(
                    MUTATIONS["stop"], {"id": actual_id},
                    operation_context={"operation": "stop"},
                )
                stop_was_idempotent = stop_data.get("idempotent_success", False)
                # Start (idempotent: treat "already running" as success)
                start_data = await make_graphql_request(
                    MUTATIONS["start"], {"id": actual_id},
                    operation_context={"operation": "start"},
                )
                result = start_data.get("docker", {}).get("start", {})
                response: dict[str, Any] = {
                    "success": True, "action": "restart", "container": result,
                }
                if stop_was_idempotent:
                    response["note"] = "Container was already stopped before restart"
                return response

            if action == "update_all":
                data = await make_graphql_request(MUTATIONS["update_all"])
                results = data.get("docker", {}).get("updateAllContainers", [])
                return {"success": True, "action": "update_all", "containers": results}

            # Single-container mutations
            if action in MUTATIONS:
                actual_id = await _resolve_container_id(container_id or "")
                op_context = {"operation": action} if action in ("start", "stop") else None
                data = await make_graphql_request(
                    MUTATIONS[action], {"id": actual_id},
                    operation_context=op_context,
                )

                # Handle idempotent success
                if data.get("idempotent_success"):
                    return {
                        "success": True,
                        "action": action,
                        "idempotent": True,
                        "message": f"Container already in desired state for '{action}'",
                    }

                docker_data = data.get("docker", {})
                result = docker_data.get(action, docker_data.get("removeContainer"))
                return {
                    "success": True,
                    "action": action,
                    "container": result,
                }

            return {}

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_docker action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute docker/{action}: {str(e)}") from e

    logger.info("Docker tool registered successfully")
