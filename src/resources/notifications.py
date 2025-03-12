"""Notification resources for Unraid MCP server"""
from typing import Dict, Any, Optional

def register_notification_resources(server, unraid_client):
    """Register notification-related resources with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    
    @server.resource("unraid://notifications/overview",
                    name="Notification Overview",
                    description="Overview of all notifications on the Unraid server",
                    mime_type="application/json")
    async def notification_overview():
        """Get an overview of all notifications"""
        try:
            query = """
            query {
                notifications {
                    overview {
                        unread {
                            info
                            warning
                            alert
                            total
                        }
                        archive {
                            info
                            warning
                            alert
                            total
                        }
                    }
                }
            }
            """
            result = await unraid_client.execute_query(query)
            if "data" in result and "notifications" in result["data"] and "overview" in result["data"]["notifications"]:
                return result["data"]["notifications"]["overview"]
            else:
                return {"error": "Failed to retrieve notification overview: Invalid response format"}
        except Exception as e:
            return {"error": f"Failed to retrieve notification overview: {str(e)}"}

    @server.resource("unraid://notifications/unread",
                    name="Unread Notifications",
                    description="List of unread notifications",
                    mime_type="application/json")
    async def unread_notifications():
        """Get all unread notifications"""
        try:
            query = """
            query {
                notifications {
                    list(filter: {
                        type: UNREAD,
                        offset: 0,
                        limit: 50
                    }) {
                        id
                        title
                        subject
                        description
                        importance
                        link
                        type
                        timestamp
                        formattedTimestamp
                    }
                }
            }
            """
            result = await unraid_client.execute_query(query)
            if "data" in result and "notifications" in result["data"] and "list" in result["data"]["notifications"]:
                return result["data"]["notifications"]["list"]
            else:
                return {"error": "Failed to retrieve unread notifications: Invalid response format"}
        except Exception as e:
            return {"error": f"Failed to retrieve unread notifications: {str(e)}"}

    @server.resource("unraid://notifications/archived",
                    name="Archived Notifications",
                    description="List of archived notifications",
                    mime_type="application/json")
    async def archived_notifications():
        """Get all archived notifications"""
        try:
            query = """
            query {
                notifications {
                    list(filter: {
                        type: ARCHIVE,
                        offset: 0,
                        limit: 50
                    }) {
                        id
                        title
                        subject
                        description
                        importance
                        link
                        type
                        timestamp
                        formattedTimestamp
                    }
                }
            }
            """
            result = await unraid_client.execute_query(query)
            if "data" in result and "notifications" in result["data"] and "list" in result["data"]["notifications"]:
                return result["data"]["notifications"]["list"]
            else:
                return {"error": "Failed to retrieve archived notifications: Invalid response format"}
        except Exception as e:
            return {"error": f"Failed to retrieve archived notifications: {str(e)}"} 