"""Tests for unraid_info tool."""

from unittest.mock import AsyncMock, patch

import pytest

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.info import (
    _analyze_disk_health,
    _process_array_status,
    _process_system_info,
)

# --- Unit tests for helper functions ---


class TestProcessSystemInfo:
    def test_processes_os_info(self) -> None:
        raw = {
            "os": {"distro": "Unraid", "release": "7.2", "platform": "linux", "arch": "x86_64", "hostname": "tower", "uptime": 3600},
            "cpu": {"manufacturer": "AMD", "brand": "Ryzen", "cores": 8, "threads": 16},
        }
        result = _process_system_info(raw)
        assert "summary" in result
        assert "details" in result
        assert result["summary"]["hostname"] == "tower"
        assert "AMD" in result["summary"]["cpu"]

    def test_handles_missing_fields(self) -> None:
        result = _process_system_info({})
        assert result["summary"] == {"memory_summary": "Memory information not available."}

    def test_processes_memory_layout(self) -> None:
        raw = {"memory": {"layout": [{"bank": "0", "type": "DDR4", "clockSpeed": 3200, "manufacturer": "G.Skill", "partNum": "XYZ"}]}}
        result = _process_system_info(raw)
        assert len(result["summary"]["memory_layout_details"]) == 1


class TestAnalyzeDiskHealth:
    def test_counts_healthy_disks(self) -> None:
        disks = [{"status": "DISK_OK"}, {"status": "DISK_OK"}]
        result = _analyze_disk_health(disks)
        assert result["healthy"] == 2

    def test_counts_failed_disks(self) -> None:
        disks = [{"status": "DISK_DSBL"}, {"status": "DISK_INVALID"}]
        result = _analyze_disk_health(disks)
        assert result["failed"] == 2

    def test_counts_warning_disks(self) -> None:
        disks = [{"status": "DISK_OK", "warning": 45}]
        result = _analyze_disk_health(disks)
        assert result["warning"] == 1

    def test_counts_missing_disks(self) -> None:
        disks = [{"status": "DISK_NP"}]
        result = _analyze_disk_health(disks)
        assert result["missing"] == 1

    def test_empty_list(self) -> None:
        result = _analyze_disk_health([])
        assert result["healthy"] == 0


class TestProcessArrayStatus:
    def test_basic_array(self) -> None:
        raw = {
            "state": "STARTED",
            "capacity": {"kilobytes": {"free": "1048576", "used": "524288", "total": "1572864"}},
            "parities": [{"status": "DISK_OK"}],
            "disks": [{"status": "DISK_OK"}],
            "caches": [],
        }
        result = _process_array_status(raw)
        assert result["summary"]["state"] == "STARTED"
        assert result["summary"]["overall_health"] == "HEALTHY"

    def test_degraded_array(self) -> None:
        raw = {
            "state": "STARTED",
            "parities": [],
            "disks": [{"status": "DISK_NP"}],
            "caches": [],
        }
        result = _process_array_status(raw)
        assert result["summary"]["overall_health"] == "DEGRADED"


# --- Integration tests for the tool function ---


class TestUnraidInfoTool:
    @pytest.fixture
    def _mock_graphql(self) -> AsyncMock:
        with patch("unraid_mcp.tools.info.make_graphql_request", new_callable=AsyncMock) as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_overview_action(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "info": {
                "os": {"distro": "Unraid", "release": "7.2", "platform": "linux", "arch": "x86_64", "hostname": "test"},
                "cpu": {"manufacturer": "Intel", "brand": "i7", "cores": 4, "threads": 8},
            }
        }
        # Import and call the inner function by simulating registration
        from fastmcp import FastMCP
        test_mcp = FastMCP("test")
        from unraid_mcp.tools.info import register_info_tool
        register_info_tool(test_mcp)
        tool_fn = test_mcp._tool_manager._tools["unraid_info"].fn
        result = await tool_fn(action="overview")
        assert "summary" in result
        _mock_graphql.assert_called_once()

    @pytest.mark.asyncio
    async def test_ups_device_requires_device_id(self, _mock_graphql: AsyncMock) -> None:
        from fastmcp import FastMCP
        test_mcp = FastMCP("test")
        from unraid_mcp.tools.info import register_info_tool
        register_info_tool(test_mcp)
        tool_fn = test_mcp._tool_manager._tools["unraid_info"].fn
        with pytest.raises(ToolError, match="device_id is required"):
            await tool_fn(action="ups_device")

    @pytest.mark.asyncio
    async def test_network_action(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"network": {"id": "net:1", "accessUrls": []}}
        from fastmcp import FastMCP
        test_mcp = FastMCP("test")
        from unraid_mcp.tools.info import register_info_tool
        register_info_tool(test_mcp)
        tool_fn = test_mcp._tool_manager._tools["unraid_info"].fn
        result = await tool_fn(action="network")
        assert result["id"] == "net:1"

    @pytest.mark.asyncio
    async def test_connect_action(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "connect": {"status": "connected", "sandbox": False, "flashGuid": "abc123"}
        }
        from fastmcp import FastMCP
        test_mcp = FastMCP("test")
        from unraid_mcp.tools.info import register_info_tool
        register_info_tool(test_mcp)
        tool_fn = test_mcp._tool_manager._tools["unraid_info"].fn
        result = await tool_fn(action="connect")
        assert result["status"] == "connected"

    @pytest.mark.asyncio
    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("unexpected")
        from fastmcp import FastMCP
        test_mcp = FastMCP("test")
        from unraid_mcp.tools.info import register_info_tool
        register_info_tool(test_mcp)
        tool_fn = test_mcp._tool_manager._tools["unraid_info"].fn
        with pytest.raises(ToolError, match="unexpected"):
            await tool_fn(action="online")
