"""Docker container management.

Provides the `unraid_docker` tool with 15 actions for container lifecycle,
logs, networks, and update management.
"""

import re
from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import safe_get


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
_MUTATION_ACTIONS = {"start", "stop", "restart", "pause", "unpause", "remove", "update"}
# NOTE (Code-M-07): "details" and "logs" are listed here because they require a
# container_id parameter, but unlike mutations they use fuzzy name matching (not
# strict). This is intentional: read-only queries are safe with fuzzy matching.
_ACTIONS_REQUIRING_CONTAINER_ID = {
    "start",
    "stop",
    "restart",
    "pause",
    "unpause",
    "remove",
    "update",
    "details",
    "logs",
}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS) | {"restart"}
_MAX_TAIL_LINES = 10_000

DOCKER_ACTIONS = Literal[
    "list",
    "details",
    "start",
    "stop",
    "restart",
    "pause",
    "unpause",
    "remove",
    "update",
    "update_all",
    "logs",
    "networks",
    "network_details",
    "port_conflicts",
    "check_updates",
]

# Full PrefixedID: 64 hex chars + optional suffix (e.g., ":local")
_DOCKER_ID_PATTERN = re.compile(r"^[a-f0-9]{64}(:[a-z0-9]+)?$", re.IGNORECASE)

# Short hex prefix: at least 12 hex chars (standard Docker short ID length)
_DOCKER_SHORT_ID_PATTERN = re.compile(r"^[a-f0-9]{12,63}$", re.IGNORECASE)


def find_container_by_identifier(
    identifier: str, containers: list[dict[str, Any]], *, strict: bool = False
) -> dict[str, Any] | None:
    """Find a container by ID or name with optional fuzzy matching.

    Match priority:
      1. Exact ID match
      2. Exact name match (case-sensitive)

    When strict=False (default), also tries:
      3. Name starts with identifier (case-insensitive)
      4. Name contains identifier as substring (case-insensitive)

    When strict=True, only exact matches (1 & 2) are used.
    Use strict=True for mutations to prevent targeting the wrong container.
    """
    if not containers:
        return None

    # Priority 1 & 2: exact matches
    for c in containers:
        if c.get("id") == identifier:
            return c
        if identifier in c.get("names", []):
            return c

    # Strict mode: no fuzzy matching allowed
    if strict:
        return None

    id_lower = identifier.lower()

    # Priority 3: prefix match (more precise than substring)
    for c in containers:
        for name in c.get("names", []):
            if name.lower().startswith(id_lower):
                logger.debug(f"Prefix match: '{identifier}' -> '{name}'")
                return c

    # Priority 4: substring match (least precise)
    for c in containers:
        for name in c.get("names", []):
            if id_lower in name.lower():
                logger.debug(f"Substring match: '{identifier}' -> '{name}'")
                return c

    return None


def get_available_container_names(containers: list[dict[str, Any]]) -> list[str]:
    """Extract all container names for error messages."""
    names: list[str] = []
    for c in containers:
        names.extend(c.get("names", []))
    return names


def _looks_like_container_id(identifier: str) -> bool:
    """Check if an identifier looks like a container ID (full or short hex prefix)."""
    return bool(_DOCKER_ID_PATTERN.match(identifier) or _DOCKER_SHORT_ID_PATTERN.match(identifier))


async def _resolve_container_id(container_id: str, *, strict: bool = False) -> str:
    """Resolve a container name/identifier to its actual PrefixedID.

    Optimization: if the identifier is a full 64-char hex ID (with optional
    :suffix), skip the container list fetch entirely and use it directly.
    If it's a short hex prefix (12-63 chars), fetch the list and match by
    ID prefix. Only fetch the container list for name-based lookups.

    Args:
        container_id: Container name or ID to resolve
        strict: When True, only exact name/ID matches are allowed (no fuzzy).
                Use for mutations to prevent targeting the wrong container.
    """
    # Full PrefixedID: skip the list fetch entirely
    if _DOCKER_ID_PATTERN.match(container_id):
        return container_id

    logger.info(f"Resolving container identifier '{container_id}' (strict={strict})")
    list_query = """
        query ResolveContainerID {
          docker { containers(skipCache: true) { id names } }
        }
    """
    data = await make_graphql_request(list_query)
    containers = safe_get(data, "docker", "containers", default=[])

    # Short hex prefix: match by ID prefix before trying name matching
    if _DOCKER_SHORT_ID_PATTERN.match(container_id):
        id_lower = container_id.lower()
        for c in containers:
            cid = (c.get("id") or "").lower()
            if cid.startswith(id_lower) or cid.split(":")[0].startswith(id_lower):
                actual_id = str(c.get("id", ""))
                logger.info(f"Resolved short ID '{container_id}' -> '{actual_id}'")
                return actual_id

    resolved = find_container_by_identifier(container_id, containers, strict=strict)
    if resolved:
        actual_id = str(resolved.get("id", ""))
        logger.info(f"Resolved '{container_id}' -> '{actual_id}'")
        return actual_id

    available = get_available_container_names(containers)
    if strict:
        msg = (
            f"Container '{container_id}' not found by exact match. "
            f"Mutations require an exact container name or full ID — "
            f"fuzzy/substring matching is not allowed for safety."
        )
    else:
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
        *,
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
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        if action in _ACTIONS_REQUIRING_CONTAINER_ID and not container_id:
            raise ToolError(f"container_id is required for '{action}' action")

        if action == "network_details" and not network_id:
            raise ToolError("network_id is required for 'network_details' action")

        if tail_lines < 1 or tail_lines > _MAX_TAIL_LINES:
            raise ToolError(f"tail_lines must be between 1 and {_MAX_TAIL_LINES}, got {tail_lines}")

        with tool_error_handler("docker", action, logger):
            logger.info(f"Executing unraid_docker action={action}")

            # --- Read-only queries ---
            if action == "list":
                data = await make_graphql_request(QUERIES["list"])
                containers = safe_get(data, "docker", "containers", default=[])
                return {"containers": containers}

            if action == "details":
                # Resolve name -> ID first (skips list fetch if already an ID)
                actual_id = await _resolve_container_id(container_id or "")
                data = await make_graphql_request(QUERIES["details"])
                containers = safe_get(data, "docker", "containers", default=[])
                # Match by resolved ID (exact match, no second list fetch needed)
                for c in containers:
                    if c.get("id") == actual_id:
                        return c
                raise ToolError(f"Container '{container_id}' not found in details response.")

            if action == "logs":
                actual_id = await _resolve_container_id(container_id or "")
                data = await make_graphql_request(
                    QUERIES["logs"], {"id": actual_id, "tail": tail_lines}
                )
                return {"logs": safe_get(data, "docker", "logs")}

            if action == "networks":
                data = await make_graphql_request(QUERIES["networks"])
                networks = data.get("dockerNetworks", [])
                return {"networks": networks}

            if action == "network_details":
                data = await make_graphql_request(QUERIES["network_details"], {"id": network_id})
                return dict(data.get("dockerNetwork") or {})

            if action == "port_conflicts":
                data = await make_graphql_request(QUERIES["port_conflicts"])
                conflicts = safe_get(data, "docker", "portConflicts", default=[])
                return {"port_conflicts": conflicts}

            if action == "check_updates":
                data = await make_graphql_request(QUERIES["check_updates"])
                statuses = safe_get(data, "docker", "containerUpdateStatuses", default=[])
                return {"update_statuses": statuses}

            # --- Mutations (strict matching: no fuzzy/substring) ---
            if action == "restart":
                actual_id = await _resolve_container_id(container_id or "", strict=True)
                # Stop (idempotent: treat "already stopped" as success)
                stop_data = await make_graphql_request(
                    MUTATIONS["stop"],
                    {"id": actual_id},
                    operation_context={"operation": "stop"},
                )
                stop_was_idempotent = stop_data.get("idempotent_success", False)
                # Start (idempotent: treat "already running" as success)
                start_data = await make_graphql_request(
                    MUTATIONS["start"],
                    {"id": actual_id},
                    operation_context={"operation": "start"},
                )
                if start_data.get("idempotent_success"):
                    result = {}
                else:
                    result = safe_get(start_data, "docker", "start", default={})
                response: dict[str, Any] = {
                    "success": True,
                    "action": "restart",
                    "container": result,
                }
                if stop_was_idempotent:
                    response["note"] = "Container was already stopped before restart"
                return response

            if action == "update_all":
                data = await make_graphql_request(MUTATIONS["update_all"])
                results = safe_get(data, "docker", "updateAllContainers", default=[])
                return {"success": True, "action": "update_all", "containers": results}

            # Single-container mutations
            if action in MUTATIONS:
                actual_id = await _resolve_container_id(container_id or "", strict=True)
                op_context: dict[str, str] | None = (
                    {"operation": action} if action in ("start", "stop") else None
                )
                data = await make_graphql_request(
                    MUTATIONS[action],
                    {"id": actual_id},
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

                docker_data = data.get("docker") or {}
                # Map action names to GraphQL response field names where they differ
                response_field_map = {
                    "update": "updateContainer",
                    "remove": "removeContainer",
                }
                field = response_field_map.get(action, action)
                result = docker_data.get(field)
                return {
                    "success": True,
                    "action": action,
                    "container": result,
                }

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Docker tool registered successfully")
