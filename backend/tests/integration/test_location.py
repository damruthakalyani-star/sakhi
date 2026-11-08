"""Integration tests for live location sharing and public link resolution."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_location_sharing_flow(client: AsyncClient, auth_headers: dict):
    # 1. Start live location share
    share_payload = {
        "latitude": 12.971598,
        "longitude": 77.594566,
        "accuracy": 8.0,
        "duration_minutes": 30,
    }
    res_share = await client.post(
        "/api/v1/location/share", json=share_payload, headers=auth_headers
    )
    assert res_share.status_code == 201
    share_data = res_share.json()
    share_token = share_data["share_token"]
    assert share_token.startswith("shr_")

    # 2. View shared location as an unauthenticated guest
    res_public = await client.get(f"/api/v1/location/shared/{share_token}")
    assert res_public.status_code == 200
    pub_data = res_public.json()
    assert pub_data["latitude"] == 12.971598
    assert pub_data["is_active"] is True
    assert "user_name" in pub_data

    # 3. Stop sharing
    res_stop = await client.delete("/api/v1/location/share", headers=auth_headers)
    assert res_stop.status_code == 204

    # 4. Public link is now expired/deactivated -> 404
    res_expired = await client.get(f"/api/v1/location/shared/{share_token}")
    assert res_expired.status_code == 404
