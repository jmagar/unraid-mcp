"""Shared input validation constants and helpers for tool domain handlers.

Centralises validation rules used across multiple domain handlers (e.g.
_rclone.py, _setting.py) so they share a single source of truth.
"""

import re


# Maximum string length for individual config/settings values
MAX_VALUE_LENGTH: int = 4096

# Pattern matching key characters that are disallowed in remote config and
# settings keys. Rejects path traversal (..), path separators, shell
# metacharacters, and control characters (ASCII < 0x20 including \n, \r, \t).
DANGEROUS_KEY_PATTERN: re.Pattern[str] = re.compile(r"\.\.|[/\\;|`$(){}]|[\x00-\x1f]")
