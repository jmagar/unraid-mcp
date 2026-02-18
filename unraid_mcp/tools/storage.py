"""Storage and disk management.

Provides the `unraid_storage` tool with 6 actions for shares, physical disks,
unassigned devices, log files, and log content retrieval.
"""

import os
from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import DISK_TIMEOUT, make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler
from ..core.utils import format_bytes


_ALLOWED_LOG_PREFIXES = ("/var/log/", "/boot/logs/", "/mnt/")
_MAX_TAIL_LINES = 10_000

QUERIES: dict[str, str] = {
    "shares": """
        query GetSharesInfo {
          shares {
            id name free used size include exclude cache nameOrig
            comment allocator splitLevel floor cow color luksStatus
          }
        }
    """,
    "disks": """
        query ListPhysicalDisks {
          disks { id device name }
        }
    """,
    "disk_details": """
        query GetDiskDetails($id: PrefixedID!) {
          disk(id: $id) {
            id device name serialNum size temperature
          }
        }
    """,
    "unassigned": """
        query GetUnassignedDevices {
          unassignedDevices { id device name size type }
        }
    """,
    "log_files": """
        query ListLogFiles {
          logFiles { name path size modifiedAt }
        }
    """,
    "logs": """
        query GetLogContent($path: String!, $lines: Int) {
          logFile(path: $path, lines: $lines) {
            path content totalLines startLine
          }
        }
    """,
}

ALL_ACTIONS = set(QUERIES)

STORAGE_ACTIONS = Literal[
    "shares",
    "disks",
    "disk_details",
    "unassigned",
    "log_files",
    "logs",
]


def register_storage_tool(mcp: FastMCP) -> None:
    """Register the unraid_storage tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_storage(
        action: STORAGE_ACTIONS,
        disk_id: str | None = None,
        log_path: str | None = None,
        tail_lines: int = 100,
    ) -> dict[str, Any]:
        """Manage Unraid storage, disks, and logs.

        Actions:
          shares - List all user shares with capacity info
          disks - List all physical disks
          disk_details - Detailed SMART info for a disk (requires disk_id)
          unassigned - List unassigned devices
          log_files - List available log files
          logs - Retrieve log content (requires log_path, optional tail_lines)
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action == "disk_details" and not disk_id:
            raise ToolError("disk_id is required for 'disk_details' action")

        if tail_lines < 1 or tail_lines > _MAX_TAIL_LINES:
            raise ToolError(f"tail_lines must be between 1 and {_MAX_TAIL_LINES}, got {tail_lines}")

        if action == "logs":
            if not log_path:
                raise ToolError("log_path is required for 'logs' action")
            # Resolve path synchronously to prevent traversal attacks.
            # Using os.path.realpath instead of anyio.Path.resolve() because the
            # async variant blocks on NFS-mounted paths under /mnt/ (Perf-AI-1).
            normalized = os.path.realpath(log_path)  # noqa: ASYNC240
            if not any(normalized.startswith(p) for p in _ALLOWED_LOG_PREFIXES):
                raise ToolError(
                    f"log_path must start with one of: {', '.join(_ALLOWED_LOG_PREFIXES)}. "
                    f"Use log_files action to discover valid paths."
                )
            log_path = normalized

        query = QUERIES[action]
        variables: dict[str, Any] | None = None
        custom_timeout = DISK_TIMEOUT if action in ("disks", "disk_details") else None

        if action == "disk_details":
            variables = {"id": disk_id}
        elif action == "logs":
            variables = {"path": log_path, "lines": tail_lines}

        with tool_error_handler("storage", action, logger):
            logger.info(f"Executing unraid_storage action={action}")
            data = await make_graphql_request(query, variables, custom_timeout=custom_timeout)

            if action == "shares":
                return {"shares": data.get("shares", [])}

            if action == "disks":
                return {"disks": data.get("disks", [])}

            if action == "disk_details":
                raw = data.get("disk", {})
                if not raw:
                    raise ToolError(f"Disk '{disk_id}' not found")
                summary = {
                    "disk_id": raw.get("id"),
                    "device": raw.get("device"),
                    "name": raw.get("name"),
                    "serial_number": raw.get("serialNum"),
                    "size_formatted": format_bytes(raw.get("size")),
                    "temperature": (
                        f"{raw['temperature']}\u00b0C"
                        if raw.get("temperature") is not None
                        else "N/A"
                    ),
                }
                return {"summary": summary, "details": raw}

            if action == "unassigned":
                return {"devices": data.get("unassignedDevices", [])}

            if action == "log_files":
                return {"log_files": data.get("logFiles", [])}

            if action == "logs":
                return dict(data.get("logFile") or {})

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Storage tool registered successfully")
