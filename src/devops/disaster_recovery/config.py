"""Configuration management for disaster recovery."""

from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DRConfig:
    """Configuration for disaster recovery testing."""
    
    backup_interval_hours: int = 24
    test_schedule: str = "weekly"
    alert_on_failure: bool = True
    retry_failed_tests: bool = True
    max_retries: int = 3
    enabled_test_types: List[str] = field(default_factory=lambda: ["backup_restore", "failover"])
    
    def __repr__(self) -> str:
        return f"DRConfig(backup_interval={self.backup_interval_hours}h, schedule={self.test_schedule})"


def load_config(config_dict: Optional[dict] = None) -> DRConfig:
    """Load configuration from dictionary."""
    if config_dict is None:
        config_dict = {}
    
    return DRConfig(**{k: v for k, v in config_dict.items() if k in DRConfig.__dataclass_fields__})
