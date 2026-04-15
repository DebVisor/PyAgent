"""Tests for Ruff pre-commit integration."""

import pytest
from ruff_precommit import (
    RuffConfig,
    RuffVersionManager,
    PreCommitRuffHook,
    RuffViolation
)


class TestRuffConfig:
    """Test Ruff configuration handling."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = RuffConfig()
        cfg = config.get_config()
        
        assert cfg["line-length"] == 100
        assert "E" in cfg["select"]
        assert "F" in cfg["select"]
    
    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = RuffConfig()
        is_valid, errors = config.validate()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_config_has_required_fields(self):
        """Test that config has required fields."""
        config = RuffConfig()
        cfg = config.get_config()
        
        assert "line-length" in cfg
        assert "select" in cfg
        assert "ignore" in cfg
        assert "exclude" in cfg


class TestRuffVersionManager:
    """Test Ruff version management."""
    
    def test_version_comparison(self):
        """Test version comparison logic."""
        manager = RuffVersionManager()
        
        assert manager.compare_versions("0.1.0", "0.2.0") < 0
        assert manager.compare_versions("0.2.0", "0.1.0") > 0
        assert manager.compare_versions("0.1.0", "0.1.0") == 0
        assert manager.compare_versions("1.0.0", "0.9.9") > 0
    
    def test_version_comparison_different_lengths(self):
        """Test version comparison with different lengths."""
        manager = RuffVersionManager()
        
        assert manager.compare_versions("0.1", "0.1.0") < 0
        assert manager.compare_versions("0.1.0", "0.1") > 0
        assert manager.compare_versions("1.0.0.0", "1.0.0") > 0
    
    def test_min_version_setting(self):
        """Test minimum version setting."""
        manager = RuffVersionManager(min_version="0.5.0")
        assert manager.min_version == "0.5.0"


class TestPreCommitRuffHook:
    """Test pre-commit hook functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = RuffConfig()
        self.hook = PreCommitRuffHook(self.config)
    
    def test_violations_empty_initially(self):
        """Test that violations list is empty initially."""
        assert len(self.hook.violations) == 0
    
    def test_format_violations_no_violations(self):
        """Test formatting when there are no violations."""
        formatted = self.hook.format_violations()
        assert "No violations found" in formatted
    
    def test_add_violation(self):
        """Test adding a violation."""
        violation = RuffViolation(
            file="test.py",
            line=10,
            column=5,
            code="E501",
            message="Line too long"
        )
        self.hook.violations.append(violation)
        
        assert len(self.hook.violations) == 1
        assert self.hook.violations[0].file == "test.py"
    
    def test_format_violations_with_violations(self):
        """Test formatting when there are violations."""
        violation = RuffViolation(
            file="test.py",
            line=10,
            column=5,
            code="E501",
            message="Line too long"
        )
        self.hook.violations = [violation]
        
        formatted = self.hook.format_violations()
        assert "1 violations" in formatted
        assert "test.py:10:5" in formatted
        assert "E501" in formatted


class TestRuffViolation:
    """Test RuffViolation dataclass."""
    
    def test_violation_creation(self):
        """Test creating a violation."""
        v = RuffViolation(
            file="app.py",
            line=42,
            column=10,
            code="F841",
            message="Local variable assigned but never used"
        )
        
        assert v.file == "app.py"
        assert v.line == 42
        assert v.column == 10
        assert v.code == "F841"
        assert v.severity == "warning"
    
    def test_violation_default_severity(self):
        """Test that default severity is 'warning'."""
        v = RuffViolation(
            file="test.py",
            line=1,
            column=1,
            code="E001",
            message="test"
        )
        assert v.severity == "warning"
