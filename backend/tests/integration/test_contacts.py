"""Integration tests for emergency contact management and IDOR protection."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contacts_crud_and_validation(client: AsyncClient, auth_headers: dict):
    # 1. Initial list should be empty
    res_list = await client.get("/api/v1/contacts", headers=auth_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 0

    # 2. Add Contact
    contact_data = {
        "name": "Anjali Sharma",
        "phone": "9876543210",
        "relationship": "Family",
    }
    res_create = await client.post(
        "/api/v1/contacts", json=contact_data, headers=auth_headers
    )
    assert res_create.status_code == 201
    created = res_create.json()
    contact_id = created["id"]
    assert created["name"] == "Anjali Sharma"
    assert created["phone"] == "9876543210"

    # 3. Duplicate phone conflict
    res_dup = await client.post(
        "/api/v1/contacts", json=contact_data, headers=auth_headers
    )
    assert res_dup.status_code == 409
    assert res_dup.json()["error"]["code"] == "DUPLICATE_PHONE_NUMBER"

    # 4. Invalid phone format validation
    res_inv = await client.post(
        "/api/v1/contacts",
        json={"name": "Bad Phone", "phone": "12345", "relationship": "Friend"},
        headers=auth_headers,
    )
    assert res_inv.status_code == 422

    # 5. Update Contact
    res_update = await client.put(
        f"/api/v1/contacts/{contact_id}",
        json={"name": "Anjali Sharma-Rao", "relationship": "Guardian"},
        headers=auth_headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Anjali Sharma-Rao"
    assert res_update.json()["relationship"] == "Guardian"

    # 6. Delete Contact
    res_del = await client.delete(
        f"/api/v1/contacts/{contact_id}", headers=auth_headers
    )
    assert res_del.status_code == 204

    # 7. List should be empty again
    res_empty = await client.get("/api/v1/contacts", headers=auth_headers)
    assert res_empty.json()["total"] == 0


@pytest.mark.asyncio
async def test_contacts_idor_protection(client: AsyncClient, auth_headers: dict):
    """Verifies that User B cannot view, edit, or delete User A's contacts."""
    # User A creates a contact
    res_a = await client.post(
        "/api/v1/contacts",
        json={
            "name": "User A Contact",
            "phone": "9876543210",
            "relationship": "Family",
        },
        headers=auth_headers,
    )
    contact_id = res_a.json()["id"]

    # Register User B
    res_b_signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "User B",
            "email": "userb@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    token_b = res_b_signup.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B attempts to update User A's contact -> 404 (Not Found / IDOR protected)
    res_b_update = await client.put(
        f"/api/v1/contacts/{contact_id}",
        json={"name": "Hacked Name"},
        headers=headers_b,
    )
    assert res_b_update.status_code == 404

    # User B attempts to delete User A's contact -> 404
    res_b_delete = await client.delete(
        f"/api/v1/contacts/{contact_id}", headers=headers_b
    )
    assert res_b_delete.status_code == 404
