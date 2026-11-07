"""
Unit Tests for Security & JWT Authentication
"""
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
)

def test_password_hashing():
    pw = "RailSignallingSecure2026!"
    hashed = get_password_hash(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_tokens():
    payload = {"sub": "user-uuid-1234", "role": "ENGINEER"}
    token = create_access_token(payload)
    decoded = verify_token(token, expected_type="access")
    assert decoded["sub"] == "user-uuid-1234"
    assert decoded["role"] == "ENGINEER"

    refresh = create_refresh_token(payload)
    decoded_refresh = verify_token(refresh, expected_type="refresh")
    assert decoded_refresh["sub"] == "user-uuid-1234"

