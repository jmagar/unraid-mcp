"""Logging configuration for Unraid MCP Server.

This module sets up structured logging with Rich console and overwrite file handlers
that cap at 10MB and start over (no rotation) for consistent use across all modules.
"""

import logging
import os
from datetime import datetime

import pytz
from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

try:
    from fastmcp.utilities.logging import get_logger as get_fastmcp_logger
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

from .settings import LOG_FILE_PATH, LOG_LEVEL_STR

# Global Rich console for consistent formatting
console = Console(stderr=True, force_terminal=True)


class OverwriteFileHandler(logging.FileHandler):
    """Custom file handler that overwrites the log file when it reaches max size."""
    
    def __init__(self, filename, max_bytes=10*1024*1024, mode='a', encoding=None, delay=False):
        """Initialize the handler.
        
        Args:
            filename: Path to the log file
            max_bytes: Maximum file size in bytes before overwriting (default: 10MB)
            mode: File open mode
            encoding: File encoding
            delay: Whether to delay file opening
        """
        self.max_bytes = max_bytes
        super().__init__(filename, mode, encoding, delay)
    
    def emit(self, record):
        """Emit a record, checking file size and overwriting if needed."""
        # Check file size before writing
        if self.stream and hasattr(self.stream, 'name'):
            try:
                if os.path.exists(self.baseFilename):
                    file_size = os.path.getsize(self.baseFilename)
                    if file_size >= self.max_bytes:
                        # Close current stream
                        if self.stream:
                            self.stream.close()
                            self.stream = None
                        
                        # Remove the old file and start fresh
                        if os.path.exists(self.baseFilename):
                            os.remove(self.baseFilename)
                        
                        # Reopen with truncate mode
                        self.stream = self._open()
                        
                        # Log a marker that the file was reset
                        reset_record = logging.LogRecord(
                            name="UnraidMCPServer.Logging",
                            level=logging.INFO,
                            pathname="",
                            lineno=0,
                            msg="=== LOG FILE RESET (10MB limit reached) ===",
                            args=(),
                            exc_info=None
                        )
                        super().emit(reset_record)
                        
            except (OSError, IOError):
                # If there's an issue checking file size, just continue normally
                pass
        
        # Emit the original record
        super().emit(record)


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
        tracebacks_show_locals=True
    )
    console_handler.setLevel(numeric_log_level)
    logger.addHandler(console_handler)

    # File Handler with 10MB cap (overwrites instead of rotating)
    file_handler = OverwriteFileHandler(
        LOG_FILE_PATH,
        max_bytes=10*1024*1024,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

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
        tracebacks_show_locals=True,
        markup=True
    )
    console_handler.setLevel(numeric_log_level)
    fastmcp_logger.addHandler(console_handler)

    # File Handler with 10MB cap (overwrites instead of rotating)
    file_handler = OverwriteFileHandler(
        LOG_FILE_PATH,
        max_bytes=10*1024*1024,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    fastmcp_logger.addHandler(file_handler)

    fastmcp_logger.setLevel(numeric_log_level)

    # Also configure the root logger to catch any other logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.propagate = False

    # Rich Console Handler for root logger
    root_console_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True
    )
    root_console_handler.setLevel(numeric_log_level)
    root_logger.addHandler(root_console_handler)

    # File Handler for root logger with 10MB cap (overwrites instead of rotating)
    root_file_handler = OverwriteFileHandler(
        LOG_FILE_PATH,
        max_bytes=10*1024*1024,
        encoding='utf-8'
    )
    root_file_handler.setLevel(numeric_log_level)
    root_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(root_file_handler)
    root_logger.setLevel(numeric_log_level)

    return fastmcp_logger


def setup_uvicorn_logging() -> logging.Logger | None:
    """Configure uvicorn and other third-party loggers to use Rich formatting."""
    # This function is kept for backward compatibility but now delegates to FastMCP
    return configure_fastmcp_logger_with_rich()


def log_configuration_status(logger: logging.Logger) -> None:
    """Log configuration status at startup.

    Args:
        logger: Logger instance to use for logging
    """
    from .settings import get_config_summary

    logger.info(f"Logging initialized (console and file: {LOG_FILE_PATH}).")

    config = get_config_summary()

    # Log configuration status
    if config['api_url_configured']:
        logger.info(f"UNRAID_API_URL loaded: {config['api_url_preview']}")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")

    if config['api_key_configured']:
        logger.info("UNRAID_API_KEY loaded: ****")  # Don't log the key itself
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")

    logger.info(f"UNRAID_MCP_PORT set to: {config['server_port']}")
    logger.info(f"UNRAID_MCP_HOST set to: {config['server_host']}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {config['transport']}")
    logger.info(f"UNRAID_MCP_LOG_LEVEL set to: {config['log_level']}")

    if not config['config_valid']:
        logger.error(f"Missing required configuration: {config['missing_config']}")


# Development logging helpers for Rich formatting
def get_est_timestamp() -> str:
    """Get current timestamp in EST timezone with YY/MM/DD format."""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    return now.strftime("%y/%m/%d %H:%M:%S")

def log_header(title: str) -> None:
    """Print a beautiful header panel with Nordic blue styling."""
    panel = Panel(
        Align.center(Text(title, style="bold white")),
        style="#5E81AC",  # Nordic blue
        padding=(0, 2),
        border_style="#81A1C1"  # Light Nordic blue
    )
    console.print(panel)

def log_with_level_and_indent(message: str, level: str = "info", indent: int = 0) -> None:
    """Log a message with specific level and indentation."""
    timestamp = get_est_timestamp()
    indent_str = "  " * indent

    # Enhanced Nordic color scheme with more blues
    level_config = {
        "error": {"color": "#BF616A", "icon": "❌", "style": "bold"},      # Nordic red
        "warning": {"color": "#EBCB8B", "icon": "⚠️", "style": ""},       # Nordic yellow
        "success": {"color": "#A3BE8C", "icon": "✅", "style": "bold"},    # Nordic green
        "info": {"color": "#5E81AC", "icon": "ℹ️", "style": "bold"},       # Nordic blue (bold)
        "status": {"color": "#81A1C1", "icon": "🔍", "style": ""},        # Light Nordic blue
        "debug": {"color": "#4C566A", "icon": "🐛", "style": ""},         # Nordic dark gray
    }

    config = level_config.get(level, {"color": "#81A1C1", "icon": "•", "style": ""})  # Default to light Nordic blue

    # Create beautifully formatted text
    text = Text()

    # Timestamp with Nordic blue styling
    text.append(f"[{timestamp}]", style="#81A1C1")  # Light Nordic blue for timestamps
    text.append(" ")

    # Indentation with Nordic blue styling
    if indent > 0:
        text.append(indent_str, style="#81A1C1")

    # Level icon (only for certain levels)
    if level in ["error", "warning", "success"]:
        # Extract emoji from message if it starts with one, to avoid duplication
        if message and len(message) > 0 and ord(message[0]) >= 0x1F600:  # Emoji range
            # Message already has emoji, don't add icon
            pass
        else:
            text.append(f"{config['icon']} ", style=config["color"])

    # Message content
    message_style = f"{config['color']} {config['style']}".strip()
    text.append(message, style=message_style)

    console.print(text)

def log_separator() -> None:
    """Print a beautiful separator line with Nordic blue styling."""
    console.print(Rule(style="#81A1C1"))

# Convenience functions for different log levels
def log_error(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "error", indent)

def log_warning(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "warning", indent)

def log_success(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "success", indent)

def log_info(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "info", indent)

def log_status(message: str, indent: int = 0) -> None:
    log_with_level_and_indent(message, "status", indent)

# Global logger instance - modules can import this directly
if FASTMCP_AVAILABLE:
    # Use FastMCP logger with Rich formatting
    _fastmcp_logger = configure_fastmcp_logger_with_rich()
    if _fastmcp_logger is not None:
        logger = _fastmcp_logger
    else:
        # Fallback to our custom logger if FastMCP configuration fails
        logger = setup_logger()
else:
    # Fallback to our custom logger if FastMCP is not available
    logger = setup_logger()
    # Setup uvicorn logging when module is imported
    setup_uvicorn_logging()
