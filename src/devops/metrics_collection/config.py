"""Configuration management for metrics collection."""

from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    
    collection_interval: int = 60
    retention_days: int = 7
    max_points_per_metric: int = 10000
    enabled_metrics: List[str] = field(default_factory=lambda: ["cpu", "memory", "disk", "network"])
    export_format: str = "json"
    
    def __repr__(self) -> str:
        return f"MetricsConfig(interval={self.collection_interval}s, metrics={len(self.enabled_metrics)})"


def load_config(config_dict: Optional[dict] = None) -> MetricsConfig:
    """Load configuration from dictionary."""
    if config_dict is None:
        config_dict = {}
    
    return MetricsConfig(**{k: v for k, v in config_dict.items() if k in MetricsConfig.__dataclass_fields__})
