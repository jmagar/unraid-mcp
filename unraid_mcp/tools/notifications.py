"""Notification management.

Provides the `unraid_notifications` tool with 9 actions for viewing,
creating, archiving, and deleting system notifications.
"""

from typing import Any, Literal

from fastmcp import FastMCP

from ..config.logging import logger
from ..core.client import make_graphql_request
from ..core.exceptions import ToolError

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
        mutation CreateNotification($input: CreateNotificationInput!) {
          notifications { createNotification(input: $input) { id title importance } }
        }
    """,
    "archive": """
        mutation ArchiveNotification($id: PrefixedID!) {
          notifications { archiveNotification(id: $id) }
        }
    """,
    "unread": """
        mutation UnreadNotification($id: PrefixedID!) {
          notifications { unreadNotification(id: $id) }
        }
    """,
    "delete": """
        mutation DeleteNotification($id: PrefixedID!, $type: NotificationType!) {
          notifications { deleteNotification(id: $id, type: $type) }
        }
    """,
    "delete_archived": """
        mutation DeleteArchivedNotifications {
          notifications { deleteArchivedNotifications }
        }
    """,
    "archive_all": """
        mutation ArchiveAllNotifications($importance: NotificationImportance) {
          notifications { archiveAll(importance: $importance) }
        }
    """,
}

DESTRUCTIVE_ACTIONS = {"delete", "delete_archived"}

NOTIFICATION_ACTIONS = Literal[
    "overview", "list", "warnings",
    "create", "archive", "unread", "delete", "delete_archived", "archive_all",
]


def register_notifications_tool(mcp: FastMCP) -> None:
    """Register the unraid_notifications tool with the FastMCP instance."""

    @mcp.tool()
    async def unraid_notifications(
        action: NOTIFICATION_ACTIONS,
        confirm: bool = False,
        notification_id: str | None = None,
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
        """
        all_actions = {**QUERIES, **MUTATIONS}
        if action not in all_actions:
            raise ToolError(f"Invalid action '{action}'. Must be one of: {list(all_actions.keys())}")

        if action in DESTRUCTIVE_ACTIONS and not confirm:
            raise ToolError(f"Action '{action}' is destructive. Set confirm=True to proceed.")

        try:
            logger.info(f"Executing unraid_notifications action={action}")

            if action == "overview":
                data = await make_graphql_request(QUERIES["overview"])
                notifications = data.get("notifications", {})
                return dict(notifications.get("overview", {}))

            if action == "list":
                filter_vars: dict[str, Any] = {
                    "type": list_type.upper(),
                    "offset": offset,
                    "limit": limit,
                }
                if importance:
                    filter_vars["importance"] = importance.upper()
                data = await make_graphql_request(
                    QUERIES["list"], {"filter": filter_vars}
                )
                notifications = data.get("notifications", {})
                result = notifications.get("list", [])
                return {"notifications": list(result) if isinstance(result, list) else []}

            if action == "warnings":
                data = await make_graphql_request(QUERIES["warnings"])
                notifications = data.get("notifications", {})
                result = notifications.get("warningsAndAlerts", [])
                return {"warnings": list(result) if isinstance(result, list) else []}

            if action == "create":
                if title is None or subject is None or description is None or importance is None:
                    raise ToolError(
                        "create requires title, subject, description, and importance"
                    )
                input_data = {
                    "title": title,
                    "subject": subject,
                    "description": description,
                    "importance": importance.upper() if importance else "INFO",
                }
                data = await make_graphql_request(
                    MUTATIONS["create"], {"input": input_data}
                )
                return {"success": True, "data": data}

            if action in ("archive", "unread"):
                if not notification_id:
                    raise ToolError(f"notification_id is required for '{action}' action")
                data = await make_graphql_request(
                    MUTATIONS[action], {"id": notification_id}
                )
                return {"success": True, "action": action, "data": data}

            if action == "delete":
                if not notification_id or not notification_type:
                    raise ToolError(
                        "delete requires notification_id and notification_type"
                    )
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

            return {}

        except ToolError:
            raise
        except Exception as e:
            logger.error(f"Error in unraid_notifications action={action}: {e}", exc_info=True)
            raise ToolError(f"Failed to execute notifications/{action}: {str(e)}") from e

    logger.info("Notifications tool registered successfully")
