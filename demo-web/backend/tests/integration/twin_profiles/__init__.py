"""
Twin Profiles Module

Manages digital twin configurations for deterministic test execution.
Provides profile loading, validation, and simulator instance management.

Available Profiles:
- a1_minimal_twin_v1: Phase A baseline with Non-RT RIC + A1 peer simulator + info sources
"""

from .loader import TwinProfileLoader, TwinProfileContextManager

__all__ = ["TwinProfileLoader", "TwinProfileContextManager"]
