"""Shared input validation constants and helpers for tool domain handlers.

Centralises validation rules used across multiple domain handlers (e.g.
_rclone.py, _setting.py) so they share a single source of truth.
"""

import re
from typing import Any

from .exceptions import ToolError


# Maximum string length for individual config/settings values
MAX_VALUE_LENGTH: int = 4096

# Pattern matching key characters that are disallowed in remote config and
# settings keys. Rejects path traversal (..), path separators, shell
# metacharacters, space (0x20), DEL (0x7F), and control characters (0x00-0x1F).
#
# INTENTIONAL BEHAVIOR CHANGE vs. original _rclone.py pattern:
# This shared pattern adds &, <, >, ', ", #, space (0x20), and DEL (0x7F)
# to the original set. Any rclone remote config key containing those characters
# will now be rejected. This is intentional — those characters are unsafe in
# shell contexts and were never expected in rclone remote names or settings keys.
DANGEROUS_KEY_PATTERN: re.Pattern[str] = re.compile(
    r"\.\.|[/\\;|`$(){}&<>\"'#\x20\x7f]|[\x00-\x1f]"
)


def validate_scalar_mapping(
    data: dict[str, Any],
    label: str,
    *,
    max_keys: int = 100,
    stringify: bool = False,
) -> dict[str, Any]:
    """Validate a flat scalar key-value mapping.

    Enforces key count cap, rejects dangerous key names, accepts only scalar
    values (str, int, float, bool), and enforces MAX_VALUE_LENGTH.

    Args:
        data: The mapping to validate.
        label: Human-readable label for error messages (e.g. "config_data").
        max_keys: Maximum number of keys allowed.
        stringify: If True, convert all values to str (rclone style).
                   If False, preserve original types (settings style).

    Returns:
        Validated mapping with the same or stringified values.
    """
    if len(data) > max_keys:
        raise ToolError(f"{label} has {len(data)} keys (max {max_keys})")
    validated: dict[str, Any] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not key.strip():
            raise ToolError(f"{label} keys must be non-empty strings, got: {type(key).__name__}")
        if DANGEROUS_KEY_PATTERN.search(key):
            raise ToolError(f"{label} key '{key}' contains disallowed characters")
        if not isinstance(value, (str, int, float, bool)):
            raise ToolError(
                f"{label}['{key}'] must be a string, number, or boolean"
                + (f", got: {type(value).__name__}" if not stringify else "")
            )
        str_value = str(value)
        if len(str_value) > MAX_VALUE_LENGTH:
            raise ToolError(
                f"{label}['{key}'] value exceeds max length ({len(str_value)} > {MAX_VALUE_LENGTH})"
            )
        validated[key] = str_value if stringify else value
    return validated
