"""
MCP Server for Unraid API
Implements the approved tool set from the design phase.
Built with FastMCP following best practices.
Transport: Streamable HTTP (recommended over deprecated SSE)
"""
import os
import sys
import json
import logging
import httpx
import asyncio
import websockets
from pathlib import Path
import threading
from typing import Optional, Dict, Any, List, Union
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dataclasses import dataclass
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Ensure the script's directory is in the Python path for potential local imports if structured differently
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Load environment variables from .env file
# In container: First try /app/.env.local (mounted), then project root .env
dotenv_paths = [
    Path('/app/.env.local'),  # Container mount point
    SCRIPT_DIR.parent / '.env.local',  # Project root .env.local
    SCRIPT_DIR.parent / '.env',  # Project root .env
    SCRIPT_DIR / '.env'  # Local .env in unraid-mcp/
]

for dotenv_path in dotenv_paths:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        break

# Configuration
UNRAID_API_URL = os.getenv("UNRAID_API_URL")
UNRAID_API_KEY = os.getenv("UNRAID_API_KEY")
UNRAID_MCP_PORT = int(os.getenv("UNRAID_MCP_PORT", "6970"))
UNRAID_MCP_HOST = os.getenv("UNRAID_MCP_HOST", "0.0.0.0")
UNRAID_MCP_TRANSPORT = os.getenv("UNRAID_MCP_TRANSPORT", "streamable-http").lower()  # Changed from sse to streamable-http

raw_verify_ssl = os.getenv("UNRAID_VERIFY_SSL", "true").lower()
if raw_verify_ssl in ["false", "0", "no"]:
    UNRAID_VERIFY_SSL: Union[bool, str] = False
elif raw_verify_ssl in ["true", "1", "yes"]:
    UNRAID_VERIFY_SSL = True
else: # Path to CA bundle
    UNRAID_VERIFY_SSL = raw_verify_ssl


# Logging setup
# Get log level from environment or default to INFO
LOG_LEVEL_STR = os.getenv('UNRAID_MCP_LOG_LEVEL', 'INFO').upper() # Changed from LOG_LEVEL
NUMERIC_LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# Define a base logger
logger = logging.getLogger("UnraidMCPServer")
logger.setLevel(NUMERIC_LOG_LEVEL)
logger.propagate = False # Prevent root logger from anoying Uvicorn/FastMCP handlers from duplicating

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(NUMERIC_LOG_LEVEL)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File Handler with Rotation (log file in the same directory as the script)
log_file_name = os.getenv("UNRAID_MCP_LOG_FILE", "unraid-mcp.log") # Use env var, default to unraid-mcp.log
log_file_path = SCRIPT_DIR / log_file_name

# Rotate logs at 5MB, keep 3 backup logs
file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setLevel(NUMERIC_LOG_LEVEL)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.info(f"Logging initialized (console and file: {log_file_path}).")

# Log loaded env vars
if UNRAID_API_URL:
    logger.info(f"UNRAID_API_URL loaded: {UNRAID_API_URL[:20]}...") # Log a preview
else:
    logger.warning("UNRAID_API_URL not found in environment or .env file.")

if UNRAID_API_KEY:
    logger.info("UNRAID_API_KEY loaded: ****") # Don't log the key itself
else:
    logger.warning("UNRAID_API_KEY not found in environment or .env file.")

logger.info(f"UNRAID_MCP_PORT set to: {UNRAID_MCP_PORT}")
logger.info(f"UNRAID_MCP_HOST set to: {UNRAID_MCP_HOST}")
logger.info(f"UNRAID_MCP_TRANSPORT set to: {UNRAID_MCP_TRANSPORT}")
logger.info(f"UNRAID_MCP_LOG_LEVEL set to: {LOG_LEVEL_STR}") # Changed from LOG_LEVEL


@dataclass
class SubscriptionData:
    """Container for subscription data with metadata"""
    data: Dict[str, Any]
    last_updated: datetime
    subscription_type: str


class SubscriptionManager:
    """Manages GraphQL subscriptions and converts them to MCP resources"""
    
    def __init__(self):
        self.active_subscriptions: Dict[str, asyncio.Task] = {}
        self.resource_data: Dict[str, SubscriptionData] = {}
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.subscription_lock = asyncio.Lock()
        
        # Configuration
        self.auto_start_enabled = os.getenv("UNRAID_AUTO_START_SUBSCRIPTIONS", "true").lower() == "true"
        self.reconnect_attempts: Dict[str, int] = {}
        self.max_reconnect_attempts = int(os.getenv("UNRAID_MAX_RECONNECT_ATTEMPTS", "10"))
        self.connection_states: Dict[str, str] = {}  # Track connection state per subscription
        self.last_error: Dict[str, str] = {}  # Track last error per subscription
        
        # Define subscription configurations
        self.subscription_configs = {
            "arraySubscription": {
                "query": """
                subscription ArraySubscription {
                    arraySubscription {
                        id
                        state
                        capacity {
                            disks { free used total }
                        }
                        disks {
                            name
                            size
                            status
                            temp
                        }
                    }
                }
                """,
                "resource": "unraid://array/status",
                "description": "Real-time array status monitoring",
                "auto_start": True
            },
            "infoSubscription": {
                "query": """
                subscription InfoSubscription {
                    infoSubscription {
                        id
                        time
                        machineId
                        os { platform distro release uptime }
                        cpu { manufacturer brand cores threads }
                        memory { total free used available }
                    }
                }
                """,
                "resource": "unraid://system/info",
                "description": "Real-time system information monitoring",
                "auto_start": True
            },
            "notificationsOverview": {
                "query": """
                subscription NotificationOverviewSubscription {
                    notificationsOverview {
                        unread { total info warning alert }
                        archive { total info warning alert }
                    }
                }
                """,
                "resource": "unraid://notifications/overview",
                "description": "Real-time notification overview monitoring",
                "auto_start": True
            },
            "parityHistorySubscription": {
                "query": """
                subscription ParityHistorySubscription {
                    parityHistorySubscription {
                        status
                        progress
                        duration
                        speed
                        errors
                    }
                }
                """,
                "resource": "unraid://parity/status", 
                "description": "Real-time parity check monitoring",
                "auto_start": True
            },
            "logFileSubscription": {
                "query": """
                subscription LogFileSubscription($path: String!) {
                    logFile(path: $path) {
                        path
                        content
                        totalLines
                    }
                }
                """,
                "resource": "unraid://logs/stream",
                "description": "Real-time log file streaming",
                "auto_start": False  # Started manually with path parameter
            }
        }
        
        logger.info(f"[SUBSCRIPTION_MANAGER] Initialized with auto_start={self.auto_start_enabled}, max_reconnects={self.max_reconnect_attempts}")
        logger.debug(f"[SUBSCRIPTION_MANAGER] Available subscriptions: {list(self.subscription_configs.keys())}")
        
    async def auto_start_all_subscriptions(self):
        """Auto-start all subscriptions marked for auto-start"""
        if not self.auto_start_enabled:
            logger.info("[SUBSCRIPTION_MANAGER] Auto-start disabled")
            return
            
        logger.info("[SUBSCRIPTION_MANAGER] Starting auto-start process...")
        auto_start_count = 0
        
        for subscription_name, config in self.subscription_configs.items():
            if config.get("auto_start", False):
                try:
                    logger.info(f"[SUBSCRIPTION_MANAGER] Auto-starting subscription: {subscription_name}")
                    await self.start_subscription(subscription_name, config["query"])
                    auto_start_count += 1
                except Exception as e:
                    logger.error(f"[SUBSCRIPTION_MANAGER] Failed to auto-start {subscription_name}: {e}")
                    self.last_error[subscription_name] = str(e)
        
        logger.info(f"[SUBSCRIPTION_MANAGER] Auto-start completed. Started {auto_start_count} subscriptions")
        
    async def start_subscription(self, subscription_name: str, query: str, variables: Dict[str, Any] = None):
        """Start a GraphQL subscription and maintain it as a resource"""
        logger.info(f"[SUBSCRIPTION:{subscription_name}] Starting subscription...")
        
        if subscription_name in self.active_subscriptions:
            logger.warning(f"[SUBSCRIPTION:{subscription_name}] Subscription already active, skipping")
            return

        # Reset connection tracking
        self.reconnect_attempts[subscription_name] = 0
        self.connection_states[subscription_name] = "starting"
        
        async with self.subscription_lock:
            try:
                task = asyncio.create_task(self._subscription_loop(subscription_name, query, variables or {}))
                self.active_subscriptions[subscription_name] = task
                logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription task created and started")
                self.connection_states[subscription_name] = "active"
            except Exception as e:
                logger.error(f"[SUBSCRIPTION:{subscription_name}] Failed to start subscription task: {e}")
                self.connection_states[subscription_name] = "failed"
                self.last_error[subscription_name] = str(e)
                raise
    
    async def stop_subscription(self, subscription_name: str):
        """Stop a specific subscription"""
        logger.info(f"[SUBSCRIPTION:{subscription_name}] Stopping subscription...")
        
        async with self.subscription_lock:
            if subscription_name in self.active_subscriptions:
                task = self.active_subscriptions[subscription_name]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Task cancelled successfully")
                del self.active_subscriptions[subscription_name]
                self.connection_states[subscription_name] = "stopped"
                logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription stopped")
            else:
                logger.warning(f"[SUBSCRIPTION:{subscription_name}] No active subscription to stop")
    
    async def _subscription_loop(self, subscription_name: str, query: str, variables: Dict[str, Any]):
        """Main loop for maintaining a GraphQL subscription with comprehensive logging"""
        retry_delay = 5
        max_retry_delay = 300  # 5 minutes max
        
        while True:
            attempt = self.reconnect_attempts.get(subscription_name, 0) + 1
            self.reconnect_attempts[subscription_name] = attempt
            
            logger.info(f"[WEBSOCKET:{subscription_name}] Connection attempt #{attempt} (max: {self.max_reconnect_attempts})")
            
            if attempt > self.max_reconnect_attempts:
                logger.error(f"[WEBSOCKET:{subscription_name}] Max reconnection attempts ({self.max_reconnect_attempts}) exceeded, stopping")
                self.connection_states[subscription_name] = "max_retries_exceeded"
                break
            
            try:
                # Build WebSocket URL with detailed logging
                if UNRAID_API_URL.startswith('https://'):
                    ws_url = 'wss://' + UNRAID_API_URL[len('https://'):]
                elif UNRAID_API_URL.startswith('http://'):
                    ws_url = 'ws://' + UNRAID_API_URL[len('http://'):]
                else:
                    ws_url = UNRAID_API_URL
                    
                if not ws_url.endswith('/graphql'):
                    ws_url = ws_url.rstrip('/') + '/graphql'
                    
                logger.debug(f"[WEBSOCKET:{subscription_name}] Connecting to: {ws_url}")
                logger.debug(f"[WEBSOCKET:{subscription_name}] API Key present: {'Yes' if UNRAID_API_KEY else 'No'}")
                
                # Connection with timeout
                connect_timeout = 10
                logger.debug(f"[WEBSOCKET:{subscription_name}] Connection timeout: {connect_timeout}s")
                
                async with websockets.connect(
                    ws_url,
                    subprotocols=["graphql-transport-ws", "graphql-ws"],
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    
                    selected_proto = websocket.subprotocol or "none"
                    logger.info(f"[WEBSOCKET:{subscription_name}] Connected! Protocol: {selected_proto}")
                    self.connection_states[subscription_name] = "connected"
                    
                    # Reset retry count on successful connection
                    self.reconnect_attempts[subscription_name] = 0
                    retry_delay = 5  # Reset delay
                    
                    # Initialize GraphQL-WS protocol
                    logger.debug(f"[PROTOCOL:{subscription_name}] Initializing GraphQL-WS protocol...")
                    init_type = "connection_init"
                    init_payload: Dict[str, Any] = {"type": init_type}
                    
                    if UNRAID_API_KEY:
                        logger.debug(f"[AUTH:{subscription_name}] Adding authentication payload")
                        auth_payload = {
                            "X-API-Key": UNRAID_API_KEY,
                            "x-api-key": UNRAID_API_KEY,
                            "authorization": f"Bearer {UNRAID_API_KEY}",
                            "Authorization": f"Bearer {UNRAID_API_KEY}",
                            "headers": {
                                "X-API-Key": UNRAID_API_KEY,
                                "x-api-key": UNRAID_API_KEY,
                                "Authorization": f"Bearer {UNRAID_API_KEY}"
                            }
                        }
                        init_payload["payload"] = auth_payload
                    else:
                        logger.warning(f"[AUTH:{subscription_name}] No API key available for authentication")

                    logger.debug(f"[PROTOCOL:{subscription_name}] Sending connection_init message")
                    await websocket.send(json.dumps(init_payload))
                    
                    # Wait for connection acknowledgment
                    logger.debug(f"[PROTOCOL:{subscription_name}] Waiting for connection_ack...")
                    init_raw = await asyncio.wait_for(websocket.recv(), timeout=30)
                    
                    try:
                        init_data = json.loads(init_raw)
                        logger.debug(f"[PROTOCOL:{subscription_name}] Received init response: {init_data.get('type')}")
                    except json.JSONDecodeError as e:
                        logger.error(f"[PROTOCOL:{subscription_name}] Failed to decode init response: {init_raw[:200]}...")
                        self.last_error[subscription_name] = f"Invalid JSON in init response: {e}"
                        break

                    # Handle connection acknowledgment
                    if init_data.get("type") == "connection_ack":
                        logger.info(f"[PROTOCOL:{subscription_name}] Connection acknowledged successfully")
                        self.connection_states[subscription_name] = "authenticated"
                    elif init_data.get("type") == "connection_error":
                        error_payload = init_data.get('payload', {})
                        logger.error(f"[AUTH:{subscription_name}] Authentication failed: {error_payload}")
                        self.last_error[subscription_name] = f"Authentication error: {error_payload}"
                        self.connection_states[subscription_name] = "auth_failed"
                        break
                    else:
                        logger.warning(f"[PROTOCOL:{subscription_name}] Unexpected init response: {init_data}")
                        # Continue anyway - some servers send other messages first
                    
                    # Start the subscription
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Starting GraphQL subscription...")
                    start_type = "subscribe" if selected_proto == "graphql-transport-ws" else "start"
                    subscription_message = {
                        "id": subscription_name,
                        "type": start_type,
                        "payload": {
                            "query": query,
                            "variables": variables
                        }
                    }
                    
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Subscription message type: {start_type}")
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Query: {query[:100]}...")
                    logger.debug(f"[SUBSCRIPTION:{subscription_name}] Variables: {variables}")
                    
                    await websocket.send(json.dumps(subscription_message))
                    logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription started successfully")
                    self.connection_states[subscription_name] = "subscribed"
                    
                    # Listen for subscription data
                    message_count = 0
                    last_data_time = datetime.now()
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            message_count += 1
                            message_type = data.get('type', 'unknown')
                            
                            logger.debug(f"[DATA:{subscription_name}] Message #{message_count}: {message_type}")
                            
                            # Handle different message types
                            expected_data_type = "next" if selected_proto == "graphql-transport-ws" else "data"
                            
                            if data.get("type") == expected_data_type and data.get("id") == subscription_name:
                                payload = data.get("payload", {})
                                
                                if payload.get("data"):
                                    logger.info(f"[DATA:{subscription_name}] Received subscription data update")
                                    self.resource_data[subscription_name] = SubscriptionData(
                                        data=payload["data"],
                                        last_updated=datetime.now(),
                                        subscription_type=subscription_name
                                    )
                                    last_data_time = datetime.now()
                                    logger.debug(f"[RESOURCE:{subscription_name}] Resource data updated successfully")
                                elif payload.get("errors"):
                                    logger.error(f"[DATA:{subscription_name}] GraphQL errors in response: {payload['errors']}")
                                    self.last_error[subscription_name] = f"GraphQL errors: {payload['errors']}"
                                else:
                                    logger.warning(f"[DATA:{subscription_name}] Empty or invalid data payload: {payload}")
                                    
                            elif data.get("type") == "ping":
                                logger.debug(f"[PROTOCOL:{subscription_name}] Received ping, sending pong")
                                await websocket.send(json.dumps({"type": "pong"}))
                                
                            elif data.get("type") == "error":
                                error_payload = data.get('payload', {})
                                logger.error(f"[SUBSCRIPTION:{subscription_name}] Subscription error: {error_payload}")
                                self.last_error[subscription_name] = f"Subscription error: {error_payload}"
                                self.connection_states[subscription_name] = "error"
                                
                            elif data.get("type") == "complete":
                                logger.info(f"[SUBSCRIPTION:{subscription_name}] Subscription completed by server")
                                self.connection_states[subscription_name] = "completed"
                                break
                                
                            elif data.get("type") in ["ka", "ping", "pong"]:
                                logger.debug(f"[PROTOCOL:{subscription_name}] Keepalive message: {message_type}")
                                
                            else:
                                logger.debug(f"[PROTOCOL:{subscription_name}] Unhandled message type: {message_type}")
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"[PROTOCOL:{subscription_name}] Failed to decode message: {message[:200]}...")
                            logger.error(f"[PROTOCOL:{subscription_name}] JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"[DATA:{subscription_name}] Error processing message: {e}")
                            logger.debug(f"[DATA:{subscription_name}] Raw message: {message[:200]}...")
                            
            except asyncio.TimeoutError:
                error_msg = "Connection or authentication timeout"
                logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
                self.last_error[subscription_name] = error_msg
                self.connection_states[subscription_name] = "timeout"
                
            except websockets.exceptions.ConnectionClosed as e:
                error_msg = f"WebSocket connection closed: {e}"
                logger.warning(f"[WEBSOCKET:{subscription_name}] {error_msg}")
                self.last_error[subscription_name] = error_msg
                self.connection_states[subscription_name] = "disconnected"
                
            except websockets.exceptions.InvalidURI as e:
                error_msg = f"Invalid WebSocket URI: {e}"
                logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
                self.last_error[subscription_name] = error_msg
                self.connection_states[subscription_name] = "invalid_uri"
                break  # Don't retry on invalid URI
                
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(f"[WEBSOCKET:{subscription_name}] {error_msg}")
                self.last_error[subscription_name] = error_msg
                self.connection_states[subscription_name] = "error"
                
            # Calculate backoff delay
            retry_delay = min(retry_delay * 1.5, max_retry_delay)
            logger.info(f"[WEBSOCKET:{subscription_name}] Reconnecting in {retry_delay:.1f} seconds...")
            self.connection_states[subscription_name] = "reconnecting"
            await asyncio.sleep(retry_delay)
    
    def get_resource_data(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """Get current resource data with enhanced logging"""
        logger.debug(f"[RESOURCE:{resource_name}] Resource data requested")
        
        if resource_name in self.resource_data:
            data = self.resource_data[resource_name]
            age_seconds = (datetime.now() - data.last_updated).total_seconds()
            logger.debug(f"[RESOURCE:{resource_name}] Data found, age: {age_seconds:.1f}s")
            return data.data
        else:
            logger.debug(f"[RESOURCE:{resource_name}] No data available")
            return None
    
    def list_active_subscriptions(self) -> List[str]:
        """List all active subscriptions"""
        active = list(self.active_subscriptions.keys())
        logger.debug(f"[SUBSCRIPTION_MANAGER] Active subscriptions: {active}")
        return active
    
    def get_subscription_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all subscriptions for diagnostics"""
        status = {}
        
        for sub_name, config in self.subscription_configs.items():
            sub_status = {
                "config": {
                    "resource": config["resource"],
                    "description": config["description"],
                    "auto_start": config.get("auto_start", False)
                },
                "runtime": {
                    "active": sub_name in self.active_subscriptions,
                    "connection_state": self.connection_states.get(sub_name, "not_started"),
                    "reconnect_attempts": self.reconnect_attempts.get(sub_name, 0),
                    "last_error": self.last_error.get(sub_name, None)
                }
            }
            
            # Add data info if available
            if sub_name in self.resource_data:
                data_info = self.resource_data[sub_name]
                age_seconds = (datetime.now() - data_info.last_updated).total_seconds()
                sub_status["data"] = {
                    "available": True,
                    "last_updated": data_info.last_updated.isoformat(),
                    "age_seconds": age_seconds
                }
            else:
                sub_status["data"] = {"available": False}
                
            status[sub_name] = sub_status
            
        logger.debug(f"[SUBSCRIPTION_MANAGER] Generated status for {len(status)} subscriptions")
        return status


# Global subscription manager
subscription_manager = SubscriptionManager()

# Track if we've started subscriptions
_subscriptions_started = False

async def ensure_subscriptions_started():
    """Ensure subscriptions are started, called from async context"""
    global _subscriptions_started
    
    if _subscriptions_started:
        return
        
    logger.info("[STARTUP] First async operation detected, starting subscriptions...")
    try:
        await autostart_subscriptions()
        _subscriptions_started = True
        logger.info("[STARTUP] Subscriptions started successfully")
    except Exception as e:
        logger.error(f"[STARTUP] Failed to start subscriptions: {e}", exc_info=True)

logger.info(f"UNRAID_MCP_LOG_FILE set to: {log_file_path}") # Added
logger.info(f"UNRAID_VERIFY_SSL set to: {UNRAID_VERIFY_SSL}")

if not UNRAID_API_URL or not UNRAID_API_KEY:
    logger.error("UNRAID_API_URL and UNRAID_API_KEY must be set in the .env file for the server to function.")
    sys.exit(1)

# Initialize FastMCP Server
mcp = FastMCP(
    name="Unraid MCP Server",
    instructions="Provides tools to interact with an Unraid server's GraphQL API.",
    version="0.1.0",
)


# MCP Resources for real-time subscription data

async def autostart_subscriptions():
    """Auto-start all subscriptions marked for auto-start in SubscriptionManager"""
    logger.info("[AUTOSTART] Initiating subscription auto-start process...")
    
    try:
        # Use the new SubscriptionManager auto-start method
        await subscription_manager.auto_start_all_subscriptions()
        logger.info("[AUTOSTART] Auto-start process completed successfully")
    except Exception as e:
        logger.error(f"[AUTOSTART] Failed during auto-start process: {e}", exc_info=True)
        
    # Optional log file subscription
    log_path = os.getenv("UNRAID_AUTOSTART_LOG_PATH")
    if log_path is None:
        # Default to syslog if available
        default_path = "/var/log/syslog"
        if Path(default_path).exists():
            log_path = default_path
            logger.info(f"[AUTOSTART] Using default log path: {default_path}")
            
    if log_path:
        try:
            logger.info(f"[AUTOSTART] Starting log file subscription for: {log_path}")
            config = subscription_manager.subscription_configs.get("logFileSubscription")
            if config:
                await subscription_manager.start_subscription("logFileSubscription", config["query"], {"path": log_path})
                logger.info(f"[AUTOSTART] Log file subscription started for: {log_path}")
            else:
                logger.error("[AUTOSTART] logFileSubscription config not found")
        except Exception as e:
            logger.error(f"[AUTOSTART] Failed to start log file subscription: {e}", exc_info=True)
    else:
        logger.info("[AUTOSTART] No log file path configured for auto-start")
@mcp.resource("unraid://array/status")
async def array_status_resource() -> str:
    """Real-time Unraid array status from subscription"""
    await ensure_subscriptions_started()
    data = subscription_manager.get_resource_data("arraySubscription")
    if data:
        return json.dumps({
            "source": "live_subscription",
            "timestamp": data.get("timestamp", "unknown"),
            "data": data
        }, indent=2)
    
    # Subscription connected but no live data yet, get current state as fallback
    try:
        fallback_data = await get_array_status()
        return json.dumps({
            "source": "fallback_query",
            "message": "Subscription connected but no live updates yet. Showing current state. Will update automatically when array changes.",
            "data": fallback_data
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "No subscription data yet", 
            "message": "Subscription connected but no data. Array might be stable (no changes to trigger updates).",
            "error": str(e)
        })

@mcp.resource("unraid://system/info")
async def system_info_resource() -> str:
    """Real-time system information from subscription"""
    await ensure_subscriptions_started()
    data = subscription_manager.get_resource_data("infoSubscription")
    if data:
        return json.dumps(data, indent=2)
    
    # If no subscription data, try to get current state via regular query as fallback
    try:
        fallback_data = await get_system_info()
        return json.dumps({
            "source": "fallback_query",
            "message": "Subscription connected but no live data yet, showing current state",
            "data": fallback_data
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "No subscription data yet", 
            "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues.",
            "fallback_error": str(e)
        })

@mcp.resource("unraid://notifications/overview")
async def notifications_overview_resource() -> str:
    """Real-time notification overview from subscription"""
    await ensure_subscriptions_started()
    data = subscription_manager.get_resource_data("notificationsOverview")
    if data:
        return json.dumps(data, indent=2)
    return json.dumps({
        "status": "No subscription data yet",
        "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues."
    })

@mcp.resource("unraid://parity/status")
async def parity_status_resource() -> str:
    """Real-time parity check status from subscription"""
    await ensure_subscriptions_started()
    data = subscription_manager.get_resource_data("parityHistorySubscription")
    if data:
        return json.dumps(data, indent=2)
    return json.dumps({
        "status": "No subscription data yet",
        "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues."
    })

@mcp.resource("unraid://logs/stream")
async def logs_stream_resource() -> str:
    """Real-time log stream data from subscription"""
    await ensure_subscriptions_started()
    data = subscription_manager.get_resource_data("logFileSubscription")
    if data:
        return json.dumps(data, indent=2)
    return json.dumps({
        "status": "No subscription data yet",
        "message": "Subscriptions auto-start on server boot. If this persists, check server logs for WebSocket/auth issues."
    })

# HTTP client timeout settings
TIMEOUT_CONFIG = httpx.Timeout(10.0, read=30.0, connect=5.0)


async def _make_graphql_request(
    query: str, 
    variables: Optional[Dict[str, Any]] = None,
    custom_timeout: Optional[httpx.Timeout] = None
) -> Dict[str, Any]:
    """Helper function to make GraphQL requests to the Unraid API."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": UNRAID_API_KEY,
        "User-Agent": "UnraidMCPServer/0.1.0" # Custom user-agent
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    logger.debug(f"Making GraphQL request to {UNRAID_API_URL}:")
    logger.debug(f"Query: {query[:200]}{'...' if len(query) > 200 else ''}") # Log truncated query
    if variables:
        logger.debug(f"Variables: {variables}")

    current_timeout = custom_timeout if custom_timeout is not None else TIMEOUT_CONFIG

    try:
        async with httpx.AsyncClient(timeout=current_timeout, verify=UNRAID_VERIFY_SSL) as client:
            response = await client.post(UNRAID_API_URL, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP error codes 4xx/5xx
            
            response_data = response.json()
            if "errors" in response_data and response_data["errors"]:
                logger.error(f"GraphQL API returned errors: {response_data['errors']}")
                # Use ToolError for GraphQL errors to provide better feedback to LLM
                error_details = "; ".join([err.get("message", str(err)) for err in response_data["errors"]])
                raise ToolError(f"GraphQL API error: {error_details}")
            
            logger.debug("GraphQL request successful.")
            return response_data.get("data", {}) # Return only the data part

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise ToolError(f"HTTP error {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise ToolError(f"Network connection error: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise ToolError(f"Invalid JSON response from Unraid API: {str(e)}")

# --- Tool Implementations Will Go Here ---

@mcp.tool()
async def get_system_info() -> Dict[str, Any]:
    """Retrieves comprehensive information about the Unraid system, OS, CPU, memory, and baseboard."""
    query = """
    query GetSystemInfo {
      info {
        os { platform distro release codename kernel arch hostname codepage logofile serial build uptime }
        cpu { manufacturer brand vendor family model stepping revision voltage speed speedmin speedmax threads cores processors socket cache flags }
        memory {
          # Avoid fetching problematic fields that cause type errors
          layout { bank type clockSpeed formFactor manufacturer partNum serialNum }
        }
        baseboard { manufacturer model version serial assetTag }
        system { manufacturer model version serial uuid sku }
        versions { kernel openssl systemOpenssl systemOpensslLib node v8 npm yarn pm2 gulp grunt git tsc mysql redis mongodb apache nginx php docker postfix postgresql perl python gcc unraid }
        apps { installed started }
        # Remove devices section as it has non-nullable fields that might be null
        machineId
        time
      }
    }
    """
    try:
        logger.info("Executing get_system_info tool")
        response_data = await _make_graphql_request(query)
        raw_info = response_data.get("info", {})
        if not raw_info:
            raise ToolError("No system info returned from Unraid API")

        # Process for human-readable output
        summary = {}
        if raw_info.get('os'):
            os_info = raw_info['os']
            summary['os'] = f"{os_info.get('distro', '')} {os_info.get('release', '')} ({os_info.get('platform', '')}, {os_info.get('arch', '')})"
            summary['hostname'] = os_info.get('hostname')
            summary['uptime'] = os_info.get('uptime')        
        
        if raw_info.get('cpu'):
            cpu_info = raw_info['cpu']
            summary['cpu'] = f"{cpu_info.get('manufacturer', '')} {cpu_info.get('brand', '')} ({cpu_info.get('cores')} cores, {cpu_info.get('threads')} threads)"
        
        if raw_info.get('memory') and raw_info['memory'].get('layout'):
            mem_layout = raw_info['memory']['layout']
            summary['memory_layout_details'] = [] # Renamed for clarity
            # The API is not returning 'size' for individual sticks in the layout, even if queried.
            # So, we cannot calculate total from layout currently.
            for stick in mem_layout:
                # stick_size = stick.get('size') # This is None in the actual API response
                summary['memory_layout_details'].append(
                    f"Bank {stick.get('bank', '?')}: Type {stick.get('type', '?')}, Speed {stick.get('clockSpeed', '?')}MHz, Manufacturer: {stick.get('manufacturer','?')}, Part: {stick.get('partNum', '?')}"
                )
            summary['memory_summary'] = "Stick layout details retrieved. Overall total/used/free memory stats are unavailable due to API limitations (Int overflow or data not provided by API)."
        else:
            summary['memory_summary'] = "Memory information (layout or stats) not available or failed to retrieve."

        # Include a key for the full details if needed by an LLM for deeper dives
        return {"summary": summary, "details": raw_info}

    except Exception as e:
        logger.error(f"Error in get_system_info: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve system information: {str(e)}")

@mcp.tool()
async def get_array_status() -> Dict[str, Any]:
    """Retrieves the current status of the Unraid storage array, including its state, capacity, and details of all disks."""
    query = """
    query GetArrayStatus {
      array {
        id
        state
        capacity {
          kilobytes { free used total }
          disks { free used total }
        }
        boot { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        parities { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        disks { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
        caches { id idx name device size status rotational temp numReads numWrites numErrors fsSize fsFree fsUsed exportable type warning critical fsType comment format transport color }
      }
    }
    """
    try:
        logger.info("Executing get_array_status tool")
        response_data = await _make_graphql_request(query)
        raw_array_info = response_data.get("array", {})
        if not raw_array_info:
            raise ToolError("No array information returned from Unraid API")

        summary = {}
        summary['state'] = raw_array_info.get('state')

        if raw_array_info.get('capacity') and raw_array_info['capacity'].get('kilobytes'):
            kb_cap = raw_array_info['capacity']['kilobytes']
            # Helper to format KB into TB/GB/MB
            def format_kb(k):
                if k is None: return "N/A"
                k = int(k) # Values are strings in SDL for PrefixedID containing types like capacity
                if k >= 1024*1024*1024: return f"{k / (1024*1024*1024):.2f} TB"
                if k >= 1024*1024: return f"{k / (1024*1024):.2f} GB"
                if k >= 1024: return f"{k / 1024:.2f} MB"
                return f"{k} KB"

            summary['capacity_total'] = format_kb(kb_cap.get('total'))
            summary['capacity_used'] = format_kb(kb_cap.get('used'))
            summary['capacity_free'] = format_kb(kb_cap.get('free'))
        
        summary['num_parity_disks'] = len(raw_array_info.get('parities', []))
        summary['num_data_disks'] = len(raw_array_info.get('disks', []))
        summary['num_cache_pools'] = len(raw_array_info.get('caches', [])) # Note: caches are pools, not individual cache disks

        # Enhanced: Add disk health summary
        def analyze_disk_health(disks, disk_type):
            """Analyze health status of disk arrays"""
            if not disks:
                return {}
            
            health_counts = {
                'healthy': 0,
                'failed': 0,
                'missing': 0,
                'new': 0,
                'warning': 0,
                'unknown': 0
            }
            
            for disk in disks:
                status = disk.get('status', '').upper()
                warning = disk.get('warning')
                critical = disk.get('critical')
                
                if status == 'DISK_OK':
                    if warning or critical:
                        health_counts['warning'] += 1
                    else:
                        health_counts['healthy'] += 1
                elif status in ['DISK_DSBL', 'DISK_INVALID']:
                    health_counts['failed'] += 1
                elif status == 'DISK_NP':
                    health_counts['missing'] += 1
                elif status == 'DISK_NEW':
                    health_counts['new'] += 1
                else:
                    health_counts['unknown'] += 1
            
            return health_counts

        # Analyze health for each disk type
        health_summary = {}
        if raw_array_info.get('parities'):
            health_summary['parity_health'] = analyze_disk_health(raw_array_info['parities'], 'parity')
        if raw_array_info.get('disks'):
            health_summary['data_health'] = analyze_disk_health(raw_array_info['disks'], 'data')
        if raw_array_info.get('caches'):
            health_summary['cache_health'] = analyze_disk_health(raw_array_info['caches'], 'cache')
        
        # Overall array health assessment
        total_failed = sum(h.get('failed', 0) for h in health_summary.values())
        total_missing = sum(h.get('missing', 0) for h in health_summary.values())
        total_warning = sum(h.get('warning', 0) for h in health_summary.values())
        
        if total_failed > 0:
            overall_health = "CRITICAL"
        elif total_missing > 0:
            overall_health = "DEGRADED"
        elif total_warning > 0:
            overall_health = "WARNING"
        else:
            overall_health = "HEALTHY"
        
        summary['overall_health'] = overall_health
        summary['health_summary'] = health_summary

        return {"summary": summary, "details": raw_array_info}

    except Exception as e:
        logger.error(f"Error in get_array_status: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve array status: {str(e)}")

@mcp.tool()
async def get_network_config() -> Dict[str, Any]:
    """Retrieves network configuration details, including access URLs."""
    query = """
    query GetNetworkConfig {
      network {
        id
        accessUrls { type name ipv4 ipv6 }
      }
    }
    """
    try:
        logger.info("Executing get_network_config tool")
        response_data = await _make_graphql_request(query)
        return response_data.get("network", {})
    except Exception as e:
        logger.error(f"Error in get_network_config: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve network configuration: {str(e)}")

@mcp.tool()
async def get_registration_info() -> Dict[str, Any]:
    """Retrieves Unraid registration details."""
    query = """
    query GetRegistrationInfo {
      registration {
        id
        type
        keyFile { location contents }
        state
        expiration
        updateExpiration
      }
    }
    """
    try:
        logger.info("Executing get_registration_info tool")
        response_data = await _make_graphql_request(query)
        return response_data.get("registration", {})
    except Exception as e:
        logger.error(f"Error in get_registration_info: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve registration information: {str(e)}")

@mcp.tool()
async def get_connect_settings() -> Dict[str, Any]:
    """Retrieves settings related to Unraid Connect."""
    # Note: The SDL shows connect.settings.values, let's query that path
    query = """
    query GetConnectSettings {
      connect {
        settings {
          values {
            sandbox
            extraOrigins
            accessType
            forwardType
            port
            ssoUserIds
          }
        }
      }
    }
    """
    try:
        logger.info("Executing get_connect_settings tool")
        response_data = await _make_graphql_request(query)
        # Navigate down to the 'values' part of the response
        if response_data.get("connect") and response_data["connect"].get("settings"):
            return response_data["connect"]["settings"].get("values", {})
        return {} # Return empty if path not found
    except Exception as e:
        logger.error(f"Error in get_connect_settings: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve Unraid Connect settings: {str(e)}")

@mcp.tool()
async def get_unraid_variables() -> Dict[str, Any]:
    """Retrieves a selection of Unraid system variables and settings. 
       Note: Many variables are omitted due to API type issues (Int overflow/NaN).
    """
    # Querying a smaller, curated set of fields to avoid Int overflow and NaN issues
    # pending Unraid API schema fixes for the full Vars type.
    query = """
    query GetSelectiveUnraidVariables {
      vars {
        id
        version
        name
        timeZone
        comment
        security
        workgroup
        domain
        domainShort
        hideDotFiles
        localMaster
        enableFruit
        useNtp
        # ntpServer1, ntpServer2, ... are strings, should be okay but numerous
        domainLogin # Boolean
        sysModel # String
        # sysArraySlots, sysCacheSlots are Int, were problematic (NaN)
        sysFlashSlots # Int, might be okay if small and always set
        useSsl # Boolean
        port # Int, usually small
        portssl # Int, usually small
        localTld # String
        bindMgt # Boolean
        useTelnet # Boolean
        porttelnet # Int, usually small
        useSsh # Boolean
        portssh # Int, usually small
        startPage # String
        startArray # Boolean
        # spindownDelay, queueDepth are Int, potentially okay if always set
        # defaultFormat, defaultFsType are String
        shutdownTimeout # Int, potentially okay
        # luksKeyfile is String
        # pollAttributes, pollAttributesDefault, pollAttributesStatus are Int/String, were problematic (NaN or type)
        # nrRequests, nrRequestsDefault, nrRequestsStatus were problematic
        # mdNumStripes, mdNumStripesDefault, mdNumStripesStatus were problematic
        # mdSyncWindow, mdSyncWindowDefault, mdSyncWindowStatus were problematic
        # mdSyncThresh, mdSyncThreshDefault, mdSyncThreshStatus were problematic
        # mdWriteMethod, mdWriteMethodDefault, mdWriteMethodStatus were problematic
        # shareDisk, shareUser, shareUserInclude, shareUserExclude are String arrays/String
        shareSmbEnabled # Boolean
        shareNfsEnabled # Boolean
        shareAfpEnabled # Boolean
        # shareInitialOwner, shareInitialGroup are String
        shareCacheEnabled # Boolean
        # shareCacheFloor is String (numeric string?)
        # shareMoverSchedule, shareMoverLogging are String
        # fuseRemember, fuseRememberDefault, fuseRememberStatus are String/Boolean, were problematic
        # fuseDirectio, fuseDirectioDefault, fuseDirectioStatus are String/Boolean, were problematic
        shareAvahiEnabled # Boolean
        # shareAvahiSmbName, shareAvahiSmbModel, shareAvahiAfpName, shareAvahiAfpModel are String
        safeMode # Boolean
        startMode # String
        configValid # Boolean
        configError # String
        joinStatus # String
        deviceCount # Int, might be okay
        flashGuid # String
        flashProduct # String
        flashVendor # String
        # regCheck, regFile, regGuid, regTy, regState, regTo, regTm, regTm2, regGen are varied, mostly String/Int
        # sbName, sbVersion, sbUpdated, sbEvents, sbState, sbClean, sbSynced, sbSyncErrs, sbSynced2, sbSyncExit are varied
        # mdColor, mdNumDisks, mdNumDisabled, mdNumInvalid, mdNumMissing, mdNumNew, mdNumErased are Int, potentially okay if counts
        # mdResync, mdResyncCorr, mdResyncPos, mdResyncDb, mdResyncDt, mdResyncAction are varied (Int/Boolean/String)
        # mdResyncSize was an overflow
        mdState # String (enum)
        mdVersion # String
        # cacheNumDevices, cacheSbNumDisks were problematic (NaN)
        # fsState, fsProgress, fsCopyPrcnt, fsNumMounted, fsNumUnmountable, fsUnmountableMask are varied
        shareCount # Int, might be okay
        shareSmbCount # Int, might be okay
        shareNfsCount # Int, might be okay
        shareAfpCount # Int, might be okay
        shareMoverActive # Boolean
        csrfToken # String
      }
    }
    """
    try:
        logger.info("Executing get_unraid_variables tool with a selective query")
        response_data = await _make_graphql_request(query)
        return response_data.get("vars", {})
    except Exception as e:
        logger.error(f"Error in get_unraid_variables: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve Unraid variables: {str(e)}")

@mcp.tool()
async def list_docker_containers(skip_cache: Optional[bool] = False) -> List[Dict[str, Any]]:
    """Lists all Docker containers on the Unraid system."""
    query = """
    query ListDockerContainers($skipCache: Boolean!) {
      docker {
        containers(skipCache: $skipCache) {
          id
          names
          image
          imageId
          command
          created
          ports { ip privatePort publicPort type }
          sizeRootFs
          labels # JSONObject
          state
          status
          hostConfig { networkMode }
          # networkSettings # JSONObject, potentially large, omit for list view
          # mounts # JSONObject array, potentially large, omit for list view
          autoStart
        }
      }
    }
    """
    variables = {"skipCache": skip_cache}
    try:
        logger.info(f"Executing list_docker_containers tool with skip_cache={skip_cache}")
        response_data = await _make_graphql_request(query, variables)
        if response_data.get("docker"):
            return response_data["docker"].get("containers", [])
        return []
    except Exception as e:
        logger.error(f"Error in list_docker_containers: {e}", exc_info=True)
        raise ToolError(f"Failed to list Docker containers: {str(e)}")

@mcp.tool()
async def manage_docker_container(container_id: str, action: str) -> Dict[str, Any]:
    """Starts or stops a specific Docker container. Action must be 'start' or 'stop'."""
    if action.lower() not in ["start", "stop"]:
        logger.warning(f"Invalid action '{action}' for manage_docker_container")
        raise ToolError("Invalid action. Must be 'start' or 'stop'.")

    mutation_name = action.lower()
    query = f"""
    mutation ManageDockerContainer($id: PrefixedID!) {{
      docker {{
        {mutation_name}(id: $id) {{
          id
          names
          image
          state
          status
          autoStart
        }}
      }}
    }}
    """
    variables = {"id": container_id}
    try:
        logger.info(f"Executing manage_docker_container tool: action={action}, id={container_id}")
        response_data = await _make_graphql_request(query, variables)
        if response_data.get("docker") and response_data["docker"].get(mutation_name):
            return response_data["docker"][mutation_name]
        raise ToolError(f"Failed to {action} container or unexpected response structure.")
    except Exception as e:
        logger.error(f"Error in manage_docker_container ({action}): {e}", exc_info=True)
        raise ToolError(f"Failed to {action} Docker container: {str(e)}")

@mcp.tool()
async def get_docker_container_details(container_identifier: str) -> Dict[str, Any]:
    """Retrieves detailed information for a specific Docker container by its ID or name."""
    # This tool fetches all containers and then filters by ID or name.
    # More detailed query for a single container if found:
    detailed_query_fields = """
          id
          names
          image
          imageId
          command
          created
          ports { ip privatePort publicPort type }
          sizeRootFs
          labels # JSONObject
          state
          status
          hostConfig { networkMode }
          networkSettings # JSONObject
          mounts # JSONObject array
          autoStart
    """

    # Fetch all containers first
    list_query = f"""
    query GetAllContainerDetailsForFiltering {{
      docker {{
        containers(skipCache: false) {{
          {detailed_query_fields}
        }}
      }}
    }}
    """
    try:
        logger.info(f"Executing get_docker_container_details for identifier: {container_identifier}")
        response_data = await _make_graphql_request(list_query)
        
        containers = []
        if response_data.get("docker"):
            containers = response_data["docker"].get("containers", [])
        
        for container in containers:
            if container.get("id") == container_identifier or container_identifier in container.get("names", []):
                logger.info(f"Found container {container_identifier}")
                return container
        
        logger.warning(f"Container with identifier '{container_identifier}' not found.")
        raise ToolError(f"Container '{container_identifier}' not found.")

    except Exception as e:
        logger.error(f"Error in get_docker_container_details: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve Docker container details: {str(e)}")

@mcp.tool()
async def list_vms() -> List[Dict[str, Any]]:
    """Lists all Virtual Machines (VMs) on the Unraid system and their current state."""
    query = """
    query ListVMs {
      vms {
        domains {
          uuid
          name
          state
        }
      }
    }
    """
    try:
        logger.info("Executing list_vms tool")
        response_data = await _make_graphql_request(query)
        if response_data.get("vms"):
            # The schema shows vms.domains and vms.domain (both resolving to [VmDomain!])
            # Prefer .domains if available, else .domain
            if response_data["vms"].get("domains") is not None:
                return response_data["vms"].get("domains", [])
            elif response_data["vms"].get("domain") is not None:
                 return response_data["vms"].get("domain", [])
        return []
    except Exception as e:
        logger.error(f"Error in list_vms: {e}", exc_info=True)
        raise ToolError(f"Failed to list virtual machines: {str(e)}")

@mcp.tool()
async def manage_vm(vm_uuid: str, action: str) -> Dict[str, Any]:
    """Manages a VM: start, stop, pause, resume, force_stop, reboot, reset. Uses VM UUID."""
    valid_actions = ["start", "stop", "pause", "resume", "forceStop", "reboot", "reset"] # Added reset operation
    if action not in valid_actions:
        logger.warning(f"Invalid action '{action}' for manage_vm")
        raise ToolError(f"Invalid action. Must be one of {valid_actions}.")

    mutation_name = action
    query = f"""
    mutation ManageVM($id: PrefixedID!) {{
      vm {{
        {mutation_name}(id: $id)
      }}
    }}
    """
    variables = {"id": vm_uuid}
    try:
        logger.info(f"Executing manage_vm tool: action={action}, uuid={vm_uuid}")
        response_data = await _make_graphql_request(query, variables)
        if response_data.get("vm") and mutation_name in response_data["vm"]:
            # Mutations for VM return Boolean for success
            success = response_data["vm"][mutation_name]
            return {"success": success, "action": action, "vm_uuid": vm_uuid}
        raise ToolError(f"Failed to {action} VM or unexpected response structure.")
    except Exception as e:
        logger.error(f"Error in manage_vm ({action}): {e}", exc_info=True)
        raise ToolError(f"Failed to {action} virtual machine: {str(e)}")

@mcp.tool()
async def get_vm_details(vm_identifier: str) -> Dict[str, Any]:
    """Retrieves detailed information for a specific VM by its UUID or name."""
    # VmDomain type in SDL has: uuid, name, state
    # This tool filters the list_vms output to find a specific VM.
    try:
        logger.info(f"Executing get_vm_details for identifier: {vm_identifier}")
        vms = await list_vms() # This returns a list of dicts

        for vm_data in vms:
            if vm_data.get("uuid") == vm_identifier or vm_data.get("name") == vm_identifier:
                logger.info(f"Found VM {vm_identifier}")
                return vm_data
        
        logger.warning(f"VM with identifier '{vm_identifier}' not found.")
        raise ToolError(f"VM '{vm_identifier}' not found.")

    except Exception as e:
        logger.error(f"Error in get_vm_details: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve VM details: {str(e)}")

@mcp.tool()
async def get_shares_info() -> List[Dict[str, Any]]:
    """Retrieves information about user shares."""
    query = """
    query GetSharesInfo {
      shares {
        id
        name
        free
        used
        size
        include
        exclude
        cache
        nameOrig
        comment
        allocator
        splitLevel
        floor
        cow
        color
        luksStatus
      }
    }
    """
    try:
        logger.info("Executing get_shares_info tool")
        response_data = await _make_graphql_request(query)
        return response_data.get("shares", [])
    except Exception as e:
        logger.error(f"Error in get_shares_info: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve shares information: {str(e)}")

@mcp.tool()
async def get_notifications_overview() -> Dict[str, Any]:
    """Retrieves an overview of system notifications (unread and archive counts by severity)."""
    query = """
    query GetNotificationsOverview {
      notifications {
        overview {
          unread { info warning alert total }
          archive { info warning alert total }
        }
      }
    }
    """
    try:
        logger.info("Executing get_notifications_overview tool")
        response_data = await _make_graphql_request(query)
        if response_data.get("notifications"):
            return response_data["notifications"].get("overview", {})
        return {}
    except Exception as e:
        logger.error(f"Error in get_notifications_overview: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve notifications overview: {str(e)}")

@mcp.tool()
async def list_notifications(
    type: str, 
    offset: int, 
    limit: int, 
    importance: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists notifications with filtering. Type: UNREAD/ARCHIVE. Importance: INFO/WARNING/ALERT."""
    query = """
    query ListNotifications($filter: NotificationFilter!) {
      notifications {
        list(filter: $filter) {
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
    variables = {
        "filter": {
            "type": type.upper(),
            "offset": offset,
            "limit": limit,
            "importance": importance.upper() if importance else None
        }
    }
    # Remove null importance from variables if not provided, as GraphQL might be strict
    if not importance:
        del variables["filter"]["importance"]
        
    try:
        logger.info(f"Executing list_notifications: type={type}, offset={offset}, limit={limit}, importance={importance}")
        response_data = await _make_graphql_request(query, variables)
        if response_data.get("notifications"):
            return response_data["notifications"].get("list", [])
        return []
    except Exception as e:
        logger.error(f"Error in list_notifications: {e}", exc_info=True)
        raise ToolError(f"Failed to list notifications: {str(e)}")

@mcp.tool()
async def list_available_log_files() -> List[Dict[str, Any]]:
    """Lists all available log files that can be queried."""
    query = """
    query ListLogFiles {
      logFiles {
        name
        path
        size
        modifiedAt
      }
    }
    """
    try:
        logger.info("Executing list_available_log_files tool")
        response_data = await _make_graphql_request(query)
        return response_data.get("logFiles", [])
    except Exception as e:
        logger.error(f"Error in list_available_log_files: {e}", exc_info=True)
        raise ToolError(f"Failed to list available log files: {str(e)}")

@mcp.tool()
async def get_logs(log_file_path: str, tail_lines: Optional[int] = 100) -> Dict[str, Any]:
    """Retrieves content from a specific log file, defaulting to the last 100 lines."""
    # The Unraid GraphQL API Query.logFile takes 'lines' and 'startLine'.
    # To implement 'tail_lines', we would ideally need to know the total lines first,
    # then calculate startLine. However, Query.logFile itself returns totalLines.
    # A simple approach for 'tail' is to request a large number of lines if totalLines is not known beforehand,
    # and let the API handle it, or make two calls (one to get totalLines, then another).
    # For now, let's assume 'lines' parameter in Query.logFile effectively means tail if startLine is not given.
    # If not, this tool might need to be smarter or the API might not directly support 'tail' easily.
    # The SDL for LogFileContent implies it returns startLine, so it seems aware of ranges.

    # Let's try fetching with just 'lines' to see if it acts as a tail, 
    # or if we need Query.logFiles first to get totalLines for calculation.
    # For robust tailing, one might need to fetch totalLines first, then calculate start_line for the tail.
    # Simplified: query for the last 'tail_lines'. If the API doesn't support tailing this way, we may need adjustment.
    # The current plan is to pass 'lines=tail_lines' directly.

    query = """
    query GetLogContent($path: String!, $lines: Int) {
      logFile(path: $path, lines: $lines) {
        path
        content
        totalLines
        startLine
      }
    }
    """
    variables = {"path": log_file_path, "lines": tail_lines}
    try:
        logger.info(f"Executing get_logs for {log_file_path}, tail_lines={tail_lines}")
        response_data = await _make_graphql_request(query, variables)
        return response_data.get("logFile", {})
    except Exception as e:
        logger.error(f"Error in get_logs for {log_file_path}: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve logs from {log_file_path}: {str(e)}")

@mcp.tool()
async def list_physical_disks() -> List[Dict[str, Any]]:
    """Lists all physical disks recognized by the Unraid system."""
    # Querying an extremely minimal set of fields for diagnostics
    query = """ 
    query ListPhysicalDisksMinimal {
      disks {
        id
        device
        name
      }
    }
    """
    try:
        logger.info("Executing list_physical_disks tool with minimal query and increased timeout")
        # Increased read timeout for this potentially slow query
        long_timeout = httpx.Timeout(10.0, read=90.0, connect=5.0) 
        response_data = await _make_graphql_request(query, custom_timeout=long_timeout)
        return response_data.get("disks", [])
    except Exception as e:
        logger.error(f"Error in list_physical_disks: {e}", exc_info=True)
        raise ToolError(f"Failed to list physical disks: {str(e)}")

@mcp.tool()
async def get_disk_details(disk_id: str) -> Dict[str, Any]:
    """Retrieves detailed SMART information and partition data for a specific physical disk."""
    # Enhanced query with more comprehensive disk information
    query = """
    query GetDiskDetails($id: PrefixedID!) {
      disk(id: $id) {
        id
        device
        type
        name
        vendor
        model
        size
        firmwareRevision
        serialNum
        interfaceType
        smartStatus
        rotational
        partitions {
          name
          fsType
          size
          mountPoint
          label
        }
        # SMART attributes if available
        smartAttributes {
          id
          name
          value
          worst
          threshold
          rawValue
          status
        }
      }
    }
    """
    variables = {"id": disk_id}
    try:
        logger.info(f"Executing get_disk_details for disk: {disk_id}")
        response_data = await _make_graphql_request(query, variables)
        raw_disk = response_data.get("disk", {})
        
        if not raw_disk:
            raise ToolError(f"Disk '{disk_id}' not found")
        
        # Process disk information for human-readable output
        def format_bytes(bytes_value):
            if bytes_value is None: return "N/A"
            bytes_value = int(bytes_value)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} EB"

        summary = {
            'disk_id': raw_disk.get('id'),
            'device': raw_disk.get('device'),
            'name': raw_disk.get('name'),
            'vendor_model': f"{raw_disk.get('vendor', '')} {raw_disk.get('model', '')}".strip(),
            'serial_number': raw_disk.get('serialNum'),
            'size_formatted': format_bytes(raw_disk.get('size')),
            'interface': raw_disk.get('interfaceType'),
            'smart_status': raw_disk.get('smartStatus'),
            'disk_type': 'SSD' if not raw_disk.get('rotational', True) else 'HDD',
            'firmware': raw_disk.get('firmwareRevision'),
            'partition_count': len(raw_disk.get('partitions', [])),
            'total_partition_size': format_bytes(sum(p.get('size', 0) for p in raw_disk.get('partitions', []) if p.get('size')))
        }
        
        # Process SMART attributes if available
        smart_summary = {}
        if raw_disk.get('smartAttributes'):
            critical_attributes = {}
            for attr in raw_disk['smartAttributes']:
                attr_name = attr.get('name', '').lower()
                # Track critical SMART attributes
                if any(keyword in attr_name for keyword in ['temperature', 'reallocated', 'pending', 'uncorrectable', 'power_on_hours']):
                    critical_attributes[attr.get('name', f"ID_{attr.get('id')}")] = {
                        'value': attr.get('value'),
                        'threshold': attr.get('threshold'),
                        'raw_value': attr.get('rawValue'),
                        'status': attr.get('status')
                    }
            smart_summary = {
                'attributes_count': len(raw_disk['smartAttributes']),
                'critical_attributes': critical_attributes
            }

        return {
            'summary': summary,
            'smart_summary': smart_summary,
            'partitions': raw_disk.get('partitions', []),
            'details': raw_disk
        }
        
    except Exception as e:
        logger.error(f"Error in get_disk_details for {disk_id}: {e}", exc_info=True)
        raise ToolError(f"Failed to retrieve disk details for {disk_id}: {str(e)}")

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Returns comprehensive health status of the Unraid MCP server and system for monitoring purposes."""
    import datetime
    import time
    
    start_time = time.time()
    health_status = "healthy"
    issues = []
    
    try:
        # Enhanced health check with multiple system components
        comprehensive_query = """
        query ComprehensiveHealthCheck {
          info {
            machineId
            time
            versions { unraid }
            os { uptime }
          }
          array {
            state
          }
          notifications {
            overview {
              unread { alert warning total }
            }
          }
          docker {
            containers(skipCache: true) {
              id
              state
              status
            }
          }
        }
        """
        
        response_data = await _make_graphql_request(comprehensive_query)
        api_latency = round((time.time() - start_time) * 1000, 2)  # ms
        
        # Base health info
        health_info = {
            "status": health_status,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "api_latency_ms": api_latency,
            "server": {
                "name": "Unraid MCP Server",
                "version": "0.1.0",
                "transport": UNRAID_MCP_TRANSPORT,
                "host": UNRAID_MCP_HOST,
                "port": UNRAID_MCP_PORT,
                "process_uptime_seconds": time.time() - start_time  # Rough estimate
            }
        }
        
        if not response_data:
            health_status = "unhealthy"
            issues.append("No response from Unraid API")
            health_info["status"] = health_status
            health_info["issues"] = issues
            return health_info
        
        # System info analysis
        info = response_data.get("info", {})
        if info:
            health_info["unraid_system"] = {
                "status": "connected",
                "url": UNRAID_API_URL,
                "machine_id": info.get("machineId"),
                "time": info.get("time"),
                "version": info.get("versions", {}).get("unraid"),
                "uptime": info.get("os", {}).get("uptime")
            }
        else:
            health_status = "degraded"
            issues.append("Unable to retrieve system info")
        
        # Array health analysis
        array_info = response_data.get("array", {})
        if array_info:
            array_state = array_info.get("state", "unknown")
            health_info["array_status"] = {
                "state": array_state,
                "healthy": array_state in ["STARTED", "STOPPED"]
            }
            if array_state not in ["STARTED", "STOPPED"]:
                health_status = "warning"
                issues.append(f"Array in unexpected state: {array_state}")
        else:
            health_status = "warning"
            issues.append("Unable to retrieve array status")
        
        # Notifications analysis
        notifications = response_data.get("notifications", {})
        if notifications and notifications.get("overview"):
            unread = notifications["overview"].get("unread", {})
            alert_count = unread.get("alert", 0)
            warning_count = unread.get("warning", 0)
            total_unread = unread.get("total", 0)
            
            health_info["notifications"] = {
                "unread_total": total_unread,
                "unread_alerts": alert_count,
                "unread_warnings": warning_count,
                "has_critical_notifications": alert_count > 0
            }
            
            if alert_count > 0:
                health_status = "warning"
                issues.append(f"{alert_count} unread alert notification(s)")
        
        # Docker services analysis  
        docker_info = response_data.get("docker", {})
        if docker_info and docker_info.get("containers"):
            containers = docker_info["containers"]
            running_containers = [c for c in containers if c.get("state") == "running"]
            stopped_containers = [c for c in containers if c.get("state") == "exited"]
            
            health_info["docker_services"] = {
                "total_containers": len(containers),
                "running_containers": len(running_containers),
                "stopped_containers": len(stopped_containers),
                "containers_healthy": len([c for c in containers if c.get("status", "").startswith("Up")])
            }
        
        # API performance assessment
        if api_latency > 5000:  # > 5 seconds
            health_status = "warning"
            issues.append(f"High API latency: {api_latency}ms")
        elif api_latency > 10000:  # > 10 seconds
            health_status = "degraded"
            issues.append(f"Very high API latency: {api_latency}ms")
        
        # Final status determination
        health_info["status"] = health_status
        if issues:
            health_info["issues"] = issues
        
        # Add performance metrics
        health_info["performance"] = {
            "api_response_time_ms": api_latency,
            "health_check_duration_ms": round((time.time() - start_time) * 1000, 2)
        }
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "error": str(e),
            "api_latency_ms": round((time.time() - start_time) * 1000, 2) if 'start_time' in locals() else None,
            "server": {
                "name": "Unraid MCP Server",
                "version": "0.1.0",
                "transport": UNRAID_MCP_TRANSPORT,
                "host": UNRAID_MCP_HOST,
                "port": UNRAID_MCP_PORT
            }
        }

# =============================================================================
# SUBSCRIPTION DIAGNOSTICS TOOLS
# =============================================================================

@mcp.tool()
async def test_subscription_query(subscription_query: str) -> Dict[str, Any]:
    """
    Test a GraphQL subscription query directly to debug schema issues.
    Use this to find working subscription field names and structure.
    """
    try:
        logger.info(f"[TEST_SUBSCRIPTION] Testing query: {subscription_query}")
        
        # Create a temporary WebSocket connection to test the query
        import websockets
        import json
        
        # Build WebSocket URL
        ws_url = UNRAID_API_URL.replace("https://", "wss://").replace("http://", "ws://") + "/graphql"
        
        # Test connection
        async with websockets.connect(
            ws_url,
            extra_headers={"Authorization": f"Bearer {UNRAID_API_KEY}"},
            ssl=UNRAID_VERIFY_SSL,
            ping_interval=30,
            ping_timeout=10
        ) as websocket:
            
            # Send connection init
            await websocket.send(json.dumps({
                "type": "connection_init",
                "payload": {"Authorization": f"Bearer {UNRAID_API_KEY}"}
            }))
            
            # Wait for ack
            response = await websocket.recv()
            init_response = json.loads(response)
            
            if init_response.get("type") != "connection_ack":
                return {"error": f"Connection failed: {init_response}"}
            
            # Send subscription
            await websocket.send(json.dumps({
                "id": "test",
                "type": "start",
                "payload": {"query": subscription_query}
            }))
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                result = json.loads(response)
                
                logger.info(f"[TEST_SUBSCRIPTION] Response: {result}")
                return {
                    "success": True,
                    "response": result,
                    "query_tested": subscription_query
                }
                
            except asyncio.TimeoutError:
                return {
                    "success": True,
                    "response": "No immediate response (subscriptions may only send data on changes)",
                    "query_tested": subscription_query,
                    "note": "Connection successful, subscription may be waiting for events"
                }
                
    except Exception as e:
        logger.error(f"[TEST_SUBSCRIPTION] Error: {e}", exc_info=True)
        return {
            "error": str(e),
            "query_tested": subscription_query
        }

@mcp.tool()
async def diagnose_subscriptions() -> Dict[str, Any]:
    """
    Comprehensive diagnostic tool for subscription system.
    Shows detailed status, connection states, errors, and troubleshooting info.
    """
    # Ensure subscriptions are started before diagnosing
    await ensure_subscriptions_started()
    
    try:
        logger.info("[DIAGNOSTIC] Running subscription diagnostics...")
        
        # Get comprehensive status
        status = subscription_manager.get_subscription_status()
        
        # Add environment info
        diagnostic_info = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "auto_start_enabled": subscription_manager.auto_start_enabled,
                "max_reconnect_attempts": subscription_manager.max_reconnect_attempts,
                "unraid_api_url": UNRAID_API_URL[:50] + "..." if UNRAID_API_URL else None,
                "api_key_configured": bool(UNRAID_API_KEY),
                "websocket_url": None
            },
            "subscriptions": status,
            "summary": {
                "total_configured": len(subscription_manager.subscription_configs),
                "auto_start_count": sum(1 for s in subscription_manager.subscription_configs.values() if s.get("auto_start")),
                "active_count": len(subscription_manager.active_subscriptions),
                "with_data": len(subscription_manager.resource_data),
                "in_error_state": 0,
                "connection_issues": []
            }
        }
        
        # Calculate WebSocket URL
        if UNRAID_API_URL:
            if UNRAID_API_URL.startswith('https://'):
                ws_url = 'wss://' + UNRAID_API_URL[len('https://'):]
            elif UNRAID_API_URL.startswith('http://'):
                ws_url = 'ws://' + UNRAID_API_URL[len('http://'):]
            else:
                ws_url = UNRAID_API_URL
            if not ws_url.endswith('/graphql'):
                ws_url = ws_url.rstrip('/') + '/graphql'
            diagnostic_info["environment"]["websocket_url"] = ws_url
        
        # Analyze issues
        for sub_name, sub_status in status.items():
            runtime = sub_status.get("runtime", {})
            connection_state = runtime.get("connection_state", "unknown")
            
            if connection_state in ["error", "auth_failed", "timeout", "max_retries_exceeded"]:
                diagnostic_info["summary"]["in_error_state"] += 1
                
            if runtime.get("last_error"):
                diagnostic_info["summary"]["connection_issues"].append({
                    "subscription": sub_name,
                    "state": connection_state,
                    "error": runtime["last_error"]
                })
        
        # Add troubleshooting recommendations
        recommendations = []
        
        if not diagnostic_info["environment"]["api_key_configured"]:
            recommendations.append("CRITICAL: No API key configured. Set UNRAID_API_KEY environment variable.")
        
        if diagnostic_info["summary"]["in_error_state"] > 0:
            recommendations.append("Some subscriptions are in error state. Check 'connection_issues' for details.")
            
        if diagnostic_info["summary"]["with_data"] == 0:
            recommendations.append("No subscriptions have received data yet. Check WebSocket connectivity and authentication.")
            
        if diagnostic_info["summary"]["active_count"] < diagnostic_info["summary"]["auto_start_count"]:
            recommendations.append("Not all auto-start subscriptions are active. Check server startup logs.")
            
        diagnostic_info["troubleshooting"] = {
            "recommendations": recommendations,
            "log_commands": [
                "Check server logs for [WEBSOCKET:*], [AUTH:*], [SUBSCRIPTION:*] prefixed messages",
                "Look for connection timeout or authentication errors",
                "Verify Unraid API URL is accessible and supports GraphQL subscriptions"
            ],
            "next_steps": [
                "If authentication fails: Verify API key has correct permissions",
                "If connection fails: Check network connectivity to Unraid server", 
                "If no data received: Enable DEBUG logging to see detailed protocol messages"
            ]
        }
        
        logger.info(f"[DIAGNOSTIC] Completed. Active: {diagnostic_info['summary']['active_count']}, With data: {diagnostic_info['summary']['with_data']}, Errors: {diagnostic_info['summary']['in_error_state']}")
        return diagnostic_info
        
    except Exception as e:
        logger.error(f"[DIAGNOSTIC] Failed to generate diagnostics: {e}")
        raise ToolError(f"Failed to generate diagnostics: {str(e)}")

# =============================================================================
# RCLONE MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
async def list_rclone_remotes() -> List[Dict[str, Any]]:
    """Retrieves all configured RClone remotes with their configuration details."""
    try:
        query = """
        query ListRCloneRemotes {
            rclone {
                remotes {
                    name
                    type
                    parameters
                    config
                }
            }
        }
        """
        
        response_data = await _make_graphql_request(query)
        
        if "rclone" in response_data and "remotes" in response_data["rclone"]:
            remotes = response_data["rclone"]["remotes"]
            logger.info(f"Retrieved {len(remotes)} RClone remotes")
            return remotes
        
        return []
        
    except Exception as e:
        logger.error(f"Failed to list RClone remotes: {str(e)}")
        raise ToolError(f"Failed to list RClone remotes: {str(e)}")

@mcp.tool()
async def get_rclone_config_form(provider_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get RClone configuration form schema for setting up new remotes.
    
    Args:
        provider_type: Optional provider type to get specific form (e.g., 's3', 'drive', 'dropbox')
    """
    try:
        query = """
        query GetRCloneConfigForm($formOptions: RCloneConfigFormInput) {
            rclone {
                configForm(formOptions: $formOptions) {
                    id
                    dataSchema
                    uiSchema
                }
            }
        }
        """
        
        variables = {}
        if provider_type:
            variables["formOptions"] = {"type": provider_type}
        
        response_data = await _make_graphql_request(query, variables)
        
        if "rclone" in response_data and "configForm" in response_data["rclone"]:
            form_data = response_data["rclone"]["configForm"]
            logger.info(f"Retrieved RClone config form for {provider_type or 'general'}")
            return form_data
        
        raise ToolError("No RClone config form data received")
        
    except Exception as e:
        logger.error(f"Failed to get RClone config form: {str(e)}")
        raise ToolError(f"Failed to get RClone config form: {str(e)}")

@mcp.tool()
async def create_rclone_remote(name: str, provider_type: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new RClone remote with the specified configuration.
    
    Args:
        name: Name for the new remote
        provider_type: Type of provider (e.g., 's3', 'drive', 'dropbox', 'ftp')
        config_data: Configuration parameters specific to the provider type
    """
    try:
        mutation = """
        mutation CreateRCloneRemote($input: CreateRCloneRemoteInput!) {
            rclone {
                createRCloneRemote(input: $input) {
                    name
                    type
                    parameters
                }
            }
        }
        """
        
        variables = {
            "input": {
                "name": name,
                "type": provider_type,
                "config": config_data
            }
        }
        
        response_data = await _make_graphql_request(mutation, variables)
        
        if "rclone" in response_data and "createRCloneRemote" in response_data["rclone"]:
            remote_info = response_data["rclone"]["createRCloneRemote"]
            logger.info(f"Successfully created RClone remote: {name}")
            return {
                "success": True,
                "message": f"RClone remote '{name}' created successfully",
                "remote": remote_info
            }
        
        raise ToolError("Failed to create RClone remote")
        
    except Exception as e:
        logger.error(f"Failed to create RClone remote {name}: {str(e)}")
        raise ToolError(f"Failed to create RClone remote {name}: {str(e)}")

@mcp.tool()
async def delete_rclone_remote(name: str) -> Dict[str, Any]:
    """
    Delete an existing RClone remote by name.
    
    Args:
        name: Name of the remote to delete
    """
    try:
        mutation = """
        mutation DeleteRCloneRemote($input: DeleteRCloneRemoteInput!) {
            rclone {
                deleteRCloneRemote(input: $input)
            }
        }
        """
        
        variables = {
            "input": {
                "name": name
            }
        }
        
        response_data = await _make_graphql_request(mutation, variables)
        
        if "rclone" in response_data and response_data["rclone"]["deleteRCloneRemote"]:
            logger.info(f"Successfully deleted RClone remote: {name}")
            return {
                "success": True,
                "message": f"RClone remote '{name}' deleted successfully"
            }
        
        raise ToolError(f"Failed to delete RClone remote '{name}'")
        
    except Exception as e:
        logger.error(f"Failed to delete RClone remote {name}: {str(e)}")
        raise ToolError(f"Failed to delete RClone remote {name}: {str(e)}")

def main():
    """Main entry point for the Unraid MCP server."""
    logger.info(f"Starting Unraid MCP Server on {UNRAID_MCP_HOST}:{UNRAID_MCP_PORT} using {UNRAID_MCP_TRANSPORT} transport...")
    try:
        # Subscriptions will auto-start on first async operation
        if UNRAID_MCP_TRANSPORT == "streamable-http":
            # Use the recommended Streamable HTTP transport
            mcp.run(
                transport="streamable-http", 
                host=UNRAID_MCP_HOST, 
                port=UNRAID_MCP_PORT,
                path="/mcp"  # Standard path for MCP
            )
        elif UNRAID_MCP_TRANSPORT == "sse":
            # Deprecated SSE transport - log warning
            logger.warning("SSE transport is deprecated and may be removed in a future version. Consider switching to 'streamable-http'.")
            mcp.run(
                transport="sse", 
                host=UNRAID_MCP_HOST, 
                port=UNRAID_MCP_PORT,
                path="/mcp"  # Keep custom path for SSE
            )
        elif UNRAID_MCP_TRANSPORT == "stdio":
            mcp.run()  # Defaults to stdio
        else:
            logger.error(f"Unsupported MCP_TRANSPORT: {UNRAID_MCP_TRANSPORT}. Choose 'streamable-http' (recommended), 'sse' (deprecated), or 'stdio'.")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Failed to start Unraid MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
