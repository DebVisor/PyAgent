"""Integration tests configuration and fixtures."""

import os
import pytest
from typing import Generator
from unittest.mock import MagicMock

# Assuming a typical Flask/FastAPI backend structure
# Adjust imports based on your actual backend framework


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/1",
        "JWT_SECRET": "test-secret-key-change-in-production",
        "API_VERSION": "v1",
    }


@pytest.fixture(scope="session")
def database_url(test_config):
    """Provide database URL for tests."""
    return test_config["DATABASE_URL"]


@pytest.fixture(scope="session")
def app_factory(test_config):
    """Create app factory for testing."""
    def create_app():
        # Placeholder - adjust based on your framework
        app = MagicMock()
        app.config.update(test_config)
        return app
    return create_app


@pytest.fixture(scope="session")
def app(app_factory):
    """Create test application."""
    return app_factory()


@pytest.fixture
def client(app):
    """Provide test client."""
    # For Flask: return app.test_client()
    # For FastAPI: from fastapi.testclient import TestClient; return TestClient(app)
    # Placeholder
    return MagicMock()


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    # Placeholder - implement based on your ORM
    yield
    # Cleanup after test


@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "email": "test@example.com",
        "password": "test-password-123",
        "name": "Test User",
        "username": "testuser",
    }


@pytest.fixture
def test_admin_data():
    """Provide test admin user data."""
    return {
        "email": "admin@example.com",
        "password": "admin-password-123",
        "name": "Admin User",
        "username": "admin",
        "is_admin": True,
    }


@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    mock = MagicMock()
    mock.get.return_value.status_code = 200
    mock.get.return_value.json.return_value = {"status": "ok"}
    return mock


@pytest.fixture
def log_capture(caplog):
    """Capture logs during tests."""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
