"""Integration tests for Forgot Password, Reset Password, and Change Password."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(client: AsyncClient, test_db):
    # 1. Signup a user
    signup_data = {
        "full_name": "Reset User",
        "email": "reset@example.com",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
    }
    res_signup = await client.post("/api/v1/auth/signup", json=signup_data)
    assert res_signup.status_code == 201

    # 2. Request forgot password
    res_forgot = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
    )
    assert res_forgot.status_code == 200

    # Retrieve reset token from mock db
    reset_doc = await test_db.password_resets.find_one({"used": False})
    assert reset_doc is not None
    # We can test with invalid token -> 422
    res_invalid_reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token_12345", "new_password": "BrandNewPassword123!"},
    )
    assert res_invalid_reset.status_code == 422


@pytest.mark.asyncio
async def test_change_password_flow(client: AsyncClient, auth_headers: dict):
    # 1. Invalid current password
    res_bad = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
        },
        headers=auth_headers,
    )
    assert res_bad.status_code == 422

    # 2. Valid password change
    res_good = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
        },
        headers=auth_headers,
    )
    assert res_good.status_code == 200
    assert "Password changed" in res_good.json()["message"]
