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
                    timeout=aiohttp.ClientTimeout(total=60)  # 60 second timeout
                ) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        # Try to parse the response as JSON for more detailed error info
                        error_details = "Unknown error"
                        try:
                            error_json = json.loads(response_text)
                            if "errors" in error_json:
                                error_details = "; ".join([error.get("message", "Unknown error") for error in error_json["errors"]])
                            elif "message" in error_json:
                                error_details = error_json["message"]
                        except:
                            error_details = response_text
                        
                        error_message = f"API request failed with status {response.status}: {error_details}"
                        logger.error(error_message)
                        logger.error(f"Request payload: {json.dumps(payload)}")
                        logger.error(f"Response: {response_text}")
                        
                        raise UnraidApiError(
                            error_message, 
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
                        logger.error(f"Request payload: {json.dumps(payload)}")
                        logger.error(f"Full response: {json.dumps(result)}")
                        raise UnraidApiError(f"GraphQL query failed: {error_message}")
                    
                    if "data" not in result:
                        logger.error(f"No data in response: {result}")
                        raise UnraidApiError("No data in API response")
                    
                    # Check for null values in the data that might indicate errors
                    if result["data"] is None:
                        logger.error(f"Null data in response: {result}")
                        raise UnraidApiError("Null data in API response")
                    
                    # Check if any of the expected fields are missing
                    # Handle nested fields like "docker.containers"
                    if '.' in operation_name:
                        # For nested paths like "docker.containers"
                        current_data = result["data"]
                        field_path = operation_name.split('.')
                        valid_path = True
                        
                        for i, key in enumerate(field_path):
                            if key and key in current_data:
                                current_data = current_data[key]
                                # If we're at the last level and it exists, we're good
                                if i == len(field_path) - 1:
                                    break
                            else:
                                if key:  # Only log if key is not empty
                                    path_so_far = '.'.join(field_path[:i])
                                    logger.error(f"Expected field '{key}' missing in path '{path_so_far}' of response data: {result['data']}")
                                    valid_path = False
                                    break
                        
                        if not valid_path:
                            # Log full response for debugging but continue execution
                            logger.warning(f"Invalid path in response, but continuing execution: {result['data']}")
                    else:
                        # Original behavior for non-nested fields
                        if operation_name and operation_name not in result["data"]:
                            logger.error(f"Expected field '{operation_name}' missing in response data: {result['data']}")
                            # Log warning but don't raise exception to allow continuing execution
                            logger.warning(f"Missing field in response, but continuing execution")
                    
                    # Log successful query results
                    if "data" in result:
                        data_keys = list(result["data"].keys())
                        logger.debug(f"Received response for '{operation_name}' with data keys: {', '.join(data_keys)}")
                    
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise UnraidApiError(f"API request failed: {str(e)}")
        except UnraidApiError:
            # Re-raise UnraidApiError exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
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
            dockerNetworks {
                id
                name
                driver
                scope
                internal
                attachable
            }
        }
        """
        result = await self.execute_query(query)
        return result["data"]["dockerNetworks"]
    
    async def start_container(self, container_name: str) -> Dict[str, Any]:
        """Start a Docker container by name
        
        WARNING: EXPERIMENTAL/UNSUPPORTED - This operation is not officially supported by the Unraid GraphQL API.
        The current API schema does not include mutations for starting Docker containers.
        This method is included for future compatibility but will likely fail with current Unraid versions.
        
        Args:
            container_name: The name of the container to start
            
        Returns:
            Dictionary with success status and message
        """
        mutation = """
        mutation ($name: String!) {
          docker {
            startContainer(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": container_name}
        
        logger.info(f"Starting Docker container: {container_name}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            # Note: This operation might not be supported by all Unraid GraphQL API versions
            # Some Unraid API implementations may return an error for this operation
            result = await self.execute_query(mutation, variables)
            logger.info(f"Start container result: {result}")
            
            # Check if the operation is supported
            if "errors" in result and any("not found" in error.get("message", "").lower() for error in result["errors"]):
                logger.warning("Docker container control operations may not be supported by this Unraid GraphQL API version")
                return {"error": "Docker container control operations may not be supported by this Unraid GraphQL API version"}
                
            return result["data"]["docker"]["startContainer"]
        except UnraidApiError as e:
            logger.error(f"API error starting container {container_name}: {str(e)}")
            logger.error(f"Status code: {e.status_code}, Response: {e.response_text}")
            
            # Check if this is due to the operation not being supported
            if "not found" in str(e).lower() or "unknown field" in str(e).lower():
                return {"error": "Docker container control operations are not supported by this Unraid GraphQL API version"}
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting container {container_name}: {str(e)}", exc_info=True)
            raise
    
    async def stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop a Docker container by name
        
        WARNING: EXPERIMENTAL/UNSUPPORTED - This operation is not officially supported by the Unraid GraphQL API.
        The current API schema does not include mutations for stopping Docker containers.
        This method is included for future compatibility but will likely fail with current Unraid versions.
        
        Args:
            container_name: The name of the container to stop
            
        Returns:
            Dictionary with success status and message
        """
        mutation = """
        mutation ($name: String!) {
          docker {
            stopContainer(name: $name) {
              success
              message
            }
          }
        }
        """
        variables = {"name": container_name}
        
        logger.info(f"Stopping Docker container: {container_name}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            # Note: This operation might not be supported by all Unraid GraphQL API versions
            # Some Unraid API implementations may return an error for this operation
            result = await self.execute_query(mutation, variables)
            logger.info(f"Stop container result: {result}")
            
            # Check if the operation is supported
            if "errors" in result and any("not found" in error.get("message", "").lower() for error in result["errors"]):
                logger.warning("Docker container control operations may not be supported by this Unraid GraphQL API version")
                return {"error": "Docker container control operations may not be supported by this Unraid GraphQL API version"}
                
            return result["data"]["docker"]["stopContainer"]
        except UnraidApiError as e:
            logger.error(f"API error stopping container {container_name}: {str(e)}")
            logger.error(f"Status code: {e.status_code}, Response: {e.response_text}")
            
            # Check if this is due to the operation not being supported
            if "not found" in str(e).lower() or "unknown field" in str(e).lower():
                return {"error": "Docker container control operations are not supported by this Unraid GraphQL API version"}
            raise
        except Exception as e:
            logger.error(f"Unexpected error stopping container {container_name}: {str(e)}", exc_info=True)
            raise
    
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
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get information about all users
        
        Returns:
            List of user objects
        """
        query = """
        query {
          users {
            id
            name
            description
            roles
          }
        }
        """
        
        logger.info("Getting users")
        logger.debug(f"Using query: {query}")
        
        try:
            result = await self.execute_query(query)
            logger.debug(f"Get users result: {result}")
            
            if "data" in result and "users" in result["data"]:
                return result["data"]["users"]
            else:
                logger.warning("Failed to get users: Invalid response format")
                return []
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise
    
    async def add_user(self, name: str, password: str, description: str = "") -> Dict[str, Any]:
        """Add a new user
        
        Args:
            name: The username
            password: The user's password
            description: Optional description for the user
            
        Returns:
            The created user object
        """
        mutation = """
        mutation ($input: addUserInput!) {
          addUser(input: $input) {
            id
            name
            description
            roles
          }
        }
        """
        variables = {
            "input": {
                "name": name,
                "password": password,
                "description": description
            }
        }
        
        logger.info(f"Adding user: {name}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            result = await self.execute_query(mutation, variables)
            logger.debug(f"Add user result: {result}")
            
            if "data" in result and "addUser" in result["data"]:
                return result["data"]["addUser"]
            else:
                logger.warning(f"Failed to add user {name}: Invalid response format")
                if "errors" in result:
                    logger.warning(f"Errors: {result['errors']}")
                return {"error": "Failed to add user"}
        except Exception as e:
            logger.error(f"Error adding user {name}: {str(e)}")
            raise
    
    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            The deleted user object
        """
        mutation = """
        mutation ($input: deleteUserInput!) {
          deleteUser(input: $input) {
            id
            name
          }
        }
        """
        variables = {
            "input": {
                "userId": user_id
            }
        }
        
        logger.info(f"Deleting user with ID: {user_id}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            result = await self.execute_query(mutation, variables)
            logger.debug(f"Delete user result: {result}")
            
            if "data" in result and "deleteUser" in result["data"]:
                return result["data"]["deleteUser"]
            else:
                logger.warning(f"Failed to delete user {user_id}: Invalid response format")
                if "errors" in result:
                    logger.warning(f"Errors: {result['errors']}")
                return {"error": "Failed to delete user"}
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise

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

    # API Key Management Methods
    
    async def create_api_key(self, name: str, description: str = "", roles: List[str] = ["admin"]) -> Dict[str, Any]:
        """Create a new API key
        
        Args:
            name: The name for the API key
            description: Optional description for the API key
            roles: List of roles to assign to the API key (default: ["admin"])
            
        Returns:
            The created API key object including the secret key
        """
        mutation = """
        mutation ($input: CreateApiKeyInput!) {
          createApiKey(input: $input) {
            id
            key
            name
            description
            roles
            createdAt
          }
        }
        """
        variables = {
            "input": {
                "name": name,
                "description": description,
                "roles": roles
            }
        }
        
        logger.info(f"Creating API key: {name}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            result = await self.execute_query(mutation, variables)
            logger.debug(f"Create API key result: {result}")
            
            if "data" in result and "createApiKey" in result["data"]:
                return result["data"]["createApiKey"]
            else:
                logger.warning(f"Failed to create API key {name}: Invalid response format")
                if "errors" in result:
                    logger.warning(f"Errors: {result['errors']}")
                return {"error": "Failed to create API key"}
        except Exception as e:
            logger.error(f"Error creating API key {name}: {str(e)}")
            raise
    
    async def get_api_keys(self) -> List[Dict[str, Any]]:
        """Get information about all API keys
        
        Returns:
            List of API key objects
        """
        query = """
        query {
          apiKeys {
            id
            name
            description
            roles
            createdAt
          }
        }
        """
        
        logger.info("Getting API keys")
        logger.debug(f"Using query: {query}")
        
        try:
            result = await self.execute_query(query)
            logger.debug(f"Get API keys result: {result}")
            
            if "data" in result and "apiKeys" in result["data"]:
                return result["data"]["apiKeys"]
            else:
                logger.warning("Failed to get API keys: Invalid response format")
                return []
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise

    # Remote Access Methods
    
    async def setup_remote_access(self, url: str) -> bool:
        """Set up remote access
        
        Args:
            url: The remote access URL
            
        Returns:
            True if successful, False otherwise
        """
        mutation = """
        mutation ($input: SetupRemoteAccessInput!) {
          setupRemoteAccess(input: $input)
        }
        """
        variables = {
            "input": {
                "url": url
            }
        }
        
        logger.info(f"Setting up remote access with URL: {url}")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            result = await self.execute_query(mutation, variables)
            logger.debug(f"Setup remote access result: {result}")
            
            if "data" in result and "setupRemoteAccess" in result["data"]:
                return result["data"]["setupRemoteAccess"]
            else:
                logger.warning(f"Failed to set up remote access: Invalid response format")
                if "errors" in result:
                    logger.warning(f"Errors: {result['errors']}")
                return False
        except Exception as e:
            logger.error(f"Error setting up remote access: {str(e)}")
            raise
    
    async def enable_dynamic_remote_access(self, enabled: bool = True) -> bool:
        """Enable or disable dynamic remote access
        
        Args:
            enabled: Whether to enable (True) or disable (False) dynamic remote access
            
        Returns:
            True if successful, False otherwise
        """
        mutation = """
        mutation ($input: EnableDynamicRemoteAccessInput!) {
          enableDynamicRemoteAccess(input: $input)
        }
        """
        variables = {
            "input": {
                "enabled": enabled
            }
        }
        
        logger.info(f"{'Enabling' if enabled else 'Disabling'} dynamic remote access")
        logger.debug(f"Using mutation: {mutation}")
        logger.debug(f"With variables: {variables}")
        
        try:
            result = await self.execute_query(mutation, variables)
            logger.debug(f"Enable dynamic remote access result: {result}")
            
            if "data" in result and "enableDynamicRemoteAccess" in result["data"]:
                return result["data"]["enableDynamicRemoteAccess"]
            else:
                logger.warning(f"Failed to {'enable' if enabled else 'disable'} dynamic remote access: Invalid response format")
                if "errors" in result:
                    logger.warning(f"Errors: {result['errors']}")
                return False
        except Exception as e:
            logger.error(f"Error {'enabling' if enabled else 'disabling'} dynamic remote access: {str(e)}")
            raise

    # Unassigned Devices Methods
    
    async def get_unassigned_devices(self) -> List[Dict[str, Any]]:
        """Get information about unassigned devices
        
        Returns:
            List of unassigned device objects
        """
        query = """
        query {
          unassignedDevices {
            id
            name
            size
            partitions {
              name
              size
              fsType
            }
          }
        }
        """
        
        logger.info("Getting unassigned devices")
        logger.debug(f"Using query: {query}")
        
        try:
            result = await self.execute_query(query)
            logger.debug(f"Get unassigned devices result: {result}")
            
            if "data" in result and "unassignedDevices" in result["data"]:
                return result["data"]["unassignedDevices"]
            else:
                logger.warning("Failed to get unassigned devices: Invalid response format")
                return []
        except Exception as e:
            logger.error(f"Error getting unassigned devices: {str(e)}")
            raise

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
        # Extract all operation names in the query
        operations = []
        current_level = 0
        capture = False
        current_op = ""
        
        # Skip the first opening brace (the query/mutation definition)
        skip_first_brace = True
        
        for line in query.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            for char in line:
                if char == '{':
                    if skip_first_brace:
                        skip_first_brace = False
                        continue
                        
                    current_level += 1
                    if current_level == 1:
                        capture = True
                elif char == '}':
                    current_level -= 1
                    if current_level == 0 and current_op:
                        operations.append(current_op.strip())
                        current_op = ""
                        capture = False
                elif capture and current_level == 1 and char not in '()':
                    current_op += char
        
        # Clean up operations
        clean_operations = []
        for op in operations:
            # Remove any parameters
            op = op.split('(')[0].strip()
            # Split by whitespace and take the first part
            op = op.split()[0].strip()
            if op:
                clean_operations.append(op)
        
        if not clean_operations:
            return "unknown_operation"
            
        # Join operations with dots to represent nesting
        return ".".join(clean_operations)
    except Exception as e:
        # Log the error but don't fail the whole operation
        logger.debug(f"Error extracting operation name: {str(e)}")
        return "unknown_operation"
