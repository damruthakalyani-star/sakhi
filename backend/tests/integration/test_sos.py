"""Integration tests for Emergency SOS trigger and resolution."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sos_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Add an emergency contact first
    await client.post(
        "/api/v1/contacts",
        json={
            "name": "Emergency Helper",
            "phone": "9876543210",
            "relationship": "Friend",
        },
        headers=auth_headers,
    )

    # 2. Check no active SOS initially
    res_initial = await client.get("/api/v1/sos/active", headers=auth_headers)
    assert res_initial.status_code == 200
    assert res_initial.json()["has_active_sos"] is False

    # 3. Trigger SOS
    sos_payload = {
        "latitude": 12.971598,
        "longitude": 77.594566,
        "accuracy": 12.5,
        "message": "Emergency! Need immediate help.",
    }
    res_trigger = await client.post(
        "/api/v1/sos/trigger", json=sos_payload, headers=auth_headers
    )
    assert res_trigger.status_code == 201
    sos_data = res_trigger.json()
    assert sos_data["status"] == "ACTIVE"
    assert sos_data["location"]["latitude"] == 12.971598
    assert len(sos_data["contacts_notified"]) == 1
    assert sos_data["contacts_notified"][0]["name"] == "Emergency Helper"

    # 4. Check active SOS
    res_active = await client.get("/api/v1/sos/active", headers=auth_headers)
    assert res_active.status_code == 200
    active_data = res_active.json()
    assert active_data["has_active_sos"] is True
    assert active_data["sos"]["status"] == "ACTIVE"

    # 5. Resolve SOS
    res_resolve = await client.post(
        "/api/v1/sos/resolve",
        json={"resolution_note": "User safely reached home"},
        headers=auth_headers,
    )
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "RESOLVED"

    # 6. Check active SOS is now False
    res_cleared = await client.get("/api/v1/sos/active", headers=auth_headers)
    assert res_cleared.json()["has_active_sos"] is False
