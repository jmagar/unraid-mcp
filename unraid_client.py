import os
import aiohttp
import json
import logging
import urllib.parse
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logging configuration from environment
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)

# Configure logging
logger = logging.getLogger("unraid_client")
logger.setLevel(log_level)

class UnraidApiError(Exception):
    """Exception raised for Unraid API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

class UnraidClient:
    """Client for communicating with the Unraid GraphQL API"""
    
    def __init__(self):
        """Initialize the Unraid API client"""
        self.api_url = os.getenv("UNRAID_API_URL")
        self.api_key = os.getenv("UNRAID_API_KEY")
        
        if not self.api_url or not self.api_key:
            raise ValueError("UNRAID_API_URL and UNRAID_API_KEY must be set in .env file")
        
        # Parse the URL to get the origin for CORS
        parsed_url = urllib.parse.urlparse(self.api_url)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
        self.headers = {
            "x-api-key": self.api_key,  # Use x-api-key header for authentication
            "Content-Type": "application/json",
            "Origin": origin,
            "Accept": "application/json"
        }
        logger.info(f"Initialized Unraid client with API URL: {self.api_url}")
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against the Unraid API
        
        Args:
            query: The GraphQL query or mutation to execute
            variables: Optional variables for the GraphQL query
            
        Returns:
            The JSON response from the API
            
        Raises:
            UnraidApiError: If the API request fails or returns GraphQL errors
        """
        if variables is None:
            variables = {}
            
        payload = {
            "query": query,
            "variables": variables
        }
        
        # Enhanced logging for templated queries
        query_type = "mutation" if "mutation" in query.strip()[:20].lower() else "query"
        operation_name = _extract_operation_name(query)
        
        if variables:
            logger.debug(f"Executing GraphQL {query_type} '{operation_name}' with variables: {json.dumps(variables)}")
        else:
            logger.debug(f"Executing GraphQL {query_type} '{operation_name}'")
            
        if log_level == logging.DEBUG:
            # Only log full queries at DEBUG level
            logger.debug(f"Full GraphQL {query_type}:\n{query}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)  # 30 second timeout
                ) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        logger.error(f"HTTP error {response.status}: {response_text}")
                        raise UnraidApiError(
                            f"API request failed with status {response.status}", 
                            status_code=response.status, 
                            response_text=response_text
                        )
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response: {response_text}")
                        raise UnraidApiError("Invalid JSON response from API", response_text=response_text)
                    
                    # Check for GraphQL errors
                    if "errors" in result:
                        errors = result["errors"]
                        error_message = "; ".join([error.get("message", "Unknown error") for error in errors])
                        logger.error(f"GraphQL errors: {error_message}")
                        raise UnraidApiError(f"GraphQL query failed: {error_message}")
                    
                    if "data" not in result:
                        logger.error(f"No data in response: {result}")
                        raise UnraidApiError("No data in API response")
                    
                    # Log successful query results
                    if "data" in result:
                        data_keys = list(result["data"].keys())
                        logger.debug(f"Received response for '{operation_name}' with data keys: {', '.join(data_keys)}")
                    
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise UnraidApiError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    # System Information Methods
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information
        
        Returns:
            Dictionary containing system information including OS, CPU, memory, and versions
        """
        query = """
        query {
            info {
                os {
                    platform
                    distro
                    release
                    uptime
                    hostname
                    kernel
                }
                cpu {
                    manufacturer
                    brand
                    cores
                    threads
                    speed
                    speedmax
                }
                memory {
                    total
                    free
                    used
                    active
                    available
                    swaptotal
                    swapused
                    swapfree
                }
                versions {
                    unraid
                    kernel
                    openssl
                    php
                    docker
                }
                system {
                    manufacturer
                    model
                    version
                    serial
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["info"]
    
    # Array Management Methods
    
    async def get_array_status(self) -> Dict[str, Any]:
        """Get array status information
        
        Returns:
            Dictionary containing array status, capacity, and disk information
        """
        query = """
        query {
            array {
                state
                capacity {
                    kilobytes {
                        free
                        used
                        total
                    }
                    disks {
                        free
                        used
                        total
                    }
                }
                parities {
                    id
                    name
                    size
                    temp
                    numErrors
                    status
                }
                disks {
                    id
                    name
                    size
                    status
                    temp
                    numReads
                    numWrites
                    numErrors
                    fsSize
                    fsFree
                    fsUsed
                }
                caches {
                    id
                    name
                    size
                    status
                    temp
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["array"]
    
    async def get_parity_history(self) -> List[Dict[str, Any]]:
        """Get parity check history
        
        Returns:
            List of dictionaries containing parity check history
        """
        query = """
        query {
            parityHistory {
                date
                duration
                speed
                status
                errors
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["parityHistory"]
    
    async def start_array(self) -> Dict[str, Any]:
        """Start the Unraid array
        
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation {
            startArray {
                state
            }
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["startArray"]
    
    async def stop_array(self) -> Dict[str, Any]:
        """Stop the Unraid array
        
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation {
            stopArray {
                state
            }
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["stopArray"]
    
    async def add_disk_to_array(self, disk_id: str, slot: Optional[int] = None) -> Dict[str, Any]:
        """Add a disk to the array
        
        Args:
            disk_id: The ID of the disk to add
            slot: Optional slot number for the disk
            
        Returns:
            Dictionary containing the result of the operation
        """
        variables = {"id": disk_id}
        if slot is not None:
            variables["slot"] = slot
            
        mutation = """
        mutation AddDiskToArray($id: ID!, $slot: Int) {
            addDiskToArray(input: {id: $id, slot: $slot}) {
                state
                disks {
                    id
                    name
                    status
                }
            }
        }
        """
        result = await self.execute_query(mutation, {"input": variables})
        return result["data"]["addDiskToArray"]
    
    async def remove_disk_from_array(self, disk_id: str) -> Dict[str, Any]:
        """Remove a disk from the array
        
        Args:
            disk_id: The ID of the disk to remove
            
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation RemoveDiskFromArray($id: ID!) {
            removeDiskFromArray(input: {id: $id}) {
                state
                disks {
                    id
                    name
                    status
                }
            }
        }
        """
        result = await self.execute_query(mutation, {"input": {"id": disk_id}})
        return result["data"]["removeDiskFromArray"]
    
    # Disk Operations Methods
    
    async def get_disks(self) -> List[Dict[str, Any]]:
        """Get information about all disks
        
        Returns:
            List of dictionaries containing disk information
        """
        query = """
        query {
            disks {
                device
                name
                size
                temperature
                smartStatus
                vendor
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["disks"]
    
    async def get_disk(self, disk_id: str) -> Dict[str, Any]:
        """Get information about a specific disk
        
        Args:
            disk_id: The ID of the disk
            
        Returns:
            Dictionary containing disk information
        """
        query = """
        query GetDisk($id: ID!) {
            disk(id: $id) {
                device
                name
                size
                temperature
                smartStatus
                vendor
            }
        }
        """
        variables = {"id": disk_id}
        result = await self.execute_query(query, variables)
        return result["data"]["disk"]
    
    async def mount_disk(self, disk_id: str) -> Dict[str, Any]:
        """Mount a disk
        
        Args:
            disk_id: The ID of the disk to mount
            
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation MountDisk($id: ID!) {
            mountArrayDisk(id: $id) {
                device
                name
            }
        }
        """
        result = await self.execute_query(mutation, {"id": disk_id})
        return result["data"]["mountArrayDisk"]
    
    async def unmount_disk(self, disk_id: str) -> Dict[str, Any]:
        """Unmount a disk
        
        Args:
            disk_id: The ID of the disk to unmount
            
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation UnmountDisk($id: ID!) {
            unmountArrayDisk(id: $id) {
                device
                name
            }
        }
        """
        result = await self.execute_query(mutation, {"id": disk_id})
        return result["data"]["unmountArrayDisk"]
    
    # Docker Management Methods
    
    async def get_docker_containers(self) -> List[Dict[str, Any]]:
        """Get information about Docker containers
        
        Returns:
            List of dictionaries containing container information
        """
        query = """
        query {
            docker {
                containers {
                    id
                    names
                    image
                    state
                    status
                    ports {
                        ip
                        privatePort
                        publicPort
                        type
                    }
                    autoStart
                    created
                    command
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["docker"]["containers"]
    
    async def get_docker_networks(self) -> List[Dict[str, Any]]:
        """Get information about Docker networks
        
        Returns:
            List of dictionaries containing network information
        """
        query = """
        query {
            docker {
                networks {
                    id
                    name
                    driver
                    scope
                    internal
                    attachable
                    created
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["docker"]["networks"]
    
    # VM Management Methods
    
    async def get_vms(self) -> Dict[str, Any]:
        """Get information about virtual machines
        
        Returns:
            Dictionary containing VM information
        """
        query = """
        query {
            vms {
                domain {
                    uuid
                    name
                    state
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["vms"]
    
    # User Management Methods
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get information about the current user
        
        Returns:
            Dictionary containing user information
        """
        query = """
        query {
            me {
                id
                name
                description
                roles
                permissions {
                    resource
                    actions
                }
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["me"]
    
    # Notification Methods
    
    async def get_notifications(self, importance=None, notification_type="UNREAD", offset=0, limit=10) -> Dict[str, Any]:
        """Get system notifications
        
        Args:
            importance: Filter by importance (ALERT, INFO, WARNING)
            notification_type: Filter by type (UNREAD, ARCHIVE)
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dictionary containing notifications
        """
        variables = {
            "filter": {
                "type": notification_type,
                "offset": offset,
                "limit": limit
            }
        }
        
        if importance:
            variables["filter"]["importance"] = importance
            
        query = """
        query GetNotifications($filter: NotificationFilter!) {
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
                list(filter: $filter) {
                    id
                    title
                    subject
                    description
                    importance
                    timestamp
                    type
                    link
                }
            }
        }
        """
        result = await self.execute_query(query, variables)
        return result["data"]["notifications"]
    
    async def create_notification(self, title: str, subject: str, description: str, importance: str, link: Optional[str] = None) -> Dict[str, Any]:
        """Create a system notification
        
        Args:
            title: Notification title
            subject: Notification subject
            description: Notification description
            importance: Notification importance (ALERT, INFO, WARNING)
            link: Optional link for the notification
            
        Returns:
            Dictionary containing the created notification
        """
        variables = {
            "input": {
                "title": title,
                "subject": subject,
                "description": description,
                "importance": importance
            }
        }
        
        if link:
            variables["input"]["link"] = link
            
        mutation = """
        mutation CreateNotification($input: NotificationData!) {
            createNotification(input: $input) {
                id
                title
                subject
                importance
                timestamp
            }
        }
        """
        result = await self.execute_query(mutation, variables)
        return result["data"]["createNotification"]
    
    async def archive_notification(self, notification_id: str) -> Dict[str, Any]:
        """Archive a notification
        
        Args:
            notification_id: The ID of the notification to archive
            
        Returns:
            Dictionary containing the archived notification
        """
        mutation = """
        mutation ArchiveNotification($id: String!) {
            archiveNotification(id: $id) {
                id
                title
                type
            }
        }
        """
        result = await self.execute_query(mutation, {"id": notification_id})
        return result["data"]["archiveNotification"]
    
    async def unread_notification(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as unread
        
        Args:
            notification_id: The ID of the notification to mark as unread
            
        Returns:
            Dictionary containing the notification
        """
        mutation = """
        mutation UnreadNotification($id: String!) {
            unreadNotification(id: $id) {
                id
                title
                type
            }
        }
        """
        result = await self.execute_query(mutation, {"id": notification_id})
        return result["data"]["unreadNotification"]
    
    # Parity Check Methods
    
    async def start_parity_check(self, correct: bool = False) -> Dict[str, Any]:
        """Start a parity check
        
        Args:
            correct: Whether to correct errors found during the check
            
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation StartParityCheck($correct: Boolean) {
            startParityCheck(correct: $correct)
        }
        """
        result = await self.execute_query(mutation, {"correct": correct})
        return result["data"]["startParityCheck"]
    
    async def pause_parity_check(self) -> Dict[str, Any]:
        """Pause a running parity check
        
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation {
            pauseParityCheck
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["pauseParityCheck"]
    
    async def resume_parity_check(self) -> Dict[str, Any]:
        """Resume a paused parity check
        
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation {
            resumeParityCheck
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["resumeParityCheck"]
    
    async def cancel_parity_check(self) -> Dict[str, Any]:
        """Cancel a running parity check
        
        Returns:
            Dictionary containing the result of the operation
        """
        mutation = """
        mutation {
            cancelParityCheck
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["cancelParityCheck"]
    
    # Share Management Methods
    
    async def get_shares(self) -> List[Dict[str, Any]]:
        """Get information about network shares
        
        Returns:
            List of dictionaries containing share information
        """
        query = """
        query {
            shares {
                name
                free
                used
                size
                include
                exclude
                cache
                comment
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["shares"]
    
    # System Control Methods
    
    async def shutdown_server(self) -> str:
        """Shutdown the Unraid server
        
        Returns:
            Result message
        """
        mutation = """
        mutation {
            shutdown
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["shutdown"]
    
    async def reboot_server(self) -> str:
        """Reboot the Unraid server
        
        Returns:
            Result message
        """
        mutation = """
        mutation {
            reboot
        }
        """
        result = await self.execute_query(mutation)
        return result["data"]["reboot"]

def _extract_operation_name(query: str) -> str:
    """Extract operation name from a GraphQL query for better logging
    
    Args:
        query: The GraphQL query string
        
    Returns:
        The operation name or a fallback
    """
    # Clean the query
    query = query.strip()
    
    # Check if it's a mutation or query
    is_mutation = query.startswith("mutation")
    
    try:
        # Get the first line and extract operation after first {
        lines = query.split('\n')
        first_line = None
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '{' in line:
                first_line = line
                break
        
        if not first_line:
            return "unknown_operation"
            
        # Extract the first operation after {
        parts = first_line.split('{')
        if len(parts) < 2:
            return "unknown_operation"
            
        second_part = parts[1].strip()
        
        # Get the first word which should be the operation
        operation = second_part.split('(')[0].split(' ')[0].strip()
        
        if not operation:
            return "unknown_operation"
            
        return operation
    except Exception:
        # Fallback if parsing fails
        return "unknown_operation" 