"""Router-specific exceptions."""

from __future__ import annotations


class RouterConfigurationError(Exception):
    """Raised when router configuration cannot be loaded or validated."""


class RouterRoutingError(Exception):
    """Raised when routing cannot be completed safely."""
