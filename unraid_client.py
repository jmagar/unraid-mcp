import os
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, Union
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
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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