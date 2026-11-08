"""Integration tests for incident reporting diary."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_incident_reporting_crud_and_idor(
    client: AsyncClient, auth_headers: dict
):
    # 1. Create incident diary record
    incident_data = {
        "category": "stalking",
        "incident_date": datetime.now(UTC).isoformat(),
        "location_summary": "Near Metro Station Gate 2",
        "notes": "Repeated vehicle following observed on commute route.",
        "witnesses": "Local shopkeeper",
    }
    res_create = await client.post(
        "/api/v1/reports/incidents", json=incident_data, headers=auth_headers
    )
    assert res_create.status_code == 201
    created = res_create.json()
    report_id = created["id"]
    assert created["category"] == "stalking"

    # 2. List incidents
    res_list = await client.get("/api/v1/reports/incidents", headers=auth_headers)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 1
    assert list_data["items"][0]["id"] == report_id

    # 3. Update incident
    res_update = await client.put(
        f"/api/v1/reports/incidents/{report_id}",
        json={"notes": "Updated narrative: informed transit police security desk."},
        headers=auth_headers,
    )
    assert res_update.status_code == 200
    assert "transit police" in res_update.json()["notes"]

    # 4. IDOR test: User B cannot access User A's report
    res_b_signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "User B",
            "email": "userb_rep@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    headers_b = {"Authorization": f"Bearer {res_b_signup.json()['access_token']}"}

    res_b_get = await client.get(
        f"/api/v1/reports/incidents/{report_id}", headers=headers_b
    )
    assert res_b_get.status_code == 404

    res_b_del = await client.delete(
        f"/api/v1/reports/incidents/{report_id}", headers=headers_b
    )
    assert res_b_del.status_code == 404

    # 5. Delete incident by owner
    res_del = await client.delete(
        f"/api/v1/reports/incidents/{report_id}", headers=auth_headers
    )
    assert res_del.status_code == 204
