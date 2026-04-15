"""Tests for Windows CI configuration."""

import yaml
import os
import pytest


def test_windows_ci_workflow_exists():
    """Test that Windows CI workflow file exists."""
    path = '.github/workflows/windows-ci.yml'
    assert os.path.exists(path), "windows-ci.yml workflow not found"


def test_windows_ci_workflow_valid_yaml():
    """Test that Windows CI workflow is valid YAML."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    assert isinstance(workflow, dict)


def test_windows_ci_has_triggers():
    """Test Windows CI has proper triggers."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    assert 'on' in workflow
    triggers = workflow['on']
    assert 'push' in triggers or 'pull_request' in triggers


def test_windows_ci_has_jobs():
    """Test Windows CI has job definitions."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    assert 'jobs' in workflow
    jobs = workflow['jobs']
    assert len(jobs) > 0
    assert 'test' in jobs or any('test' in job.lower() for job in jobs)


def test_windows_ci_has_python_matrix():
    """Test Windows CI tests multiple Python versions."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    strategy = test_job.get('strategy', {})
    matrix = strategy.get('matrix', {})
    
    python_versions = matrix.get('python-version', [])
    assert len(python_versions) >= 2
    assert '3.9' in python_versions or '3.9' in str(python_versions)


def test_windows_ci_has_os_matrix():
    """Test Windows CI tests on multiple Windows versions."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    strategy = test_job.get('strategy', {})
    matrix = strategy.get('matrix', {})
    
    os_list = matrix.get('os', [])
    assert len(os_list) > 0
    # Should test on Windows runners
    assert any('windows' in str(os).lower() for os in os_list)


def test_windows_ci_installs_dependencies():
    """Test Windows CI installs project dependencies."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    steps = test_job.get('steps', [])
    
    # Check for pip install step
    has_pip_install = any(
        'pip install' in str(step.get('run', '')) or 
        'requirements' in str(step.get('run', ''))
        for step in steps
    )
    assert has_pip_install, "Windows CI should install dependencies"


def test_windows_ci_runs_tests():
    """Test Windows CI runs pytest."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    steps = test_job.get('steps', [])
    
    # Check for pytest run
    has_pytest = any(
        'pytest' in str(step.get('run', ''))
        for step in steps
    )
    assert has_pytest, "Windows CI should run pytest"


def test_windows_ci_has_coverage():
    """Test Windows CI checks code coverage."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    steps = test_job.get('steps', [])
    
    # Check for coverage-related step
    has_coverage = any(
        'coverage' in str(step.get('run', '')) or
        'cov-' in str(step.get('run', ''))
        for step in steps
    )
    assert has_coverage, "Windows CI should check coverage"


def test_windows_ci_has_linting():
    """Test Windows CI runs linting checks."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    steps = test_job.get('steps', [])
    
    # Check for linting: pylint, flake8, ruff, or mypy
    has_lint = any(
        'pylint' in str(step.get('run', '')) or
        'flake8' in str(step.get('run', '')) or
        'ruff' in str(step.get('run', '')) or
        'mypy' in str(step.get('run', ''))
        for step in steps
    )
    assert has_lint, "Windows CI should run linting checks"


def test_windows_ci_has_upload_artifacts():
    """Test Windows CI uploads test results."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    steps = test_job.get('steps', [])
    
    # Check for artifact upload
    has_upload = any(
        'upload-artifact' in str(step) or
        'upload' in str(step.get('uses', ''))
        for step in steps
    )
    assert has_upload, "Windows CI should upload artifacts"


@pytest.mark.parametrize('python_version', ['3.9', '3.10', '3.11', '3.12'])
def test_windows_ci_tests_python_version(python_version):
    """Test Windows CI includes all supported Python versions."""
    with open('.github/workflows/windows-ci.yml', 'r') as f:
        workflow = yaml.safe_load(f)
    
    jobs = workflow['jobs']
    test_job = jobs.get('test', {})
    strategy = test_job.get('strategy', {})
    matrix = strategy.get('matrix', {})
    
    python_versions = matrix.get('python-version', [])
    python_str = str(python_versions)
    assert python_version in python_str, f"Windows CI should test Python {python_version}"
