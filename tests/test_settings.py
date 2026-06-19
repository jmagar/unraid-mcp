"""Tests for the setting subactions of the consolidated unraid tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

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

    async def test_update_system_time(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSystemTime": {"currentTime": "x", "timeZone": "UTC", "useNtp": True}
        }
        result = await _make_tool()(
            action="setting",
            subaction="update_system_time",
            config_input={"timeZone": "UTC", "useNtp": True},
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
