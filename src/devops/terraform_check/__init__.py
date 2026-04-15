"""Terraform compliance checking module.

Provides utilities for validating Terraform configurations against compliance
policies and best practices.
"""

from .core import (
    TerraformChecker,
    ComplianceResult,
    ComplianceIssue,
)
from .config import ComplianceConfig
from .errors import (
    TerraformError,
    ConfigError,
    PolicyError,
)

__all__ = [
    "TerraformChecker",
    "ComplianceResult",
    "ComplianceIssue",
    "ComplianceConfig",
    "TerraformError",
    "ConfigError",
    "PolicyError",
]

__version__ = "0.1.0"
