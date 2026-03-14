"""Logging configuration for Unraid MCP Server.

This module sets up structured logging with Rich console and overwrite file handlers
that cap at 10MB and start over (no rotation) for consistent use across all modules.
"""

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


try:
    from fastmcp.utilities.logging import get_logger as get_fastmcp_logger

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

from .settings import LOG_FILE_PATH, LOG_LEVEL_STR


# Global Rich console for consistent formatting
console = Console(stderr=True)


class OverwriteFileHandler(logging.FileHandler):
    """Custom file handler that overwrites the log file when it reaches max size."""

    def __init__(self, filename, max_bytes=10 * 1024 * 1024, mode="a", encoding=None, delay=False):
        """Initialize the handler.

        Args:
            filename: Path to the log file
            max_bytes: Maximum file size in bytes before overwriting (default: 10MB)
            mode: File open mode
            encoding: File encoding
            delay: Whether to delay file opening
        """
        self.max_bytes = max_bytes
        self._emit_count = 0
        self._check_interval = 100
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        """Emit a record, checking file size periodically and overwriting if needed."""
        self._emit_count += 1
        if (
            (self._emit_count == 1 or self._emit_count % self._check_interval == 0)
            and self.stream
            and hasattr(self.stream, "name")
        ):
            try:
                base_path = Path(self.baseFilename)
                file_size = base_path.stat().st_size if base_path.exists() else 0
                if file_size >= self.max_bytes:
                    old_stream = self.stream
                    self.stream = None
                    try:
                        old_stream.close()
                        base_path.unlink(missing_ok=True)
                        self.stream = self._open()
                    except OSError:
                        # Recovery: attempt to reopen even if unlink failed
                        try:
                            self.stream = self._open()
                        except OSError:
                            # old_stream is already closed — do NOT restore it.
                            # Leave self.stream = None so super().emit() skips output
                            # rather than writing to a closed file descriptor.
                            import sys

                            print(
                                "WARNING: Failed to reopen log file after rotation. "
                                "File logging suspended until next successful open.",
                                file=sys.stderr,
                            )

                    if self.stream is not None:
                        reset_record = logging.LogRecord(
                            name="UnraidMCPServer.Logging",
                            level=logging.INFO,
                            pathname="",
                            lineno=0,
                            msg="=== LOG FILE RESET (10MB limit reached) ===",
                            args=(),
                            exc_info=None,
                        )
                        super().emit(reset_record)

            except OSError as e:
                import sys

                print(
                    f"WARNING: Log file size check failed: {e}. Continuing without rotation.",
                    file=sys.stderr,
                )

        # Emit the original record
        super().emit(record)


def _create_shared_file_handler() -> OverwriteFileHandler:
    """Create the single shared file handler for all loggers.

    Returns:
        Configured OverwriteFileHandler instance
    """
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)
    handler = OverwriteFileHandler(LOG_FILE_PATH, max_bytes=10 * 1024 * 1024, encoding="utf-8")
    handler.setLevel(numeric_log_level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
        )
    )
    return handler


# Single shared file handler — all loggers reuse this instance to avoid
# race conditions from multiple OverwriteFileHandler instances on the same file.
_shared_file_handler = _create_shared_file_handler()


def setup_logger(name: str = "UnraidMCPServer") -> logging.Logger:
    """Set up and configure the logger with console and file handlers.

    Args:
        name: Logger name (defaults to UnraidMCPServer)

    Returns:
        Configured logger instance
    """
    # Get numeric log level
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)

    # Define the logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_log_level)
    logger.propagate = False  # Prevent root logger from duplicating handlers

    # Clear any existing handlers
    logger.handlers.clear()

    # Rich Console Handler for beautiful output
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
    )
    console_handler.setLevel(numeric_log_level)
    logger.addHandler(console_handler)

    # Reuse the shared file handler
    logger.addHandler(_shared_file_handler)

    return logger


def configure_fastmcp_logger_with_rich() -> logging.Logger | None:
    """Configure FastMCP logger to use Rich formatting with Nordic colors."""
    if not FASTMCP_AVAILABLE:
        return None

    # Get numeric log level
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)

    # Get the FastMCP logger
    fastmcp_logger = get_fastmcp_logger("UnraidMCPServer")

    # Clear existing handlers
    fastmcp_logger.handlers.clear()
    fastmcp_logger.propagate = False

    # Rich Console Handler
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True,
    )
    console_handler.setLevel(numeric_log_level)
    fastmcp_logger.addHandler(console_handler)

    # Reuse the shared file handler
    fastmcp_logger.addHandler(_shared_file_handler)

    fastmcp_logger.setLevel(numeric_log_level)

    # Attach shared file handler to the root logger so that library/third-party
    # loggers (httpx, websockets, etc.) whose propagate=True flows up to root
    # will also be written to the log file, not just the console.
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_log_level)
    if _shared_file_handler not in root_logger.handlers:
        root_logger.addHandler(_shared_file_handler)

    return fastmcp_logger


def log_configuration_status(logger: logging.Logger) -> None:
    """Log configuration status at startup.

    Args:
        logger: Logger instance to use for logging
    """
    from .settings import get_config_summary

    logger.info(f"Logging initialized (console and file: {LOG_FILE_PATH}).")

    config = get_config_summary()

    # Log configuration status
    if config["api_url_configured"]:
        logger.info(f"UNRAID_API_URL loaded: {config['api_url_preview']}")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")

    if config["api_key_configured"]:
        logger.info("UNRAID_API_KEY loaded: ****")  # Don't log the key itself
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")

    logger.info(f"UNRAID_MCP_PORT set to: {config['server_port']}")
    logger.info(f"UNRAID_MCP_HOST set to: {config['server_host']}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {config['transport']}")
    logger.info(f"UNRAID_MCP_LOG_LEVEL set to: {config['log_level']}")

    if not config["config_valid"]:
        logger.error(f"Missing required configuration: {config['missing_config']}")


# Global logger instance - modules can import this directly
if FASTMCP_AVAILABLE:
    # Use FastMCP logger with Rich formatting
    _fastmcp_logger = configure_fastmcp_logger_with_rich()
    logger = _fastmcp_logger if _fastmcp_logger is not None else setup_logger()
else:
    # Fallback to our custom logger if FastMCP is not available
    logger = setup_logger()
