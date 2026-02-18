"""Shared utilities for the subscription system."""

import ssl as _ssl

from ..config.settings import UNRAID_API_URL, UNRAID_VERIFY_SSL


def build_ws_url() -> str:
    """Build a WebSocket URL from the configured UNRAID_API_URL.

    Converts http(s) scheme to ws(s) and ensures /graphql path suffix.

    Returns:
        The WebSocket URL string (e.g. "wss://10.1.0.2:31337/graphql").

    Raises:
        ValueError: If UNRAID_API_URL is not configured.
    """
    if not UNRAID_API_URL:
        raise ValueError("UNRAID_API_URL is not configured")

    if UNRAID_API_URL.startswith("https://"):
        ws_url = "wss://" + UNRAID_API_URL[len("https://") :]
    elif UNRAID_API_URL.startswith("http://"):
        ws_url = "ws://" + UNRAID_API_URL[len("http://") :]
    else:
        ws_url = UNRAID_API_URL

    if not ws_url.endswith("/graphql"):
        ws_url = ws_url.rstrip("/") + "/graphql"

    return ws_url


def build_ws_ssl_context(ws_url: str) -> _ssl.SSLContext | None:
    """Build an SSL context for WebSocket connections when using wss://.

    Args:
        ws_url: The WebSocket URL to connect to.

    Returns:
        An SSLContext configured per UNRAID_VERIFY_SSL, or None for non-TLS URLs.
    """
    if not ws_url.startswith("wss://"):
        return None
    if isinstance(UNRAID_VERIFY_SSL, str):
        return _ssl.create_default_context(cafile=UNRAID_VERIFY_SSL)
    if UNRAID_VERIFY_SSL:
        return _ssl.create_default_context()
    # Explicitly disable verification (equivalent to verify=False)
    ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    return ctx
