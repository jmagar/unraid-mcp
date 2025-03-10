import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class UnraidClient:
    """Client for communicating with the Unraid GraphQL API"""
    
    def __init__(self):
        self.api_url = os.getenv("UNRAID_API_URL")
        self.api_key = os.getenv("UNRAID_API_KEY")
        
        if not self.api_url or not self.api_key:
            raise ValueError("UNRAID_API_URL and UNRAID_API_KEY must be set in .env file")
            
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def execute_query(self, query, variables=None):
        """Execute a GraphQL query against the Unraid API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={"query": query, "variables": variables or {}},
                headers=self.headers
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Query failed with status {response.status}: {text}")
                
                result = await response.json()
                
                # Check for GraphQL errors
                if "errors" in result:
                    errors = result["errors"]
                    error_message = "; ".join([error.get("message", "Unknown error") for error in errors])
                    raise Exception(f"GraphQL query failed: {error_message}")
                
                return result 