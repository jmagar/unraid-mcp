"""Disk domain handler for the Unraid MCP tool.

Covers: shares, disks, disk_details, log_files, logs, flash_backup* (6 subactions).
"""

import os
from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.client import DISK_TIMEOUT
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action
from ..core.utils import format_bytes


# ===========================================================================
# DISK (shares, physical disks, logs, flash backup)
# ===========================================================================

_DISK_QUERIES: dict[str, str] = {
    "shares": "query GetSharesInfo { shares { id name free used size include exclude cache nameOrig comment allocator splitLevel floor cow color luksStatus } }",
    "disks": "query ListPhysicalDisks { disks { id device name } }",
    "disk_details": "query GetDiskDetails($id: PrefixedID!) { disk(id: $id) { id device name serialNum size temperature } }",
    "log_files": "query ListLogFiles { logFiles { name path size modifiedAt } }",
    "logs": "query GetLogContent($path: String!, $lines: Int) { logFile(path: $path, lines: $lines) { path content totalLines startLine } }",
}

_DISK_MUTATIONS: dict[str, str] = {
    "flash_backup": "mutation InitiateFlashBackup($input: InitiateFlashBackupInput!) { initiateFlashBackup(input: $input) { status jobId } }",
}

_DISK_SUBACTIONS: set[str] = set(_DISK_QUERIES) | set(_DISK_MUTATIONS)
_DISK_DESTRUCTIVE: set[str] = {"flash_backup"}
_ALLOWED_LOG_PREFIXES = ("/var/log/", "/boot/logs/")
_MAX_TAIL_LINES = 10_000


def _validate_path(path: str, allowed_prefixes: tuple[str, ...], label: str) -> str:
    """Validate a remote path string for traversal and allowed prefix.

    Uses pure string normalization — no filesystem access. The path is validated
    locally but consumed on the remote Unraid server, so realpath would resolve
    against the wrong filesystem.

    Returns the normalized path. Raises ToolError on any violation.
    """
    if ".." in path:
        raise ToolError(f"{label} must not contain path traversal sequences (../)")
    normalized = os.path.normpath(path)
    if not any(normalized.startswith(p) for p in allowed_prefixes):
        raise ToolError(f"{label} must start with one of: {', '.join(allowed_prefixes)}")
    return normalized


async def _handle_disk(
    subaction: str,
    disk_id: str | None,
    log_path: str | None,
    tail_lines: int,
    remote_name: str | None,
    source_path: str | None,
    destination_path: str | None,
    backup_options: dict[str, Any] | None,
    ctx: Context | None,
    confirm: bool,
) -> dict[str, Any]:
    if subaction not in _DISK_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for disk. Must be one of: {sorted(_DISK_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _DISK_DESTRUCTIVE,
        confirm,
        f"Back up flash drive to **{remote_name}:{destination_path}**. Existing backups will be overwritten.",
    )

    if subaction == "disk_details" and not disk_id:
        raise ToolError("disk_id is required for disk/disk_details")

    if subaction == "logs":
        if tail_lines < 1 or tail_lines > _MAX_TAIL_LINES:
            raise ToolError(f"tail_lines must be between 1 and {_MAX_TAIL_LINES}, got {tail_lines}")
        if not log_path:
            raise ToolError("log_path is required for disk/logs")
        log_path = _validate_path(log_path, _ALLOWED_LOG_PREFIXES, "log_path")

    if subaction == "flash_backup":
        if not remote_name:
            raise ToolError("remote_name is required for disk/flash_backup")
        if not source_path:
            raise ToolError("source_path is required for disk/flash_backup")
        if not destination_path:
            raise ToolError("destination_path is required for disk/flash_backup")
        # Validate paths — flash backup source must come from /boot/ only
        if ".." in source_path:
            raise ToolError("source_path must not contain path traversal sequences (../)")
        normalized = os.path.normpath(source_path)  # noqa: ASYNC240 — pure string, no I/O
        if not (normalized == "/boot" or normalized.startswith("/boot/")):
            raise ToolError("source_path must start with /boot/ (flash drive only)")
        source_path = normalized
        if ".." in destination_path:
            raise ToolError("destination_path must not contain path traversal sequences (../)")
        input_data: dict[str, Any] = {
            "remoteName": remote_name,
            "sourcePath": source_path,
            "destinationPath": destination_path,
        }
        if backup_options is not None:
            input_data["options"] = backup_options
        with tool_error_handler("disk", subaction, logger):
            logger.info(
                f"Executing unraid action=disk subaction={subaction} remote={remote_name!r} source={source_path!r}"
            )
            data = await _client.make_graphql_request(
                _DISK_MUTATIONS["flash_backup"], {"input": input_data}
            )
            backup = data.get("initiateFlashBackup")
            if not backup:
                raise ToolError("Failed to start flash backup: no confirmation from server")
            return {"success": True, "subaction": "flash_backup", "data": backup}

    custom_timeout = DISK_TIMEOUT if subaction in ("disks", "disk_details") else None
    variables: dict[str, Any] | None = None
    if subaction == "disk_details":
        variables = {"id": disk_id}
    elif subaction == "logs":
        variables = {"path": log_path, "lines": tail_lines}

    with tool_error_handler("disk", subaction, logger):
        logger.info(f"Executing unraid action=disk subaction={subaction}")
        data = await _client.make_graphql_request(
            _DISK_QUERIES[subaction], variables, custom_timeout=custom_timeout
        )

        if subaction == "shares":
            return {"shares": data.get("shares", [])}
        if subaction == "disks":
            return {"disks": data.get("disks", [])}
        if subaction == "disk_details":
            raw = data.get("disk", {})
            if not raw:
                raise ToolError(f"Disk '{disk_id}' not found")
            return {
                "summary": {
                    "disk_id": raw.get("id"),
                    "device": raw.get("device"),
                    "name": raw.get("name"),
                    "serial_number": raw.get("serialNum"),
                    "size_formatted": format_bytes(raw.get("size")),
                    "temperature": f"{raw['temperature']}\u00b0C"
                    if raw.get("temperature") is not None
                    else "N/A",
                },
                "details": raw,
            }
        if subaction == "log_files":
            return {"log_files": data.get("logFiles", [])}
        if subaction == "logs":
            return dict(data.get("logFile") or {})

        raise ToolError(f"Unhandled disk subaction '{subaction}' — this is a bug")
