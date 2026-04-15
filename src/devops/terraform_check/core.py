"""Core Terraform compliance checking implementation."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComplianceSeverity(Enum):
    """Compliance issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ComplianceIssue:
    """Represents a compliance violation."""
    rule_id: str
    rule_name: str
    severity: ComplianceSeverity
    resource_type: str
    resource_id: Optional[str] = None
    message: str = ""
    remediation: Optional[str] = None

    def __repr__(self) -> str:
        return f"ComplianceIssue(rule={self.rule_id}, severity={self.severity.value})"


@dataclass
class ComplianceResult:
    """Results of Terraform compliance checking."""
    configuration_file: str
    compliant: bool = True
    issues: List[ComplianceIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_issue(self, rule_id: str, rule_name: str, severity: ComplianceSeverity,
                  resource_type: str, message: str, resource_id: Optional[str] = None) -> None:
        """Add a compliance issue."""
        issue = ComplianceIssue(
            rule_id=rule_id,
            rule_name=rule_name,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message
        )
        self.issues.append(issue)
        
        if severity == ComplianceSeverity.CRITICAL:
            self.critical_count += 1
            self.compliant = False
        elif severity == ComplianceSeverity.HIGH:
            self.high_count += 1
            self.compliant = False

    def __repr__(self) -> str:
        return f"ComplianceResult(file={self.configuration_file}, compliant={self.compliant}, issues={len(self.issues)})"


class TerraformChecker:
    """Terraform compliance checker."""

    def __init__(self, policies: Optional[List[str]] = None):
        """Initialize Terraform checker.
        
        Args:
            policies: List of policy names to apply
        """
        self.policies = policies or []
        self.logger = logger

    def check_configuration(self, config: Dict[str, Any], file_path: str = "main.tf") -> ComplianceResult:
        """Check Terraform configuration for compliance.
        
        Args:
            config: Parsed Terraform configuration
            file_path: Original file path for reference
            
        Returns:
            ComplianceResult with identified issues
        """
        self.logger.info(f"Checking compliance for: {file_path}")
        
        result = ComplianceResult(configuration_file=file_path)
        
        if not isinstance(config, dict):
            result.add_issue(
                "type_check",
                "Configuration type error",
                ComplianceSeverity.CRITICAL,
                "root"
            )
            return result
        
        # Check for required fields in resources
        resources = config.get("resource", {})
        for resource_type, resources_dict in resources.items():
            for resource_id, resource_config in resources_dict.items():
                # Check for tags
                if "tags" not in resource_config:
                    result.add_issue(
                        "missing_tags",
                        "Resource missing tags",
                        ComplianceSeverity.MEDIUM,
                        resource_type,
                        resource_id=resource_id,
                        message=f"{resource_type}.{resource_id} is missing required tags"
                    )
        
        self.logger.info(f"Compliance check complete: {result}")
        return result

    def validate_syntax(self, config: Dict[str, Any]) -> bool:
        """Validate Terraform configuration syntax.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(config, dict):
            return False
        
        # Basic syntax validation
        if "terraform" in config and not isinstance(config["terraform"], dict):
            return False
        
        if "variable" in config and not isinstance(config["variable"], dict):
            return False
        
        if "resource" in config and not isinstance(config["resource"], dict):
            return False
        
        return True
