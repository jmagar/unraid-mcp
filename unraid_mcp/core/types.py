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

    def __post_init__(self) -> None:
        if self.last_updated.tzinfo is None:
            raise ValueError(
                "last_updated must be timezone-aware; use datetime.now(UTC)"
            )
        if not self.subscription_type.strip():
            raise ValueError("subscription_type must be a non-empty string")
