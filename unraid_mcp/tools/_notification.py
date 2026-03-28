"""Notification domain handler for the Unraid MCP tool.

Covers: overview, list, create, archive, mark_unread, recalculate, archive_all,
archive_many, unarchive_many, unarchive_all, delete*, delete_archived* (12 subactions).
"""

from typing import Any

from fastmcp import Context

from ..config.logging import logger
from ..core import client as _client
from ..core.exceptions import ToolError, tool_error_handler
from ..core.guards import gate_destructive_action


# ===========================================================================
# NOTIFICATION
# ===========================================================================

_NOTIFICATION_QUERIES: dict[str, str] = {
    "overview": "query GetNotificationsOverview { notifications { overview { unread { info warning alert total } archive { info warning alert total } } } }",
    "list": "query ListNotifications($filter: NotificationFilter!) { notifications { list(filter: $filter) { id title subject description importance link type timestamp formattedTimestamp } } }",
}

_NOTIFICATION_MUTATIONS: dict[str, str] = {
    "create": "mutation CreateNotification($input: NotificationData!) { createNotification(input: $input) { id title importance } }",
    "archive": "mutation ArchiveNotification($id: PrefixedID!) { archiveNotification(id: $id) { id title importance } }",
    "mark_unread": "mutation UnreadNotification($id: PrefixedID!) { unreadNotification(id: $id) { id title importance } }",
    "delete": "mutation DeleteNotification($id: PrefixedID!, $type: NotificationType!) { deleteNotification(id: $id, type: $type) { unread { info warning alert total } archive { info warning alert total } } }",
    "delete_archived": "mutation DeleteArchivedNotifications { deleteArchivedNotifications { unread { info warning alert total } archive { info warning alert total } } }",
    "archive_all": "mutation ArchiveAllNotifications($importance: NotificationImportance) { archiveAll(importance: $importance) { unread { info warning alert total } archive { info warning alert total } } }",
    "archive_many": "mutation ArchiveNotifications($ids: [PrefixedID!]!) { archiveNotifications(ids: $ids) { unread { info warning alert total } archive { info warning alert total } } }",
    "unarchive_many": "mutation UnarchiveNotifications($ids: [PrefixedID!]!) { unarchiveNotifications(ids: $ids) { unread { info warning alert total } archive { info warning alert total } } }",
    "unarchive_all": "mutation UnarchiveAll($importance: NotificationImportance) { unarchiveAll(importance: $importance) { unread { info warning alert total } archive { info warning alert total } } }",
    "recalculate": "mutation RecalculateOverview { recalculateOverview { unread { info warning alert total } archive { info warning alert total } } }",
}

_NOTIFICATION_SUBACTIONS: set[str] = set(_NOTIFICATION_QUERIES) | set(_NOTIFICATION_MUTATIONS)
_NOTIFICATION_DESTRUCTIVE: set[str] = {"delete", "delete_archived"}
_VALID_IMPORTANCE = frozenset({"ALERT", "WARNING", "INFO"})
_VALID_LIST_TYPES = frozenset({"UNREAD", "ARCHIVE"})


async def _handle_notification(
    subaction: str,
    ctx: Context | None,
    confirm: bool,
    notification_id: str | None,
    notification_ids: list[str] | None,
    notification_type: str | None,
    importance: str | None,
    offset: int,
    limit: int,
    list_type: str,
    title: str | None,
    subject: str | None,
    description: str | None,
) -> dict[str, Any]:
    if subaction not in _NOTIFICATION_SUBACTIONS:
        raise ToolError(
            f"Invalid subaction '{subaction}' for notification. Must be one of: {sorted(_NOTIFICATION_SUBACTIONS)}"
        )

    await gate_destructive_action(
        ctx,
        subaction,
        _NOTIFICATION_DESTRUCTIVE,
        confirm,
        {
            "delete": f"Delete notification **{notification_id}** permanently. This cannot be undone.",
            "delete_archived": "Delete ALL archived notifications permanently. This cannot be undone.",
        },
    )

    if list_type.upper() not in _VALID_LIST_TYPES:
        raise ToolError(
            f"Invalid list_type '{list_type}'. Must be one of: {sorted(_VALID_LIST_TYPES)}"
        )
    if importance is not None and importance.upper() not in _VALID_IMPORTANCE:
        raise ToolError(
            f"Invalid importance '{importance}'. Must be one of: {sorted(_VALID_IMPORTANCE)}"
        )
    if notification_type is not None and notification_type.upper() not in _VALID_LIST_TYPES:
        raise ToolError(
            f"Invalid notification_type '{notification_type}'. Must be one of: {sorted(_VALID_LIST_TYPES)}"
        )

    with tool_error_handler("notification", subaction, logger):
        logger.info(f"Executing unraid action=notification subaction={subaction}")

        if subaction == "overview":
            data = await _client.make_graphql_request(_NOTIFICATION_QUERIES["overview"])
            return dict((data.get("notifications") or {}).get("overview") or {})

        if subaction == "list":
            filter_vars: dict[str, Any] = {
                "type": list_type.upper(),
                "offset": offset,
                "limit": limit,
            }
            if importance:
                filter_vars["importance"] = importance.upper()
            data = await _client.make_graphql_request(
                _NOTIFICATION_QUERIES["list"], {"filter": filter_vars}
            )
            return {"notifications": (data.get("notifications", {}) or {}).get("list", [])}

        if subaction == "create":
            if title is None or subject is None or description is None or importance is None:
                raise ToolError("create requires title, subject, description, and importance")
            if len(title) > 200:
                raise ToolError(f"title must be at most 200 characters (got {len(title)})")
            if len(subject) > 500:
                raise ToolError(f"subject must be at most 500 characters (got {len(subject)})")
            if len(description) > 2000:
                raise ToolError(
                    f"description must be at most 2000 characters (got {len(description)})"
                )
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["create"],
                {
                    "input": {
                        "title": title,
                        "subject": subject,
                        "description": description,
                        "importance": importance.upper(),
                    }
                },
            )
            notif = data.get("createNotification")
            if notif is None:
                raise ToolError("Notification creation failed: server returned no data")
            return {"success": True, "notification": notif}

        if subaction in ("archive", "mark_unread"):
            if not notification_id:
                raise ToolError(f"notification_id is required for notification/{subaction}")
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS[subaction], {"id": notification_id}
            )
            return {"success": True, "subaction": subaction, "data": data}

        if subaction == "delete":
            if not notification_id or not notification_type:
                raise ToolError("delete requires notification_id and notification_type")
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["delete"],
                {"id": notification_id, "type": notification_type.upper()},
            )
            return {"success": True, "subaction": "delete", "data": data}

        if subaction == "delete_archived":
            data = await _client.make_graphql_request(_NOTIFICATION_MUTATIONS["delete_archived"])
            return {"success": True, "subaction": "delete_archived", "data": data}

        if subaction == "archive_all":
            variables: dict[str, Any] | None = (
                {"importance": importance.upper()} if importance else None
            )
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["archive_all"], variables
            )
            return {"success": True, "subaction": "archive_all", "data": data}

        if subaction == "archive_many":
            if not notification_ids:
                raise ToolError("notification_ids is required for notification/archive_many")
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["archive_many"], {"ids": notification_ids}
            )
            return {"success": True, "subaction": "archive_many", "data": data}

        if subaction == "unarchive_many":
            if not notification_ids:
                raise ToolError("notification_ids is required for notification/unarchive_many")
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["unarchive_many"], {"ids": notification_ids}
            )
            return {"success": True, "subaction": "unarchive_many", "data": data}

        if subaction == "unarchive_all":
            vars_: dict[str, Any] | None = (
                {"importance": importance.upper()} if importance else None
            )
            data = await _client.make_graphql_request(
                _NOTIFICATION_MUTATIONS["unarchive_all"], vars_
            )
            return {"success": True, "subaction": "unarchive_all", "data": data}

        if subaction == "recalculate":
            data = await _client.make_graphql_request(_NOTIFICATION_MUTATIONS["recalculate"])
            return {"success": True, "subaction": "recalculate", "data": data}

        raise ToolError(f"Unhandled notification subaction '{subaction}' — this is a bug")
