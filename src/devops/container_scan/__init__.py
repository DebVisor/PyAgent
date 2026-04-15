"""
Container image vulnerability scanning module.

Provides utilities for scanning container images for security vulnerabilities,
managing scan results, and integrating with container registries.
"""

from .core import (
    ContainerScanner,
    ScanResult,
    Vulnerability,
)
from .config import ScanConfig
from .errors import (
    ScanError,
    RegistryError,
    ImageNotFoundError,
)

__all__ = [
    "ContainerScanner",
    "ScanResult",
    "Vulnerability",
    "ScanConfig",
    "ScanError",
    "RegistryError",
    "ImageNotFoundError",
]

__version__ = "0.1.0"
