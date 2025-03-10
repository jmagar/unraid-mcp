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
        
        logger.debug(f"Executing GraphQL query: {query[:100]}...")
        logger.debug(f"Variables: {json.dumps(variables)}")
        
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
                    
                    logger.debug(f"Received response with keys: {', '.join(result['data'].keys())}")
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise UnraidApiError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise 