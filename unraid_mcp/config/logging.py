"""Logging configuration for Unraid MCP Server.

This module sets up structured logging with console and rotating file handlers
that can be used consistently across all modules.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from .settings import LOG_LEVEL_STR, LOG_FILE_PATH


def setup_logger(name: str = "UnraidMCPServer") -> logging.Logger:
    """Set up and configure the logger with console and file handlers.
    
    Args:
        name: Logger name (defaults to UnraidMCPServer)
        
    Returns:
        Configured logger instance
    """
    # Get numeric log level
    numeric_log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)
    
    # Define the logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_log_level)
    logger.propagate = False  # Prevent root logger from duplicating handlers
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_log_level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler with Rotation
    # Rotate logs at 5MB, keep 3 backup logs
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, 
        maxBytes=5*1024*1024, 
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def log_configuration_status(logger: logging.Logger) -> None:
    """Log configuration status at startup.
    
    Args:
        logger: Logger instance to use for logging
    """
    from .settings import get_config_summary
    
    logger.info(f"Logging initialized (console and file: {LOG_FILE_PATH}).")
    
    config = get_config_summary()
    
    # Log configuration status
    if config['api_url_configured']:
        logger.info(f"UNRAID_API_URL loaded: {config['api_url_preview']}")
    else:
        logger.warning("UNRAID_API_URL not found in environment or .env file.")
    
    if config['api_key_configured']:
        logger.info("UNRAID_API_KEY loaded: ****")  # Don't log the key itself
    else:
        logger.warning("UNRAID_API_KEY not found in environment or .env file.")
    
    logger.info(f"UNRAID_MCP_PORT set to: {config['server_port']}")
    logger.info(f"UNRAID_MCP_HOST set to: {config['server_host']}")
    logger.info(f"UNRAID_MCP_TRANSPORT set to: {config['transport']}")
    logger.info(f"UNRAID_MCP_LOG_LEVEL set to: {config['log_level']}")
    
    if not config['config_valid']:
        logger.error(f"Missing required configuration: {config['missing_config']}")


# Global logger instance - modules can import this directly
logger = setup_logger()