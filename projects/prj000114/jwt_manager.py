"""JWT Token Management

This module provides JWT token generation, validation, and refresh token support.
"""

import hmac
import hashlib
import json
import base64
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class TokenClaims:
    """Represents JWT token claims."""
    sub: str  # Subject (usually user ID)
    exp: int  # Expiration time
    iat: int  # Issued at
    iss: str = "PyAgent"  # Issuer
    aud: str = "api"  # Audience
    
    def to_dict(self) -> Dict:
        """Convert claims to dictionary."""
        return asdict(self)


class JWTEncoder:
    """Encodes and decodes JWT tokens."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def encode(self, claims: Dict[str, Any]) -> str:
        """Encode claims into JWT token."""
        # Header
        header = {
            "alg": self.algorithm,
            "typ": "JWT"
        }
        
        # Encode header and payload
        header_encoded = self._base64_urlsafe_encode(json.dumps(header))
        payload_encoded = self._base64_urlsafe_encode(json.dumps(claims))
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = self._sign(message)
        signature_encoded = self._base64_urlsafe_encode(signature)
        
        return f"{message}.{signature_encoded}"
    
    def decode(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Decode and verify JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False, None, "Invalid token format"
            
            header_encoded, payload_encoded, signature_encoded = parts
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = self._sign(message)
            expected_signature_encoded = self._base64_urlsafe_encode(
                expected_signature
            )
            
            if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
                return False, None, "Invalid signature"
            
            # Decode payload
            try:
                payload_json = self._base64_urlsafe_decode(payload_encoded)
                payload = json.loads(payload_json)
                return True, payload, None
            except (json.JSONDecodeError, ValueError) as e:
                return False, None, f"Failed to decode payload: {e}"
        
        except Exception as e:
            return False, None, str(e)
    
    def _sign(self, message: str) -> bytes:
        """Create HMAC signature."""
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    
    @staticmethod
    def _base64_urlsafe_encode(data: str) -> str:
        """Base64 URL-safe encoding."""
        if isinstance(data, str):
            data = data.encode()
        return base64.urlsafe_b64encode(data).decode().rstrip("=")
    
    @staticmethod
    def _base64_urlsafe_decode(data: str) -> str:
        """Base64 URL-safe decoding."""
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data).decode()


class TokenValidator:
    """Validates JWT tokens."""
    
    def __init__(self, encoder: JWTEncoder):
        self.encoder = encoder
    
    def validate(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate token signature and expiration."""
        is_valid, claims, error = self.encoder.decode(token)
        if not is_valid:
            return False, None, error
        
        # Check expiration
        if "exp" in claims:
            exp_time = claims["exp"]
            current_time = int(datetime.utcnow().timestamp())
            if current_time > exp_time:
                return False, None, "Token expired"
        
        return True, claims, None
    
    def get_claims(self, token: str) -> Optional[Dict]:
        """Extract claims from token without full validation."""
        is_valid, claims, _ = self.encoder.decode(token)
        return claims if is_valid else None
    
    def extract_claim(self, token: str, claim_name: str) -> Optional[Any]:
        """Extract specific claim from token."""
        claims = self.get_claims(token)
        return claims.get(claim_name) if claims else None


class RefreshTokenManager:
    """Manages access and refresh token pairs."""
    
    def __init__(
        self,
        encoder: JWTEncoder,
        access_token_lifetime: int = 3600,  # 1 hour
        refresh_token_lifetime: int = 604800  # 7 days
    ):
        self.encoder = encoder
        self.validator = TokenValidator(encoder)
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime
        self.refresh_token_store: Dict[str, Dict] = {}
    
    def generate_token_pair(
        self,
        subject: str,
        additional_claims: Dict = None
    ) -> Tuple[str, str]:
        """Generate access and refresh token pair."""
        now = int(datetime.utcnow().timestamp())
        
        # Access token claims
        access_claims = {
            "sub": subject,
            "iat": now,
            "exp": now + self.access_token_lifetime,
            "iss": "PyAgent",
            "type": "access"
        }
        if additional_claims:
            access_claims.update(additional_claims)
        
        access_token = self.encoder.encode(access_claims)
        
        # Refresh token claims
        refresh_claims = {
            "sub": subject,
            "iat": now,
            "exp": now + self.refresh_token_lifetime,
            "iss": "PyAgent",
            "type": "refresh"
        }
        
        refresh_token = self.encoder.encode(refresh_claims)
        
        # Store refresh token
        self.refresh_token_store[refresh_token] = {
            "subject": subject,
            "created_at": now,
            "expires_at": now + self.refresh_token_lifetime
        }
        
        return access_token, refresh_token
    
    def refresh_access_token(
        self,
        refresh_token: str,
        additional_claims: Dict = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Generate new access token from refresh token."""
        # Validate refresh token
        is_valid, claims, error = self.validator.validate(refresh_token)
        if not is_valid:
            return False, None, error
        
        if claims.get("type") != "refresh":
            return False, None, "Invalid token type"
        
        # Check if refresh token is in store
        if refresh_token not in self.refresh_token_store:
            return False, None, "Refresh token revoked"
        
        # Generate new access token
        subject = claims.get("sub")
        now = int(datetime.utcnow().timestamp())
        
        new_claims = {
            "sub": subject,
            "iat": now,
            "exp": now + self.access_token_lifetime,
            "iss": "PyAgent",
            "type": "access"
        }
        if additional_claims:
            new_claims.update(additional_claims)
        
        new_access_token = self.encoder.encode(new_claims)
        return True, new_access_token, None
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token."""
        if refresh_token in self.refresh_token_store:
            del self.refresh_token_store[refresh_token]
            return True
        return False
