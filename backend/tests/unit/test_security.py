"""Unit tests for security, cryptography, and token helpers."""

import jwt
import pytest
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hashing():
    raw = "MySecretPassword2026!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert hashed.startswith("$2")
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_token_hashing():
    token = "some_sample_token_123"
    t_hash1 = hash_token(token)
    t_hash2 = hash_token(token)
    assert t_hash1 == t_hash2
    assert len(t_hash1) == 64  # SHA-256


def test_generate_secure_token():
    t1 = generate_secure_token(32)
    t2 = generate_secure_token(32)
    assert t1 != t2
    assert len(t1) >= 32


def test_jwt_access_token():
    user_id = "user_12345"
    token = create_access_token(user_id, role="admin", extra_claims={"foo": "bar"})
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert payload["foo"] == "bar"


def test_jwt_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid.token.payload")


def test_refresh_token_creation():
    raw, family, expires = create_refresh_token("user_123")
    assert raw.startswith("rft_")
    assert len(family) == 32
    assert expires is not None
