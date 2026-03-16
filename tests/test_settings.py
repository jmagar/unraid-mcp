"""Tests for the unraid_settings tool."""

from collections.abc import Generator
from typing import get_args
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import FastMCP

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.settings import SETTINGS_ACTIONS, register_settings_tool


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


# ---------------------------------------------------------------------------
# Regression: removed actions must not appear in SETTINGS_ACTIONS
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "action",
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
def test_removed_settings_actions_are_gone(action: str) -> None:
    assert action not in get_args(SETTINGS_ACTIONS), (
        f"{action} references a non-existent mutation and must not be in SETTINGS_ACTIONS"
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# configure_ups
# ---------------------------------------------------------------------------


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
