"""Tests for the unraid_settings tool."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.settings import register_settings_tool


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch("unraid_mcp.tools.settings.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool() -> AsyncMock:
    test_mcp = FastMCP("test")
    register_settings_tool(test_mcp)
    # FastMCP 3.x stores tools in providers[0]._components keyed as "tool:{name}@"
    local_provider = test_mcp.providers[0]
    tool = local_provider._components["tool:unraid_settings@"]
    return tool.fn  # type: ignore[union-attr]


class TestSettingsValidation:
    """Tests for action validation and destructive guard."""

    async def test_invalid_action(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="Invalid action"):
            await tool_fn(action="nonexistent_action")

    async def test_destructive_configure_ups_requires_confirm(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action="configure_ups", ups_config={"mode": "slave"})

    async def test_destructive_setup_remote_access_requires_confirm(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(action="setup_remote_access", access_type="STATIC")

    async def test_destructive_enable_dynamic_remote_access_requires_confirm(
        self, _mock_graphql: AsyncMock
    ) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="confirm=True"):
            await tool_fn(
                action="enable_dynamic_remote_access", access_url_type="WAN", dynamic_enabled=True
            )


class TestSettingsUpdate:
    """Tests for update action."""

    async def test_update_requires_settings_input(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="settings_input is required"):
            await tool_fn(action="update")

    async def test_update_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSettings": {"restartRequired": False, "values": {}, "warnings": []}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update", settings_input={"shareCount": 5})
        assert result["success"] is True
        assert result["action"] == "update"

    async def test_update_temperature_requires_config(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="temperature_config is required"):
            await tool_fn(action="update_temperature")

    async def test_update_temperature_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateTemperatureConfig": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="update_temperature", temperature_config={"unit": "C"})
        assert result["success"] is True
        assert result["action"] == "update_temperature"


class TestSystemTime:
    """Tests for update_time action."""

    async def test_update_time_requires_at_least_one_field(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="update_time requires"):
            await tool_fn(action="update_time")

    async def test_update_time_with_timezone(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSystemTime": {
                "currentTime": "2026-03-13T00:00:00Z",
                "timeZone": "America/New_York",
                "useNtp": True,
                "ntpServers": [],
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_time", time_zone="America/New_York")
        assert result["success"] is True
        assert result["action"] == "update_time"

    async def test_update_time_with_ntp(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateSystemTime": {"useNtp": True, "ntpServers": ["0.pool.ntp.org"]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_time", use_ntp=True, ntp_servers=["0.pool.ntp.org"])
        assert result["success"] is True

    async def test_update_time_manual(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateSystemTime": {"currentTime": "2026-03-13T12:00:00Z"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="update_time", manual_datetime="2026-03-13T12:00:00Z")
        assert result["success"] is True


class TestUpsConfig:
    """Tests for configure_ups action."""

    async def test_configure_ups_requires_ups_config(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="ups_config is required"):
            await tool_fn(action="configure_ups", confirm=True)

    async def test_configure_ups_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"configureUps": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="configure_ups", confirm=True, ups_config={"mode": "master", "cable": "usb"}
        )
        assert result["success"] is True
        assert result["action"] == "configure_ups"


class TestApiSettings:
    """Tests for update_api action."""

    async def test_update_api_requires_at_least_one_field(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="update_api requires"):
            await tool_fn(action="update_api")

    async def test_update_api_with_port(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "updateApiSettings": {"accessType": "STATIC", "forwardType": "NONE", "port": 8080}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="update_api", port=8080)
        assert result["success"] is True
        assert result["action"] == "update_api"

    async def test_update_api_with_access_type(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"updateApiSettings": {"accessType": "STATIC"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="update_api", access_type="STATIC")
        assert result["success"] is True


class TestConnectActions:
    """Tests for connect_sign_in and connect_sign_out actions."""

    async def test_connect_sign_in_requires_api_key(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="api_key is required"):
            await tool_fn(action="connect_sign_in")

    async def test_connect_sign_in_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"connectSignIn": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="connect_sign_in", api_key="test-api-key-abc123")
        assert result["success"] is True
        assert result["action"] == "connect_sign_in"

    async def test_connect_sign_in_with_user_info(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"connectSignIn": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="connect_sign_in",
            api_key="test-api-key",
            username="testuser",
            email="test@example.com",
            avatar="https://example.com/avatar.png",
        )
        assert result["success"] is True

    async def test_connect_sign_out_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"connectSignOut": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="connect_sign_out")
        assert result["success"] is True
        assert result["action"] == "connect_sign_out"


class TestRemoteAccess:
    """Tests for setup_remote_access and enable_dynamic_remote_access actions."""

    async def test_setup_remote_access_requires_access_type(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="access_type is required"):
            await tool_fn(action="setup_remote_access", confirm=True)

    async def test_setup_remote_access_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setupRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(action="setup_remote_access", confirm=True, access_type="STATIC")
        assert result["success"] is True
        assert result["action"] == "setup_remote_access"

    async def test_setup_remote_access_with_port(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"setupRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="setup_remote_access",
            confirm=True,
            access_type="STATIC",
            forward_type="UPNP",
            port=9999,
        )
        assert result["success"] is True

    async def test_enable_dynamic_requires_url_type(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="access_url_type is required"):
            await tool_fn(action="enable_dynamic_remote_access", confirm=True, dynamic_enabled=True)

    async def test_enable_dynamic_requires_dynamic_enabled(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="dynamic_enabled is required"):
            await tool_fn(
                action="enable_dynamic_remote_access", confirm=True, access_url_type="WAN"
            )

    async def test_enable_dynamic_success(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"enableDynamicRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="enable_dynamic_remote_access",
            confirm=True,
            access_url_type="WAN",
            dynamic_enabled=True,
        )
        assert result["success"] is True
        assert result["action"] == "enable_dynamic_remote_access"

    async def test_enable_dynamic_with_optional_fields(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"enableDynamicRemoteAccess": True}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="enable_dynamic_remote_access",
            confirm=True,
            access_url_type="WAN",
            dynamic_enabled=False,
            access_url_name="myserver",
            access_url_ipv4="1.2.3.4",
            access_url_ipv6="::1",
        )
        assert result["success"] is True
