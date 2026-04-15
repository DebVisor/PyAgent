#!/usr/bin/env python3
"""Tests for Docker Compose configuration."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestDockerConfiguration:
    """Test Docker Compose configuration."""

    def test_docker_compose_file_exists(self) -> None:
        """Test that docker-compose file exists."""
        root = Path(__file__).parent.parent.parent
        compose_paths = [
            root / "deploy" / "docker-compose.yaml",
            root / "deploy" / "docker-compose.yml",
        ]
        
        exists = any(p.exists() for p in compose_paths)
        if not exists:
            # Check for any docker-compose files
            glob_results = list(root.glob("**/docker-compose*.yaml"))
            glob_results.extend(root.glob("**/docker-compose*.yml"))
            assert len(glob_results) > 0 or exists

    def test_env_template_exists(self) -> None:
        """Test that environment template exists."""
        root = Path(__file__).parent.parent.parent
        env_files = [
            root / ".env.template",
            root / ".env.example",
            root / ".env",
        ]
        
        assert any(f.exists() for f in env_files)


class TestDockerServices:
    """Test Docker service configuration."""

    def test_compose_file_readable(self) -> None:
        """Test that compose file is readable."""
        root = Path(__file__).parent.parent.parent
        compose_file = root / "deploy" / "docker-compose.yaml"
        
        if compose_file.exists():
            content = compose_file.read_text()
            # Should be YAML-like content
            assert content
            assert "services:" in content or "version:" in content


class TestEnvironmentConfiguration:
    """Test environment variable configuration."""

    def test_env_template_readable(self) -> None:
        """Test that environment template is readable."""
        root = Path(__file__).parent.parent.parent
        env_file = root / ".env.template"
        
        if env_file.exists():
            content = env_file.read_text()
            # Should have some environment variables
            assert "=" in content or ":" in content
