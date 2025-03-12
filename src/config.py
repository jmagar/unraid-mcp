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
    SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    
    # MCP options
    CLAUDE_MODE = os.getenv("CLAUDE_MCP_SERVER", "false").lower() in ("true", "1", "yes")
    
    # Logging configuration
    LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME.upper(), logging.DEBUG)
    LOG_FILE = os.getenv("LOG_FILE", "unraid_mcp.log")
    
    @classmethod
    def validate(cls):
        """Validate required configuration is present"""
        if not cls.API_URL or not cls.API_KEY:
            raise ValueError("UNRAID_API_URL and UNRAID_API_KEY must be set in .env file")
        return True

# Configure logging
def setup_logging(name="unraid_mcp", log_level=None):
    """Set up logging with the configured level"""
    # Use provided log_level or default to Config.LOG_LEVEL
    if log_level is None:
        log_level = Config.LOG_LEVEL
    
    # Configure root logger first to catch all loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Default to WARNING for all loggers
    
    # Set up our specific logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # Don't propagate to root logger
    
    # Clear existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Add file handler
    try:
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Log to console if file handler fails
        console_handler.setLevel(logging.DEBUG)
        logger.error(f"Failed to create file handler: {str(e)}")
    
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
    
    # Log a test message to verify logging is working
    logger.debug(f"Logging initialized for {name} at level {logging.getLevelName(log_level)}")
    
    return logger
