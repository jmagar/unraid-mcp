"""WebSocket subscription manager for real-time Unraid data.

This module manages GraphQL subscriptions over WebSocket connections,
providing real-time data streaming for MCP resources with comprehensive
error handling, reconnection logic, and authentication.
"""

import asyncio
import json
import os
import ssl
from datetime import datetime
from typing import Any

import websockets
from websockets.legacy.protocol import Subprotocol

from ..config.logging import logger
from ..config.settings import UNRAID_API_KEY, UNRAID_API_URL, UNRAID_VERIFY_SSL
from ..core.types import SubscriptionData


class SubscriptionManager:
    """Manages GraphQL subscriptions and converts them to MCP resources."""

    def __init__(self) -> None:
        self.active_subscriptions: dict[str, asyncio.Task[None]] = {}
        self.resource_data: dict[str, SubscriptionData] = {}
        self.websocket: websockets.WebSocketServerProtocol | None = None
        self.subscription_lock = asyncio.Lock()

        # Configuration
        self.auto_start_enabled = os.getenv("UNRAID_AUTO_START_SUBSCRIPTIONS", "true").lower() == "true"
        self.reconnect_attempts: dict[str, int] = {}
        self.max_reconnect_attempts = int(os.getenv("UNRAID_MAX_RECONNECT_ATTEMPTS", "10"))
        self.connection_states: dict[str, str] = {}  # Track connection state per subscription
        self.last_error: dict[str, str] = {}  # Track last error per subscription

        # Define subscription configurations
        self.subscription_configs = {
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

    async def auto_start_all_subscriptions(self) -> None:
        """Auto-start all subscriptions marked for auto-start."""
        if not self.auto_start_enabled:
            logger.info("[SUBSCRIPTION_MANAGER] Auto-start disabled")
            return

        logger.info("[SUBSCRIPTION_MANAGER] Starting auto-start process...")
        auto_start_count = 0

        for subscription_name, config in self.subscription_configs.items():
            if config.get("auto_start", False):
                try:
                    logger.info(f"[SUBSCRIPTION_MANAGER] Auto-starting subscription: {subscription_name}")
                    await self.start_subscription(subscription_name, str(config["query"]))
                    auto_start_count += 1
                except Exception as e:
                    logger.error(f"[SUBSCRIPTION_MANAGER] Failed to auto-start {subscription_name}: {e}")
                    self.last_error[subscription_name] = str(e)

        logger.info(f"[SUBSCRIPTION_MANAGER] Auto-start completed. Started {auto_start_count} subscriptions")

    async def start_subscription(self, subscription_name: str, query: str, variables: dict[str, Any] | None = None) -> None:
        """Start a GraphQL subscription and maintain it as a resource."""
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

    async def stop_subscription(self, subscription_name: str) -> None:
        """Stop a specific subscription."""
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

    async def _subscription_loop(self, subscription_name: str, query: str, variables: dict[str, Any] | None) -> None:
        """Main loop for maintaining a GraphQL subscription with comprehensive logging."""
        retry_delay: int | float = 5
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
                if not UNRAID_API_URL:
                    raise ValueError("UNRAID_API_URL is not configured")

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

                # Build SSL context for wss:// connections
                ssl_context = None
                if ws_url.startswith('wss://'):
                    if isinstance(UNRAID_VERIFY_SSL, str):
                        ssl_context = ssl.create_default_context(cafile=UNRAID_VERIFY_SSL)
                    elif UNRAID_VERIFY_SSL:
                        ssl_context = ssl.create_default_context()
                    else:
                        ssl_context = ssl._create_unverified_context()

                # Connection with timeout
                connect_timeout = 10
                logger.debug(f"[WEBSOCKET:{subscription_name}] Connection timeout: {connect_timeout}s")

                async with websockets.connect(
                    ws_url,
                    subprotocols=[Subprotocol("graphql-transport-ws"), Subprotocol("graphql-ws")],
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10,
                    ssl=ssl_context
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
                    init_payload: dict[str, Any] = {"type": init_type}

                    if UNRAID_API_KEY:
                        logger.debug(f"[AUTH:{subscription_name}] Adding authentication payload")
                        # Use standard X-API-Key header format (matching HTTP client)
                        auth_payload = {
                            "headers": {
                                "X-API-Key": UNRAID_API_KEY
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
                        init_preview = init_raw[:200] if isinstance(init_raw, str) else init_raw[:200].decode('utf-8', errors='replace')
                        logger.error(f"[PROTOCOL:{subscription_name}] Failed to decode init response: {init_preview}...")
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
                            msg_preview = message[:200] if isinstance(message, str) else message[:200].decode('utf-8', errors='replace')
                            logger.error(f"[PROTOCOL:{subscription_name}] Failed to decode message: {msg_preview}...")
                            logger.error(f"[PROTOCOL:{subscription_name}] JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"[DATA:{subscription_name}] Error processing message: {e}")
                            msg_preview = message[:200] if isinstance(message, str) else message[:200].decode('utf-8', errors='replace')
                            logger.debug(f"[DATA:{subscription_name}] Raw message: {msg_preview}...")

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

    def get_resource_data(self, resource_name: str) -> dict[str, Any] | None:
        """Get current resource data with enhanced logging."""
        logger.debug(f"[RESOURCE:{resource_name}] Resource data requested")

        if resource_name in self.resource_data:
            data = self.resource_data[resource_name]
            age_seconds = (datetime.now() - data.last_updated).total_seconds()
            logger.debug(f"[RESOURCE:{resource_name}] Data found, age: {age_seconds:.1f}s")
            return data.data
        else:
            logger.debug(f"[RESOURCE:{resource_name}] No data available")
            return None

    def list_active_subscriptions(self) -> list[str]:
        """List all active subscriptions."""
        active = list(self.active_subscriptions.keys())
        logger.debug(f"[SUBSCRIPTION_MANAGER] Active subscriptions: {active}")
        return active

    def get_subscription_status(self) -> dict[str, dict[str, Any]]:
        """Get detailed status of all subscriptions for diagnostics."""
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


# Global subscription manager instance
subscription_manager = SubscriptionManager()
