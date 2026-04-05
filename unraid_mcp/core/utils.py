"""Shared utility functions for Unraid MCP tools."""

from typing import Any
from urllib.parse import urlparse


_MISSING: object = object()


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict keys, handling missing keys and None intermediates.

    Args:
        data: The root dictionary to traverse.
        *keys: Sequence of keys to follow.
        default: Value to return if any key is absent or any intermediate value
            is not a dict.

    Returns:
        The value at the end of the key chain (including explicit ``None``),
        or ``default`` if a key is missing or an intermediate is not a dict.
        This preserves the distinction between ``{"k": None}`` (returns ``None``)
        and ``{}`` (returns ``default``).
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, _MISSING)
        if current is _MISSING:
            return default
    return current


def format_bytes(bytes_value: int | None) -> str:
    """Format byte values into human-readable sizes.

    Args:
        bytes_value: Number of bytes, or None.

    Returns:
        Human-readable string like "1.00 GB" or "N/A" if input is None/invalid.
    """
    if bytes_value is None:
        return "N/A"
    try:
        value = float(int(bytes_value))
    except (ValueError, TypeError):
        return "N/A"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} EB"


def safe_display_url(url: str | None) -> str | None:
    """Return a redacted URL showing only scheme + host + port.

    Strips path, query parameters, credentials, and fragments to avoid
    leaking internal network topology or embedded secrets (CWE-200).
    """
    if not url:
        return None
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "unknown"
        if parsed.port:
            return f"{parsed.scheme}://{host}:{parsed.port}"
        return f"{parsed.scheme}://{host}"
    except ValueError:
        # urlparse raises ValueError for invalid URLs (e.g. contains control chars)
        return "<unparseable>"


def format_kb(k: Any) -> str:
    """Format kilobyte values into human-readable sizes.

    Delegates to :func:`format_bytes` after converting kilobytes to bytes,
    ensuring consistent formatting and full scale coverage (B through EB).

    Args:
        k: Number of kilobytes, or None.

    Returns:
        Human-readable string like "1.00 GB" or "N/A" if input is None/invalid.
    """
    if k is None:
        return "N/A"
    try:
        kb = int(k)
    except (ValueError, TypeError):
        return "N/A"
    return format_bytes(kb * 1024)


def validate_subaction(subaction: str, valid_set: set[str], domain: str) -> None:
    """Raise ToolError if subaction is not in the valid set.

    Args:
        subaction: The subaction string to validate.
        valid_set: Set of valid subaction names.
        domain: The domain name for error messages (e.g. "docker").
    """
    from .exceptions import ToolError

    if subaction not in valid_set:
        raise ToolError(
            f"Invalid subaction '{subaction}' for {domain}. Must be one of: {sorted(valid_set)}"
        )
