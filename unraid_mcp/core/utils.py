"""Shared utility functions for Unraid MCP tools."""

from typing import Any
from urllib.parse import urlparse


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict keys, handling None intermediates.

    Args:
        data: The root dictionary to traverse.
        *keys: Sequence of keys to follow.
        default: Value to return if any key is missing or None.

    Returns:
        The value at the end of the key chain, or default if unreachable.
        Explicit ``None`` values at the final key also return ``default``.
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


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

    Args:
        k: Number of kilobytes, or None.

    Returns:
        Human-readable string like "1.00 GB" or "N/A" if input is None/invalid.
    """
    if k is None:
        return "N/A"
    try:
        k = int(k)
    except (ValueError, TypeError):
        return "N/A"
    if k >= 1024 * 1024 * 1024:
        return f"{k / (1024 * 1024 * 1024):.2f} TB"
    if k >= 1024 * 1024:
        return f"{k / (1024 * 1024):.2f} GB"
    if k >= 1024:
        return f"{k / 1024:.2f} MB"
    return f"{k:.2f} KB"
