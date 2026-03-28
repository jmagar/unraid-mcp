"""Array domain handler for the Unraid MCP tool.

Covers: parity_status, parity_history, parity_start, parity_pause, parity_resume,
parity_cancel, start_array, stop_array*, add_disk, remove_disk*, mount_disk,
unmount_disk, clear_disk_stats* (13 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


# ===========================================================================
# ARRAY
# ===========================================================================

_ARRAY_QUERIES: dict[str, str] = {
    "parity_status": "query GetParityStatus { array { parityCheckStatus { progress speed errors status paused running correcting } } }",
    "parity_history": "query GetParityHistory { parityHistory { date duration speed status errors progress correcting paused running } }",
}

_ARRAY_MUTATIONS: dict[str, str] = {
    "parity_start": "mutation StartParityCheck($correct: Boolean!) { parityCheck { start(correct: $correct) } }",
    "parity_pause": "mutation PauseParityCheck { parityCheck { pause } }",
    "parity_resume": "mutation ResumeParityCheck { parityCheck { resume } }",
    "parity_cancel": "mutation CancelParityCheck { parityCheck { cancel } }",
    "start_array": "mutation StartArray { array { setState(input: { desiredState: START }) { state capacity { kilobytes { free used total } } } } }",
    "stop_array": "mutation StopArray { array { setState(input: { desiredState: STOP }) { state } } }",
    "add_disk": "mutation AddDisk($id: PrefixedID!, $slot: Int) { array { addDiskToArray(input: { id: $id, slot: $slot }) { state disks { id name device type status } } } }",
    "remove_disk": "mutation RemoveDisk($id: PrefixedID!) { array { removeDiskFromArray(input: { id: $id }) { state disks { id name device type } } } }",
    "mount_disk": "mutation MountDisk($id: PrefixedID!) { array { mountArrayDisk(id: $id) { id name device status } } }",
    "unmount_disk": "mutation UnmountDisk($id: PrefixedID!) { array { unmountArrayDisk(id: $id) { id name device status } } }",
    "clear_disk_stats": "mutation ClearDiskStats($id: PrefixedID!) { array { clearArrayDiskStatistics(id: $id) } }",
}

_ARRAY_SUBACTIONS: set[str] = set(_ARRAY_QUERIES) | set(_ARRAY_MUTATIONS)
_ARRAY_DESTRUCTIVE: set[str] = {"remove_disk", "clear_disk_stats", "stop_array"}


async def _handle_array(
    subaction: str,
    disk_id: str | None,
    correct: bool | None,
    slot: int | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _ARRAY_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for array. Must be one of: {sorted(_ARRAY_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _ARRAY_DESTRUCTIVE,
        confirm,
        {
            "remove_disk": f"Remove disk **{disk_id}** from the array. The array must be stopped first.",
            "clear_disk_stats": f"Clear all I/O statistics for disk **{disk_id}**. This cannot be undone.",
            "stop_array": "Stop the Unraid array. Running containers and VMs may lose access to array shares.",
        },
    )

    with tool_error_handler("array", subaction, logger):
        logger.info(f"Executing unraid action=array subaction={subaction}")

        if subaction in _ARRAY_QUERIES:
            data = await _client.make_graphql_request(_ARRAY_QUERIES[subaction])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "parity_start":
            if correct is None:
                raise ToolError("correct is required for array/parity_start")
            data = await _client.make_graphql_request(
                _ARRAY_MUTATIONS[subaction], {"correct": correct}
            )
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in (
            "parity_pause",
            "parity_resume",
            "parity_cancel",
            "start_array",
            "stop_array",
        ):
            data = await _client.make_graphql_request(_ARRAY_MUTATIONS[subaction])
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "add_disk":
            if not disk_id:
                raise ToolError("disk_id is required for array/add_disk")
            variables: dict[str, Any] = {"id": disk_id}
            if slot is not None:
                variables["slot"] = slot
            data = await _client.make_graphql_request(_ARRAY_MUTATIONS[subaction], variables)
            return {"success": True, "subaction": subaction, "data": data}

        if subaction in ("remove_disk", "mount_disk", "unmount_disk", "clear_disk_stats"):
            if not disk_id:
                raise ToolError(f"disk_id is required for array/{subaction}")
            data = await _client.make_graphql_request(_ARRAY_MUTATIONS[subaction], {"id": disk_id})
            return {"success": True, "subaction": subaction, "data": data}

        raise ToolError(f"Unhandled array subaction '{subaction}' — this is a bug")
