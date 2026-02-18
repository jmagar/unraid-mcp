"""Array parity check operations.

Provides the `unraid_array` tool with 5 actions for parity check management.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "parity_status": """
        query GetParityStatus {
          array { parityCheckStatus { progress speed errors } }
        }
    """,
}

MUTATIONS: dict[str, str] = {
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
}

ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

ARRAY_ACTIONS = Literal[
    "parity_start",
    "parity_pause",
    "parity_resume",
    "parity_cancel",
    "parity_status",
]


def register_array_tool(mcp: FastMCP) -> None:
    """Register the unraid_array tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_array(
        action: ARRAY_ACTIONS,
        correct: bool | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid array parity checks.

        Actions:
          parity_start - Start parity check (optional correct=True to fix errors)
          parity_pause - Pause running parity check
          parity_resume - Resume paused parity check
          parity_cancel - Cancel running parity check
          parity_status - Get current parity check status
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        with tool_error_handler("array", action, logger):
            logger.info(f"Executing unraid_array action={action}")

            if action in QUERIES:
                data = await make_graphql_request(QUERIES[action])
                return {"success": True, "action": action, "data": data}

            query = MUTATIONS[action]
            variables: dict[str, Any] | None = None

            if action == "parity_start" and correct is not None:
                variables = {"correct": correct}

            data = await make_graphql_request(query, variables)

            return {
                "success": True,
                "action": action,
                "data": data,
            }

    logger.info("Array tool registered successfully")
