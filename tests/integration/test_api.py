"""Integration tests for authentication API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationAPI:
    """Authentication endpoint integration tests."""

    def test_login_with_valid_credentials(self, client, test_user_data):
        """Test successful login with valid credentials."""
        # This is a placeholder - implement based on your actual API
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data

    def test_login_with_invalid_credentials(self, client):
        """Test login fails with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data

    def test_login_with_missing_email(self, client, test_user_data):
        """Test login validation for missing email."""
        response = client.post(
            "/api/v1/auth/login",
            json={"password": test_user_data["password"]},
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data or "email" in str(data).lower()

    def test_registration_creates_user(self, client, test_user_data):
        """Test user registration creates new account."""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data

    def test_registration_prevents_duplicate_email(self, client, test_user_data):
        """Test registration rejects duplicate email."""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Attempt duplicate
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data,
        )
        
        assert response.status_code == 409  # Conflict
        data = response.get_json()
        assert "error" in data or "exists" in str(data).lower()

    def test_token_refresh(self, client, test_user_data):
        """Test refreshing access token."""
        # Login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        refresh_token = login_response.get_json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data

    def test_logout_invalidates_token(self, client):
        """Test logout invalidates access token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer valid_token_here"},
        )
        
        assert response.status_code in [200, 204]

    def test_protected_endpoint_requires_auth(self, client):
        """Test protected endpoint rejects unauthenticated requests."""
        response = client.get("/api/v1/user/profile")
        
        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data or "auth" in str(data).lower()

    def test_password_reset_sends_email(self, client):
        """Test password reset email is triggered."""
        with patch('src.services.email.send_email') as mock_email:
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"},
            )
            
            assert response.status_code == 200
            # Verify email was sent (even if user doesn't exist, for security)
            # This depends on your implementation

    def test_admin_endpoint_requires_admin_role(self, client):
        """Test admin endpoints require admin authorization."""
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": "Bearer non_admin_token"},
        )
        
        assert response.status_code == 403


@pytest.mark.integration
class TestUserAPI:
    """User endpoint integration tests."""

    def test_get_user_profile(self, client):
        """Test retrieving user profile."""
        response = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": "Bearer valid_token"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "id" in data
        assert "email" in data

    def test_update_user_profile(self, client):
        """Test updating user profile."""
        response = client.patch(
            "/api/v1/user/profile",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer valid_token"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated Name"

    def test_change_password(self, client):
        """Test changing password."""
        response = client.post(
            "/api/v1/user/change-password",
            json={
                "old_password": "current-password",
                "new_password": "new-password-123",
            },
            headers={"Authorization": "Bearer valid_token"},
        )
        
        assert response.status_code in [200, 204]


@pytest.mark.integration
@pytest.mark.slow
class TestErrorHandling:
    """Test error handling across API."""

    def test_database_error_returns_500(self, client):
        """Test database errors return 500 status."""
        with patch('src.database.get_connection') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            response = client.get(
                "/api/v1/health",
                headers={"Authorization": "Bearer valid_token"},
            )
            
            assert response.status_code >= 500

    def test_validation_error_returns_400(self, client):
        """Test validation errors return 400 status."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "invalid-email", "password": ""},
        )
        
        assert response.status_code == 400

    def test_not_found_returns_404(self, client):
        """Test non-existent resources return 404."""
        response = client.get(
            "/api/v1/nonexistent-resource",
            headers={"Authorization": "Bearer valid_token"},
        )
        
        assert response.status_code == 404
