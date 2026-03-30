"""Tests for ASGI-level bearer token authentication middleware.

Covers:
  - Pass-through: non-HTTP scopes, disabled=True
  - 401 missing: no Authorization header
  - 401 invalid: wrong token, non-bearer scheme
  - 200 valid: correct token accepted
  - RFC 6750 headers: WWW-Authenticate values differentiate missing vs invalid
  - Per-IP rate limiting: 60 failures → 429
  - os.environ.pop after ensure_token_exists (token not leaked to subprocesses)
  - Startup guard: sys.exit(1) when HTTP + no token + auth not disabled
"""

import asyncio
import os
import time
from unittest.mock import patch

import pytest

from unraid_mcp.core.auth import _RATE_MAX_FAILURES, _RATE_WINDOW_SECS, BearerAuthMiddleware


# ---------------------------------------------------------------------------
# ASGI test helpers
# ---------------------------------------------------------------------------


def _make_http_scope(
    headers: list[tuple[bytes, bytes]] | None = None, client_ip: str = "127.0.0.1"
) -> dict:
    return {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": headers or [],
        "client": (client_ip, 9999),
    }


def _make_ws_scope() -> dict:
    return {"type": "websocket", "path": "/mcp", "headers": [], "client": ("127.0.0.1", 9999)}


def _make_lifespan_scope() -> dict:
    return {"type": "lifespan"}


async def _collect_response(
    middleware: BearerAuthMiddleware, scope: dict
) -> tuple[int, dict[str, str], bytes]:
    """Run middleware and return (status, headers_dict, body)."""
    received: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict):
        received.append(message)

    await middleware(scope, receive, send)

    start = next(m for m in received if m["type"] == "http.response.start")
    body_msg = next(m for m in received if m["type"] == "http.response.body")

    headers = {k.decode(): v.decode() for k, v in start["headers"]}
    return start["status"], headers, body_msg["body"]


async def _noop_send(message):
    pass


async def _noop_receive():
    return {"type": "http.request", "body": b"", "more_body": False}


def _app_called_flag():
    """Return an app callable that sets a flag when called."""
    called = {"value": False}

    async def app(scope, receive, send):
        called["value"] = True
        # Send a minimal 200 so the test can detect it was reached
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    return app, called


# ---------------------------------------------------------------------------
# Pass-through cases
# ---------------------------------------------------------------------------


class TestPassThrough:
    def test_websocket_scope_passes_through(self):
        app, called = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret", disabled=False)
        asyncio.get_event_loop().run_until_complete(mw(_make_ws_scope(), _noop_receive, _noop_send))
        assert called["value"]

    def test_lifespan_scope_passes_through(self):
        app, called = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret", disabled=False)
        asyncio.get_event_loop().run_until_complete(
            mw(_make_lifespan_scope(), _noop_receive, _noop_send)
        )
        assert called["value"]

    def test_disabled_passes_all_http_requests(self):
        app, called = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret", disabled=True)
        scope = _make_http_scope()  # no auth header
        asyncio.get_event_loop().run_until_complete(mw(scope, _noop_receive, _noop_send))
        assert called["value"]


# ---------------------------------------------------------------------------
# 401 cases
# ---------------------------------------------------------------------------


class TestUnauthorized:
    def setup_method(self):
        app, self.called = _app_called_flag()
        self.mw = BearerAuthMiddleware(app, token="correct-token")

    def _run(self, headers=None, ip="10.0.0.1"):
        scope = _make_http_scope(headers=headers, client_ip=ip)
        return asyncio.get_event_loop().run_until_complete(_collect_response(self.mw, scope))

    def test_missing_header_returns_401(self):
        status, headers, body = self._run()
        assert status == 401
        assert not self.called["value"]

    def test_missing_header_includes_www_authenticate_realm(self):
        _, headers, _ = self._run()
        assert headers["www-authenticate"] == 'Bearer realm="unraid-mcp"'

    def test_missing_header_body_is_json_unauthorized(self):
        _, _, body = self._run()
        assert b'"error":"unauthorized"' in body

    def test_wrong_token_returns_401(self):
        status, _, _ = self._run(headers=[(b"authorization", b"Bearer wrong-token")])
        assert status == 401

    def test_wrong_token_www_authenticate_includes_error_param(self):
        _, headers, _ = self._run(headers=[(b"authorization", b"Bearer wrong-token")])
        assert 'error="invalid_token"' in headers["www-authenticate"]

    def test_wrong_token_body_is_json_invalid_token(self):
        _, _, body = self._run(headers=[(b"authorization", b"Bearer wrong-token")])
        assert b'"error":"invalid_token"' in body

    def test_non_bearer_scheme_treated_as_missing(self):
        status, headers, _ = self._run(headers=[(b"authorization", b"Basic dXNlcjpwYXNz")])
        assert status == 401
        # Should show missing-style header (no error="invalid_token")
        assert "invalid_token" not in headers["www-authenticate"]

    def test_case_insensitive_bearer_scheme(self):
        """BEARER and Bearer and bearer are all valid per RFC 6750."""
        for scheme in [b"BEARER correct-token", b"Bearer correct-token", b"bearer correct-token"]:
            app, called = _app_called_flag()
            mw = BearerAuthMiddleware(app, token="correct-token")
            scope = _make_http_scope(headers=[(b"authorization", scheme)])
            asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
            assert called["value"], f"scheme {scheme!r} was rejected but should pass"


# ---------------------------------------------------------------------------
# 200 valid token
# ---------------------------------------------------------------------------


class TestValidToken:
    def test_correct_token_forwards_to_app(self):
        app, called = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="my-secret-token")
        scope = _make_http_scope(headers=[(b"authorization", b"Bearer my-secret-token")])
        status, _, _ = asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
        assert status == 200
        assert called["value"]

    def test_token_with_leading_trailing_spaces_accepted(self):
        """Starlette strips surrounding whitespace from header values; we strip too."""
        app, called = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="tok")
        scope = _make_http_scope(headers=[(b"authorization", b"Bearer  tok ")])
        asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
        assert called["value"]


# ---------------------------------------------------------------------------
# Per-IP rate limiting → 429
# ---------------------------------------------------------------------------


class TestRateLimiting:
    def _hammer(self, mw: BearerAuthMiddleware, ip: str, count: int) -> list[int]:
        statuses = []
        for _ in range(count):
            scope = _make_http_scope(headers=[(b"authorization", b"Bearer wrong")], client_ip=ip)
            status, _, _ = asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
            statuses.append(status)
        return statuses

    def test_below_limit_returns_401_not_429(self):
        app, _ = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret")
        statuses = self._hammer(mw, "192.168.1.1", _RATE_MAX_FAILURES - 1)
        assert all(s == 401 for s in statuses)

    def test_at_limit_returns_429(self):
        app, _ = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret")
        # Hit the limit
        self._hammer(mw, "192.168.2.2", _RATE_MAX_FAILURES)
        # Next request should be 429
        scope = _make_http_scope(
            headers=[(b"authorization", b"Bearer wrong")], client_ip="192.168.2.2"
        )
        status, headers, _ = asyncio.get_event_loop().run_until_complete(
            _collect_response(mw, scope)
        )
        assert status == 429
        assert headers.get("retry-after") == "60"

    def test_different_ips_have_independent_counters(self):
        app, _ = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret")
        # Max out ip A
        self._hammer(mw, "10.0.0.1", _RATE_MAX_FAILURES)
        # ip B should still get 401 (not 429)
        scope = _make_http_scope(
            headers=[(b"authorization", b"Bearer wrong")], client_ip="10.0.0.2"
        )
        status, _, _ = asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
        assert status == 401

    def test_window_expiry_resets_counter(self):
        """After the window expires, the counter resets and 401 is returned again."""
        app, _ = _app_called_flag()
        mw = BearerAuthMiddleware(app, token="secret")
        ip = "172.16.0.1"
        # Inject old failures beyond the window to simulate expiry
        mw._ip_failures[ip] = __import__("collections").deque(
            [time.monotonic() - _RATE_WINDOW_SECS - 1] * _RATE_MAX_FAILURES
        )
        # These are all stale — next request should be 401, not 429
        scope = _make_http_scope(headers=[(b"authorization", b"Bearer wrong")], client_ip=ip)
        status, _, _ = asyncio.get_event_loop().run_until_complete(_collect_response(mw, scope))
        assert status == 401


# ---------------------------------------------------------------------------
# ensure_token_exists + startup guard
# ---------------------------------------------------------------------------


class TestEnsureTokenExists:
    def test_no_op_when_token_already_set(self, tmp_path):
        """ensure_token_exists does nothing when a token is already configured."""
        import unraid_mcp.config.settings as s

        original = s.UNRAID_MCP_BEARER_TOKEN
        try:
            s.UNRAID_MCP_BEARER_TOKEN = "existing-token"
            with patch("unraid_mcp.server.CREDENTIALS_DIR", tmp_path):
                from unraid_mcp.server import ensure_token_exists

                ensure_token_exists()
            # No new file written
            assert not (tmp_path / ".env").exists()
        finally:
            s.UNRAID_MCP_BEARER_TOKEN = original

    def test_no_op_when_auth_disabled(self, tmp_path):
        import unraid_mcp.config.settings as s

        orig_token = s.UNRAID_MCP_BEARER_TOKEN
        orig_disabled = s.UNRAID_MCP_DISABLE_HTTP_AUTH
        try:
            s.UNRAID_MCP_BEARER_TOKEN = None
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = True
            with patch("unraid_mcp.server.CREDENTIALS_DIR", tmp_path):
                from unraid_mcp.server import ensure_token_exists

                ensure_token_exists()
            assert not (tmp_path / ".env").exists()
        finally:
            s.UNRAID_MCP_BEARER_TOKEN = orig_token
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = orig_disabled

    def test_generates_token_when_none_set(self, tmp_path):
        import unraid_mcp.config.settings as s

        orig_token = s.UNRAID_MCP_BEARER_TOKEN
        orig_disabled = s.UNRAID_MCP_DISABLE_HTTP_AUTH
        try:
            s.UNRAID_MCP_BEARER_TOKEN = None
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = False

            env_path = tmp_path / ".env"
            with (
                patch("unraid_mcp.server.CREDENTIALS_DIR", tmp_path),
                patch("unraid_mcp.server.CREDENTIALS_ENV_PATH", env_path),
            ):
                from unraid_mcp.server import ensure_token_exists

                ensure_token_exists()

            # Token written to the module global
            assert s.UNRAID_MCP_BEARER_TOKEN is not None
            assert len(s.UNRAID_MCP_BEARER_TOKEN) > 0

        finally:
            s.UNRAID_MCP_BEARER_TOKEN = orig_token
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = orig_disabled

    def test_token_popped_from_environ_after_generation(self, tmp_path):
        import unraid_mcp.config.settings as s

        orig_token = s.UNRAID_MCP_BEARER_TOKEN
        orig_disabled = s.UNRAID_MCP_DISABLE_HTTP_AUTH
        try:
            s.UNRAID_MCP_BEARER_TOKEN = None
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = False
            # Simulate token being in environ (e.g. set before startup)
            os.environ["UNRAID_MCP_BEARER_TOKEN"] = "should-be-removed"

            env_path = tmp_path / ".env"
            with (
                patch("unraid_mcp.server.CREDENTIALS_DIR", tmp_path),
                patch("unraid_mcp.server.CREDENTIALS_ENV_PATH", env_path),
            ):
                from unraid_mcp.server import ensure_token_exists

                ensure_token_exists()

            assert "UNRAID_MCP_BEARER_TOKEN" not in os.environ
        finally:
            s.UNRAID_MCP_BEARER_TOKEN = orig_token
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = orig_disabled
            os.environ.pop("UNRAID_MCP_BEARER_TOKEN", None)


class TestStartupGuard:
    def test_startup_guard_exits_when_http_no_token_no_disable(self):
        """run_server must sys.exit(1) if HTTP + no token + auth not disabled."""
        import unraid_mcp.config.settings as s

        orig_transport = s.UNRAID_MCP_TRANSPORT
        orig_token = s.UNRAID_MCP_BEARER_TOKEN
        orig_disabled = s.UNRAID_MCP_DISABLE_HTTP_AUTH
        try:
            s.UNRAID_MCP_TRANSPORT = "streamable-http"
            s.UNRAID_MCP_BEARER_TOKEN = None
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = False

            # ensure_token_exists is a no-op when token is None but also we patch it
            with (
                patch("unraid_mcp.server.ensure_token_exists"),
                pytest.raises(SystemExit) as exc_info,
            ):
                from unraid_mcp.server import run_server

                run_server()

            assert exc_info.value.code == 1
        finally:
            s.UNRAID_MCP_TRANSPORT = orig_transport
            s.UNRAID_MCP_BEARER_TOKEN = orig_token
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = orig_disabled

    def test_startup_guard_skipped_when_auth_disabled(self):
        """run_server should NOT exit when DISABLE_HTTP_AUTH=true."""
        import unraid_mcp.config.settings as s

        orig_transport = s.UNRAID_MCP_TRANSPORT
        orig_token = s.UNRAID_MCP_BEARER_TOKEN
        orig_disabled = s.UNRAID_MCP_DISABLE_HTTP_AUTH
        try:
            s.UNRAID_MCP_TRANSPORT = "streamable-http"
            s.UNRAID_MCP_BEARER_TOKEN = None
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = True

            from unraid_mcp.server import mcp as _mcp

            with (
                patch("unraid_mcp.server.ensure_token_exists"),
                patch("unraid_mcp.server.log_configuration_status"),
                patch.object(_mcp, "run"),
            ):
                from unraid_mcp.server import run_server

                # Should NOT raise SystemExit
                run_server()
        finally:
            s.UNRAID_MCP_TRANSPORT = orig_transport
            s.UNRAID_MCP_BEARER_TOKEN = orig_token
            s.UNRAID_MCP_DISABLE_HTTP_AUTH = orig_disabled
