"""Configuration management for Terraform checking."""

from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceConfig:
    """Configuration for Terraform compliance checking."""
    
    policy_path: Optional[str] = None
    strict_mode: bool = True
    required_policies: List[str] = field(default_factory=lambda: ["security", "tagging"])
    fail_on_critical: bool = True
    fail_on_high: bool = False
    
    def __repr__(self) -> str:
        return f"ComplianceConfig(strict={self.strict_mode}, policies={len(self.required_policies)})"


def load_config(config_dict: Optional[dict] = None) -> ComplianceConfig:
    """Load configuration from dictionary."""
    if config_dict is None:
        config_dict = {}
    
    return ComplianceConfig(**{k: v for k, v in config_dict.items() if k in ComplianceConfig.__dataclass_fields__})
