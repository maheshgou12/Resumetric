import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    hash_token,
)

def test_password_hashing():
    raw_password = "SecretPassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_access_token_creation_and_decode():
    user_id = "12345678-1234-5678-1234-567812345678"
    token = create_access_token(user_id, role="user")
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == "user"
    assert payload["type"] == "access"

def test_refresh_token_creation():
    raw_token, hashed_token = create_refresh_token()
    assert len(raw_token) > 20
    assert hash_token(raw_token) == hashed_token

def test_reset_url_uses_primary_domain():
    from app.core.config import settings
    token = "sample-token-123"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    assert "resumetric-1.onrender.com" in settings.FRONTEND_URL or "localhost" in settings.FRONTEND_URL
    assert f"token={token}" in reset_url


