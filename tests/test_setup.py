import pytest

from unraid_mcp.core.exceptions import CredentialsNotConfiguredError, ToolError


def test_credentials_not_configured_error_exists():
    err = CredentialsNotConfiguredError()
    assert str(err) == "Unraid credentials are not configured."


def test_credentials_not_configured_error_is_exception():
    """CredentialsNotConfiguredError must be catchable as a plain Exception."""
    with pytest.raises(Exception):
        raise CredentialsNotConfiguredError()


def test_credentials_not_configured_error_is_not_tool_error():
    """CredentialsNotConfiguredError must NOT be a ToolError — it bypasses MCP protocol error handling."""
    assert not issubclass(CredentialsNotConfiguredError, ToolError)
