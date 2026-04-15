"""Tests for Frontend E2E configuration."""

import os
import pytest


def test_playwright_config_exists():
    """Test that Playwright config exists."""
    path = 'web/tests/e2e/playwright.config.ts'
    assert os.path.exists(path), "playwright.config.ts not found"


def test_playwright_config_valid():
    """Test that Playwright config has valid content."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    # Check for required config structure
    assert 'defineConfig' in content
    assert 'testDir' in content
    assert 'webServer' in content


def test_playwright_config_has_browsers():
    """Test that Playwright config includes multiple browsers."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'chromium' in content
    assert 'firefox' in content
    assert 'webkit' in content or 'Safari' in content


def test_playwright_config_has_projects():
    """Test that Playwright has project definitions."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'projects' in content


def test_playwright_config_has_reporter():
    """Test that Playwright config has reporters."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'reporter' in content
    assert 'html' in content


def test_playwright_config_has_web_server():
    """Test that Playwright config starts web server."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'webServer' in content
    # Should have command to start dev server
    assert 'command' in content or 'npm run dev' in content


def test_playwright_fixtures_exist():
    """Test that Playwright fixtures file exists."""
    path = 'web/tests/e2e/fixtures/page.ts'
    assert os.path.exists(path), "fixtures/page.ts not found"


def test_playwright_fixtures_has_auth():
    """Test that fixtures have authentication setup."""
    with open('web/tests/e2e/fixtures/page.ts', 'r') as f:
        content = f.read()
    
    assert 'authenticatedPage' in content or 'auth' in content.lower()


def test_e2e_tests_exist():
    """Test that E2E test files exist."""
    path = 'web/tests/e2e/specs/auth.spec.ts'
    assert os.path.exists(path), "e2e test file not found"


def test_e2e_tests_have_test_cases():
    """Test that E2E tests have test cases."""
    with open('web/tests/e2e/specs/auth.spec.ts', 'r') as f:
        content = f.read()
    
    # Check for test definitions
    assert 'test(' in content or 'describe(' in content


def test_e2e_auth_tests():
    """Test that E2E tests include auth tests."""
    with open('web/tests/e2e/specs/auth.spec.ts', 'r') as f:
        content = f.read()
    
    assert 'login' in content.lower()
    assert 'logout' in content.lower()


def test_e2e_tests_check_assertions():
    """Test that E2E tests use assertions."""
    with open('web/tests/e2e/specs/auth.spec.ts', 'r') as f:
        content = f.read()
    
    assert 'expect(' in content or 'assert' in content.lower()


def test_e2e_tests_use_page_objects():
    """Test that E2E tests use page object pattern."""
    with open('web/tests/e2e/specs/auth.spec.ts', 'r') as f:
        content = f.read()
    
    # Should use locators for page interactions
    assert 'locator' in content or 'page.goto' in content


def test_e2e_tests_handle_errors():
    """Test that E2E tests check error messages."""
    with open('web/tests/e2e/specs/auth.spec.ts', 'r') as f:
        content = f.read()
    
    assert 'error' in content.lower()


def test_playwright_config_has_tracing():
    """Test that Playwright has tracing for debugging."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'trace' in content or 'screenshot' in content


def test_playwright_config_has_timeout():
    """Test that Playwright has timeout configuration."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'timeout' in content


def test_playwright_config_parallel():
    """Test that Playwright runs tests in parallel."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert 'Parallel' in content or 'fullyParallel' in content


@pytest.mark.parametrize('browser', ['chromium', 'firefox', 'webkit'])
def test_e2e_browsers_supported(browser):
    """Test that E2E tests support all major browsers."""
    with open('web/tests/e2e/playwright.config.ts', 'r') as f:
        content = f.read()
    
    assert browser in content, f"E2E tests should support {browser}"
