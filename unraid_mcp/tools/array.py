"""Array management: parity checks, array state, and disk operations.

Provides the `unraid_array` tool with 13 actions covering parity check
management, array start/stop, and disk add/remove/mount operations.
"""

from __future__ import annotations

from typing import Any, Literal, get_args

from fastmcp import Context, FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_destructive_confirmation


QUERIES: dict[str, str] = {
    "parity_status": """
        query GetParityStatus {
          array { parityCheckStatus { progress speed errors status paused running correcting } }
        }
    """,
    "parity_history": """
        query GetParityHistory {
          parityHistory {
            date duration speed status errors progress correcting paused running
          }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "parity_start": """
        mutation StartParityCheck($correct: Boolean!) {
          parityCheck { start(correct: $correct) }
        }
    """,
    "parity_pause": """
        mutation PauseParityCheck {
          parityCheck { pause }
        }
    """,
    "parity_resume": """
        mutation ResumeParityCheck {
          parityCheck { resume }
        }
    """,
    "parity_cancel": """
        mutation CancelParityCheck {
          parityCheck { cancel }
        }
    """,
    "start_array": """
        mutation StartArray {
          array { setState(input: { desiredState: START }) {
            state capacity { kilobytes { free used total } }
          }}
        }
    """,
    "stop_array": """
        mutation StopArray {
          array { setState(input: { desiredState: STOP }) {
            state
          }}
        }
    """,
    "add_disk": """
        mutation AddDisk($id: PrefixedID!, $slot: Int) {
          array { addDiskToArray(input: { id: $id, slot: $slot }) {
            state disks { id name device type status }
          }}
        }
    """,
    "remove_disk": """
        mutation RemoveDisk($id: PrefixedID!) {
          array { removeDiskFromArray(input: { id: $id }) {
            state disks { id name device type }
          }}
        }
    """,
    "mount_disk": """
        mutation MountDisk($id: PrefixedID!) {
          array { mountArrayDisk(id: $id) { id name device status } }
        }
    """,
    "unmount_disk": """
        mutation UnmountDisk($id: PrefixedID!) {
          array { unmountArrayDisk(id: $id) { id name device status } }
        }
    """,
    "clear_disk_stats": """
        mutation ClearDiskStats($id: PrefixedID!) {
          array { clearArrayDiskStatistics(id: $id) }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"remove_disk", "clear_disk_stats"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

ARRAY_ACTIONS = Literal[
    "add_disk",
    "clear_disk_stats",
    "mount_disk",
    "parity_cancel",
    "parity_history",
    "parity_pause",
    "parity_resume",
    "parity_start",
    "parity_status",
    "remove_disk",
    "start_array",
    "stop_array",
    "unmount_disk",
]

if set(get_args(ARRAY_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(ARRAY_ACTIONS))
    _extra = set(get_args(ARRAY_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"ARRAY_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_array_tool(mcp: FastMCP) -> None:
    """Register the unraid_array tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_array(
        action: ARRAY_ACTIONS,
        ctx: Context | None = None,
        confirm: bool = False,
        correct: bool | None = None,
        disk_id: str | None = None,
        slot: int | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid array: parity checks, array state, and disk operations.

        Parity check actions:
          parity_start   - Start parity check (correct=True to write fixes; required)
          parity_pause   - Pause running parity check
          parity_resume  - Resume paused parity check
          parity_cancel  - Cancel running parity check
          parity_status  - Get current parity check status and progress
          parity_history - Get parity check history log

        Array state actions:
          start_array    - Start the array (desiredState=START)
          stop_array     - Stop the array (desiredState=STOP)

        Disk operations (requires disk_id):
          add_disk       - Add a disk to the array (requires disk_id; optional slot)
          remove_disk    - Remove a disk from the array (requires disk_id, confirm=True; array must be stopped)
          mount_disk     - Mount a disk (requires disk_id)
          unmount_disk   - Unmount a disk (requires disk_id)
          clear_disk_stats - Clear I/O statistics for a disk (requires disk_id, confirm=True)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            desc_map = {
                "remove_disk": f"Remove disk **{disk_id}** from the array. The array must be stopped first.",
                "clear_disk_stats": f"Clear all I/O statistics for disk **{disk_id}**. This cannot be undone.",
            }
            confirmed = await elicit_destructive_confirmation(ctx, action, desc_map[action])
            if not confirmed:
                raise ToolError(
                    f"Action '{action}' was not confirmed. "
                    "Re-run with confirm=True to bypass elicitation."
                )

        with tool_error_handler("array", action, logger):
            logger.info(f"Executing unraid_array action={action}")

            # --- Queries ---
            if action in QUERIES:
                data = await make_graphql_request(QUERIES[action])
                return {"success": True, "action": action, "data": data}

            # --- Mutations ---
            if action == "parity_start":
                if correct is None:
                    raise ToolError("correct is required for 'parity_start' action")
                data = await make_graphql_request(MUTATIONS[action], {"correct": correct})
                return {"success": True, "action": action, "data": data}

            if action in ("parity_pause", "parity_resume", "parity_cancel"):
                data = await make_graphql_request(MUTATIONS[action])
                return {"success": True, "action": action, "data": data}

            if action in ("start_array", "stop_array"):
                data = await make_graphql_request(MUTATIONS[action])
                return {"success": True, "action": action, "data": data}

            if action == "add_disk":
                if not disk_id:
                    raise ToolError("disk_id is required for 'add_disk' action")
                variables: dict[str, Any] = {"id": disk_id}
                if slot is not None:
                    variables["slot"] = slot
                data = await make_graphql_request(MUTATIONS[action], variables)
                return {"success": True, "action": action, "data": data}

            if action in ("remove_disk", "mount_disk", "unmount_disk", "clear_disk_stats"):
                if not disk_id:
                    raise ToolError(f"disk_id is required for '{action}' action")
                data = await make_graphql_request(MUTATIONS[action], {"id": disk_id})
                return {"success": True, "action": action, "data": data}

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Array tool registered successfully")
