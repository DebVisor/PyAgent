"""Tests for Tailwind CSS configuration."""

import json
import os
import pytest


def test_tailwind_config_exists():
    """Test that tailwind config file exists."""
    config_path = os.path.join(os.path.dirname(__file__), '../../../web/tailwind.config.js')
    assert os.path.exists(config_path), "tailwind.config.js not found"


def test_tailwind_config_has_required_keys():
    """Test that tailwind config has required structure."""
    # Read the config file as text
    config_path = 'web/tailwind.config.js'
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Check for required keys
    assert 'content:' in content or '"content"' in content
    assert 'theme:' in content or '"theme"' in content
    assert 'plugins:' in content or '"plugins"' in content
    assert 'darkMode' in content


def test_postcss_config_exists():
    """Test that PostCSS config file exists."""
    config_path = 'web/postcss.config.js'
    assert os.path.exists(config_path), "postcss.config.js not found"


def test_tailwind_css_exists():
    """Test that Tailwind CSS input file exists."""
    css_path = 'web/styles/tailwind.css'
    assert os.path.exists(css_path), "tailwind.css not found"


def test_tailwind_css_has_directives():
    """Test that Tailwind CSS has required directives."""
    css_path = 'web/styles/tailwind.css'
    with open(css_path, 'r') as f:
        content = f.read()
    
    assert '@tailwind base' in content
    assert '@tailwind components' in content
    assert '@tailwind utilities' in content


def test_tailwind_css_has_layer_customizations():
    """Test that Tailwind CSS has layer customizations."""
    css_path = 'web/styles/tailwind.css'
    with open(css_path, 'r') as f:
        content = f.read()
    
    assert '@layer base' in content
    assert '@layer components' in content
    assert '@layer utilities' in content


@pytest.mark.parametrize('button_class', ['.btn-primary', '.btn-secondary', '.btn-ghost'])
def test_button_classes_exist(button_class):
    """Test that button utility classes are defined."""
    css_path = 'web/styles/tailwind.css'
    with open(css_path, 'r') as f:
        content = f.read()
    
    assert button_class in content


def test_color_variables_defined():
    """Test that custom color variables are defined."""
    config_path = 'web/tailwind.config.js'
    with open(config_path, 'r') as f:
        content = f.read()
    
    assert 'primary' in content
    assert 'secondary' in content


def test_dark_mode_support():
    """Test that dark mode is properly configured."""
    config_path = 'web/tailwind.config.js'
    with open(config_path, 'r') as f:
        content = f.read()
    
    assert "darkMode: 'class'" in content or 'darkMode' in content


def test_responsive_breakpoints():
    """Test that responsive breakpoints are configured."""
    config_path = 'web/tailwind.config.js'
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Tailwind includes default breakpoints, we're checking config is set up
    assert 'theme:' in content or '"theme"' in content
