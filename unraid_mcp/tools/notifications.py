"""Notification management.

Provides the `unraid_notifications` tool with 9 actions for viewing,
creating, archiving, and deleting system notifications.
"""

from typing import Any, Literal, get_args

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError, tool_error_handler


QUERIES: dict[str, str] = {
    "overview": """
        query GetNotificationsOverview {
          notifications {
            overview {
              unread { info warning alert total }
              archive { info warning alert total }
            }
          }
        }
    """,
    "list": """
        query ListNotifications($filter: NotificationFilter!) {
          notifications {
            list(filter: $filter) {
              id title subject description importance link type timestamp formattedTimestamp
            }
          }
        }
    """,
    "warnings": """
        query GetWarningsAndAlerts {
          notifications {
            warningsAndAlerts { id title subject description importance type timestamp }
          }
        }
    """,
}

MUTATIONS: dict[str, str] = {
    "create": """
        mutation CreateNotification($input: NotificationData!) {
          createNotification(input: $input) { id title importance }
        }
    """,
    "archive": """
        mutation ArchiveNotification($id: PrefixedID!) {
          archiveNotification(id: $id) { id title importance }
        }
    """,
    "unread": """
        mutation UnreadNotification($id: PrefixedID!) {
          unreadNotification(id: $id) { id title importance }
        }
    """,
    "delete": """
        mutation DeleteNotification($id: PrefixedID!, $type: NotificationType!) {
          deleteNotification(id: $id, type: $type) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "delete_archived": """
        mutation DeleteArchivedNotifications {
          deleteArchivedNotifications {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "archive_all": """
        mutation ArchiveAllNotifications($importance: NotificationImportance) {
          archiveAll(importance: $importance) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "archive_many": """
        mutation ArchiveNotifications($ids: [PrefixedID!]!) {
          archiveNotifications(ids: $ids) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "create_unique": """
        mutation NotifyIfUnique($input: NotificationData!) {
          notifyIfUnique(input: $input) { id title importance }
        }
    """,
    "unarchive_many": """
        mutation UnarchiveNotifications($ids: [PrefixedID!]!) {
          unarchiveNotifications(ids: $ids) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "unarchive_all": """
        mutation UnarchiveAll($importance: NotificationImportance) {
          unarchiveAll(importance: $importance) {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
    "recalculate": """
        mutation RecalculateOverview {
          recalculateOverview {
            unread { info warning alert total }
            archive { info warning alert total }
          }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete", "delete_archived"}
ALL_ACTIONS = set(QUERIES) | set(MUTATIONS)
_VALID_IMPORTANCE = {"ALERT", "WARNING", "INFO"}

NOTIFICATION_ACTIONS = Literal[
    "overview",
    "list",
    "warnings",
    "create",
    "archive",
    "unread",
    "delete",
    "delete_archived",
    "archive_all",
    "archive_many",
    "create_unique",
    "unarchive_many",
    "unarchive_all",
    "recalculate",
]

if set(get_args(NOTIFICATION_ACTIONS)) != ALL_ACTIONS:
    _missing = ALL_ACTIONS - set(get_args(NOTIFICATION_ACTIONS))
    _extra = set(get_args(NOTIFICATION_ACTIONS)) - ALL_ACTIONS
    raise RuntimeError(
        f"NOTIFICATION_ACTIONS and ALL_ACTIONS are out of sync. "
        f"Missing from Literal: {_missing or 'none'}. Extra in Literal: {_extra or 'none'}"
    )


def register_notifications_tool(mcp: FastMCP) -> None:
    """Register the unraid_notifications tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_notifications(
        action: NOTIFICATION_ACTIONS,
        confirm: bool = False,
        notification_id: str | None = None,
        notification_ids: list[str] | None = None,
        notification_type: str | None = None,
        importance: str | None = None,
        offset: int = 0,
        limit: int = 20,
        list_type: str = "UNREAD",
        title: str | None = None,
        subject: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Manage Unraid system notifications.

        Actions:
          overview - Notification counts by severity (unread/archive)
          list - List notifications with filtering (list_type=UNREAD/ARCHIVE, importance=INFO/WARNING/ALERT)
          warnings - Get deduplicated unread warnings and alerts
          create - Create notification (requires title, subject, description, importance)
          archive - Archive a notification (requires notification_id)
          unread - Mark notification as unread (requires notification_id)
          delete - Delete a notification (requires notification_id, notification_type, confirm=True)
          delete_archived - Delete all archived notifications (requires confirm=True)
          archive_all - Archive all notifications (optional importance filter)
          archive_many - Archive multiple notifications by ID (requires notification_ids)
          create_unique - Create notification only if no equivalent unread exists (requires title, subject, description, importance)
          unarchive_many - Move notifications back to unread (requires notification_ids)
          unarchive_all - Move all archived notifications to unread (optional importance filter)
          recalculate - Recompute overview counts from disk
        """
        if action not in ALL_ACTIONS:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {sorted(ALL_ACTIONS)}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        with tool_error_handler("notifications", action, logger):
            logger.info(f"Executing unraid_notifications action={action}")

            if action == "overview":
                data = await make_graphql_request(QUERIES["overview"])
                notifications = data.get("notifications") or {}
                return dict(notifications.get("overview") or {})

            if action == "list":
                filter_vars: dict[str, Any] = {
                    "type": list_type.upper(),
                    "offset": offset,
                    "limit": limit,
                }
                if importance:
                    filter_vars["importance"] = importance.upper()
                data = await make_graphql_request(QUERIES["list"], {"filter": filter_vars})
                notifications = data.get("notifications", {})
                return {"notifications": notifications.get("list", [])}

            if action == "warnings":
                data = await make_graphql_request(QUERIES["warnings"])
                notifications = data.get("notifications", {})
                return {"warnings": notifications.get("warningsAndAlerts", [])}

            if action == "create":
                if title is None or subject is None or description is None or importance is None:
                    raise ToolError("create requires title, subject, description, and importance")
                if importance.upper() not in _VALID_IMPORTANCE:
                    raise ToolError(
                        f"importance must be one of: {', '.join(sorted(_VALID_IMPORTANCE))}. "
                        f"Got: '{importance}'"
                    )
                if len(title) > 200:
                    raise ToolError(f"title must be at most 200 characters (got {len(title)})")
                if len(subject) > 500:
                    raise ToolError(f"subject must be at most 500 characters (got {len(subject)})")
                if len(description) > 2000:
                    raise ToolError(
                        f"description must be at most 2000 characters (got {len(description)})"
                    )
                input_data = {
                    "title": title,
                    "subject": subject,
                    "description": description,
                    "importance": importance.upper(),
                }
                data = await make_graphql_request(MUTATIONS["create"], {"input": input_data})
                return {"success": True, "data": data}

            if action in ("archive", "unread"):
                if not notification_id:
                    raise ToolError(f"notification_id is required for '{action}' action")
                data = await make_graphql_request(MUTATIONS[action], {"id": notification_id})
                return {"success": True, "action": action, "data": data}

            if action == "delete":
                if not notification_id or not notification_type:
                    raise ToolError("delete requires notification_id and notification_type")
                data = await make_graphql_request(
                    MUTATIONS["delete"],
                    {"id": notification_id, "type": notification_type.upper()},
                )
                return {"success": True, "action": "delete", "data": data}

            if action == "delete_archived":
                data = await make_graphql_request(MUTATIONS["delete_archived"])
                return {"success": True, "action": "delete_archived", "data": data}

            if action == "archive_all":
                variables: dict[str, Any] | None = None
                if importance:
                    variables = {"importance": importance.upper()}
                data = await make_graphql_request(MUTATIONS["archive_all"], variables)
                return {"success": True, "action": "archive_all", "data": data}

            if action == "archive_many":
                if not notification_ids:
                    raise ToolError("notification_ids is required for 'archive_many' action")
                data = await make_graphql_request(
                    MUTATIONS["archive_many"], {"ids": notification_ids}
                )
                return {"success": True, "action": "archive_many", "data": data}

            if action == "create_unique":
                if title is None or subject is None or description is None or importance is None:
                    raise ToolError(
                        "create_unique requires title, subject, description, and importance"
                    )
                if importance.upper() not in _VALID_IMPORTANCE:
                    raise ToolError(
                        f"importance must be one of: {', '.join(sorted(_VALID_IMPORTANCE))}. "
                        f"Got: '{importance}'"
                    )
                input_data = {
                    "title": title,
                    "subject": subject,
                    "description": description,
                    "importance": importance.upper(),
                }
                data = await make_graphql_request(MUTATIONS["create_unique"], {"input": input_data})
                notification = data.get("notifyIfUnique")
                if notification is None:
                    return {"success": True, "duplicate": True, "data": None}
                return {"success": True, "duplicate": False, "data": notification}

            if action == "unarchive_many":
                if not notification_ids:
                    raise ToolError("notification_ids is required for 'unarchive_many' action")
                data = await make_graphql_request(
                    MUTATIONS["unarchive_many"], {"ids": notification_ids}
                )
                return {"success": True, "action": "unarchive_many", "data": data}

            if action == "unarchive_all":
                vars_: dict[str, Any] | None = None
                if importance:
                    vars_ = {"importance": importance.upper()}
                data = await make_graphql_request(MUTATIONS["unarchive_all"], vars_)
                return {"success": True, "action": "unarchive_all", "data": data}

            if action == "recalculate":
                data = await make_graphql_request(MUTATIONS["recalculate"])
                return {"success": True, "action": "recalculate", "data": data}

            raise ToolError(f"Unhandled action '{action}' — this is a bug")

    logger.info("Notifications tool registered successfully")
