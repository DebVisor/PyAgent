"""Configuration management for container scanning."""

from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Configuration for container scanning operations."""
    
    registry_url: Optional[str] = None
    timeout_seconds: int = 300
    max_vulnerabilities: int = 1000
    fail_on_critical: bool = True
    fail_on_high: bool = False
    severity_levels: List[str] = field(default_factory=lambda: ["critical", "high", "medium"])
    excluded_packages: List[str] = field(default_factory=list)
    
    def is_critical_failure(self) -> bool:
        """Check if scanner should fail on critical vulnerabilities."""
        return self.fail_on_critical
    
    def is_high_failure(self) -> bool:
        """Check if scanner should fail on high severity vulnerabilities."""
        return self.fail_on_high
    
    def should_scan_severity(self, severity: str) -> bool:
        """Check if a severity level should be scanned."""
        return severity.lower() in [s.lower() for s in self.severity_levels]
    
    def __repr__(self) -> str:
        return f"ScanConfig(registry={self.registry_url}, timeout={self.timeout_seconds}s)"


def load_config(config_dict: Optional[dict] = None) -> ScanConfig:
    """Load configuration from dictionary.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        ScanConfig instance
    """
    if config_dict is None:
        config_dict = {}
    
    return ScanConfig(**{k: v for k, v in config_dict.items() if k in ScanConfig.__dataclass_fields__})
