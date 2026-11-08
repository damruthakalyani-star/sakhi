"""Pytest fixtures for unit and integration tests."""

from collections.abc import AsyncGenerator

import mongomock_motor
import pytest_asyncio
from backend.app.core.rate_limit import limiter
from backend.app.db.indexes import create_indexes
from backend.app.db.mongo import db_manager
from backend.app.main import app
from httpx import ASGITransport, AsyncClient

# Disable rate limiting during automated test suite runs
limiter.enabled = False


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Sets up a clean in-memory mock MongoDB database for each test function."""
    mock_client = mongomock_motor.AsyncMongoMockClient()
    mock_db = mock_client["test_sakhisahay_db"]

    # Point db_manager to mock database
    db_manager.client = mock_client
    db_manager.db = mock_db
    db_manager._is_mock = True

    await create_indexes(mock_db)

    yield mock_db

    # Clean up after test
    await mock_client.drop_database("test_sakhisahay_db")
    mock_client.close()
    db_manager.client = None
    db_manager.db = None
    db_manager._is_mock = False


@pytest_asyncio.fixture(scope="function")
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient bound to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient) -> dict:
    """Creates a registered test user and returns Authorization Bearer headers."""
    signup_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
    }
    response = await client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
