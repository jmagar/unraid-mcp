"""Tests for shared input validation constants in unraid_mcp.core.validation."""

import pytest

from unraid_mcp.core.validation import DANGEROUS_KEY_PATTERN


class TestDangerousKeyPattern:
    """DANGEROUS_KEY_PATTERN should block all documented dangerous characters."""

    @pytest.mark.parametrize(
        "char",
        [
            "&",
            "<",
            ">",
            "'",
            '"',
            "#",
            " ",  # space (0x20)
            "\x7f",  # DEL
            "\x00",  # null
            "\x1f",  # control character
            "..",  # path traversal sequence
            "/",
            "\\",
            ";",
            "|",
            "`",
            "$",
            "(",
            ")",
            "{",
            "}",
        ],
    )
    def test_dangerous_chars_match(self, char: str) -> None:
        """Each documented dangerous character or sequence must match the pattern."""
        assert DANGEROUS_KEY_PATTERN.search(char), (
            f"Expected DANGEROUS_KEY_PATTERN to match {char!r} but it did not"
        )

    @pytest.mark.parametrize(
        "key",
        [
            "my_remote",
            "gdrive",
            "s3-backup",
            "UNRAID_API_URL",
            "setting123",
            "CamelCase",
        ],
    )
    def test_safe_keys_do_not_match(self, key: str) -> None:
        """Alphanumeric keys with underscores/hyphens should NOT match."""
        assert not DANGEROUS_KEY_PATTERN.search(key), (
            f"Expected DANGEROUS_KEY_PATTERN NOT to match {key!r} but it did"
        )
