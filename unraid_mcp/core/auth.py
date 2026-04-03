"""ASGI-level bearer token authentication middleware for HTTP transport.

Pure ASGI ``__call__`` pattern — no BaseHTTPMiddleware — to avoid anyio
stream allocation overhead and to support WebSocket pass-through.

RFC 6750 compliance:
  - Missing header  → 401 WWW-Authenticate: Bearer realm="unraid-mcp"
  - Invalid token   → 401 WWW-Authenticate: Bearer realm="unraid-mcp", error="invalid_token"
  - Rate exceeded   → 429 Retry-After: 60

Also exports:
  - ``HealthMiddleware`` — responds 200 to ``GET /health`` without auth
    so Docker healthchecks work regardless of bearer token configuration.
  - ``WellKnownMiddleware`` — serves RFC 9728 OAuth 2.0 Protected Resource
    Metadata at ``GET /.well-known/oauth-protected-resource`` without auth.
    MCP clients (e.g. Claude Code) probe this URL when they receive a 401 to
    discover how to authenticate.  Returning a valid response stops the cascade
    of 401s and tells the client: "use a pre-shared Bearer token — there is no
    OAuth authorization server."
"""

from __future__ import annotations

import hmac
import re
import time
from collections import deque
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send

# Sanitize client IPs/hostnames before logging to prevent log injection
_SAFE_HOST_RE = re.compile(r"[^A-Za-z0-9.:\-]")

# Per-IP failure rate limiting window
_RATE_WINDOW_SECS = 60.0
_RATE_MAX_FAILURES = 60

# Log throttle: emit at most one warning per IP per this many seconds
_LOG_THROTTLE_SECS = 30.0


class BearerAuthMiddleware:
    """ASGI middleware enforcing bearer token auth on HTTP requests.

    Pass-through scopes:
    - WebSocket (``scope["type"] == "websocket"``) — not an HTTP request.
    - Lifespan (``scope["type"] == "lifespan"``) — startup/shutdown events.
    - All scopes when ``disabled=True`` (UNRAID_MCP_DISABLE_HTTP_AUTH=true).

    Rejected requests receive JSON error bodies per RFC 6750.
    """

    def __init__(self, app: ASGIApp, *, token: str, disabled: bool = False) -> None:
        self.app = app
        # Pre-encode once; hmac.compare_digest works on bytes
        self._token: bytes = token.encode()
        self.disabled = disabled
        # Pre-serialised response bodies (allocated once at startup)
        self._body_401_missing = (
            b'{"error":"unauthorized","error_description":"Authentication required"}'
        )
        self._body_401_invalid = (
            b'{"error":"invalid_token","error_description":"Invalid bearer token"}'
        )
        self._body_429 = (
            b'{"error":"too_many_requests","error_description":"Too many failed auth attempts"}'
        )
        # Per-IP failure timestamps — deque for O(1) append/popleft
        self._ip_failures: dict[str, deque[float]] = {}
        # Per-IP last-warning time for log throttling
        self._ip_last_warn: dict[str, float] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Pass non-HTTP scopes (websocket, lifespan) through unchanged
        if scope["type"] != "http" or self.disabled:
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)

        # Rate-limit check before any token work
        if self._is_rate_limited(client_ip):
            await self._send_response(
                send,
                status=429,
                body=self._body_429,
                extra_headers=[(b"retry-after", b"60")],
            )
            return

        # Extract Authorization header from raw ASGI headers list
        auth_header: bytes | None = None
        for key, val in scope.get("headers", []):
            if key.lower() == b"authorization":
                auth_header = val
                break

        if auth_header is None:
            # No Authorization header at all — prompt client per RFC 6750
            self._record_failure(client_ip)
            self._maybe_warn(client_ip, "missing authorization header")
            await self._send_response(
                send,
                status=401,
                body=self._body_401_missing,
                extra_headers=[(b"www-authenticate", b'Bearer realm="unraid-mcp"')],
            )
            return

        # Headers are latin-1 per RFC 7230; decode before string operations
        auth_str = auth_header.decode("latin-1")
        if not auth_str.lower().startswith("bearer "):
            # Wrong scheme — treat as missing (don't hint that bearer exists)
            self._record_failure(client_ip)
            self._maybe_warn(client_ip, "non-bearer auth scheme")
            await self._send_response(
                send,
                status=401,
                body=self._body_401_missing,
                extra_headers=[(b"www-authenticate", b'Bearer realm="unraid-mcp"')],
            )
            return

        # Extract token from original string (value is verbatim after scheme)
        provided: bytes = auth_str[len("bearer ") :].strip().encode()

        # Constant-time comparison prevents timing side-channel attacks
        if not hmac.compare_digest(provided, self._token):
            self._record_failure(client_ip)
            self._maybe_warn(client_ip, "invalid token")
            await self._send_response(
                send,
                status=401,
                body=self._body_401_invalid,
                extra_headers=[
                    (
                        b"www-authenticate",
                        b'Bearer realm="unraid-mcp", error="invalid_token"',
                    )
                ],
            )
            return

        # Valid token — forward to application
        await self.app(scope, receive, send)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_client_ip(self, scope: Scope) -> str:
        """Extract and sanitize the client IP from the ASGI scope."""
        client = scope.get("client")
        if client and isinstance(client, (list, tuple)) and len(client) >= 1:
            raw = str(client[0])
        else:
            raw = "unknown"
        # Strip anything that could inject newlines or control chars into logs
        return _SAFE_HOST_RE.sub("", raw) or "unknown"

    def _is_rate_limited(self, ip: str) -> bool:
        """Return True if this IP has hit the failure rate limit."""
        if ip not in self._ip_failures:
            return False
        self._prune_ip_state(ip)
        return len(self._ip_failures.get(ip, ())) >= _RATE_MAX_FAILURES

    def _record_failure(self, ip: str) -> None:
        """Record one failed auth attempt for this IP."""
        self._prune_ip_state(ip)
        if ip not in self._ip_failures:
            self._ip_failures[ip] = deque()
        self._ip_failures[ip].append(time.monotonic())

    def _maybe_warn(self, ip: str, reason: str) -> None:
        """Emit a throttled WARNING log for this IP (at most once per 30 s)."""
        # Lazy import to avoid circular at module load time
        from ..config.logging import logger

        now = time.monotonic()
        if now - self._ip_last_warn.get(ip, 0.0) >= _LOG_THROTTLE_SECS:
            self._ip_last_warn[ip] = now
            logger.warning("Bearer auth rejected (%s) from %s", reason, ip)

    def _prune_ip_state(self, ip: str) -> None:
        """Drop stale failure and warning-tracking state for one IP."""
        now = time.monotonic()
        q = self._ip_failures.get(ip)
        if q is not None:
            cutoff = now - _RATE_WINDOW_SECS
            while q and q[0] < cutoff:
                q.popleft()
            if not q:
                self._ip_failures.pop(ip, None)

        last_warn = self._ip_last_warn.get(ip)
        if last_warn is not None and (now - last_warn) >= _RATE_WINDOW_SECS:
            self._ip_last_warn.pop(ip, None)

    @staticmethod
    async def _send_response(
        send: Send,
        *,
        status: int,
        body: bytes,
        extra_headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        """Send a complete HTTP response (start + body)."""
        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ]
        if extra_headers:
            headers.extend(extra_headers)

        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": body, "more_body": False})


class HealthMiddleware:
    """ASGI middleware that responds 200 to GET /health without authentication.

    Place this OUTSIDE BearerAuthMiddleware (first in the middleware list) so it
    intercepts GET /health before auth — no bypass needed in BearerAuthMiddleware.
    Only GET is handled; other methods fall through to the auth layer.
    """

    _BODY: bytes = b'{"status":"ok"}'
    # Tuple-of-tuples: immutable, safe to share across requests.
    # content-length is computed from _BODY so they stay in sync.
    _HEADERS: tuple[tuple[bytes, bytes], ...] = (
        (b"content-type", b"application/json"),
        (b"content-length", str(len(_BODY)).encode()),
    )

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # scope["path"] is always present in ASGI HTTP scopes (required field).
        if scope["type"] == "http" and scope["path"] == "/health" and scope["method"] == "GET":
            await send({"type": "http.response.start", "status": 200, "headers": self._HEADERS})
            await send({"type": "http.response.body", "body": self._BODY, "more_body": False})
            return
        await self.app(scope, receive, send)


class WellKnownMiddleware:
    """ASGI middleware serving RFC 9728 OAuth Protected Resource Metadata.

    MCP clients (e.g. Claude Code) probe ``GET /.well-known/oauth-protected-resource``
    when they receive a 401 from the MCP endpoint — trying to discover an OAuth
    authorization server.  Without a valid response here they cascade into a series
    of failed discovery requests and surface a generic "unknown error" to the user.

    This server does NOT implement OAuth.  Returning the resource metadata with an
    empty ``authorization_servers`` list tells compliant clients: "Bearer auth is
    required; you must configure the token yourself — there is no OAuth flow."

    Place this OUTSIDE BearerAuthMiddleware (before it in the middleware list) so
    the discovery endpoint is reachable without a token.  Only GET is handled for
    the well-known paths; all other requests fall through to the auth layer.
    """

    # Paths defined by RFC 9728 §3.1 that MCP clients probe.
    _WELL_KNOWN_PATHS: frozenset[str] = frozenset(
        {
            "/.well-known/oauth-protected-resource",
            "/.well-known/oauth-protected-resource/mcp",
        }
    )

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")
        method: str = scope.get("method", "").upper()

        if method != "GET" or path not in self._WELL_KNOWN_PATHS:
            await self.app(scope, receive, send)
            return

        # Derive the resource URI from the request Host header (RFC 9728 §2).
        host = "localhost"
        for key, val in scope.get("headers", []):
            if key.lower() == b"host":
                host = val.decode("latin-1")
                break

        scheme = scope.get("scheme", "http")
        resource = f"{scheme}://{host}"

        body: bytes = json.dumps(
            {
                "resource": resource,
                # No authorization_servers → client must use a pre-configured token.
                "bearer_methods_supported": ["header"],
            },
            separators=(",", ":"),
        ).encode()

        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ]
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": body, "more_body": False})
