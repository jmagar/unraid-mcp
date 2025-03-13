"""Notification management tools for Unraid MCP server"""
from mcp.types import TextContent
import logging
import traceback
import json

# Get logger
logger = logging.getLogger("unraid_mcp.notification_tools")

def register_notification_tools(server, unraid_client):
    """Register notification-related tools with the MCP server
    
    Args:
        server: The MCP server instance
        unraid_client: The Unraid API client
    """
    logger.info("Registering notification tools")
    
    @server.tool(description="Get notifications")
    async def get_notifications(
        notification_type: str = "UNREAD",
        importance: str = None,
        limit: int = 100,
        ctx=None
    ):
        """Get notifications from the Unraid server
        
        Args:
            notification_type: Type of notifications to retrieve (UNREAD or ARCHIVE)
            importance: Optional filter by importance (INFO, WARNING, ALERT)
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications and overview statistics
        """
        logger.info(f"Tool called: get_notifications(type={notification_type}, importance={importance}, limit={limit})")
        
        if ctx:
            await ctx.info(f"Retrieving {notification_type.lower()} notifications...")
        else:
            print(f"Retrieving {notification_type.lower()} notifications...")
        
        try:
            importance_str = ""
            if importance:
                importance_str = f", importance: {importance}"
                
            query = f"""
            query {{
                notifications {{
                    list(filter: {{
                        type: {notification_type}{importance_str},
                        offset: 0,
                        limit: {limit}
                    }}) {{
                        id
                        title
                        subject
                        description
                        importance
                        link
                        type
                        timestamp
                        formattedTimestamp
                    }}
                    overview {{
                        unread {{
                            info
                            warning
                            alert
                            total
                        }}
                        archive {{
                            info
                            warning
                            alert
                            total
                        }}
                    }}
                }}
            }}
            """
            response = await unraid_client.execute_query(query)
            logger.debug(f"Notifications response: {response}")
            
            if "data" in response and "notifications" in response["data"]:
                notifications = response["data"]["notifications"]
                logger.info(f"Retrieved notifications successfully")
                
                # Format the notifications in a human-readable way
                formatted_text = "🔔 NOTIFICATIONS\n"
                formatted_text += "══════════════════\n\n"
                
                # Add overview statistics
                if "overview" in notifications:
                    overview = notifications["overview"]
                    formatted_text += "📊 OVERVIEW\n"
                    
                    # Unread notifications
                    if "unread" in overview:
                        unread = overview["unread"]
                        formatted_text += f"  • Unread: {unread.get('total', 0)} total "
                        formatted_text += f"({unread.get('info', 0)} info, {unread.get('warning', 0)} warning, {unread.get('alert', 0)} alert)\n"
                    
                    # Archived notifications
                    if "archive" in overview:
                        archive = overview["archive"]
                        formatted_text += f"  • Archived: {archive.get('total', 0)} total "
                        formatted_text += f"({archive.get('info', 0)} info, {archive.get('warning', 0)} warning, {archive.get('alert', 0)} alert)\n"
                    
                    formatted_text += "\n"
                
                # List notifications
                if "list" in notifications and notifications["list"]:
                    notification_list = notifications["list"]
                    formatted_text += f"📋 {notification_type.upper()} NOTIFICATIONS ({len(notification_list)})\n\n"
                    
                    for notification in notification_list:
                        # Importance emoji
                        importance_emoji = "ℹ️"
                        if notification.get("importance") == "WARNING":
                            importance_emoji = "⚠️"
                        elif notification.get("importance") == "ALERT":
                            importance_emoji = "🚨"
                        
                        # Notification title and timestamp
                        formatted_text += f"{importance_emoji} {notification.get('title', 'Untitled')}\n"
                        if "formattedTimestamp" in notification:
                            formatted_text += f"  • Time: {notification.get('formattedTimestamp')}\n"
                        
                        # Subject and description
                        if "subject" in notification:
                            formatted_text += f"  • Subject: {notification.get('subject')}\n"
                        if "description" in notification:
                            formatted_text += f"  • Description: {notification.get('description')}\n"
                        
                        # Link if available
                        if "link" in notification and notification["link"]:
                            formatted_text += f"  • Link: {notification.get('link')}\n"
                        
                        # ID for reference
                        formatted_text += f"  • ID: {notification.get('id')}\n\n"
                else:
                    formatted_text += f"No {notification_type.lower()} notifications found.\n"
                
                return TextContent(type="text", text=formatted_text)
            else:
                logger.warning("Failed to retrieve notifications: Invalid response format")
                return TextContent(type="text", text="❌ Failed to retrieve notifications: Invalid response format")
        except Exception as e:
            error_msg = f"Error retrieving notifications: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    @server.tool(description="Create a notification")
    async def create_notification(
        title: str,
        subject: str,
        description: str,
        importance: str = "INFO",
        link: str = None,
        ctx=None
    ):
        """Create a new notification
        
        Args:
            title: The notification title
            subject: The notification subject
            description: The notification description
            importance: Importance level (INFO, WARNING, ALERT)
            link: Optional link
            
        Returns:
            The created notification
        """
        logger.info(f"Tool called: create_notification(title={title}, subject={subject}, importance={importance})")
        
        if ctx:
            await ctx.info(f"Creating {importance.lower()} notification: {title}")
        else:
            print(f"Creating {importance.lower()} notification: {title}")
        
        try:
            link_str = ""
            if link:
                link_str = f', link: "{link}"'
                
            mutation = f"""
            mutation {{
                createNotification(input: {{
                    title: "{title}",
                    subject: "{subject}",
                    description: "{description}",
                    importance: {importance}{link_str}
                }}) {{
                    id
                    title
                    subject
                    description
                    importance
                    timestamp
                    formattedTimestamp
                }}
            }}
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Create notification response: {response}")
            
            if "data" in response and "createNotification" in response["data"]:
                notification = response["data"]["createNotification"]
                logger.info(f"Created notification successfully with ID: {notification['id']}")
                
                # Format the created notification in a human-readable way
                formatted_text = "🔔 NOTIFICATION CREATED\n"
                formatted_text += "══════════════════════\n\n"
                
                # Importance emoji
                importance_emoji = "ℹ️"
                if notification.get("importance") == "WARNING":
                    importance_emoji = "⚠️"
                elif notification.get("importance") == "ALERT":
                    importance_emoji = "🚨"
                
                # Notification title and timestamp
                formatted_text += f"{importance_emoji} {notification.get('title', 'Untitled')}\n"
                if "formattedTimestamp" in notification:
                    formatted_text += f"  • Time: {notification.get('formattedTimestamp')}\n"
                elif "timestamp" in notification:
                    formatted_text += f"  • Time: {notification.get('timestamp')}\n"
                
                # Subject and description
                if "subject" in notification:
                    formatted_text += f"  • Subject: {notification.get('subject')}\n"
                if "description" in notification:
                    formatted_text += f"  • Description: {notification.get('description')}\n"
                
                # Link if available
                if "link" in notification and notification["link"]:
                    formatted_text += f"  • Link: {notification.get('link')}\n"
                
                # ID for reference
                formatted_text += f"  • ID: {notification.get('id')}\n\n"
                
                formatted_text += "✅ Notification created successfully!\n"
                
                return TextContent(type="text", text=formatted_text)
            else:
                logger.warning("Failed to create notification: Invalid response format")
                return TextContent(type="text", text="❌ Failed to create notification: Invalid response format")
        except Exception as e:
            error_msg = f"Error creating notification: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    # The archive_notification tool has been removed as it was not working correctly
    # and was causing errors when trying to archive notifications
    
    # Log that tools were registered
    logger.info("Notification tools registered successfully")
