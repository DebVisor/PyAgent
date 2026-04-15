"""Configuration management for Kubernetes validation."""

from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuration for Kubernetes validation."""
    
    cluster_name: Optional[str] = None
    api_version: str = "v1"
    timeout_seconds: int = 30
    strict_mode: bool = True
    required_labels: List[str] = field(default_factory=lambda: ["app", "version"])
    required_annotations: List[str] = field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"ValidationConfig(cluster={self.cluster_name}, strict={self.strict_mode})"


def load_config(config_dict: Optional[dict] = None) -> ValidationConfig:
    """Load configuration from dictionary."""
    if config_dict is None:
        config_dict = {}
    
    return ValidationConfig(**{k: v for k, v in config_dict.items() if k in ValidationConfig.__dataclass_fields__})
