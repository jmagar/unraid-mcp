"""Tests for unraid_mcp.core.client — GraphQL client infrastructure."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from unraid_mcp.core.client import (
    DEFAULT_TIMEOUT,
    DISK_TIMEOUT,
    _redact_sensitive,
    is_idempotent_error,
    make_graphql_request,
)
from unraid_mcp.core.exceptions import ToolError


# ---------------------------------------------------------------------------
# is_idempotent_error
# ---------------------------------------------------------------------------


class TestIsIdempotentError:
    """Verify all idempotent error pattern matches."""

    def test_start_already_started(self) -> None:
        assert is_idempotent_error("Container already started", "start") is True

    def test_start_container_already_running(self) -> None:
        assert is_idempotent_error("container already running", "start") is True

    def test_start_http_code_304(self) -> None:
        assert is_idempotent_error("HTTP code 304 - not modified", "start") is True

    def test_stop_already_stopped(self) -> None:
        assert is_idempotent_error("Container already stopped", "stop") is True

    def test_stop_not_running(self) -> None:
        assert is_idempotent_error("container not running", "stop") is True

    def test_stop_http_code_304(self) -> None:
        assert is_idempotent_error("HTTP code 304", "stop") is True

    def test_start_unrelated_error(self) -> None:
        assert is_idempotent_error("permission denied", "start") is False

    def test_stop_unrelated_error(self) -> None:
        assert is_idempotent_error("image not found", "stop") is False

    def test_unknown_operation(self) -> None:
        assert is_idempotent_error("already started", "restart") is False

    def test_case_insensitive(self) -> None:
        assert is_idempotent_error("ALREADY STARTED", "start") is True
        assert is_idempotent_error("ALREADY STOPPED", "stop") is True


# ---------------------------------------------------------------------------
# _redact_sensitive
# ---------------------------------------------------------------------------


class TestRedactSensitive:
    """Verify recursive redaction of sensitive keys."""

    def test_flat_dict(self) -> None:
        data = {"username": "admin", "password": "hunter2", "host": "10.0.0.1"}
        result = _redact_sensitive(data)
        assert result["username"] == "admin"
        assert result["password"] == "***"
        assert result["host"] == "10.0.0.1"

    def test_nested_dict(self) -> None:
        data = {"config": {"apiKey": "abc123", "url": "http://host"}}
        result = _redact_sensitive(data)
        assert result["config"]["apiKey"] == "***"
        assert result["config"]["url"] == "http://host"

    def test_list_of_dicts(self) -> None:
        data = [{"token": "t1"}, {"name": "safe"}]
        result = _redact_sensitive(data)
        assert result[0]["token"] == "***"
        assert result[1]["name"] == "safe"

    def test_deeply_nested(self) -> None:
        data = {"a": {"b": {"c": {"secret": "deep"}}}}
        result = _redact_sensitive(data)
        assert result["a"]["b"]["c"]["secret"] == "***"

    def test_non_dict_passthrough(self) -> None:
        assert _redact_sensitive("plain_string") == "plain_string"
        assert _redact_sensitive(42) == 42
        assert _redact_sensitive(None) is None

    def test_case_insensitive_keys(self) -> None:
        data = {"Password": "p1", "TOKEN": "t1", "ApiKey": "k1", "Secret": "s1", "Key": "x1"}
        result = _redact_sensitive(data)
        for v in result.values():
            assert v == "***"

    def test_compound_key_names(self) -> None:
        """Keys containing sensitive substrings (e.g. 'user_password') are redacted."""
        data = {
            "user_password": "p1",
            "api_key_value": "k1",
            "auth_token_expiry": "t1",
            "client_secret_id": "s1",
            "username": "safe",
            "host": "safe",
        }
        result = _redact_sensitive(data)
        assert result["user_password"] == "***"
        assert result["api_key_value"] == "***"
        assert result["auth_token_expiry"] == "***"
        assert result["client_secret_id"] == "***"
        assert result["username"] == "safe"
        assert result["host"] == "safe"

    def test_mixed_list_content(self) -> None:
        data = [{"key": "val"}, "string", 123, [{"token": "inner"}]]
        result = _redact_sensitive(data)
        assert result[0]["key"] == "***"
        assert result[1] == "string"
        assert result[2] == 123
        assert result[3][0]["token"] == "***"


# ---------------------------------------------------------------------------
# Timeout constants
# ---------------------------------------------------------------------------


class TestTimeoutConstants:
    def test_default_timeout_read(self) -> None:
        assert DEFAULT_TIMEOUT.read == 30.0

    def test_default_timeout_connect(self) -> None:
        assert DEFAULT_TIMEOUT.connect == 5.0

    def test_disk_timeout_read(self) -> None:
        assert DISK_TIMEOUT.read == 90.0

    def test_disk_timeout_connect(self) -> None:
        assert DISK_TIMEOUT.connect == 5.0


# ---------------------------------------------------------------------------
# make_graphql_request — success paths
# ---------------------------------------------------------------------------


class TestMakeGraphQLRequestSuccess:
    """Test successful request paths."""

    @pytest.fixture(autouse=True)
    def _patch_config(self):
        with (
            patch("unraid_mcp.core.client.UNRAID_API_URL", "https://unraid.local/graphql"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "test-key"),
        ):
            yield

    async def test_simple_query(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": {"info": {"os": "Unraid"}}}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request("{ info { os } }")
        assert result == {"info": {"os": "Unraid"}}

    async def test_query_with_variables(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": {"container": {"name": "plex"}}}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request(
                "query ($id: String!) { container(id: $id) { name } }",
                variables={"id": "abc123"},
            )
        assert result == {"container": {"name": "plex"}}
        # Verify variables were passed in the payload
        call_kwargs = mock_client.post.call_args
        assert call_kwargs.kwargs["json"]["variables"] == {"id": "abc123"}

    async def test_custom_timeout_passed(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": {}}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        custom_timeout = httpx.Timeout(10.0, read=90.0)
        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            await make_graphql_request("{ info }", custom_timeout=custom_timeout)
        call_kwargs = mock_client.post.call_args
        assert call_kwargs.kwargs["timeout"] is custom_timeout

    async def test_empty_data_returns_empty_dict(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"data": None}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request("{ info }")
        assert result == {}

    async def test_missing_data_key_returns_empty_dict(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request("{ info }")
        assert result == {}


# ---------------------------------------------------------------------------
# make_graphql_request — error paths
# ---------------------------------------------------------------------------


class TestMakeGraphQLRequestErrors:
    """Test error handling in make_graphql_request."""

    @pytest.fixture(autouse=True)
    def _patch_config(self):
        with (
            patch("unraid_mcp.core.client.UNRAID_API_URL", "https://unraid.local/graphql"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "test-key"),
        ):
            yield

    async def test_missing_api_url(self) -> None:
        with (
            patch("unraid_mcp.core.client.UNRAID_API_URL", ""),
            pytest.raises(ToolError, match="UNRAID_API_URL not configured"),
        ):
            await make_graphql_request("{ info }")

    async def test_missing_api_key(self) -> None:
        with (
            patch("unraid_mcp.core.client.UNRAID_API_KEY", ""),
            pytest.raises(ToolError, match="UNRAID_API_KEY not configured"),
        ):
            await make_graphql_request("{ info }")

    async def test_http_401_error(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        http_error = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="HTTP error 401"),
        ):
            await make_graphql_request("{ info }")

    async def test_http_500_error(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        http_error = httpx.HTTPStatusError(
            "500 Internal Server Error", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="HTTP error 500"),
        ):
            await make_graphql_request("{ info }")

    async def test_http_503_error(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        http_error = httpx.HTTPStatusError(
            "503 Service Unavailable", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="HTTP error 503"),
        ):
            await make_graphql_request("{ info }")

    async def test_network_connection_refused(self) -> None:
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Network connection error"),
        ):
            await make_graphql_request("{ info }")

    async def test_network_timeout(self) -> None:
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ReadTimeout("Read timed out")

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Network connection error"),
        ):
            await make_graphql_request("{ info }")

    async def test_json_decode_error(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Invalid JSON response"),
        ):
            await make_graphql_request("{ info }")


# ---------------------------------------------------------------------------
# make_graphql_request — GraphQL error handling
# ---------------------------------------------------------------------------


class TestGraphQLErrorHandling:
    """Test GraphQL-level error parsing and idempotent handling."""

    @pytest.fixture(autouse=True)
    def _patch_config(self):
        with (
            patch("unraid_mcp.core.client.UNRAID_API_URL", "https://unraid.local/graphql"),
            patch("unraid_mcp.core.client.UNRAID_API_KEY", "test-key"),
        ):
            yield

    async def test_graphql_error_raises_tool_error(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Field 'bogus' not found"}]}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Field 'bogus' not found"),
        ):
            await make_graphql_request("{ bogus }")

    async def test_multiple_graphql_errors_joined(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "errors": [
                {"message": "Error one"},
                {"message": "Error two"},
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Error one; Error two"),
        ):
            await make_graphql_request("{ info }")

    async def test_idempotent_start_returns_success(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Container already running"}]}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request(
                'mutation { docker { start(id: "x") } }',
                operation_context={"operation": "start"},
            )
        assert result["idempotent_success"] is True
        assert result["operation"] == "start"

    async def test_idempotent_stop_returns_success(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Container not running"}]}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("unraid_mcp.core.client.get_http_client", return_value=mock_client):
            result = await make_graphql_request(
                'mutation { docker { stop(id: "x") } }',
                operation_context={"operation": "stop"},
            )
        assert result["idempotent_success"] is True
        assert result["operation"] == "stop"

    async def test_non_idempotent_error_with_context_raises(self) -> None:
        """An error that doesn't match idempotent patterns still raises even with context."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Permission denied"}]}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="Permission denied"),
        ):
            await make_graphql_request(
                'mutation { docker { start(id: "x") } }',
                operation_context={"operation": "start"},
            )

    async def test_graphql_error_without_message_key(self) -> None:
        """Error objects without a 'message' key fall back to str()."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"code": "UNKNOWN", "detail": "something broke"}]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with (
            patch("unraid_mcp.core.client.get_http_client", return_value=mock_client),
            pytest.raises(ToolError, match="GraphQL API error"),
        ):
            await make_graphql_request("{ info }")
