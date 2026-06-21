"""Configuration management for Unraid MCP Server.

This module handles loading environment variables from multiple .env locations
and provides all configuration constants used throughout the application.

The simple, type-coercible environment variables are modelled declaratively with
a :class:`pydantic_settings.BaseSettings` subclass (``Settings``). The subtle,
security-relevant behaviours that pydantic-settings does not cover natively are
retained as hand-written code that runs at import time:

* multi-location ``.env`` discovery with the canonical ``~/.unraid-mcp/.env``
  taking priority (``_load_env_files``);
* refusal to load a *symlinked* env file (CWE-22 / symlink-attack guard);
* the issue-#28 fix where an empty-string credential env var must NOT shadow the
  value coming from a ``.env`` file;
* the fatal ``sys.exit(1)`` startup guards for ports and the
  ``UNRAID_VERIFY_SSL`` / ``UNRAID_ALLOW_INSECURE_TLS`` (S-H1) interaction.

Every name this module historically exported is re-exported, unchanged, at the
end of the file so existing imports (``from ..config.settings import X`` and
``_settings.X``) keep working with identical types and values.
"""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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

# Truthy tokens used for boolean env coercion. This intentionally matches the
# historical hand-rolled ``raw in ("true", "1", "yes")`` behaviour rather than
# pydantic's broader default bool parsing (which also accepts "on"/"off"/"f"…).
_BOOL_TRUE_TOKENS = ("true", "1", "yes")


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


class Settings(BaseSettings):
    """Declarative model for the simple, type-coercible Unraid MCP env vars.

    Only the straightforward variables live here. The ``UNRAID_VERIFY_SSL`` union
    (bool-or-CA-path) plus its S-H1 fatal guard are resolved separately at module
    level because the guard's ``sys.exit(1)`` depends on cross-field state and is
    clearer kept inline.

    Field aliases are the exact env-var names; ``populate_by_name`` lets tests and
    callers construct the model with either the field name or the env-var alias.
    """

    model_config = SettingsConfigDict(
        populate_by_name=True,
        extra="ignore",
        case_sensitive=True,
    )

    # Core API Configuration. None when absent (mirrors os.getenv()).
    unraid_api_url: str | None = Field(default=None, alias="UNRAID_API_URL")
    unraid_api_key: str | None = Field(default=None, alias="UNRAID_API_KEY")

    # Server Configuration
    unraid_mcp_port: int = Field(default=6970, alias="UNRAID_MCP_PORT")
    unraid_mcp_host: str = Field(default="0.0.0.0", alias="UNRAID_MCP_HOST")  # noqa: S104
    unraid_mcp_transport: str = Field(default="streamable-http", alias="UNRAID_MCP_TRANSPORT")

    # Maximum serialized tool-response size in bytes. Responses larger than this are
    # replaced with a structured, still-parseable truncation marker (see
    # core/response_limit.py) rather than hard-cut mid-JSON. Default 40 KB (~10K
    # tokens) keeps a single response a small fraction of the client context window;
    # the per-list cap_list defaults do the primary bounding, this is the backstop.
    unraid_mcp_max_response_bytes: int = Field(default=40000, alias="UNRAID_MCP_MAX_RESPONSE_BYTES")

    # HTTP Authentication
    # Bearer token for HTTP transport (streamable-http / sse).
    # Auto-generated on first HTTP startup if absent; written to CREDENTIALS_ENV_PATH.
    # Set UNRAID_MCP_DISABLE_HTTP_AUTH=true only when an upstream gateway handles auth.
    unraid_mcp_bearer_token: str | None = Field(default=None, alias="UNRAID_MCP_BEARER_TOKEN")
    unraid_mcp_disable_http_auth: bool = Field(default=False, alias="UNRAID_MCP_DISABLE_HTTP_AUTH")

    # Affirms that a trusted reverse proxy (e.g. SWAG) fronts this server and enforces
    # authentication. Required when UNRAID_MCP_DISABLE_HTTP_AUTH=true AND the bind host is
    # not loopback — otherwise the server would expose an unauthenticated MCP endpoint on a
    # public/LAN interface (finding S-H3). The documented topology runs behind SWAG, so the
    # operator must explicitly opt in to that arrangement; leaving it false fails closed.
    unraid_mcp_trust_proxy: bool = Field(default=False, alias="UNRAID_MCP_TRUST_PROXY")

    # SSL Configuration — second explicit opt-in gating disabled TLS verification (S-H1).
    unraid_allow_insecure_tls: bool = Field(default=False, alias="UNRAID_ALLOW_INSECURE_TLS")

    # Raw UNRAID_VERIFY_SSL string; resolved to bool|str (CA-bundle path) below.
    raw_verify_ssl: str = Field(default="true", alias="UNRAID_VERIFY_SSL")

    # Logging Configuration
    log_level_str: str = Field(default="INFO", alias="UNRAID_MCP_LOG_LEVEL")
    log_file_name: str = Field(default="unraid-mcp.log", alias="UNRAID_MCP_LOG_FILE")

    # -- validators -----------------------------------------------------------

    @field_validator("unraid_api_url", "unraid_api_key", "unraid_mcp_bearer_token", mode="before")
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        """Mirror ``os.getenv(...) or None`` — empty string becomes None."""
        if value == "":
            return None
        return value

    @field_validator("unraid_mcp_port", mode="before")
    @classmethod
    def _parse_port(cls, value: object) -> int:
        """Parse + validate a port number, exiting fatally on bad input.

        Mirrors the original ``_parse_port`` helper: a non-integer or
        out-of-range value is a fatal startup error (``sys.exit(1)``), not a
        silent fallback.
        """
        raw = str(value)
        try:
            port = int(raw)
        except ValueError:
            print(
                f"FATAL: UNRAID_MCP_PORT={raw!r} is not a valid integer port number",
                file=sys.stderr,
            )
            sys.exit(1)
        if not (1 <= port <= 65535):
            print(
                f"FATAL: UNRAID_MCP_PORT={port} outside valid port range 1-65535",
                file=sys.stderr,
            )
            sys.exit(1)
        return port

    @field_validator("unraid_mcp_max_response_bytes", mode="before")
    @classmethod
    def _parse_positive_int(cls, value: object) -> int:
        """Parse a positive integer, falling back to the default on error.

        Mirrors the original ``_parse_positive_int`` helper: bad / non-positive
        values emit a WARNING and fall back rather than aborting startup.
        """
        default = 40000
        if value is None:
            return default
        raw = value if isinstance(value, int) else str(value)
        if isinstance(raw, str) and raw.strip() == "":
            return default
        try:
            parsed = int(raw)
        except ValueError:
            print(
                f"WARNING: UNRAID_MCP_MAX_RESPONSE_BYTES={raw!r} is not a valid integer; "
                f"using default {default}",
                file=sys.stderr,
            )
            return default
        if parsed <= 0:
            print(
                f"WARNING: UNRAID_MCP_MAX_RESPONSE_BYTES={parsed} must be positive; "
                f"using default {default}",
                file=sys.stderr,
            )
            return default
        return parsed

    @field_validator(
        "unraid_mcp_disable_http_auth",
        "unraid_mcp_trust_proxy",
        "unraid_allow_insecure_tls",
        mode="before",
    )
    @classmethod
    def _coerce_bool(cls, value: object) -> bool:
        """Coerce to bool using the historical truthy token set.

        Matches ``raw.lower() in ("true", "1", "yes")`` exactly so behaviour is
        identical to the pre-migration code (and narrower than pydantic's default
        bool parsing).
        """
        if isinstance(value, bool):
            return value
        return str(value).lower() in _BOOL_TRUE_TOKENS

    @field_validator("unraid_mcp_transport", mode="before")
    @classmethod
    def _lower_transport(cls, value: object) -> str:
        return str(value).lower()

    @field_validator("raw_verify_ssl", mode="before")
    @classmethod
    def _lower_verify_ssl(cls, value: object) -> str:
        return str(value).lower()

    @field_validator("log_level_str", mode="before")
    @classmethod
    def _upper_log_level(cls, value: object) -> str:
        return str(value).upper()


_settings = Settings()

# Core API Configuration
# Loaded once at startup from the .env hierarchy / process env. Consumers should
# read the current value via a local import (from ..config import settings as
# _settings; _settings.UNRAID_API_URL), so a future reload picks up the latest
# binding rather than a stale module-import snapshot.
UNRAID_API_URL = _settings.unraid_api_url
UNRAID_API_KEY = _settings.unraid_api_key

# Server Configuration
UNRAID_MCP_PORT = _settings.unraid_mcp_port
UNRAID_MCP_HOST = _settings.unraid_mcp_host
UNRAID_MCP_TRANSPORT = _settings.unraid_mcp_transport

UNRAID_MCP_MAX_RESPONSE_BYTES = _settings.unraid_mcp_max_response_bytes

# HTTP Authentication
UNRAID_MCP_BEARER_TOKEN: str | None = _settings.unraid_mcp_bearer_token
UNRAID_MCP_DISABLE_HTTP_AUTH: bool = _settings.unraid_mcp_disable_http_auth
UNRAID_MCP_TRUST_PROXY: bool = _settings.unraid_mcp_trust_proxy

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
UNRAID_ALLOW_INSECURE_TLS: bool = _settings.unraid_allow_insecure_tls

raw_verify_ssl = _settings.raw_verify_ssl
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
LOG_LEVEL_STR = _settings.log_level_str
LOG_FILE_NAME = _settings.log_file_name
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
