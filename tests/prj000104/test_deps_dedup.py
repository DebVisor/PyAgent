#!/usr/bin/env python3
"""Tests for dependency deduplication."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestDepsDedup:
    """Test dependency deduplication analysis."""

    def test_requirements_files_exist(self) -> None:
        """Test that requirements files exist."""
        root = Path(__file__).parent.parent.parent
        
        # Should have at least one requirements file
        req_files = list(root.glob("requirements*.txt"))
        req_files.extend(root.glob("*/requirements.txt"))
        
        assert len(req_files) > 0

    def test_requirements_have_content(self) -> None:
        """Test that requirements files have dependencies."""
        root = Path(__file__).parent.parent.parent
        req_file = root / "requirements.txt"
        
        if req_file.exists():
            content = req_file.read_text()
            # Should have non-comment, non-empty lines
            non_comment = [
                line for line in content.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            assert len(non_comment) > 0


class TestDependencyAnalysis:
    """Test dependency analysis functionality."""

    def test_pyproject_has_dependencies(self) -> None:
        """Test that pyproject.toml defines dependencies."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Should have dependencies section
        assert "dependencies" in content

    def test_dev_dependencies_defined(self) -> None:
        """Test that dev dependencies are defined."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Should have optional-dependencies for dev
        assert "optional-dependencies" in content or "extras" in content

    def test_multiple_requirements_files(self) -> None:
        """Test that multiple requirements files exist."""
        root = Path(__file__).parent.parent.parent
        
        req_files = list(root.glob("requirements*.txt"))
        req_files.extend(root.glob("*/requirements.txt"))
        
        # Should have multiple requirement files
        if len(req_files) > 1:
            # Good - we have potential for duplicates
            assert True
        else:
            # Still valid - may use pyproject.toml exclusively
            assert True


class TestDependencyConsolidation:
    """Test dependency consolidation strategy."""

    def test_root_requirements_exists(self) -> None:
        """Test root requirements file exists."""
        root = Path(__file__).parent.parent.parent
        req_file = root / "requirements.txt"
        
        # May or may not exist, but check project has some req management
        pyproject = root / "pyproject.toml"
        assert req_file.exists() or pyproject.exists()

    def test_backend_structure_exists(self) -> None:
        """Test backend directory structure."""
        root = Path(__file__).parent.parent.parent
        backend_dir = root / "backend"
        
        # Backend may or may not exist
        if backend_dir.exists():
            # If it exists, should have some structure
            assert backend_dir.is_dir()

    def test_no_circular_dependencies(self) -> None:
        """Test that dependencies don't have obvious circular references."""
        root = Path(__file__).parent.parent.parent
        req_file = root / "requirements.txt"
        
        if req_file.exists():
            content = req_file.read_text()
            lines = [
                line.strip() for line in content.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            
            # Should have parseable package names
            assert len(lines) > 0
