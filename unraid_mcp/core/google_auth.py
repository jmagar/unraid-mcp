"""Optional Google OAuth authentication for the HTTP transport.

The server's default authentication is a pre-shared bearer token enforced by the
ASGI middleware in :mod:`unraid_mcp.core.auth`. As an alternative, operators can
delegate HTTP authentication to **Google OAuth**: when both
``UNRAID_MCP_GOOGLE_CLIENT_ID`` and ``UNRAID_MCP_GOOGLE_CLIENT_SECRET`` are set,
the server attaches FastMCP's :class:`GoogleProvider` (an OAuth-proxy auth
backend) to the ``FastMCP`` instance, and MCP clients authenticate via the
standard OAuth browser flow instead of sending a static token.

The two mechanisms are mutually exclusive at the HTTP layer: when Google OAuth is
active, ``server.py`` does NOT install ``BearerAuthMiddleware`` /
``WellKnownMiddleware`` (the provider serves its own ``.well-known`` discovery
metadata and gates requests itself). Everything here is gated entirely on
environment variables, so a deployment that sets none of them is byte-for-byte
unchanged.

Token persistence
-----------------
By default the provider keeps issued tokens in memory, so every restart
invalidates existing client sessions (clients transparently re-authenticate). To
persist tokens across restarts WITHOUT standing up Redis, set BOTH
``UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY`` and ``UNRAID_MCP_GOOGLE_ENCRYPTION_KEY``:
tokens are then written under ``UNRAID_MCP_GOOGLE_STORAGE_DIR`` (default
``~/.unraid-mcp/oauth-tokens``) through a ``FileTreeStore`` wrapped in a
``FernetEncryptionWrapper`` so they are encrypted at rest. Setting only one of the
two keys is a configuration error — encrypted persistence needs both.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..config import settings as _settings
from ..config.logging import logger
from ..config.settings import CREDENTIALS_DIR


if TYPE_CHECKING:
    from fastmcp.server.auth.providers.google import GoogleProvider
    from key_value.aio.protocols.key_value import AsyncKeyValue


# Default scopes match the FastMCP Google integration guide: an OpenID Connect
# login plus the user's email address.
_DEFAULT_SCOPES: tuple[str, ...] = (
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
)


class GoogleOAuthConfigError(RuntimeError):
    """Raised when Google OAuth env vars are present but invalid or incomplete.

    ``server.py`` catches this at import time and converts it to a fatal startup
    error (``sys.exit(1)``), mirroring the other fail-closed config guards.
    """


def google_oauth_enabled() -> bool:
    """Return True when Google OAuth should replace the bearer-token auth.

    The gate is the presence of BOTH the client id and secret. Empty strings are
    normalised to ``None`` upstream (see ``Settings._empty_to_none``), so an
    unset plugin option cannot accidentally enable OAuth.
    """
    return bool(
        (_settings.UNRAID_MCP_GOOGLE_CLIENT_ID or "").strip()
        and (_settings.UNRAID_MCP_GOOGLE_CLIENT_SECRET or "").strip()
    )


def _parse_scopes(raw: str | None) -> list[str]:
    """Split a comma/space-separated scope string, falling back to the defaults."""
    if not raw or not raw.strip():
        return list(_DEFAULT_SCOPES)
    parts = [scope.strip() for chunk in raw.split(",") for scope in chunk.split() if scope.strip()]
    return parts or list(_DEFAULT_SCOPES)


def _storage_dir() -> Path:
    """Resolve the directory used for persisted encrypted OAuth tokens."""
    configured = (_settings.UNRAID_MCP_GOOGLE_STORAGE_DIR or "").strip()
    if configured:
        return Path(configured).expanduser()
    return CREDENTIALS_DIR / "oauth-tokens"


def _build_encrypted_storage(encryption_key: str) -> AsyncKeyValue:
    """Build a disk-backed, Fernet-encrypted key-value store for OAuth tokens.

    Uses ``FileTreeStore`` (no external services — plain files on disk) wrapped in
    ``FernetEncryptionWrapper`` so token values are encrypted at rest. The storage
    directory is created with ``0o700`` permissions since it holds sensitive
    material even after encryption.
    """
    # Imported lazily so the module (and the whole server) loads fine when the
    # optional persistence path is unused.
    from cryptography.fernet import Fernet
    from key_value.aio.stores.filetree import (
        FileTreeStore,
        FileTreeV1CollectionSanitizationStrategy,
        FileTreeV1KeySanitizationStrategy,
    )
    from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

    try:
        fernet = Fernet(encryption_key.encode())
    except (ValueError, TypeError) as exc:
        raise GoogleOAuthConfigError(
            "UNRAID_MCP_GOOGLE_ENCRYPTION_KEY is not a valid Fernet key. Generate one with:\n"
            '  python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"'
        ) from exc

    storage_dir = _storage_dir()
    storage_dir.mkdir(parents=True, exist_ok=True)
    try:
        storage_dir.chmod(0o700)
    except OSError:
        logger.debug("Could not chmod %s (volume mount?) — skipping", storage_dir)

    store = FileTreeStore(
        data_directory=storage_dir,
        key_sanitization_strategy=FileTreeV1KeySanitizationStrategy(storage_dir),
        collection_sanitization_strategy=FileTreeV1CollectionSanitizationStrategy(storage_dir),
    )
    return FernetEncryptionWrapper(key_value=store, fernet=fernet)


def build_google_provider() -> GoogleProvider | None:
    """Construct the Google OAuth provider from the environment, or ``None``.

    Returns ``None`` when Google OAuth is not enabled (the default), leaving the
    bearer-token path untouched. When enabled, raises :class:`GoogleOAuthConfigError`
    on any misconfiguration (missing base URL, partial persistence config, or an
    invalid Fernet key) so startup fails closed with an actionable message.
    """
    if not google_oauth_enabled():
        return None

    from fastmcp.server.auth.providers.google import GoogleProvider

    client_id = (_settings.UNRAID_MCP_GOOGLE_CLIENT_ID or "").strip()
    client_secret = (_settings.UNRAID_MCP_GOOGLE_CLIENT_SECRET or "").strip()

    base_url = (_settings.UNRAID_MCP_GOOGLE_BASE_URL or "").strip()
    if not base_url:
        raise GoogleOAuthConfigError(
            "Google OAuth is enabled (UNRAID_MCP_GOOGLE_CLIENT_ID/SECRET are set) but "
            "UNRAID_MCP_GOOGLE_BASE_URL is not. Set it to this server's public base URL "
            "(e.g. https://unraid-mcp.example.com) — it must match the Authorized redirect "
            "URI configured for the OAuth client in Google Cloud."
        )

    scopes = _parse_scopes(_settings.UNRAID_MCP_GOOGLE_REQUIRED_SCOPES)
    redirect_path = (_settings.UNRAID_MCP_GOOGLE_REDIRECT_PATH or "").strip() or None

    jwt_signing_key = _settings.UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY
    encryption_key = _settings.UNRAID_MCP_GOOGLE_ENCRYPTION_KEY
    client_storage: AsyncKeyValue | None = None
    if jwt_signing_key or encryption_key:
        if not (jwt_signing_key and encryption_key):
            raise GoogleOAuthConfigError(
                "Encrypted token persistence requires BOTH "
                "UNRAID_MCP_GOOGLE_JWT_SIGNING_KEY and UNRAID_MCP_GOOGLE_ENCRYPTION_KEY. "
                "Set both to persist tokens across restarts, or neither to keep them in "
                "memory (cleared on restart)."
            )
        client_storage = _build_encrypted_storage(encryption_key)

    # Pass every optional argument explicitly. ``redirect_path=None`` selects the
    # provider's default ("/auth/callback"); ``client_storage``/``jwt_signing_key``
    # are both None unless encrypted persistence was configured above (enforced
    # both-or-neither), so passing them directly is safe.
    provider = GoogleProvider(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url,
        required_scopes=scopes,
        redirect_path=redirect_path,
        client_storage=client_storage,
        jwt_signing_key=jwt_signing_key,
    )

    logger.info(
        "Google OAuth enabled (base_url=%s, scopes=%s, redirect_path=%s, persistence=%s)",
        base_url,
        ",".join(scopes),
        redirect_path or "/auth/callback",
        "encrypted-filetree" if client_storage is not None else "in-memory",
    )
    return provider
