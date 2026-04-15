"""Observability metrics collection module.

Provides utilities for collecting, aggregating, and reporting system metrics
for monitoring and observability.
"""

from .core import (
    MetricsCollector,
    Metric,
    MetricPoint,
)
from .config import MetricsConfig
from .errors import (
    MetricsError,
    CollectionError,
    StorageError,
)

__all__ = [
    "MetricsCollector",
    "Metric",
    "MetricPoint",
    "MetricsConfig",
    "MetricsError",
    "CollectionError",
    "StorageError",
]

__version__ = "0.1.0"
