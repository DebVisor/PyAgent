"""Tests for JWT token management."""

import pytest
import time
from datetime import datetime
from jwt_manager import (
    TokenClaims,
    JWTEncoder,
    TokenValidator,
    RefreshTokenManager
)


class TestTokenClaims:
    """Test TokenClaims dataclass."""
    
    def test_claims_creation(self):
        """Test creating claims."""
        now = int(datetime.utcnow().timestamp())
        claims = TokenClaims(
            sub="user123",
            exp=now + 3600,
            iat=now
        )
        
        assert claims.sub == "user123"
        assert claims.iss == "PyAgent"
    
    def test_claims_to_dict(self):
        """Test converting claims to dict."""
        now = int(datetime.utcnow().timestamp())
        claims = TokenClaims(
            sub="user123",
            exp=now + 3600,
            iat=now
        )
        
        claims_dict = claims.to_dict()
        assert isinstance(claims_dict, dict)
        assert claims_dict["sub"] == "user123"


class TestJWTEncoder:
    """Test JWT encoding and decoding."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.encoder = JWTEncoder("test-secret-key")
    
    def test_encode_decode_roundtrip(self):
        """Test encoding and decoding."""
        now = int(datetime.utcnow().timestamp())
        original_claims = {
            "sub": "user123",
            "exp": now + 3600,
            "iat": now
        }
        
        token = self.encoder.encode(original_claims)
        assert isinstance(token, str)
        assert len(token.split(".")) == 3
        
        is_valid, decoded_claims, error = self.encoder.decode(token)
        assert is_valid is True
        assert error is None
        assert decoded_claims["sub"] == "user123"
    
    def test_encode_creates_valid_jwt(self):
        """Test that encoded token is a valid JWT."""
        claims = {"sub": "user", "iat": 123, "exp": 456}
        token = self.encoder.encode(claims)
        
        parts = token.split(".")
        assert len(parts) == 3
        assert all(part for part in parts)
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        is_valid, claims, error = self.encoder.decode("invalid.token.format")
        assert is_valid is False
        assert error is not None
        assert claims is None
    
    def test_decode_tampered_token(self):
        """Test decoding tampered token."""
        now = int(datetime.utcnow().timestamp())
        claims = {"sub": "user123", "exp": now + 3600, "iat": now}
        
        token = self.encoder.encode(claims)
        parts = token.split(".")
        
        # Tamper with payload
        tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
        
        is_valid, decoded, error = self.encoder.decode(tampered_token)
        assert is_valid is False
        assert "signature" in error.lower()
    
    def test_different_secret_fails_validation(self):
        """Test that different secret fails validation."""
        now = int(datetime.utcnow().timestamp())
        claims = {"sub": "user", "exp": now + 3600, "iat": now}
        
        token = self.encoder.encode(claims)
        
        different_encoder = JWTEncoder("different-secret")
        is_valid, _, error = different_encoder.decode(token)
        
        assert is_valid is False


class TestTokenValidator:
    """Test token validation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.encoder = JWTEncoder("secret-key")
        self.validator = TokenValidator(self.encoder)
    
    def test_validate_valid_token(self):
        """Test validating a valid token."""
        now = int(datetime.utcnow().timestamp())
        claims = {
            "sub": "user123",
            "exp": now + 3600,
            "iat": now
        }
        
        token = self.encoder.encode(claims)
        is_valid, decoded, error = self.validator.validate(token)
        
        assert is_valid is True
        assert error is None
        assert decoded["sub"] == "user123"
    
    def test_validate_expired_token(self):
        """Test validating expired token."""
        now = int(datetime.utcnow().timestamp())
        claims = {
            "sub": "user123",
            "exp": now - 100,  # Expired 100 seconds ago
            "iat": now - 200
        }
        
        token = self.encoder.encode(claims)
        is_valid, decoded, error = self.validator.validate(token)
        
        assert is_valid is False
        assert "expired" in error.lower()
    
    def test_extract_claim(self):
        """Test extracting specific claim."""
        now = int(datetime.utcnow().timestamp())
        claims = {
            "sub": "user123",
            "exp": now + 3600,
            "iat": now,
            "role": "admin"
        }
        
        token = self.encoder.encode(claims)
        role = self.validator.extract_claim(token, "role")
        
        assert role == "admin"
    
    def test_extract_claim_invalid_token(self):
        """Test extracting claim from invalid token."""
        role = self.validator.extract_claim("invalid.token.here", "role")
        assert role is None


class TestRefreshTokenManager:
    """Test refresh token management."""
    
    def setup_method(self):
        """Setup test fixtures."""
        encoder = JWTEncoder("secret-key")
        self.manager = RefreshTokenManager(
            encoder,
            access_token_lifetime=3600,
            refresh_token_lifetime=604800
        )
    
    def test_generate_token_pair(self):
        """Test generating access and refresh token pair."""
        access_token, refresh_token = self.manager.generate_token_pair("user123")
        
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert access_token != refresh_token
    
    def test_token_pair_in_store(self):
        """Test that refresh token is stored."""
        access_token, refresh_token = self.manager.generate_token_pair("user123")
        
        assert refresh_token in self.manager.refresh_token_store
        stored = self.manager.refresh_token_store[refresh_token]
        assert stored["subject"] == "user123"
    
    def test_refresh_access_token(self):
        """Test refreshing access token."""
        access_token, refresh_token = self.manager.generate_token_pair("user123")
        
        is_valid, new_access_token, error = self.manager.refresh_access_token(refresh_token)
        
        assert is_valid is True
        assert error is None
        assert new_access_token != access_token
    
    def test_refresh_with_expired_refresh_token(self):
        """Test refresh with expired refresh token."""
        # Create manager with very short lifetime
        encoder = JWTEncoder("secret-key")
        manager = RefreshTokenManager(
            encoder,
            access_token_lifetime=1,
            refresh_token_lifetime=1
        )
        
        access_token, refresh_token = manager.generate_token_pair("user123")
        
        # Wait for token to expire
        time.sleep(2)
        
        is_valid, new_access, error = manager.refresh_access_token(refresh_token)
        assert is_valid is False
    
    def test_revoke_refresh_token(self):
        """Test revoking refresh token."""
        access_token, refresh_token = self.manager.generate_token_pair("user123")
        
        assert self.manager.revoke_refresh_token(refresh_token) is True
        assert refresh_token not in self.manager.refresh_token_store
    
    def test_refresh_revoked_token_fails(self):
        """Test that refreshing revoked token fails."""
        access_token, refresh_token = self.manager.generate_token_pair("user123")
        self.manager.revoke_refresh_token(refresh_token)
        
        is_valid, new_access, error = self.manager.refresh_access_token(refresh_token)
        assert is_valid is False
        assert "revoked" in error.lower()
    
    def test_generate_with_additional_claims(self):
        """Test generating token with additional claims."""
        additional = {"role": "admin", "permissions": ["read", "write"]}
        access_token, refresh_token = self.manager.generate_token_pair(
            "user123",
            additional_claims=additional
        )
        
        is_valid, claims, error = self.manager.validator.validate(access_token)
        assert claims["role"] == "admin"
