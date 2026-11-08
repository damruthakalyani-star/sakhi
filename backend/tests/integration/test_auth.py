"""Integration tests for Authentication, JWT rotation, and Account Lockout."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_full_lifecycle(client: AsyncClient):
    # 1. Signup
    signup_payload = {
        "full_name": "Kavya Murthy",
        "email": "kavya@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }
    res_signup = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert res_signup.status_code == 201
    signup_data = res_signup.json()
    assert "access_token" in signup_data
    assert signup_data["user"]["email"] == "kavya@example.com"
    assert "refresh_token" in res_signup.cookies

    # 2. Duplicate Signup Conflict
    res_dup = await client.post("/api/v1/auth/signup", json=signup_payload)
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    # 3. Login
    login_payload = {
        "email": "kavya@example.com",
        "password": "SecurePassword123!",
    }
    res_login = await client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    access_token = res_login.json()["access_token"]
    refresh_token = res_login.cookies["refresh_token"]

    # 4. Get Current User ("Me")
    headers = {"Authorization": f"Bearer {access_token}"}
    res_me = await client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == "kavya@example.com"
    assert me_data["emergency_contacts_count"] == 0

    # 5. Token Refresh Rotation
    res_refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert res_refresh.status_code == 200
    new_access_token = res_refresh.json()["access_token"]
    new_refresh_token = res_refresh.cookies["refresh_token"]
    assert new_access_token != access_token
    assert new_refresh_token != refresh_token

    # 6. Reuse Detection: attempting to use the OLD rotated refresh token
    res_reuse = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert res_reuse.status_code == 401
    assert res_reuse.json()["error"]["code"] == "TOKEN_REUSE_DETECTED"

    # 7. Logout
    res_logout = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access_token}"},
        cookies={"refresh_token": new_refresh_token},
    )
    assert res_logout.status_code == 204


@pytest.mark.asyncio
async def test_account_lockout_after_failures(client: AsyncClient):
    # Signup a test user
    signup_data = {
        "full_name": "Lockout Test",
        "email": "lockout@example.com",
        "password": "CorrectPassword123!",
        "confirm_password": "CorrectPassword123!",
    }
    await client.post("/api/v1/auth/signup", json=signup_data)

    # 4 failed login attempts -> 401
    for _ in range(4):
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": "lockout@example.com", "password": "WrongPassword!"},
        )
        assert res.status_code == 401

    # 5th failed attempt triggers lockout -> 403
    res_5th = await client.post(
        "/api/v1/auth/login",
        json={"email": "lockout@example.com", "password": "WrongPassword!"},
    )
    assert res_5th.status_code == 403
    assert res_5th.json()["error"]["code"] == "ACCOUNT_LOCKED"

    # Even with the CORRECT password, locked account is rejected with 403
    res_locked = await client.post(
        "/api/v1/auth/login",
        json={"email": "lockout@example.com", "password": "CorrectPassword123!"},
    )
    assert res_locked.status_code == 403
    assert res_locked.json()["error"]["code"] == "ACCOUNT_LOCKED"
