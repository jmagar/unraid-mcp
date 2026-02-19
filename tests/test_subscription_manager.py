"""Tests for _cap_log_content in subscriptions/manager.py.

_cap_log_content is a pure utility that prevents unbounded memory growth from
log subscription data. It must: return a NEW dict (not mutate), recursively
cap nested 'content' fields, and only truncate when both byte limit and line
limit are exceeded.
"""

from unittest.mock import patch

from unraid_mcp.subscriptions.manager import _cap_log_content


class TestCapLogContentImmutability:
    """The function must return a new dict — never mutate the input."""

    def test_returns_new_dict(self) -> None:
        data = {"key": "value"}
        result = _cap_log_content(data)
        assert result is not data

    def test_input_not_mutated_on_passthrough(self) -> None:
        data = {"content": "short text", "other": "value"}
        original_content = data["content"]
        _cap_log_content(data)
        assert data["content"] == original_content

    def test_input_not_mutated_on_truncation(self) -> None:
        # Use small limits so the truncation path is exercised
        large_content = "\n".join(f"line {i}" for i in range(200))
        data = {"content": large_content}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            _cap_log_content(data)
        # Original data must be unchanged
        assert data["content"] == large_content


class TestCapLogContentSmallData:
    """Content below the byte limit must be returned unchanged."""

    def test_small_content_unchanged(self) -> None:
        data = {"content": "just a few lines\nof log data\n"}
        result = _cap_log_content(data)
        assert result["content"] == data["content"]

    def test_non_content_keys_passed_through(self) -> None:
        data = {"name": "cpu_subscription", "timestamp": "2026-02-18T00:00:00Z"}
        result = _cap_log_content(data)
        assert result == data

    def test_integer_value_passed_through(self) -> None:
        data = {"count": 42, "active": True}
        result = _cap_log_content(data)
        assert result == data


class TestCapLogContentTruncation:
    """Content exceeding both byte AND line limits must be truncated to the last N lines."""

    def test_oversized_content_truncated_and_byte_capped(self) -> None:
        # 200 lines, tiny byte limit: must keep recent content within byte cap.
        lines = [f"line {i}" for i in range(200)]
        data = {"content": "\n".join(lines)}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            result = _cap_log_content(data)
        result_lines = result["content"].splitlines()
        assert len(result["content"].encode("utf-8", errors="replace")) <= 10
        # Must keep the most recent line suffix.
        assert result_lines[-1] == "line 199"

    def test_content_with_fewer_lines_than_limit_still_honors_byte_cap(self) -> None:
        """If byte limit is exceeded, output must still be capped even with few lines."""
        # 30 lines, byte limit 10, line limit 50 -> must cap bytes regardless of line count
        lines = [f"line {i}" for i in range(30)]
        data = {"content": "\n".join(lines)}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            result = _cap_log_content(data)
        assert len(result["content"].encode("utf-8", errors="replace")) <= 10

    def test_non_content_keys_preserved_alongside_truncated_content(self) -> None:
        lines = [f"line {i}" for i in range(200)]
        data = {"content": "\n".join(lines), "path": "/var/log/syslog", "total_lines": 200}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            result = _cap_log_content(data)
        assert result["path"] == "/var/log/syslog"
        assert result["total_lines"] == 200
        assert len(result["content"].encode("utf-8", errors="replace")) <= 10


class TestCapLogContentNested:
    """Nested 'content' fields inside sub-dicts must also be capped recursively."""

    def test_nested_content_field_capped(self) -> None:
        lines = [f"line {i}" for i in range(200)]
        data = {"logFile": {"content": "\n".join(lines), "path": "/var/log/syslog"}}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            result = _cap_log_content(data)
        assert len(result["logFile"]["content"].encode("utf-8", errors="replace")) <= 10
        assert result["logFile"]["path"] == "/var/log/syslog"

    def test_deeply_nested_content_capped(self) -> None:
        lines = [f"line {i}" for i in range(200)]
        data = {"outer": {"inner": {"content": "\n".join(lines)}}}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 50),
        ):
            result = _cap_log_content(data)
        assert len(result["outer"]["inner"]["content"].encode("utf-8", errors="replace")) <= 10

    def test_nested_non_content_keys_unaffected(self) -> None:
        data = {"metrics": {"cpu": 42.5, "memory": 8192}}
        result = _cap_log_content(data)
        assert result == data


class TestCapLogContentSingleMassiveLine:
    """A single line larger than the byte cap must be hard-capped at byte level."""

    def test_single_massive_line_hard_caps_bytes(self) -> None:
        # One line, no newlines, larger than the byte cap.
        # The while-loop can't reduce it (len(lines) == 1), so the
        # last-resort byte-slice path at manager.py:65-69 must fire.
        huge_content = "x" * 200
        data = {"content": huge_content}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 5_000),
        ):
            result = _cap_log_content(data)
        assert len(result["content"].encode("utf-8", errors="replace")) <= 10

    def test_single_massive_line_input_not_mutated(self) -> None:
        huge_content = "x" * 200
        data = {"content": huge_content}
        with (
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_BYTES", 10),
            patch("unraid_mcp.subscriptions.manager._MAX_RESOURCE_DATA_LINES", 5_000),
        ):
            _cap_log_content(data)
        assert data["content"] == huge_content
