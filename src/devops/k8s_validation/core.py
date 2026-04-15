"""Core Kubernetes validation implementation."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error."""
    rule: str
    severity: ValidationSeverity
    message: str
    resource: Optional[str] = None
    field: Optional[str] = None

    def __repr__(self) -> str:
        return f"ValidationError(rule={self.rule}, severity={self.severity.value})"


@dataclass
class ValidationResult:
    """Results of Kubernetes manifest validation."""
    manifest_file: str
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, rule: str, message: str, resource: Optional[str] = None) -> None:
        """Add validation error."""
        error = ValidationError(
            rule=rule,
            severity=ValidationSeverity.ERROR,
            message=message,
            resource=resource
        )
        self.errors.append(error)
        self.valid = False

    def add_warning(self, rule: str, message: str, resource: Optional[str] = None) -> None:
        """Add validation warning."""
        warning = ValidationError(
            rule=rule,
            severity=ValidationSeverity.WARNING,
            message=message,
            resource=resource
        )
        self.warnings.append(warning)

    def __repr__(self) -> str:
        return f"ValidationResult(file={self.manifest_file}, valid={self.valid}, errors={len(self.errors)})"


class K8sValidator:
    """Kubernetes manifest validator."""

    def __init__(self):
        """Initialize K8s validator."""
        self.logger = logger

    def validate_manifest(self, manifest: Dict[str, Any], file_path: str = "manifest.yaml") -> ValidationResult:
        """Validate a Kubernetes manifest.
        
        Args:
            manifest: Parsed manifest dictionary
            file_path: Original file path for reference
            
        Returns:
            ValidationResult containing validation errors and warnings
        """
        self.logger.info(f"Validating manifest: {file_path}")
        
        result = ValidationResult(manifest_file=file_path)
        
        # Validate required fields
        if not isinstance(manifest, dict):
            result.add_error("type_check", "Manifest must be a dictionary")
            return result
        
        if "apiVersion" not in manifest:
            result.add_error("required_field", "Missing required field: apiVersion")
        
        if "kind" not in manifest:
            result.add_error("required_field", "Missing required field: kind")
        
        if "metadata" not in manifest:
            result.add_error("required_field", "Missing required field: metadata")
        
        # Validate metadata
        if isinstance(manifest.get("metadata"), dict):
            metadata = manifest["metadata"]
            if "name" not in metadata:
                result.add_error("required_field", "Missing metadata.name")
        
        # Check for resource requests/limits
        if self._should_have_resources(manifest):
            if not self._has_resource_limits(manifest):
                result.add_warning(
                    "best_practice",
                    "Resource limits/requests should be defined",
                    resource=manifest.get("metadata", {}).get("name")
                )
        
        self.logger.info(f"Validation complete: {result}")
        return result

    def detect_drift(self, current: Dict[str, Any], desired: Dict[str, Any]) -> ValidationResult:
        """Detect configuration drift between current and desired states.
        
        Args:
            current: Current manifest state
            desired: Desired manifest state
            
        Returns:
            ValidationResult indicating drift
        """
        self.logger.info("Checking for configuration drift")
        result = ValidationResult(manifest_file="drift_check")
        
        # Simple drift detection
        if current != desired:
            result.valid = False
            result.add_error("drift", "Configuration drift detected")
        
        return result

    def _should_have_resources(self, manifest: Dict[str, Any]) -> bool:
        """Check if manifest should have resource limits."""
        kind = manifest.get("kind", "")
        return kind in ["Deployment", "StatefulSet", "DaemonSet", "Pod"]

    def _has_resource_limits(self, manifest: Dict[str, Any]) -> bool:
        """Check if manifest defines resource limits."""
        spec = manifest.get("spec", {})
        template = spec.get("template", {})
        containers = template.get("spec", {}).get("containers", [])
        
        for container in containers:
            if "resources" in container:
                return True
        return False
