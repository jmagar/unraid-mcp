import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
class Config:
    """Configuration for the Unraid MCP server"""
    
    # API configuration
    API_URL = os.getenv("UNRAID_API_URL")
    API_KEY = os.getenv("UNRAID_API_KEY")
    
    # Server configuration
    SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8400"))
    
    # MCP options
    CLAUDE_MODE = os.getenv("CLAUDE_MCP_SERVER", "false").lower() in ("true", "1", "yes")
    
    # Logging configuration
    LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO")
    LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME.upper(), logging.INFO)
    LOG_FILE = os.getenv("LOG_FILE", "unraid_mcp.log")
    
    @classmethod
    def validate(cls):
        """Validate required configuration is present"""
        if not cls.API_URL or not cls.API_KEY:
            raise ValueError("UNRAID_API_URL and UNRAID_API_KEY must be set in .env file")
        return True

# Configure logging
def setup_logging(name="unraid_mcp"):
    """Set up logging with the configured level"""
    # Configure root logger first to catch all loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Default to WARNING for all loggers
    
    # Set up our specific logger
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    logger.propagate = False  # Don't propagate to root logger
    
    # Add console handler if not already added
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(Config.LOG_LEVEL)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # Also add a handler to root logger for consistency
        root_console = logging.StreamHandler()
        root_console.setLevel(logging.WARNING)
        root_console.setFormatter(formatter)
        root_logger.addHandler(root_console)
    
    # Explicitly quiet some noisy loggers
    for logger_name in ['uvicorn', 'uvicorn.error', 'uvicorn.access', 'mcp.server']:
        noisy_logger = logging.getLogger(logger_name)
        noisy_logger.setLevel(logging.WARNING)
        noisy_logger.propagate = False
    
    return logger
