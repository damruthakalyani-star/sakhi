"""Unit tests for configuration and production validation guards."""

import pytest
from backend.app.core.config import Settings
from pydantic import ValidationError


def test_dev_settings():
    s = Settings(APP_ENV="development", DEBUG=True, SECRET_KEY="dev-insecure-key-123")
    assert s.APP_ENV == "development"
    assert s.DEBUG is True
    assert len(s.cors_origins_list) > 0


def test_production_guard_rejects_insecure_secret():
    with pytest.raises(ValidationError, match="cryptographically strong secret"):
        Settings(APP_ENV="production", SECRET_KEY="dev-insecure-weak-key", DEBUG=False)


def test_production_guard_rejects_debug_true():
    with pytest.raises(
        ValidationError, match="DEBUG must be set to False in production"
    ):
        Settings(
            APP_ENV="production",
            SECRET_KEY="a" * 64,
            DEBUG=True,
            CORS_ORIGINS="https://sakhisahay.example",
        )


def test_production_guard_rejects_cors_wildcard():
    with pytest.raises(ValidationError, match="CORS_ORIGINS cannot contain wildcards"):
        Settings(
            APP_ENV="production",
            SECRET_KEY="a" * 64,
            DEBUG=False,
            CORS_ORIGINS="*",
        )


def test_production_valid_settings():
    s = Settings(
        APP_ENV="production",
        SECRET_KEY="a" * 64,
        DEBUG=False,
        CORS_ORIGINS="https://sakhisahay.example,https://app.sakhisahay.example",
    )
    assert s.APP_ENV == "production"
    assert s.DEBUG is False
    assert len(s.cors_origins_list) == 2
