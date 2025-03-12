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
                return TextContent(type="text", text=json.dumps(notifications, indent=2))
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
                return TextContent(type="text", text=json.dumps(notification, indent=2))
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
    
    @server.tool(description="Archive a notification")
    async def archive_notification(
        notification_id: str,
        ctx=None
    ):
        """Archive a notification
        
        Args:
            notification_id: ID of the notification to archive
            
        Returns:
            The archived notification
        """
        logger.info(f"Tool called: archive_notification(id={notification_id})")
        
        if ctx:
            await ctx.info(f"Archiving notification: {notification_id}")
        else:
            print(f"Archiving notification: {notification_id}")
        
        try:
            mutation = f"""
            mutation {{
                archiveNotification(id: "{notification_id}") {{
                    id
                    title
                    type
                }}
            }}
            """
            response = await unraid_client.execute_query(mutation)
            logger.debug(f"Archive notification response: {response}")
            
            if "data" in response and "archiveNotification" in response["data"]:
                notification = response["data"]["archiveNotification"]
                logger.info(f"Archived notification successfully: {notification['id']}")
                return TextContent(type="text", text=json.dumps(notification, indent=2))
            else:
                logger.warning("Failed to archive notification: Invalid response format")
                return TextContent(type="text", text="❌ Failed to archive notification: Invalid response format")
        except Exception as e:
            error_msg = f"Error archiving notification: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Get the full stack trace for debugging
            stack_trace = traceback.format_exc()
            logger.error(f"Stack trace: {stack_trace}")
            
            if ctx:
                await ctx.error(error_msg)
            else:
                print(error_msg)
            return TextContent(type="text", text=f"❌ Error occurred: {str(e)}\n\nPlease check the server logs for more details.")
    
    # Log that tools were registered
    logger.info("Notification tools registered successfully") 