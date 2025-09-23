"""
Unit tests for authentication and security utilities.

Tests the core security functions including password hashing,
JWT token creation and verification, and user authentication logic.
"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (create_access_token, get_password_hash,
                               verify_password, verify_token)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_creation(self):
        """Test that password hashing works correctly."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 50  # bcrypt hashes are long
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_password_verification_success(self):
        """Test that correct password verification works."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test that incorrect password verification fails."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Due to salt, hashes should be different
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test that access token creation works."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)

        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long

        # Decode the token to verify contents
        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert decoded["sub"] == subject
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_access_token_custom_expiry(self):
        """Test token creation with custom expiry time."""
        subject = "test@example.com"
        expires_delta = timedelta(hours=1)

        token = create_access_token(subject=subject, expires_delta=expires_delta)

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check that expiry is approximately 1 hour from now
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)

        # Check that the difference between exp and iat is approximately 1 hour
        time_diff = exp_time - iat_time
        expected_diff = expires_delta

        # Allow 10 second tolerance
        assert abs((time_diff - expected_diff).total_seconds()) < 10

    def test_verify_valid_token(self):
        """Test verification of valid token."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)

        email = verify_token(token)
        assert email == subject

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"

        email = verify_token(invalid_token)
        assert email is None

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        subject = "test@example.com"

        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(subject=subject, expires_delta=expires_delta)

        email = verify_token(token)
        assert email is None

    def test_verify_token_wrong_secret(self):
        """Test that token with wrong secret fails verification."""
        subject = "test@example.com"

        # Create token with different secret
        token = jwt.encode(
            {
                "sub": subject,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "iat": datetime.now(timezone.utc),
            },
            "wrong_secret",
            algorithm=settings.ALGORITHM,
        )

        email = verify_token(token)
        assert email is None

    def test_token_contains_required_claims(self):
        """Test that token contains all required claims."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check required claims
        assert "sub" in decoded  # Subject
        assert "exp" in decoded  # Expiration
        assert "iat" in decoded  # Issued at

        # Verify values
        assert decoded["sub"] == subject
        assert isinstance(decoded["exp"], int)
        assert isinstance(decoded["iat"], int)
        assert decoded["exp"] > decoded["iat"]


class TestSecurityIntegration:
    """Integration tests for security functions."""

    def test_password_token_workflow(self):
        """Test complete password and token workflow."""
        # 1. Hash password
        password = "securepassword123"
        hashed_password = get_password_hash(password)

        # 2. Verify password
        assert verify_password(password, hashed_password) is True

        # 3. Create token for user
        email = "user@example.com"
        token = create_access_token(subject=email)

        # 4. Verify token
        verified_email = verify_token(token)
        assert verified_email == email

    def test_security_edge_cases(self):
        """Test edge cases and error conditions."""
        # Empty password
        with pytest.raises(ValueError):
            get_password_hash("")

        # None password
        with pytest.raises((ValueError, TypeError)):
            get_password_hash(None)

        # Empty token
        assert verify_token("") is None

        # None token
        assert verify_token(None) is None

        # Malformed token
        assert verify_token("not.a.token") is None
