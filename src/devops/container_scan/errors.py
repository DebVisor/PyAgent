"""Custom exceptions for container scanning."""


class ScanError(Exception):
    """Base exception for scanning errors."""
    pass


class RegistryError(ScanError):
    """Exception for registry-related errors."""
    pass


class ImageNotFoundError(ScanError):
    """Exception when image cannot be found."""
    pass


class ScanTimeoutError(ScanError):
    """Exception when scan times out."""
    pass
