"""Shared data types for Unraid MCP Server.

This module defines data classes and type definitions used across
multiple modules for consistent data handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SubscriptionData:
    """Container for subscription data with metadata.

    Note: last_updated must be timezone-aware (use datetime.now(UTC)).
    """

    data: dict[str, Any]
    last_updated: datetime  # Must be timezone-aware (UTC)
    subscription_type: str


@dataclass(slots=True)
class SystemHealth:
    """Container for system health status information.

    Note: last_checked must be timezone-aware (use datetime.now(UTC)).
    """

    is_healthy: bool
    issues: list[str]
    warnings: list[str]
    last_checked: datetime  # Must be timezone-aware (UTC)
    component_status: dict[str, str]


@dataclass(slots=True)
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
