"""Configuration management for Unraid MCP Server.

This module handles loading environment variables from multiple .env locations
and provides all configuration constants used throughout the application.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from ..version import VERSION as APP_VERSION


# Get the script directory (config module location)
SCRIPT_DIR = Path(__file__).parent  # /home/user/code/unraid-mcp/unraid_mcp/config/
UNRAID_MCP_DIR = SCRIPT_DIR.parent  # /home/user/code/unraid-mcp/unraid_mcp/
PROJECT_ROOT = UNRAID_MCP_DIR.parent  # /home/user/code/unraid-mcp/

# Canonical credentials directory — version-agnostic, survives plugin version bumps.
# Override with UNRAID_CREDENTIALS_DIR env var (useful for containers).
CREDENTIALS_DIR = Path(os.getenv("UNRAID_CREDENTIALS_DIR", str(Path.home() / ".unraid-mcp")))
CREDENTIALS_ENV_PATH = CREDENTIALS_DIR / ".env"

# Load environment variables from .env file
# Priority: canonical ~/.unraid-mcp/.env first, then dev/container fallbacks.
dotenv_paths = [
    CREDENTIALS_ENV_PATH,  # primary — ~/.unraid-mcp/.env (all runtimes)
    CREDENTIALS_DIR / ".env.local",  # only used if ~/.unraid-mcp/.env absent
    Path("/app/.env.local"),  # Docker compat mount
    PROJECT_ROOT / ".env.local",  # dev overrides
    PROJECT_ROOT / ".env",  # dev fallback
    UNRAID_MCP_DIR / ".env",  # last resort
]

for dotenv_path in dotenv_paths:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        break

# Core API Configuration
UNRAID_API_URL = os.getenv("UNRAID_API_URL")
UNRAID_API_KEY = os.getenv("UNRAID_API_KEY")


# Server Configuration
def _parse_port(env_var: str, default: int) -> int:
    """Parse a port number from environment variable with validation."""
    raw = os.getenv(env_var, str(default))
    try:
        port = int(raw)
    except ValueError:
        import sys

        print(f"FATAL: {env_var}={raw!r} is not a valid integer port number", file=sys.stderr)
        sys.exit(1)
    if not (1 <= port <= 65535):
        import sys

        print(f"FATAL: {env_var}={port} outside valid port range 1-65535", file=sys.stderr)
        sys.exit(1)
    return port


UNRAID_MCP_PORT = _parse_port("UNRAID_MCP_PORT", 6970)
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

# Google OAuth Configuration (Optional)
# -------------------------------------
# When set, the MCP HTTP server requires Google login before tool calls.
# UNRAID_MCP_BASE_URL must match the public URL clients use to reach this server.
# Google Cloud Console → Credentials → Authorized redirect URIs:
#   Add: <UNRAID_MCP_BASE_URL>/auth/callback
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
UNRAID_MCP_BASE_URL = os.getenv("UNRAID_MCP_BASE_URL", "")

# JWT signing key for FastMCP OAuth tokens.
# MUST be set to a stable secret so tokens survive server restarts.
# Generate once: python3 -c "import secrets; print(secrets.token_hex(32))"
# Never change this value — all existing tokens will be invalidated.
UNRAID_MCP_JWT_SIGNING_KEY = os.getenv("UNRAID_MCP_JWT_SIGNING_KEY", "")


def is_google_auth_configured() -> bool:
    """Return True when all required Google OAuth vars are present."""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and UNRAID_MCP_BASE_URL)


# Logging Configuration
LOG_LEVEL_STR = os.getenv("UNRAID_MCP_LOG_LEVEL", "INFO").upper()
LOG_FILE_NAME = os.getenv("UNRAID_MCP_LOG_FILE", "unraid-mcp.log")
# Use /.dockerenv as the container indicator for robust Docker detection.
IS_DOCKER = Path("/.dockerenv").exists()
LOGS_DIR = Path("/app/logs") if IS_DOCKER else PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOGS_DIR / LOG_FILE_NAME

# Ensure logs directory exists; if creation fails, fall back to PROJECT_ROOT / ".cache" / "logs".
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    LOGS_DIR = PROJECT_ROOT / ".cache" / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE_PATH = LOGS_DIR / LOG_FILE_NAME

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


def is_configured() -> bool:
    """Return True if both required credentials are present."""
    return bool(UNRAID_API_URL and UNRAID_API_KEY)


def apply_runtime_config(api_url: str, api_key: str) -> None:
    """Update module-level credential globals at runtime (post-elicitation).

    Also sets matching environment variables so submodules that read
    os.getenv() after import see the new values.
    """
    global UNRAID_API_URL, UNRAID_API_KEY
    UNRAID_API_URL = api_url
    UNRAID_API_KEY = api_key
    os.environ["UNRAID_API_URL"] = api_url
    os.environ["UNRAID_API_KEY"] = api_key


def get_config_summary() -> dict[str, Any]:
    """Get a summary of current configuration (safe for logging).

    Returns:
        dict: Configuration summary with sensitive data redacted.
    """
    is_valid, missing = validate_required_config()

    from ..core.utils import safe_display_url

    return {
        "api_url_configured": bool(UNRAID_API_URL),
        "api_url_preview": safe_display_url(UNRAID_API_URL) if UNRAID_API_URL else None,
        "api_key_configured": bool(UNRAID_API_KEY),
        "server_host": UNRAID_MCP_HOST,
        "server_port": UNRAID_MCP_PORT,
        "transport": UNRAID_MCP_TRANSPORT,
        "ssl_verify": UNRAID_VERIFY_SSL,
        "log_level": LOG_LEVEL_STR,
        "log_file": str(LOG_FILE_PATH),
        "config_valid": is_valid,
        "missing_config": missing if not is_valid else None,
        "google_auth_enabled": is_google_auth_configured(),
        "google_auth_base_url": UNRAID_MCP_BASE_URL if is_google_auth_configured() else None,
        "jwt_signing_key_configured": bool(UNRAID_MCP_JWT_SIGNING_KEY),
    }


# Re-export application version from a single source of truth.
VERSION = APP_VERSION
