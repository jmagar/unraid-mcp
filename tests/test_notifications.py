"""Tests for unraid_notifications tool."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_tool_fn

from unraid_mcp.core.exceptions import ToolError


@pytest.fixture
def _mock_graphql() -> Generator[AsyncMock, None, None]:
    with patch(
        "unraid_mcp.tools.notifications.make_graphql_request", new_callable=AsyncMock
    ) as mock:
        yield mock


def _make_tool():
    return make_tool_fn(
        "unraid_mcp.tools.notifications", "register_notifications_tool", "unraid_notifications"
    )


class TestNotificationsValidation:
    async def test_delete_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete", notification_id="n:1", notification_type="UNREAD")

    async def test_delete_archived_requires_confirm(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="destructive"):
            await tool_fn(action="delete_archived")

    async def test_create_requires_fields(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="requires title"):
            await tool_fn(action="create")

    async def test_archive_requires_id(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="notification_id"):
            await tool_fn(action="archive")

    async def test_delete_requires_id_and_type(self, _mock_graphql: AsyncMock) -> None:
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="requires notification_id"):
            await tool_fn(action="delete", confirm=True)


class TestNotificationsActions:
    async def test_overview(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifications": {
                "overview": {
                    "unread": {"info": 5, "warning": 2, "alert": 0, "total": 7},
                    "archive": {"info": 10, "warning": 1, "alert": 0, "total": 11},
                }
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="overview")
        assert result["unread"]["total"] == 7

    async def test_list(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifications": {"list": [{"id": "n:1", "title": "Test", "importance": "INFO"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="list")
        assert len(result["notifications"]) == 1

    async def test_warnings(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifications": {"warningsAndAlerts": [{"id": "n:1", "importance": "WARNING"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="warnings")
        assert len(result["warnings"]) == 1

    async def test_create(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifications": {
                "createNotification": {"id": "n:new", "title": "Test", "importance": "INFO"}
            }
        }
        tool_fn = _make_tool()
        result = await tool_fn(
            action="create",
            title="Test",
            subject="Test Subject",
            description="Test Desc",
            importance="normal",
        )
        assert result["success"] is True

    async def test_archive_notification(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"notifications": {"archiveNotification": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="archive", notification_id="n:1")
        assert result["success"] is True

    async def test_delete_with_confirm(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"notifications": {"deleteNotification": True}}
        tool_fn = _make_tool()
        result = await tool_fn(
            action="delete",
            notification_id="n:1",
            notification_type="unread",
            confirm=True,
        )
        assert result["success"] is True

    async def test_archive_all(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"notifications": {"archiveAll": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="archive_all")
        assert result["success"] is True

    async def test_unread_notification(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"notifications": {"unreadNotification": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="unread", notification_id="n:1")
        assert result["success"] is True
        assert result["action"] == "unread"

    async def test_list_with_importance_filter(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {
            "notifications": {"list": [{"id": "n:1", "title": "Alert", "importance": "WARNING"}]}
        }
        tool_fn = _make_tool()
        result = await tool_fn(action="list", importance="warning", limit=10, offset=5)
        assert len(result["notifications"]) == 1
        call_args = _mock_graphql.call_args
        filter_var = call_args[0][1]["filter"]
        assert filter_var["importance"] == "WARNING"
        assert filter_var["limit"] == 10
        assert filter_var["offset"] == 5

    async def test_delete_archived(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.return_value = {"notifications": {"deleteArchivedNotifications": True}}
        tool_fn = _make_tool()
        result = await tool_fn(action="delete_archived", confirm=True)
        assert result["success"] is True
        assert result["action"] == "delete_archived"

    async def test_generic_exception_wraps(self, _mock_graphql: AsyncMock) -> None:
        _mock_graphql.side_effect = RuntimeError("boom")
        tool_fn = _make_tool()
        with pytest.raises(ToolError, match="boom"):
            await tool_fn(action="overview")
