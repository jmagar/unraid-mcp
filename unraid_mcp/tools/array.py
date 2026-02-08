"""Array operations and system power management.

Provides the `unraid_array` tool with 12 actions for array lifecycle,
parity operations, disk management, and system power control.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError

QUERIES: dict[str, str] = {
    "parity_history": """
        query GetParityHistory {
          array { parityCheckStatus { progress speed errors } }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "start": """
        mutation StartArray {
          setState(input: { desiredState: STARTED }) { state }
        }
    """,
    "stop": """
        mutation StopArray {
          setState(input: { desiredState: STOPPED }) { state }
        }
    """,
    "parity_start": """
        mutation StartParityCheck($correct: Boolean) {
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
    "mount_disk": """
        mutation MountDisk($id: PrefixedID!) {
          mountArrayDisk(id: $id)
        }
    """,
    "unmount_disk": """
        mutation UnmountDisk($id: PrefixedID!) {
          unmountArrayDisk(id: $id)
        }
    """,
    "clear_stats": """
        mutation ClearStats($id: PrefixedID!) {
          clearArrayDiskStatistics(id: $id)
        }
    """,
    "shutdown": """
        mutation Shutdown {
          shutdown
        }
    """,
    "reboot": """
        mutation Reboot {
          reboot
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"start", "stop", "shutdown", "reboot"}
DISK_ACTIONS = {"mount_disk", "unmount_disk", "clear_stats"}

ARRAY_ACTIONS = Literal[
    "start", "stop",
    "parity_start", "parity_pause", "parity_resume", "parity_cancel", "parity_history",
    "mount_disk", "unmount_disk", "clear_stats",
    "shutdown", "reboot",
]


def register_array_tool(mcp: FastMCP) -> None:
    """Register the unraid_array tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_array(
        action: ARRAY_ACTIONS,
        confirm: bool = False,
        disk_id: str | None = None,
        correct: bool | None = None,
    ) -> dict[str, Any]:
        """Manage the Unraid array and system power.

        Actions:
          start - Start the array (destructive, requires confirm=True)
          stop - Stop the array (destructive, requires confirm=True)
          parity_start - Start parity check (optional correct=True to fix errors)
          parity_pause - Pause running parity check
          parity_resume - Resume paused parity check
          parity_cancel - Cancel running parity check
          parity_history - Get parity check status/history
          mount_disk - Mount an array disk (requires disk_id)
          unmount_disk - Unmount an array disk (requires disk_id)
          clear_stats - Clear disk statistics (requires disk_id)
          shutdown - Shut down the server (destructive, requires confirm=True)
          reboot - Reboot the server (destructive, requires confirm=True)
        """
        all_actions = set(QUERIES) | set(MUTATIONS)
        if action not in all_actions:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(all_actions)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(
                f"Action '{action}' is destructive. Set confirm=True to proceed."
            )

        if action in DISK_ACTIONS and not disk_id:
            raise ToolError(f"disk_id is required for '{action}' action")

        try:
            logger.info(f"Executing unraid_array action={action}")

            # Read-only query
            if action in QUERIES:
                data = await make_graphql_request(QUERIES[action])
                return {"success": True, "action": action, "data": data}

            # Mutations
            query = MUTATIONS[action]
            variables: dict[str, Any] | None = None

            if action in DISK_ACTIONS:
                variables = {"id": disk_id}
            elif action == "parity_start" and correct is not None:
                variables = {"correct": correct}

            data = await make_graphql_request(query, variables)

            return {
                "success": True,
                "action": action,
                "data": data,
            }

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_array action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute array/{action}: {str(e)}") from e

    logger.info("Array tool registered successfully")
