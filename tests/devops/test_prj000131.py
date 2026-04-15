"""Tests for prj000131: Container Scanning Security."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from devops.container_scan import (
    ContainerScanner,
    ScanResult,
    Vulnerability,
    ScanConfig,
    SeverityLevel,
)


class TestContainerScanner:
    """Test container image scanner."""

    def test_scanner_initialization(self):
        """Test scanner can be initialized."""
        scanner = ContainerScanner()
        assert scanner is not None

    def test_scan_image_basic(self):
        """Test basic image scanning."""
        scanner = ContainerScanner()
        result = scanner.scan_image("ubuntu:22.04")
        
        assert isinstance(result, ScanResult)
        assert result.image == "ubuntu:22.04"
        assert result.scan_id is not None

    def test_scan_vulnerable_image(self):
        """Test scanning image with vulnerabilities."""
        scanner = ContainerScanner()
        result = scanner.scan_image("vulnerable:latest")
        
        assert len(result.vulnerabilities) > 0
        assert result.critical_count > 0

    def test_validate_image(self):
        """Test image name validation."""
        scanner = ContainerScanner()
        
        assert scanner.validate_image("ubuntu:22.04") is True
        assert scanner.validate_image("invalid-image") is False
        assert scanner.validate_image("") is False

    def test_vulnerability_creation(self):
        """Test creating vulnerability objects."""
        vuln = Vulnerability(
            id="vuln-001",
            cve="CVE-2024-0001",
            severity=SeverityLevel.CRITICAL,
            package="openssl",
            version="1.1.1"
        )
        
        assert vuln.cve == "CVE-2024-0001"
        assert vuln.severity == SeverityLevel.CRITICAL

    def test_scan_config(self):
        """Test scan configuration."""
        config = ScanConfig(
            registry_url="registry.example.com",
            timeout_seconds=600,
            fail_on_critical=True
        )
        
        assert config.registry_url == "registry.example.com"
        assert config.is_critical_failure() is True
        assert config.should_scan_severity("high") is True


class TestScanResult:
    """Test scan result handling."""

    def test_result_creation(self):
        """Test creating scan result."""
        result = ScanResult(
            image="ubuntu:22.04",
            scan_id="test123"
        )
        
        assert result.image == "ubuntu:22.04"
        assert result.scan_id == "test123"
        assert len(result.vulnerabilities) == 0

    def test_get_by_severity(self):
        """Test filtering vulnerabilities by severity."""
        result = ScanResult(image="test", scan_id="1")
        
        result.vulnerabilities = [
            Vulnerability("1", "CVE-1", SeverityLevel.CRITICAL, "pkg", "1.0"),
            Vulnerability("2", "CVE-2", SeverityLevel.HIGH, "pkg", "1.0"),
        ]
        
        critical = result.get_by_severity(SeverityLevel.CRITICAL)
        assert len(critical) == 1

    def test_has_critical(self):
        """Test critical vulnerability detection."""
        result = ScanResult(image="test", scan_id="1", critical_count=1)
        assert result.has_critical() is True
        
        result2 = ScanResult(image="test", scan_id="2", critical_count=0)
        assert result2.has_critical() is False


class TestCodeQuality:
    """Code quality validation tests."""

    def test_module_imports(self):
        """Test all exports can be imported."""
        from devops.container_scan import (
            ContainerScanner,
            ScanResult,
            Vulnerability,
            ScanConfig,
            ScanError,
        )
        assert all([ContainerScanner, ScanResult, Vulnerability, ScanConfig, ScanError])

    def test_type_hints(self):
        """Test type hints are present."""
        import inspect
        scanner = ContainerScanner()
        sig = inspect.signature(scanner.scan_image)
        assert sig.return_annotation is not inspect.Parameter.empty

    def test_docstrings(self):
        """Test docstrings are present."""
        assert ContainerScanner.__doc__ is not None
        assert ContainerScanner.scan_image.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
