# tests/test_plugins.py
"""Tests for plugin subactions of the consolidated unraid tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from conftest import make_tool_fn


@pytest.fixture
def _mock_graphql():
    with patch("unraid_mcp.core.client.make_graphql_request") as m:
        yield m


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.unraid", "register_unraid_tool", "unraid")


@pytest.mark.asyncio
async def test_list_returns_plugins(_mock_graphql):
    _mock_graphql.return_value = {
        "plugins": [
            {"name": "my-plugin", "version": "1.0.0", "hasApiModule": True, "hasCliModule": False}
        ]
    }
    result = await _make_tool()(action="plugin", subaction="list")
    assert result["success"] is True
    assert len(result["plugins"]) == 1
    assert result["page"]["truncated"] is False


@pytest.mark.asyncio
async def test_list_caps_and_surfaces_page(_mock_graphql):
    _mock_graphql.return_value = {
        "plugins": [
            {"name": f"p{i}", "version": "1.0.0", "hasApiModule": True, "hasCliModule": False}
            for i in range(10)
        ]
    }
    result = await _make_tool()(action="plugin", subaction="list", limit=3)
    assert len(result["plugins"]) == 3
    assert result["page"]["truncated"] is True
    assert result["page"]["total"] == 10
    # Response must be a clean dict, not a raw GraphQL envelope.
    assert "data" not in result


@pytest.mark.asyncio
async def test_add_requires_names(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="names"):
        await _make_tool()(action="plugin", subaction="add")


@pytest.mark.asyncio
async def test_add_success(_mock_graphql):
    _mock_graphql.return_value = {"addPlugin": False}  # False = auto-restart triggered
    result = await _make_tool()(action="plugin", subaction="add", names=["my-plugin"])
    assert result["success"] is True


@pytest.mark.asyncio
async def test_remove_requires_confirm(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="not confirmed"):
        await _make_tool()(action="plugin", subaction="remove", names=["my-plugin"], confirm=False)


@pytest.mark.asyncio
async def test_remove_with_confirm(_mock_graphql):
    _mock_graphql.return_value = {"removePlugin": True}
    result = await _make_tool()(
        action="plugin", subaction="remove", names=["my-plugin"], confirm=True
    )
    assert result["success"] is True


@pytest.mark.asyncio
async def test_installed_unraid(_mock_graphql):
    _mock_graphql.return_value = {"installedUnraidPlugins": ["a.plg", "b.plg"]}
    result = await _make_tool()(action="plugin", subaction="installed_unraid")
    assert result["plugins"] == ["a.plg", "b.plg"]


@pytest.mark.asyncio
async def test_install_operations(_mock_graphql):
    _mock_graphql.return_value = {"pluginInstallOperations": [{"id": "op1", "status": "RUNNING"}]}
    result = await _make_tool()(action="plugin", subaction="install_operations")
    assert result["operations"][0]["status"] == "RUNNING"


@pytest.mark.asyncio
async def test_install_operation_requires_id(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="operation_id is required"):
        await _make_tool()(action="plugin", subaction="install_operation")


@pytest.mark.asyncio
async def test_install_requires_confirm(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    # install is destructive (runs a .plg as root) — gated before the url check.
    with pytest.raises(ToolError, match="confirm=True"):
        await _make_tool()(action="plugin", subaction="install", url="https://example.com/x.plg")


@pytest.mark.asyncio
async def test_install_requires_url(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="url is required"):
        await _make_tool()(action="plugin", subaction="install", confirm=True)


@pytest.mark.asyncio
async def test_install_rejects_bad_url_scheme(_mock_graphql):
    from unraid_mcp.core.exceptions import ToolError

    with pytest.raises(ToolError, match="http or https"):
        await _make_tool()(
            action="plugin", subaction="install", url="file:///etc/passwd", confirm=True
        )


@pytest.mark.asyncio
async def test_install_passes_input(_mock_graphql):
    _mock_graphql.return_value = {
        "unraidPlugins": {"installPlugin": {"id": "op2", "status": "QUEUED"}}
    }
    result = await _make_tool()(
        action="plugin",
        subaction="install",
        url="https://example.com/x.plg",
        plugin_name="x",
        forced=True,
        confirm=True,
    )
    assert result["operation"]["status"] == "QUEUED"
    sent = _mock_graphql.call_args.args[1]
    assert sent["input"] == {"url": "https://example.com/x.plg", "forced": True, "name": "x"}
