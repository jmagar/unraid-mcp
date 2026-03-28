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
# Regression: removed subactions must raise Invalid subaction
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "subaction",
    [
        "update_temperature",
        "update_time",
        "update_api",
        "connect_sign_in",
        "connect_sign_out",
        "setup_remote_access",
        "enable_dynamic_remote_access",
        "update_ssh",
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
