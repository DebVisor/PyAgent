"""Custom exceptions for metrics collection."""


class MetricsError(Exception):
    """Base exception for metrics errors."""
    pass


class CollectionError(MetricsError):
    """Exception for collection errors."""
    pass


class StorageError(MetricsError):
    """Exception for storage errors."""
    pass
