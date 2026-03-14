"""Array parity check operations.

Provides the `unraid_array` tool with 5 actions for parity check management.
"""

from typing import Any, Literal, get_args

from fastmcp import Context as _Context
from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import CredentialsNotConfiguredError as _CredErr
from ..core.exceptions import ToolError, tool_error_handler
from ..core.setup import elicit_and_configure as _elicit


# Re-export at module scope so tests can patch "unraid_mcp.tools.array.elicit_and_configure"
# and "unraid_mcp.tools.array.CredentialsNotConfiguredError"
elicit_and_configure = _elicit
CredentialsNotConfiguredError = _CredErr
Context = _Context


QUERIES: dict[str, str] = {
    "parity_status": """
        query GetParityStatus {
          array { parityCheckStatus { progress speed errors } }
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
}

ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)

ARRAY_ACTIONS = Literal[
    "parity_start",
    "parity_pause",
    "parity_resume",
    "parity_cancel",
    "parity_status",
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
        correct: bool | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid array parity checks.

        Actions:
          parity_start - Start parity check (correct=True to fix errors, correct=False for read-only; required)
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
                try:
                    data = await make_graphql_request(QUERIES[action])
                except CredentialsNotConfiguredError:
                    configured = await elicit_and_configure(ctx)
                    if not configured:
                        raise ToolError(
                            "Credentials required. Run `unraid_health action=setup` to configure."
                        )
                    data = await make_graphql_request(QUERIES[action])
                return {"success": True, "action": action, "data": data}

            query = MUTATIONS[action]
            variables: dict[str, Any] | None = None

            if action == "parity_start":
                if correct is None:
                    raise ToolError("correct is required for 'parity_start' action")
                variables = {"correct": correct}

            try:
                data = await make_graphql_request(query, variables)
            except CredentialsNotConfiguredError:
                configured = await elicit_and_configure(ctx)
                if not configured:
                    raise ToolError(
                        "Credentials required. Run `unraid_health action=setup` to configure."
                    )
                data = await make_graphql_request(query, variables)

            return {
                "success": True,
                "action": action,
                "data": data,
            }

    logger.info("Array tool registered successfully")
