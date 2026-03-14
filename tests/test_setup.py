def test_credentials_not_configured_error_exists():
    from unraid_mcp.core.exceptions import CredentialsNotConfiguredError

    err = CredentialsNotConfiguredError()
    assert str(err) == "Unraid credentials are not configured."


def test_credentials_not_configured_error_is_exception():
    from unraid_mcp.core.exceptions import CredentialsNotConfiguredError

    assert issubclass(CredentialsNotConfiguredError, Exception)
