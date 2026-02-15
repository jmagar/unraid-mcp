"""Tests for unraid_storage tool."""

from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError
from unraid_mcp.tools.storage import format_bytes

# --- Unit tests for helpers ---


class TestFormatBytes:
    def test_none(self) -> None:
        assert format_bytes(None) == "N/A"

    def test_bytes(self) -> None:
        assert format_bytes(512) == "512.00 B"

    def test_kilobytes(self) -> None:
        assert format_bytes(2048) == "2.00 KB"

    def test_megabytes(self) -> None:
        assert format_bytes(1048576) == "1.00 MB"

    def test_gigabytes(self) -> None:
        assert format_bytes(1073741824) == "1.00 GB"

    def test_terabytes(self) -> None:
        assert format_bytes(1099511627776) == "1.00 TB"


# --- Integration tests ---


@pytest.fixture
def _mock_graphql() -> AsyncMock:
    with patch("unraid_mcp.tools.storage.make_graphql_request", new_callable=AsyncMock) as mock:
        yield mock


def _make_tool():
    return make_tool_fn("unraid_mcp.tools.storage", "register_storage_tool", "unraid_storage")


class TestStorageValidation:
    async def test_disk_details_requires_disk_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="disk_id"):
            await tool_fn(action="disk_details")

    async def test_logs_requires_log_path(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="log_path"):
            await tool_fn(action="logs")

    async def test_logs_rejects_invalid_path(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="log_path must start with"):
            await tool_fn(action="logs", log_path="/etc/shadow")

    async def test_logs_rejects_path_traversal(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        # Traversal that escapes /var/log/ to reach /etc/shadow
        with pytest.raises(ToolError, match="log_path must start with"):
            await tool_fn(action="logs", log_path="/var/log/../../etc/shadow")
        # Traversal that escapes /mnt/ to reach /etc/passwd
        with pytest.raises(ToolError, match="log_path must start with"):
            await tool_fn(action="logs", log_path="/mnt/../etc/passwd")

    async def test_logs_allows_valid_paths(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"logFile": {"path": "/var/log/syslog", "content": "ok"}}
        tool_fn = _make_tool()
        result = await tool_fn(action="logs", log_path="/var/log/syslog")
        assert result["content"] == "ok"


class TestStorageActions:
    async def test_shares(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "shares": [{"id": "s:1", "name": "media"}, {"id": "s:2", "name": "backups"}]
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="shares")
        assert len(result["shares"]) == 2

    async def test_disks(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"disks": [{"id": "d:1", "device": "sda"}]}
        tool_fn = _make_tool()
        result = await tool_fn(action="disks")
        assert len(result["disks"]) == 1

    async def test_disk_details(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "disk": {"id": "d:1", "device": "sda", "name": "WD", "serialNum": "SN1", "size": 1073741824, "temperature": 35}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="disk_details", disk_id="d:1")
        assert result["summary"]["temperature"] == "35C"
        assert "1.00 GB" in result["summary"]["size_formatted"]

    async def test_disk_details_not_found(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"disk": None}
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="not found"):
            await tool_fn(action="disk_details", disk_id="d:missing")

    async def test_unassigned(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"unassignedDevices": []}
        tool_fn = _make_tool()
        result = await tool_fn(action="unassigned")
        assert result["devices"] == []

    async def test_log_files(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"logFiles": [{"name": "syslog", "path": "/var/log/syslog"}]}
        tool_fn = _make_tool()
        result = await tool_fn(action="log_files")
        assert len(result["log_files"]) == 1

    async def test_logs(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"logFile": {"path": "/var/log/syslog", "content": "log line", "totalLines": 1}}
        tool_fn = _make_tool()
        result = await tool_fn(action="logs", log_path="/var/log/syslog")
        assert result["content"] == "log line"
