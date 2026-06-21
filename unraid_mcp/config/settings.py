"""Configuration management for Unraid MCP Server.

This module handles loading environment variables from multiple .env locations
and provides all configuration constants used throughout the application.
"""

import os
import sys
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

# Credential env vars that an empty string must NOT shadow. The bundled
# `.mcp.json` passes `${CLAUDE_PLUGIN_OPTION_UNRAID_API_URL}` (and key), which
# resolves to "" when the plugin option is unset. With load_dotenv's default
# override=False, those empty values would otherwise take precedence over every
# .env on the search path — including the canonical ~/.unraid-mcp/.env — so the
# credentials silently never load. See GitHub issue #28.
_EMPTY_AS_UNSET_KEYS = ("UNRAID_API_URL", "UNRAID_API_KEY")


def _load_env_files() -> None:
    """Load environment variables from the first existing .env on the search path.

    Priority: canonical ~/.unraid-mcp/.env first, then dev/container fallbacks.

    Before loading, empty-string entries for the credential keys are removed from
    os.environ so that ``load_dotenv(override=False)`` can populate them from the
    .env file. A genuinely-set (non-empty) shell export is still respected.
    """
    # Treat empty-string credential env vars as unset (issue #28).
    for key in _EMPTY_AS_UNSET_KEYS:
        if os.environ.get(key, "").strip() == "":
            os.environ.pop(key, None)

    dotenv_paths = [
        CREDENTIALS_ENV_PATH,  # primary — ~/.unraid-mcp/.env (all runtimes)
        CREDENTIALS_DIR / ".env.local",  # only used if ~/.unraid-mcp/.env absent
        Path("/app/.env.local"),  # Docker compat mount
        PROJECT_ROOT / ".env.local",  # dev overrides
        PROJECT_ROOT / ".env",  # dev fallback
        UNRAID_MCP_DIR / ".env",  # last resort
    ]

    for dotenv_path in dotenv_paths:
        if not dotenv_path.exists():
            continue
        # Refuse a symlinked credentials/env file — it holds secrets and a planted
        # symlink could redirect the read to attacker-controlled content (CWE-22).
        # Mirrors the rmcp-template / axon convention.
        if dotenv_path.is_symlink():
            print(
                f"WARNING: refusing to load symlinked env file {dotenv_path} "
                "(potential symlink attack); skipping.",
                file=sys.stderr,
            )
            continue
        load_dotenv(dotenv_path=dotenv_path)
        break


_load_env_files()

# Core API Configuration
# Loaded once at startup from the .env hierarchy / process env. Consumers should
# read the current value via a local import (from ..config import settings as
# _settings; _settings.UNRAID_API_URL), so a future reload picks up the latest
# binding rather than a stale module-import snapshot.
UNRAID_API_URL = os.getenv("UNRAID_API_URL")
UNRAID_API_KEY = os.getenv("UNRAID_API_KEY")


# Server Configuration
def _parse_port(env_var: str, default: int) -> int:
    """Parse a port number from environment variable with validation."""
    raw = os.getenv(env_var, str(default))
    try:
        port = int(raw)
    except ValueError:
        print(f"FATAL: {env_var}={raw!r} is not a valid integer port number", file=sys.stderr)
        sys.exit(1)
    if not (1 <= port <= 65535):
        print(f"FATAL: {env_var}={port} outside valid port range 1-65535", file=sys.stderr)
        sys.exit(1)
    return port


def _parse_positive_int(env_var: str, default: int) -> int:
    """Parse a positive integer from an environment variable, falling back on error."""
    raw = os.getenv(env_var)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        print(
            f"WARNING: {env_var}={raw!r} is not a valid integer; using default {default}",
            file=sys.stderr,
        )
        return default
    if value <= 0:
        print(
            f"WARNING: {env_var}={value} must be positive; using default {default}",
            file=sys.stderr,
        )
        return default
    return value


UNRAID_MCP_PORT = _parse_port("UNRAID_MCP_PORT", 6970)
UNRAID_MCP_HOST = os.getenv("UNRAID_MCP_HOST", "0.0.0.0")  # noqa: S104 — intentional for Docker
UNRAID_MCP_TRANSPORT = os.getenv("UNRAID_MCP_TRANSPORT", "streamable-http").lower()

# Maximum serialized tool-response size in bytes. Responses larger than this are
# replaced with a structured, still-parseable truncation marker (see
# core/response_limit.py) rather than hard-cut mid-JSON. Default 40 KB (~10K
# tokens) keeps a single response a small fraction of the client context window;
# the per-list cap_list defaults do the primary bounding, this is the backstop.
UNRAID_MCP_MAX_RESPONSE_BYTES = _parse_positive_int("UNRAID_MCP_MAX_RESPONSE_BYTES", 40000)

# HTTP Authentication
# Bearer token for HTTP transport (streamable-http / sse).
# Auto-generated on first HTTP startup if absent; written to CREDENTIALS_ENV_PATH.
# Set UNRAID_MCP_DISABLE_HTTP_AUTH=true only when an upstream gateway handles auth.
UNRAID_MCP_BEARER_TOKEN: str | None = os.getenv("UNRAID_MCP_BEARER_TOKEN") or None
_raw_disable_auth = os.getenv("UNRAID_MCP_DISABLE_HTTP_AUTH", "false").lower()
UNRAID_MCP_DISABLE_HTTP_AUTH: bool = _raw_disable_auth in ("true", "1", "yes")

# Affirms that a trusted reverse proxy (e.g. SWAG) fronts this server and enforces
# authentication. Required when UNRAID_MCP_DISABLE_HTTP_AUTH=true AND the bind host is
# not loopback — otherwise the server would expose an unauthenticated MCP endpoint on a
# public/LAN interface. The documented topology runs behind SWAG, so the operator must
# explicitly opt in to that arrangement.
_raw_trust_proxy = os.getenv("UNRAID_MCP_TRUST_PROXY", "false").lower()
UNRAID_MCP_TRUST_PROXY: bool = _raw_trust_proxy in ("true", "1", "yes")

# SSL Configuration
# UNRAID_VERIFY_SSL accepts: true/1/yes (verify, default), false/0/no (disable —
# DANGEROUS), or a filesystem path to a CA bundle (the recommended way to trust a
# self-signed cert without disabling verification entirely).
#
# Disabling verification is gated behind a SECOND explicit opt-in
# (UNRAID_ALLOW_INSECURE_TLS=true). With verification off, the API key is sent to an
# unverified peer over BOTH the httpx GraphQL client AND the WebSocket subscription
# connection, so a man-in-the-middle can capture it. The CA-bundle path is the safe
# alternative for self-signed certs.
_raw_allow_insecure_tls = os.getenv("UNRAID_ALLOW_INSECURE_TLS", "false").lower()
UNRAID_ALLOW_INSECURE_TLS: bool = _raw_allow_insecure_tls in ("true", "1", "yes")

raw_verify_ssl = os.getenv("UNRAID_VERIFY_SSL", "true").lower()
if raw_verify_ssl in ["false", "0", "no"]:
    if not UNRAID_ALLOW_INSECURE_TLS:
        print(
            "FATAL: UNRAID_VERIFY_SSL is disabled but UNRAID_ALLOW_INSECURE_TLS is not set. "
            "Disabling TLS verification sends the API key to an unverified peer over both the "
            "HTTP and WebSocket connections, exposing it to man-in-the-middle interception. "
            "Prefer pointing UNRAID_VERIFY_SSL at a CA-bundle path to trust a self-signed cert "
            "without disabling verification. To proceed anyway, set "
            "UNRAID_ALLOW_INSECURE_TLS=true.",
            file=sys.stderr,
        )
        sys.exit(1)
    UNRAID_VERIFY_SSL: bool | str = False
elif raw_verify_ssl in ["true", "1", "yes"]:
    UNRAID_VERIFY_SSL = True
else:  # Path to CA bundle
    UNRAID_VERIFY_SSL = raw_verify_ssl

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


def apply_bearer_token(token: str) -> None:
    """Store the generated bearer token in the module global.

    Called by ``ensure_token_exists()`` in server.py after writing the token
    to disk.  We do NOT set os.environ here — the caller is responsible for
    calling ``os.environ.pop("UNRAID_MCP_BEARER_TOKEN", None)`` immediately
    after, so the token is no longer accessible via os.environ.
    """
    global UNRAID_MCP_BEARER_TOKEN
    UNRAID_MCP_BEARER_TOKEN = token


def get_config_summary() -> dict[str, Any]:
    """Get a summary of current configuration (safe for logging).

    Returns:
        dict: Configuration summary with sensitive data redacted.
    """
    is_valid, missing = validate_required_config()

    from ..core.utils import safe_display_url

    is_http = UNRAID_MCP_TRANSPORT in ("streamable-http", "sse")
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
        # Auth fields only meaningful in HTTP mode
        "http_auth_enabled": is_http and not UNRAID_MCP_DISABLE_HTTP_AUTH,
        "http_auth_token_set": bool(UNRAID_MCP_BEARER_TOKEN) if is_http else False,
    }


# Re-export application version from a single source of truth.
VERSION = APP_VERSION
