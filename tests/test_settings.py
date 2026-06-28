"""Tests for the setting subactions of the consolidated unraid tool."""

import importlib
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.config import settings as settings_module
from unraid_mcp.config.settings import Settings
from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.core.client.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


# ---------------------------------------------------------------------------
# Regression: wrong-domain / mis-named subactions must raise Invalid subaction.
# update_ssh / update_temperature / update_system_time ARE valid setting
# subactions; the Connect-related ones live under the `connect` action, and the
# names below are deliberate near-misses that must NOT resolve under `setting`.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subaction",
    [
        "update_time",  # real name is update_system_time
        "update_api",  # lives under connect as update_api_settings
        "connect_sign_in",  # lives under connect as sign_in
        "connect_sign_out",  # lives under connect as sign_out
        "setup_remote_access",  # lives under connect
        "enable_dynamic_remote_access",  # lives under connect
    ],
)
async def test_removed_settings_subactions_are_invalid(subaction: str) -> None:
    tool_fn = _make_tool()
    with pytest.raises(ToolError, match="Invalid subaction"):
        await tool_fn(action="setting", subaction=subaction)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestSettingsValidation:
    """Tests for subaction validation and destructive guard."""

    async def test_invalid_subaction(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid subaction"):
            await tool_fn(action="setting", subaction="nonexistent_action")

    async def test_destructive_configure_ups_requires_confirm(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action="setting", subaction="configure_ups", ups_config={"mode": "slave"})


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestSettingsUpdate:
    """Tests for update subaction."""

    async def test_update_requires_settings_input(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="settings_input is required"):
            await tool_fn(action="setting", subaction="update")

    async def test_update_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSettings": {"restartRequired": False, "values": {}, "warnings": []}
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="setting", subaction="update", settings_input={"shareCount": 5}
        )
        assert result["success"] is True
        assert result["subaction"] == "update"

    async def test_update_allows_nested_json_values(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSettings": {"restartRequired": False, "values": {}, "warnings": []}
        }
        tool_fn = _make_tool()
        payload = {
            "themeOverrides": {"sidebar": None, "panels": ["cpu", "memory"]},
            "advanced": [1, True, {"nested": "ok"}],
        }
        result = await tool_fn(action="setting", subaction="update", settings_input=payload)
        assert result["success"] is True
        _mock_graphql.assert_awaited_once()
        sent_payload = _mock_graphql.await_args.args[1]["input"]
        assert sent_payload == payload


# ---------------------------------------------------------------------------
# configure_ups
# ---------------------------------------------------------------------------


class TestUpsConfig:
    """Tests for configure_ups subaction."""

    async def test_configure_ups_requires_ups_config(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ups_config is required"):
            await tool_fn(action="setting", subaction="configure_ups", confirm=True)

    async def test_configure_ups_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"configureUps": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="setting",
            subaction="configure_ups",
            confirm=True,
            ups_config={"mode": "master", "cable": "usb"},
        )
        assert result["success"] is True
        assert result["subaction"] == "configure_ups"

    async def test_configure_ups_rejects_nested_values(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="must be a string, number, or boolean"):
            await tool_fn(
                action="setting",
                subaction="configure_ups",
                confirm=True,
                ups_config={"mode": {"nested": "invalid"}},
            )


# ---------------------------------------------------------------------------
# System-config mutations (ssh / temperature / system time / identity)
# ---------------------------------------------------------------------------


class TestSettingsSystemConfig:
    async def test_update_ssh_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="confirm=True"):
            await _make_tool()(
                action="setting",
                subaction="update_ssh",
                config_input={"enabled": True, "port": 22},
            )

    async def test_update_ssh_with_confirm(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateSshSettings": {"id": "vars", "version": "7.3"}}
        result = await _make_tool()(
            action="setting",
            subaction="update_ssh",
            config_input={"enabled": True, "port": 22},
            confirm=True,
        )
        assert result["success"] is True
        assert _mock_graphql.call_args.args[1] == {"input": {"enabled": True, "port": 22}}

    async def test_update_temperature_requires_input(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="config_input is required"):
            await _make_tool()(action="setting", subaction="update_temperature")

    async def test_update_temperature(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateTemperatureConfig": True}
        result = await _make_tool()(
            action="setting",
            subaction="update_temperature",
            config_input={"enabled": True, "default_unit": "CELSIUS"},
        )
        assert result["result"] is True

    async def test_update_system_time_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        # update_system_time is destructive (clock changes break TLS/services).
        with pytest.raises(ToolError, match="confirm=True"):
            await _make_tool()(
                action="setting",
                subaction="update_system_time",
                config_input={"timeZone": "UTC"},
            )

    async def test_update_system_time(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSystemTime": {"currentTime": "x", "timeZone": "UTC", "useNtp": True}
        }
        result = await _make_tool()(
            action="setting",
            subaction="update_system_time",
            config_input={"timeZone": "UTC", "useNtp": True},
            confirm=True,
        )
        assert result["result"]["timeZone"] == "UTC"

    async def test_update_server_identity_requires_name(self, _mock_graphql: AsyncMock) -> None:
        with pytest.raises(ToolError, match="name is required"):
            await _make_tool()(action="setting", subaction="update_server_identity")

    async def test_update_server_identity(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateServerIdentity": {"id": "s", "name": "Tower", "comment": "hi"}
        }
        result = await _make_tool()(
            action="setting",
            subaction="update_server_identity",
            name="Tower",
            comment="hi",
            sys_model="Custom",
        )
        assert result["server"]["name"] == "Tower"
        assert _mock_graphql.call_args.args[1] == {
            "name": "Tower",
            "comment": "hi",
            "sysModel": "Custom",
        }


class TestSettingsSuccessDerivation:
    async def test_update_temperature_false_is_not_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateTemperatureConfig": False}
        result = await _make_tool()(
            action="setting",
            subaction="update_temperature",
            config_input={"enabled": False},
        )
        assert result["success"] is False


class TestSettingsServerIdentitySuccess:
    async def test_update_server_identity_null_is_not_success(
        self, _mock_graphql: AsyncMock
    ) -> None:
        _mock_graphql.return_value = {"updateServerIdentity": None}
        result = await _make_tool()(
            action="setting", subaction="update_server_identity", name="Tower"
        )
        assert result["success"] is False


# ---------------------------------------------------------------------------
# Module-level startup guards (S-H1 SSL fail-closed + port range)
#
# These are security-relevant guards in unraid_mcp/config/settings.py that lost
# direct coverage in the pydantic migration:
#   * the port guard is now the pydantic field validator Settings._parse_port —
#     testable by instantiating Settings(...) directly;
#   * the S-H1 verify-ssl guard is genuinely module-level (it depends on the
#     cross-field UNRAID_VERIFY_SSL / UNRAID_ALLOW_INSECURE_TLS interaction and
#     calls sys.exit(1) after Settings()) — only reachable by re-executing the
#     module, so these tests reload it under a patched os.environ.
# ---------------------------------------------------------------------------


class TestPortGuard:
    """Direct coverage for the Settings._parse_port pydantic field validator."""

    @pytest.mark.parametrize("bad_port", ["abc", "0", "65536"])
    def test_bad_port_exits(self, bad_port: str) -> None:
        # Non-integer or out-of-range (1-65535) ports are a fatal startup error.
        with pytest.raises(SystemExit) as excinfo:
            Settings(UNRAID_MCP_PORT=bad_port)
        assert excinfo.value.code == 1

    def test_valid_port_parsed_to_int(self) -> None:
        settings = Settings(UNRAID_MCP_PORT="8080")
        assert settings.unraid_mcp_port == 8080
        assert isinstance(settings.unraid_mcp_port, int)


class TestGoogleOAuthSettings:
    def test_google_oauth_empty_plugin_values_become_none(self) -> None:
        settings = Settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="",
            UNRAID_MCP_GOOGLE_BASE_URL="",
            UNRAID_MCP_GOOGLE_ALLOWED_EMAILS="",
            UNRAID_MCP_GOOGLE_ALLOWED_DOMAINS="",
            UNRAID_MCP_GOOGLE_STORAGE_DIR="",
        )
        assert settings.unraid_mcp_google_client_id is None
        assert settings.unraid_mcp_google_client_secret is None
        assert settings.unraid_mcp_google_base_url is None
        assert settings.unraid_mcp_google_allowed_emails is None
        assert settings.unraid_mcp_google_allowed_domains is None
        assert settings.unraid_mcp_google_storage_dir is None

    def test_google_oauth_aliases_populate_model(self) -> None:
        settings = Settings(
            UNRAID_MCP_GOOGLE_CLIENT_ID="client",
            UNRAID_MCP_GOOGLE_CLIENT_SECRET="secret",
            UNRAID_MCP_GOOGLE_BASE_URL="https://mcp.example.com",
            UNRAID_MCP_GOOGLE_ALLOWED_EMAILS="owner@example.com",
            UNRAID_MCP_GOOGLE_ALLOWED_DOMAINS="example.com",
            UNRAID_MCP_GOOGLE_ALLOW_ANY_USER=True,
        )
        assert settings.unraid_mcp_google_client_id == "client"
        assert settings.unraid_mcp_google_client_secret == "secret"
        assert settings.unraid_mcp_google_base_url == "https://mcp.example.com"
        assert settings.unraid_mcp_google_allowed_emails == "owner@example.com"
        assert settings.unraid_mcp_google_allowed_domains == "example.com"
        assert settings.unraid_mcp_google_allow_any_user is True


@pytest.fixture
def _reload_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """Reload the settings module under a controlled env, restoring it afterwards.

    The S-H1 guard fires while the module body executes, so it can only be
    exercised by re-importing the module. After the test, reload once more with a
    clean (verify-on) env so the global module state other tests share is left in
    a known-good shape rather than whatever the last test forced.
    """
    # Clear the TLS-related vars so each test starts from a known baseline and
    # only the values it sets are in effect.
    monkeypatch.delenv("UNRAID_VERIFY_SSL", raising=False)
    monkeypatch.delenv("UNRAID_ALLOW_INSECURE_TLS", raising=False)
    try:
        yield
    finally:
        monkeypatch.delenv("UNRAID_VERIFY_SSL", raising=False)
        monkeypatch.delenv("UNRAID_ALLOW_INSECURE_TLS", raising=False)
        importlib.reload(settings_module)


class TestVerifySslGuard:
    """Coverage for the S-H1 SSL fail-closed guard (module-level, cross-field)."""

    @pytest.mark.parametrize("falsey", ["false", "0", "no"])
    def test_disabled_without_opt_in_exits(
        self, _reload_settings: None, monkeypatch: pytest.MonkeyPatch, falsey: str
    ) -> None:
        # Disabling verification without the explicit UNRAID_ALLOW_INSECURE_TLS
        # opt-in must fail closed with sys.exit(1).
        monkeypatch.setenv("UNRAID_VERIFY_SSL", falsey)
        with pytest.raises(SystemExit) as excinfo:
            importlib.reload(settings_module)
        assert excinfo.value.code == 1

    @pytest.mark.parametrize("falsey", ["false", "0", "no"])
    def test_disabled_with_opt_in_allowed(
        self, _reload_settings: None, monkeypatch: pytest.MonkeyPatch, falsey: str
    ) -> None:
        # With the second opt-in present, verification may be disabled: no exit,
        # and UNRAID_VERIFY_SSL resolves to the bool False.
        monkeypatch.setenv("UNRAID_VERIFY_SSL", falsey)
        monkeypatch.setenv("UNRAID_ALLOW_INSECURE_TLS", "true")
        importlib.reload(settings_module)
        assert settings_module.UNRAID_VERIFY_SSL is False

    def test_ca_bundle_path_preserved_as_str(
        self, _reload_settings: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # A value that is neither truthy nor falsey is treated as a CA-bundle
        # path and preserved verbatim as a str (the safe self-signed-cert route).
        ca_path = "/etc/ssl/certs/myca.pem"
        monkeypatch.setenv("UNRAID_VERIFY_SSL", ca_path)
        importlib.reload(settings_module)
        assert ca_path == settings_module.UNRAID_VERIFY_SSL
        assert isinstance(settings_module.UNRAID_VERIFY_SSL, str)
