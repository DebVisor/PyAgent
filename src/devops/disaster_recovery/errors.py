"""Custom exceptions for disaster recovery."""


class DRError(Exception):
    """Base exception for DR errors."""
    pass


class PlanError(DRError):
    """Exception for plan-related errors."""
    pass


class TestError(DRError):
    """Exception for test-related errors."""
    pass
