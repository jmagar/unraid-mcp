"""Configuration management for Unraid MCP Server.

This module handles loading environment variables from multiple .env locations
and provides all configuration constants used throughout the application.
"""

import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


# Get the script directory (config module location)
SCRIPT_DIR = Path(__file__).parent  # /home/user/code/unraid-mcp/unraid_mcp/config/
UNRAID_MCP_DIR = SCRIPT_DIR.parent  # /home/user/code/unraid-mcp/unraid_mcp/
PROJECT_ROOT = UNRAID_MCP_DIR.parent  # /home/user/code/unraid-mcp/

# Load environment variables from .env file
# In container: First try /app/.env.local (mounted), then project root .env
dotenv_paths = [
    Path("/app/.env.local"),  # Container mount point
    PROJECT_ROOT / ".env.local",  # Project root .env.local
    PROJECT_ROOT / ".env",  # Project root .env
    UNRAID_MCP_DIR / ".env",  # Local .env in unraid_mcp/
]

for dotenv_path in dotenv_paths:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        break

# Application Version (single source of truth: pyproject.toml)
try:
    VERSION = version("unraid-mcp")
except PackageNotFoundError:
    VERSION = "0.0.0"

# Core API Configuration
UNRAID_API_URL = os.getenv("UNRAID_API_URL")
UNRAID_API_KEY = os.getenv("UNRAID_API_KEY")

# Server Configuration
UNRAID_MCP_PORT = int(os.getenv("UNRAID_MCP_PORT", "6970"))
UNRAID_MCP_HOST = os.getenv("UNRAID_MCP_HOST", "0.0.0.0")  # noqa: S104 — intentional for Docker
UNRAID_MCP_TRANSPORT = os.getenv("UNRAID_MCP_TRANSPORT", "streamable-http").lower()

# SSL Configuration
raw_verify_ssl = os.getenv("UNRAID_VERIFY_SSL", "true").lower()
if raw_verify_ssl in ["false", "0", "no"]:
    UNRAID_VERIFY_SSL: bool | str = False
elif raw_verify_ssl in ["true", "1", "yes"]:
    UNRAID_VERIFY_SSL = True
else:  # Path to CA bundle
    UNRAID_VERIFY_SSL = raw_verify_ssl

# Logging Configuration
LOG_LEVEL_STR = os.getenv("UNRAID_MCP_LOG_LEVEL", "INFO").upper()
LOG_FILE_NAME = os.getenv("UNRAID_MCP_LOG_FILE", "unraid-mcp.log")
# Use /app/logs in Docker, project-relative logs/ directory otherwise
LOGS_DIR = Path("/app/logs") if Path("/app").is_dir() else PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOGS_DIR / LOG_FILE_NAME

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# HTTP Client Configuration
TIMEOUT_CONFIG = {
    "default": 30,
    "disk_operations": 90,  # Longer timeout for SMART data queries
}


def validate_required_config() -> tuple[bool, list[str]]:
    """Validate that required configuration is present.

    Returns:
        bool: True if all required config is present, False otherwise.
    """
    required_vars = [("UNRAID_API_URL", UNRAID_API_URL), ("UNRAID_API_KEY", UNRAID_API_KEY)]

    missing = []
    for name, value in required_vars:
        if not value:
            missing.append(name)

    return len(missing) == 0, missing


def get_config_summary() -> dict[str, Any]:
    """Get a summary of current configuration (safe for logging).

    Returns:
        dict: Configuration summary with sensitive data redacted.
    """
    is_valid, missing = validate_required_config()

    return {
        "api_url_configured": bool(UNRAID_API_URL),
        "api_url_preview": UNRAID_API_URL[:20] + "..." if UNRAID_API_URL else None,
        "api_key_configured": bool(UNRAID_API_KEY),
        "server_host": UNRAID_MCP_HOST,
        "server_port": UNRAID_MCP_PORT,
        "transport": UNRAID_MCP_TRANSPORT,
        "ssl_verify": UNRAID_VERIFY_SSL,
        "log_level": LOG_LEVEL_STR,
        "log_file": str(LOG_FILE_PATH),
        "config_valid": is_valid,
        "missing_config": missing if not is_valid else None,
    }
