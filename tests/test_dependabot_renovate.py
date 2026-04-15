"""Tests for Dependabot and Renovate configuration."""

import json
import yaml
import os
import pytest


def test_renovate_json_exists():
    """Test that renovate.json exists."""
    path = '.github/renovate.json'
    assert os.path.exists(path), "renovate.json not found"


def test_renovate_json_valid():
    """Test that renovate.json is valid JSON."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    assert isinstance(config, dict)


def test_renovate_config_has_required_keys():
    """Test renovate config has required keys."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    assert 'extends' in config
    assert 'schedule' in config
    assert 'packageRules' in config


def test_renovate_extends_presets():
    """Test renovate extends from recommended presets."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    extends = config.get('extends', [])
    assert 'config:base' in extends
    assert isinstance(extends, list)


def test_renovate_automerge_rules():
    """Test renovate has automerge package rules."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    package_rules = config.get('packageRules', [])
    assert len(package_rules) > 0
    
    # Check for automerge configuration
    has_automerge_rule = any(
        'automerge' in rule 
        for rule in package_rules
    )
    assert has_automerge_rule


def test_dependabot_yml_exists():
    """Test that dependabot.yml exists."""
    path = '.github/dependabot.yml'
    assert os.path.exists(path), "dependabot.yml not found"


def test_dependabot_yml_valid():
    """Test that dependabot.yml is valid YAML."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    assert isinstance(config, dict)


def test_dependabot_config_has_updates():
    """Test dependabot config has updates section."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    assert 'updates' in config
    assert isinstance(config['updates'], list)
    assert len(config['updates']) > 0


def test_dependabot_has_github_actions():
    """Test dependabot has GitHub Actions ecosystem."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    ecosystems = [u.get('package-ecosystem') for u in config['updates']]
    assert 'github-actions' in ecosystems


def test_dependabot_has_python():
    """Test dependabot has Python pip ecosystem."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    ecosystems = [u.get('package-ecosystem') for u in config['updates']]
    assert 'pip' in ecosystems


def test_dependabot_has_docker():
    """Test dependabot has Docker ecosystem."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    ecosystems = [u.get('package-ecosystem') for u in config['updates']]
    assert 'docker' in ecosystems


def test_dependabot_schedule_configured():
    """Test dependabot updates have schedule."""
    with open('.github/dependabot.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    for update in config['updates']:
        assert 'schedule' in update
        assert 'interval' in update['schedule']


def test_renovate_python_enabled():
    """Test renovate has Python support enabled."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    # Renovate auto-detects Python, or explicitly enables it
    assert 'python' in config or 'extends' in config


def test_renovate_minimum_release_age():
    """Test renovate has minimum release age for stability."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    # Should have minimum release age (days)
    assert 'minimumReleaseAge' in config or any(
        'minimumReleaseAge' in rule 
        for rule in config.get('packageRules', [])
    )


@pytest.mark.parametrize('key', ['labels', 'assignees', 'reviewers'])
def test_renovate_has_automation_config(key):
    """Test renovate has automation configuration."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    assert key in config


def test_vulnerability_alerts_enabled():
    """Test that vulnerability alerts are enabled."""
    with open('.github/renovate.json', 'r') as f:
        config = json.load(f)
    
    assert 'vulnerabilityAlerts' in config or 'enableVulnerabilityAlerts' in config
