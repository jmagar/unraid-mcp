"""Docker domain handler for the Unraid MCP tool.

Covers: list, details, start, stop, restart, networks, network_details (7 subactions).
"""

import re
from typing import Any

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import safe_get, validate_subaction


# ===========================================================================
# DOCKER
# ===========================================================================

_DOCKER_QUERIES: dict[str, str] = {
    "list": "query ListDockerContainers { docker { containers { id names image state status autoStart } } }",
    "details": "query GetContainerDetails { docker { containers { id names image imageId command created ports { ip privatePort publicPort type } sizeRootFs labels state status hostConfig { networkMode } networkSettings mounts autoStart } } }",
    "networks": "query GetDockerNetworks { docker { networks { id name driver scope } } }",
    "network_details": "query GetDockerNetwork { docker { networks { id name driver scope enableIPv6 internal attachable containers options labels } } }",
}

# Internal query used only for container ID resolution — not a public subaction.
_DOCKER_RESOLVE_QUERY = "query ResolveContainerID { docker { containers { id names } } }"

_DOCKER_MUTATIONS: dict[str, str] = {
    "start": "mutation StartContainer($id: PrefixedID!) { docker { start(id: $id) { id names state status } } }",
    "stop": "mutation StopContainer($id: PrefixedID!) { docker { stop(id: $id) { id names state status } } }",
}

# "logs" has no GraphQL query (field removed in Unraid 7.2.x) but is still a
# recognised subaction so validation passes and the informative ToolError below
# is returned rather than a generic "Invalid action" message.
_DOCKER_SUBACTIONS: set[str] = set(_DOCKER_QUERIES) | set(_DOCKER_MUTATIONS) | {"restart", "logs"}
_DOCKER_NEEDS_CONTAINER_ID = {"start", "stop", "details", "restart"}
_DOCKER_ID_PATTERN = re.compile(r"^[a-f0-9]{64}(:[a-z0-9]+)?$", re.IGNORECASE)
_DOCKER_SHORT_ID_PATTERN = re.compile(r"^[a-f0-9]{12,63}$", re.IGNORECASE)


def _find_container(
    identifier: str, containers: list[dict[str, Any]], *, strict: bool = False
) -> dict[str, Any] | None:
    for c in containers:
        if c.get("id") == identifier or identifier in c.get("names", []):
            return c
    if strict:
        return None
    id_lower = identifier.lower()
    # Collect prefix matches first, then fall back to substring matches.
    prefix_matches = [
        c for c in containers if any(n.lower().startswith(id_lower) for n in c.get("names", []))
    ]
    candidates = prefix_matches or [
        c for c in containers if any(id_lower in n.lower() for n in c.get("names", []))
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    names = [n for c in candidates for n in c.get("names", [])]
    raise ToolError(
        f"Container identifier '{identifier}' is ambiguous — matches: {', '.join(names[:10])}. "
        "Use a more specific name or the full container ID."
    )


async def _resolve_container_id(container_id: str, *, strict: bool = False) -> str:
    if _DOCKER_ID_PATTERN.match(container_id):
        return container_id
    data = await _client.make_graphql_request(_DOCKER_RESOLVE_QUERY)
    containers = safe_get(data, "docker", "containers", default=[])
    if _DOCKER_SHORT_ID_PATTERN.match(container_id):
        id_lower = container_id.lower()
        matches = [
            c for c in containers if (c.get("id") or "").lower().split(":")[0].startswith(id_lower)
        ]
        if len(matches) == 1:
            return str(matches[0].get("id", ""))
        if len(matches) > 1:
            raise ToolError(
                f"Short ID prefix '{container_id}' is ambiguous. Matches: {', '.join(str(c.get('id', '')) for c in matches[:5])}."
            )
    resolved = _find_container(container_id, containers, strict=strict)
    if resolved:
        return str(resolved.get("id", ""))
    names: list[str] = []
    for c in containers:
        names.extend(c.get("names", []))
    msg = (
        f"Container '{container_id}' not found by exact match. Mutations require exact name or full ID."
        if strict
        else f"Container '{container_id}' not found."
    )
    if names:
        msg += f" Available: {', '.join(names[:10])}"
    raise ToolError(msg)


async def _handle_docker(
    subaction: str, container_id: str | None, network_id: str | None
) -> dict[str, Any]:
    validate_subaction(subaction, _DOCKER_SUBACTIONS, "docker")
    if subaction in _DOCKER_NEEDS_CONTAINER_ID and not container_id:
        raise ToolError(f"container_id is required for docker/{subaction}")
    if subaction == "network_details" and not network_id:
        raise ToolError("network_id is required for docker/network_details")

    with tool_error_handler("docker", subaction, logger):
        logger.info(f"Executing unraid action=docker subaction={subaction}")

        if subaction == "list":
            data = await _client.make_graphql_request(_DOCKER_QUERIES["list"])
            return {"containers": safe_get(data, "docker", "containers", default=[])}

        if subaction == "details":
            actual_id = await _resolve_container_id(container_id or "")
            data = await _client.make_graphql_request(_DOCKER_QUERIES["details"])
            for c in safe_get(data, "docker", "containers", default=[]):
                if c.get("id") == actual_id:
                    return c
            raise ToolError(f"Container '{container_id}' not found in details response.")

        if subaction == "networks":
            data = await _client.make_graphql_request(_DOCKER_QUERIES["networks"])
            return {"networks": safe_get(data, "docker", "networks", default=[])}

        if subaction == "network_details":
            data = await _client.make_graphql_request(_DOCKER_QUERIES["network_details"])
            for net in safe_get(data, "docker", "networks", default=[]):
                if net.get("id") == network_id or net.get("name") == network_id:
                    return dict(net)
            raise ToolError(f"Network '{network_id}' not found.")

        if subaction == "logs":
            raise ToolError(
                "Container logs are not available via the Unraid GraphQL API. "
                "Use the Unraid terminal or SSH to run: "
                f"`docker logs {container_id or '<container_id>'} --tail 100`"
            )

        if subaction == "restart":
            actual_id = await _resolve_container_id(container_id or "", strict=True)
            stop_data = await _client.make_graphql_request(
                _DOCKER_MUTATIONS["stop"],
                {"id": actual_id},
                operation_context={"operation": "stop"},
            )
            stop_was_idempotent = stop_data.get("idempotent_success", False)
            start_data = await _client.make_graphql_request(
                _DOCKER_MUTATIONS["start"],
                {"id": actual_id},
                operation_context={"operation": "start"},
            )
            result = (
                {}
                if start_data.get("idempotent_success")
                else safe_get(start_data, "docker", "start", default={})
            )
            response: dict[str, Any] = {
                "success": True,
                "subaction": "restart",
                "container": result,
            }
            if stop_was_idempotent:
                response["note"] = "Container was already stopped before restart"
            return response

        actual_id = await _resolve_container_id(container_id or "", strict=True)
        data = await _client.make_graphql_request(
            _DOCKER_MUTATIONS[subaction],
            {"id": actual_id},
            operation_context={"operation": subaction},
        )
        if data.get("idempotent_success"):
            return {
                "success": True,
                "subaction": subaction,
                "idempotent": True,
                "message": f"Container already in desired state for '{subaction}'",
            }
        return {
            "success": True,
            "subaction": subaction,
            "container": (data.get("docker") or {}).get(subaction),
        }
