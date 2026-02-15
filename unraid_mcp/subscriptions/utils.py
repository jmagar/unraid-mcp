"""Shared utilities for the subscription system."""

import ssl as _ssl

from ..config.settings import UNRAID_VERIFY_SSL


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
