"""Shared data types for Unraid MCP Server.

This module defines data classes and type definitions used across
multiple modules for consistent data handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SubscriptionData:
    """Container for subscription data with metadata."""

    data: dict[str, Any]
    last_updated: datetime
    subscription_type: str


@dataclass
class SystemHealth:
    """Container for system health status information."""

    is_healthy: bool
    issues: list[str]
    warnings: list[str]
    last_checked: datetime
    component_status: dict[str, str]


@dataclass
class APIResponse:
    """Container for standardized API response data."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


# Type aliases for common data structures
ConfigValue = str | int | bool | float | None
ConfigDict = dict[str, ConfigValue]
GraphQLVariables = dict[str, Any]
HealthStatus = dict[str, str | bool | int | list[Any]]
