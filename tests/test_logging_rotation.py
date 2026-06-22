"""Tests for OverwriteFileHandler's overwrite/reset contract.

These exercise the OBSERVABLE behavior through the public handler API (logging a
record), not private internals: writing enough data crosses the cap, the file is
overwritten (not grown unbounded), and a reset marker is emitted.
"""

import logging
from pathlib import Path

from unraid_mcp.config.logging import OverwriteFileHandler


def _make_handler(path: Path, max_bytes: int) -> OverwriteFileHandler:
    handler = OverwriteFileHandler(path, max_bytes=max_bytes, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    # Force a size check on every emit so tests don't need 100+ records.
    handler._check_interval = 1
    return handler


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_file_overwritten_when_cap_crossed(tmp_path: Path) -> None:
    """Writing past the cap overwrites the file instead of growing it unbounded."""
    log_path = tmp_path / "test.log"
    # Small cap so a handful of records crosses it.
    handler = _make_handler(log_path, max_bytes=200)

    # Each record is ~100 bytes; write well past the cap.
    for _ in range(50):
        handler.emit(_record("X" * 100))
    handler.flush()

    size = log_path.stat().st_size
    # The file must have been overwritten — bounded near the cap, not 50 * ~100 bytes.
    assert size < 50 * 100, f"file grew unbounded: {size} bytes"
    handler.close()


def test_reset_marker_emitted_on_overwrite(tmp_path: Path) -> None:
    """A reset marker line appears in the file after an overwrite occurs."""
    log_path = tmp_path / "test.log"
    handler = _make_handler(log_path, max_bytes=200)

    for _ in range(50):
        handler.emit(_record("Y" * 100))
    handler.flush()

    contents = log_path.read_text(encoding="utf-8")
    assert "LOG FILE RESET" in contents, "reset marker was never written"
    handler.close()


def test_no_overwrite_below_cap(tmp_path: Path) -> None:
    """Staying under the cap leaves the file intact with no reset marker."""
    log_path = tmp_path / "test.log"
    handler = _make_handler(log_path, max_bytes=10 * 1024 * 1024)

    for i in range(20):
        handler.emit(_record(f"line {i}"))
    handler.flush()

    contents = log_path.read_text(encoding="utf-8")
    assert "LOG FILE RESET" not in contents
    assert "line 0" in contents
    assert "line 19" in contents
    handler.close()


def test_seeds_byte_counter_from_existing_file(tmp_path: Path) -> None:
    """An already-large existing file triggers an overwrite on the first emit."""
    log_path = tmp_path / "test.log"
    # Pre-fill the file past the cap before the handler is created.
    log_path.write_text("Z" * 500, encoding="utf-8")

    handler = _make_handler(log_path, max_bytes=200)
    handler.emit(_record("first line after restart"))
    handler.flush()

    contents = log_path.read_text(encoding="utf-8")
    # The pre-existing oversized content must have been discarded.
    assert "Z" * 500 not in contents
    assert "LOG FILE RESET" in contents
    assert "first line after restart" in contents
    handler.close()
