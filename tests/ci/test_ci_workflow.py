#!/usr/bin/env python3
"""Tests for CI workflow."""

import os

import yaml


def test_ci_workflow_exists() -> None:
    """The CI workflow file should exist in the expected location."""
    path = ".github/workflows/ci.yml"
    assert os.path.isfile(path)


def test_ci_workflow_sanity() -> None:
    """The CI workflow file should contain expected keys and structure."""
    with open(".github/workflows/ci.yml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "jobs" in data
    assert "test" in data["jobs"]
