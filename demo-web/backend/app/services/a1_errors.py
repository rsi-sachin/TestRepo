"""Shared A1 service-layer exceptions."""


class A1ConflictError(ValueError):
    """Raised when an A1 resource update conflicts with current state."""
