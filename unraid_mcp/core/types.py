"""Shared data types for Unraid MCP Server.

This module defines data classes and type definitions used across
multiple modules for consistent data handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union


@dataclass
class SubscriptionData:
    """Container for subscription data with metadata."""
    data: Dict[str, Any]
    last_updated: datetime
    subscription_type: str


@dataclass
class SystemHealth:
    """Container for system health status information."""
    is_healthy: bool
    issues: list[str]
    warnings: list[str]
    last_checked: datetime
    component_status: Dict[str, str]


@dataclass
class APIResponse:
    """Container for standardized API response data."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Type aliases for common data structures
ConfigValue = Union[str, int, bool, float, None]
ConfigDict = Dict[str, ConfigValue]
GraphQLVariables = Dict[str, Any]
HealthStatus = Dict[str, Union[str, bool, int, list]]