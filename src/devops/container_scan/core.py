"""Core container scanning implementation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Represents a detected vulnerability."""
    id: str
    cve: str
    severity: SeverityLevel
    package: str
    version: str
    description: Optional[str] = None
    fix_version: Optional[str] = None

    def __repr__(self) -> str:
        return f"Vulnerability(cve={self.cve}, severity={self.severity.value}, package={self.package})"


@dataclass
class ScanResult:
    """Results of a container image scan."""
    image: str
    scan_id: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    total_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_by_severity(self, severity: SeverityLevel) -> List[Vulnerability]:
        """Get vulnerabilities filtered by severity level."""
        return [v for v in self.vulnerabilities if v.severity == severity]

    def has_critical(self) -> bool:
        """Check if any critical vulnerabilities exist."""
        return self.critical_count > 0

    def __repr__(self) -> str:
        return f"ScanResult(image={self.image}, critical={self.critical_count}, high={self.high_count})"


class ContainerScanner:
    """Main container image scanner class."""

    def __init__(self, registry_url: Optional[str] = None):
        """Initialize container scanner.
        
        Args:
            registry_url: Optional container registry URL for authentication
        """
        self.registry_url = registry_url
        self.logger = logger

    def scan_image(self, image_name: str) -> ScanResult:
        """Scan a container image for vulnerabilities.
        
        Args:
            image_name: Full image name (e.g., 'ubuntu:22.04')
            
        Returns:
            ScanResult containing identified vulnerabilities
        """
        self.logger.info(f"Starting scan of image: {image_name}")
        
        # Create scan result
        result = ScanResult(
            image=image_name,
            scan_id=self._generate_scan_id(image_name),
        )
        
        # Simulate scanning (in production, this would call actual scanners)
        vulnerabilities = self._detect_vulnerabilities(image_name)
        
        result.vulnerabilities = vulnerabilities
        result.total_count = len(vulnerabilities)
        result.critical_count = len(result.get_by_severity(SeverityLevel.CRITICAL))
        result.high_count = len(result.get_by_severity(SeverityLevel.HIGH))
        
        self.logger.info(f"Scan complete: {result}")
        return result

    def validate_image(self, image_name: str) -> bool:
        """Validate that an image can be scanned.
        
        Args:
            image_name: Image name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not image_name or ":" not in image_name:
            self.logger.warning(f"Invalid image format: {image_name}")
            return False
        return True

    def _generate_scan_id(self, image_name: str) -> str:
        """Generate unique scan ID."""
        import hashlib
        return hashlib.md5(image_name.encode()).hexdigest()[:8]

    def _detect_vulnerabilities(self, image_name: str) -> List[Vulnerability]:
        """Detect vulnerabilities in image."""
        # Simulated vulnerability detection
        if "vulnerable" in image_name.lower():
            return [
                Vulnerability(
                    id="vuln-001",
                    cve="CVE-2024-0001",
                    severity=SeverityLevel.CRITICAL,
                    package="openssl",
                    version="1.1.1",
                    description="Critical vulnerability in OpenSSL",
                    fix_version="1.1.1k"
                )
            ]
        return []
