"""Kubernetes deployment validation module.

Provides utilities for validating Kubernetes manifests, detecting configuration
drift, and ensuring deployment best practices.
"""

from .core import (
    K8sValidator,
    ValidationResult,
    ValidationError,
)
from .config import ValidationConfig
from .errors import (
    K8sError,
    ManifestError,
    ClusterError,
)

__all__ = [
    "K8sValidator",
    "ValidationResult",
    "ValidationError",
    "ValidationConfig",
    "K8sError",
    "ManifestError",
    "ClusterError",
]

__version__ = "0.1.0"
