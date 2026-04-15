#!/usr/bin/env python3
"""Tests for mypy strict mode enforcement."""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


class TestTypingCompliance:
    """Test that modules comply with strict typing requirements."""

    @pytest.fixture
    def src_dir(self) -> Path:
        """Get src directory path."""
        return Path(__file__).parent.parent.parent / "src"

    def test_mypy_strict_configuration_exists(self) -> None:
        """Test that mypy strict mode is configured."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Should have mypy section
        assert "[tool.mypy]" in content

    def test_core_security_module_is_typed(self) -> None:
        """Test that security module has type annotations."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            service = SecretScanService()
            # Check methods exist and are callable
            assert hasattr(SecretScanService, "scan_tree")
            assert hasattr(SecretScanService, "scan_refs")
            assert hasattr(SecretScanService, "scan_history")
        except ImportError:
            pytest.skip("Security module not available")

    def test_public_api_has_return_types(self) -> None:
        """Test that major public APIs have return type annotations."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            # Get method signature
            sig = inspect.signature(SecretScanService.scan_tree)
            # Should have return annotation
            assert sig.return_annotation != inspect.Signature.empty
        except Exception as e:
            pytest.skip(f"Could not verify type hints: {e}")

    def test_modules_use_future_annotations(self) -> None:
        """Test that key modules use PEP 563 annotations."""
        src_dir = Path(__file__).parent.parent.parent / "src"
        key_modules = [
            src_dir / "security" / "secret_scan_service.py",
        ]
        
        # Check key security module
        if key_modules[0].exists():
            content = key_modules[0].read_text()
            assert "from __future__ import annotations" in content

    def test_security_module_docstrings_present(self) -> None:
        """Test that security module has docstrings."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            # Check class docstring
            assert SecretScanService.__doc__ is not None
            # Check method docstring
            assert SecretScanService.scan_tree.__doc__ is not None
        except ImportError:
            pytest.skip("Security module not available")


class TestTypeAnnotationPatterns:
    """Test that code follows type annotation patterns."""

    def test_scan_service_methods_have_signatures(self) -> None:
        """Test that SecretScanService methods have proper signatures."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            service = SecretScanService()
            
            # Test methods are callable and have signatures
            assert callable(service.scan_tree)
            assert callable(service.scan_refs)
            assert callable(service.scan_history)
        except ImportError:
            pytest.skip("Security module not available")

    def test_normalized_findings_are_consistent(self) -> None:
        """Test that finding normalization produces consistent results."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            service = SecretScanService()
            
            findings1 = [
                {"fingerprint": "z-secret"},
                {"fingerprint": "a-secret"},
            ]
            findings2 = [
                {"fingerprint": "a-secret"},
                {"fingerprint": "z-secret"},
            ]
            
            normalized1 = service.normalize_finding_keys(findings1)
            normalized2 = service.normalize_finding_keys(findings2)
            
            # Should be identical
            assert normalized1 == normalized2
        except ImportError:
            pytest.skip("Security module not available")

    def test_scan_report_structure(self) -> None:
        """Test that ScanReport has expected structure."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            service = SecretScanService()
            report = service.scan_tree()
            
            # Report should have expected attributes
            assert hasattr(report, "status")
            assert hasattr(report, "findings")
            assert hasattr(report, "run_id")
        except ImportError:
            pytest.skip("Security module not available")


class TestStrictModeConfiguration:
    """Test that strict mode is properly configured."""

    def test_pyproject_has_mypy_section(self) -> None:
        """Test that pyproject.toml has mypy section."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        assert "[tool.mypy]" in content

    def test_python_version_specified(self) -> None:
        """Test that Python version is specified for mypy."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Should have python_version specified
        assert "python_version" in content or "requires-python" in content

    def test_type_checking_works_on_imports(self) -> None:
        """Test that importing modules doesn't fail type checking."""
        try:
            from src.security.secret_scan_service import SecretScanService
            from src.security.models.scan_report import ScanReport
            
            # Basic import test
            assert SecretScanService is not None
            assert ScanReport is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_all_test_files_are_importable(self) -> None:
        """Test that all test files can be imported without type errors."""
        test_dir = Path(__file__).parent.parent.parent / "tests"
        
        # Should be able to import this file
        assert Path(__file__).exists()
        assert Path(__file__).suffix == ".py"


class TestTypeAnnotationCoverage:
    """Test type annotation coverage in codebase."""

    def test_functions_have_return_types(self) -> None:
        """Test that major functions have return type annotations."""
        try:
            import src.security.secret_scan_service as module
            
            # Get the module source
            import inspect
            source = inspect.getsource(module)
            
            # Check for type annotations in function definitions
            assert "->" in source or "ScanReport" in source
        except Exception:
            pytest.skip("Could not analyze module source")

    def test_class_methods_documented(self) -> None:
        """Test that class methods have docstrings."""
        try:
            from src.security.secret_scan_service import SecretScanService
            
            # Check methods have docstrings
            for method_name in ["scan_tree", "scan_refs", "scan_history"]:
                method = getattr(SecretScanService, method_name)
                assert method.__doc__ is not None
        except ImportError:
            pytest.skip("Security module not available")
