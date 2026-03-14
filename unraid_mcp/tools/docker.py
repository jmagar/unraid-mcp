"""Docker container management.

Provides the `unraid_docker` tool with 26 actions for container lifecycle,
logs, networks, update management, and Docker organizer operations.
"""

import re
from typing import Any, Literal, get_args

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
          docker { logs(id: $id, tail: $tail) { containerId lines { timestamp message } cursor } }
        }
    """,
    "networks": """
        query GetDockerNetworks {
          docker { networks { id name driver scope } }
        }
    """,
    "network_details": """
        query GetDockerNetwork {
          docker { networks { id name driver scope enableIPv6 internal attachable containers options labels } }
        }
    """,
    "port_conflicts": """
        query GetPortConflicts {
          docker { portConflicts { containerPorts { privatePort type containers { id name } } lanPorts { lanIpPort publicPort type containers { id name } } } }
        }
    """,
    "check_updates": """
        query CheckContainerUpdates {
          docker { containerUpdateStatuses { name updateStatus } }
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
    "create_folder": """
        mutation CreateDockerFolder($name: String!, $parentId: String, $childrenIds: [String!]) {
          createDockerFolder(name: $name, parentId: $parentId, childrenIds: $childrenIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "set_folder_children": """
        mutation SetDockerFolderChildren($folderId: String, $childrenIds: [String!]!) {
          setDockerFolderChildren(folderId: $folderId, childrenIds: $childrenIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "delete_entries": """
        mutation DeleteDockerEntries($entryIds: [String!]!) {
          deleteDockerEntries(entryIds: $entryIds) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "move_to_folder": """
        mutation MoveDockerEntriesToFolder($sourceEntryIds: [String!]!, $destinationFolderId: String!) {
          moveDockerEntriesToFolder(sourceEntryIds: $sourceEntryIds, destinationFolderId: $destinationFolderId) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "move_to_position": """
        mutation MoveDockerItemsToPosition($sourceEntryIds: [String!]!, $destinationFolderId: String!, $position: Float!) {
          moveDockerItemsToPosition(sourceEntryIds: $sourceEntryIds, destinationFolderId: $destinationFolderId, position: $position) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "rename_folder": """
        mutation RenameDockerFolder($folderId: String!, $newName: String!) {
          renameDockerFolder(folderId: $folderId, newName: $newName) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "create_folder_with_items": """
        mutation CreateDockerFolderWithItems($name: String!, $parentId: String, $sourceEntryIds: [String!], $position: Float) {
          createDockerFolderWithItems(name: $name, parentId: $parentId, sourceEntryIds: $sourceEntryIds, position: $position) {
            version views { id name rootId flatEntries { id type name parentId depth position path hasChildren childrenIds } }
          }
        }
    """,
    "update_view_prefs": """
        mutation UpdateDockerViewPreferences($viewId: String, $prefs: JSON!) {
          updateDockerViewPreferences(viewId: $viewId, prefs: $prefs) {
            version views { id name rootId }
          }
        }
    """,
    "sync_templates": """
        mutation SyncDockerTemplatePaths {
          syncDockerTemplatePaths { scanned matched skipped errors }
        }
    """,
    "reset_template_mappings": """
        mutation ResetDockerTemplateMappings {
          resetDockerTemplateMappings
        }
    """,
    "refresh_digests": """
        mutation RefreshDockerDigests {
          refreshDockerDigests
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"remove", "update_all", "delete_entries", "reset_template_mappings"}
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
    "create_folder",
    "set_folder_children",
    "delete_entries",
    "move_to_folder",
    "move_to_position",
    "rename_folder",
    "create_folder_with_items",
    "update_view_prefs",
    "sync_templates",
    "reset_template_mappings",
    "refresh_digests",
]

if set(get_args(DOCKER_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(DOCKER_ACTIONS))
    _extra = set(get_args(DOCKER_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"DOCKER_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )

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
        matches: list[dict[str, Any]] = []
        for c in containers:
            cid = (c.get("id") or "").lower()
            if cid.startswith(id_lower) or cid.split(":")[0].startswith(id_lower):
                matches.append(c)
        if len(matches) == 1:
            actual_id = str(matches[0].get("id", ""))
            logger.info(f"Resolved short ID '{container_id}' -> '{actual_id}'")
            return actual_id
        if len(matches) > 1:
            candidate_ids = [str(c.get("id", "")) for c in matches[:5]]
            raise ToolError(
                f"Short container ID prefix '{container_id}' is ambiguous. "
                f"Matches: {', '.join(candidate_ids)}. Use a longer ID or exact name."
            )

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
        folder_name: str | None = None,
        folder_id: str | None = None,
        parent_id: str | None = None,
        children_ids: list[str] | None = None,
        entry_ids: list[str] | None = None,
        source_entry_ids: list[str] | None = None,
        destination_folder_id: str | None = None,
        position: float | None = None,
        new_folder_name: str | None = None,
        view_id: str = "default",
        view_prefs: dict[str, Any] | None = None,
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
          create_folder - Create Docker organizer folder (requires folder_name)
          set_folder_children - Set children of a folder (requires children_ids)
          delete_entries - Delete organizer entries (requires entry_ids, confirm=True)
          move_to_folder - Move entries to a folder (requires source_entry_ids, destination_folder_id)
          move_to_position - Move entries to position in folder (requires source_entry_ids, destination_folder_id, position)
          rename_folder - Rename a folder (requires folder_id, new_folder_name)
          create_folder_with_items - Create folder with items (requires folder_name)
          update_view_prefs - Update organizer view preferences (requires view_prefs)
          sync_templates - Sync Docker template paths
          reset_template_mappings - Reset template mappings (confirm=True)
          refresh_digests - Refresh container image digests
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        if action in _ACTIONS_REQUIRING_CONTAINER_ID and not container_id:
            raise ToolError(f"container_id is required for '{action}' action")

        if action == "network_details" and not network_id:
            raise ToolError("network_id is required for 'network_details' action")

        if action == "logs" and (tail_lines < 1 or tail_lines > _MAX_TAIL_LINES):
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
                logs_data = safe_get(data, "docker", "logs")
                if logs_data is None:
                    raise ToolError(f"No logs returned for container '{container_id}'")
                # Extract log lines into a plain text string for backward compatibility.
                # The GraphQL response is { containerId, lines: [{ timestamp, message }], cursor }
                # but callers expect result["logs"] to be a string of log text.
                lines = logs_data.get("lines", []) if isinstance(logs_data, dict) else []
                log_text = "\n".join(
                    f"{line.get('timestamp', '')} {line.get('message', '')}".strip()
                    for line in lines
                )
                return {
                    "logs": log_text,
                    "cursor": logs_data.get("cursor") if isinstance(logs_data, dict) else None,
                }

            if action == "networks":
                data = await make_graphql_request(QUERIES["networks"])
                networks = safe_get(data, "docker", "networks", default=[])
                return {"networks": networks}

            if action == "network_details":
                data = await make_graphql_request(QUERIES["network_details"])
                all_networks = safe_get(data, "docker", "networks", default=[])
                # Filter client-side by network_id since the API returns all networks
                for net in all_networks:
                    if net.get("id") == network_id or net.get("name") == network_id:
                        return dict(net)
                raise ToolError(f"Network '{network_id}' not found.")

            if action == "port_conflicts":
                data = await make_graphql_request(QUERIES["port_conflicts"])
                conflicts_data = safe_get(data, "docker", "portConflicts", default={})
                # The GraphQL response is { containerPorts: [...], lanPorts: [...] }
                # but callers expect result["port_conflicts"] to be a flat list.
                # Merge both conflict lists for backward compatibility.
                if isinstance(conflicts_data, dict):
                    conflicts: list[Any] = []
                    conflicts.extend(conflicts_data.get("containerPorts", []))
                    conflicts.extend(conflicts_data.get("lanPorts", []))
                else:
                    conflicts = list(conflicts_data) if conflicts_data else []
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

            # --- Docker organizer mutations ---
            if action == "create_folder":
                if not folder_name:
                    raise ToolError("folder_name is required for 'create_folder' action")
                _vars: dict[str, Any] = {"name": folder_name}
                if parent_id is not None:
                    _vars["parentId"] = parent_id
                if children_ids is not None:
                    _vars["childrenIds"] = children_ids
                data = await make_graphql_request(MUTATIONS["create_folder"], _vars)
                organizer = data.get("createDockerFolder")
                if organizer is None:
                    raise ToolError("create_folder failed: server returned no data")
                return {"success": True, "action": "create_folder", "organizer": organizer}

            if action == "set_folder_children":
                if children_ids is None:
                    raise ToolError("children_ids is required for 'set_folder_children' action")
                _vars = {"childrenIds": children_ids}
                if folder_id is not None:
                    _vars["folderId"] = folder_id
                data = await make_graphql_request(MUTATIONS["set_folder_children"], _vars)
                organizer = data.get("setDockerFolderChildren")
                if organizer is None:
                    raise ToolError("set_folder_children failed: server returned no data")
                return {"success": True, "action": "set_folder_children", "organizer": organizer}

            if action == "delete_entries":
                if not entry_ids:
                    raise ToolError("entry_ids is required for 'delete_entries' action")
                data = await make_graphql_request(
                    MUTATIONS["delete_entries"], {"entryIds": entry_ids}
                )
                organizer = data.get("deleteDockerEntries")
                if organizer is None:
                    raise ToolError("delete_entries failed: server returned no data")
                return {"success": True, "action": "delete_entries", "organizer": organizer}

            if action == "move_to_folder":
                if not source_entry_ids:
                    raise ToolError("source_entry_ids is required for 'move_to_folder' action")
                if not destination_folder_id:
                    raise ToolError("destination_folder_id is required for 'move_to_folder' action")
                data = await make_graphql_request(
                    MUTATIONS["move_to_folder"],
                    {
                        "sourceEntryIds": source_entry_ids,
                        "destinationFolderId": destination_folder_id,
                    },
                )
                organizer = data.get("moveDockerEntriesToFolder")
                if organizer is None:
                    raise ToolError("move_to_folder failed: server returned no data")
                return {"success": True, "action": "move_to_folder", "organizer": organizer}

            if action == "move_to_position":
                if not source_entry_ids:
                    raise ToolError("source_entry_ids is required for 'move_to_position' action")
                if not destination_folder_id:
                    raise ToolError(
                        "destination_folder_id is required for 'move_to_position' action"
                    )
                if position is None:
                    raise ToolError("position is required for 'move_to_position' action")
                data = await make_graphql_request(
                    MUTATIONS["move_to_position"],
                    {
                        "sourceEntryIds": source_entry_ids,
                        "destinationFolderId": destination_folder_id,
                        "position": position,
                    },
                )
                organizer = data.get("moveDockerItemsToPosition")
                if organizer is None:
                    raise ToolError("move_to_position failed: server returned no data")
                return {"success": True, "action": "move_to_position", "organizer": organizer}

            if action == "rename_folder":
                if not folder_id:
                    raise ToolError("folder_id is required for 'rename_folder' action")
                if not new_folder_name:
                    raise ToolError("new_folder_name is required for 'rename_folder' action")
                data = await make_graphql_request(
                    MUTATIONS["rename_folder"], {"folderId": folder_id, "newName": new_folder_name}
                )
                organizer = data.get("renameDockerFolder")
                if organizer is None:
                    raise ToolError("rename_folder failed: server returned no data")
                return {"success": True, "action": "rename_folder", "organizer": organizer}

            if action == "create_folder_with_items":
                if not folder_name:
                    raise ToolError("folder_name is required for 'create_folder_with_items' action")
                _vars = {"name": folder_name}
                if parent_id is not None:
                    _vars["parentId"] = parent_id
                if source_entry_ids is not None:
                    _vars["sourceEntryIds"] = source_entry_ids
                if position is not None:
                    _vars["position"] = position
                data = await make_graphql_request(MUTATIONS["create_folder_with_items"], _vars)
                organizer = data.get("createDockerFolderWithItems")
                if organizer is None:
                    raise ToolError("create_folder_with_items failed: server returned no data")
                return {
                    "success": True,
                    "action": "create_folder_with_items",
                    "organizer": organizer,
                }

            if action == "update_view_prefs":
                if view_prefs is None:
                    raise ToolError("view_prefs is required for 'update_view_prefs' action")
                data = await make_graphql_request(
                    MUTATIONS["update_view_prefs"], {"viewId": view_id, "prefs": view_prefs}
                )
                organizer = data.get("updateDockerViewPreferences")
                if organizer is None:
                    raise ToolError("update_view_prefs failed: server returned no data")
                return {"success": True, "action": "update_view_prefs", "organizer": organizer}

            if action == "sync_templates":
                data = await make_graphql_request(MUTATIONS["sync_templates"])
                result = data.get("syncDockerTemplatePaths")
                if result is None:
                    raise ToolError("sync_templates failed: server returned no data")
                return {"success": True, "action": "sync_templates", "result": result}

            if action == "reset_template_mappings":
                data = await make_graphql_request(MUTATIONS["reset_template_mappings"])
                return {
                    "success": True,
                    "action": "reset_template_mappings",
                    "result": data.get("resetDockerTemplateMappings"),
                }

            if action == "refresh_digests":
                data = await make_graphql_request(MUTATIONS["refresh_digests"])
                return {
                    "success": True,
                    "action": "refresh_digests",
                    "result": data.get("refreshDockerDigests"),
                }

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
