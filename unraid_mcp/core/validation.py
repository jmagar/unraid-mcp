"""Shared input validation constants and helpers for tool domain handlers.

Centralises validation rules used across multiple domain handlers (e.g.
_rclone.py, _setting.py) so they share a single source of truth.
"""

import re


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
