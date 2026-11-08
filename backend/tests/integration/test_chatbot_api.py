"""Integration tests for Chatbot API endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chatbot_api_message(client: AsyncClient):
    req_body = {
        "message": "What should I do if someone is following me?",
        "language": "en",
    }
    response = await client.post("/api/v1/chatbot/message", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["key_topic"] == "followed"
    assert data["emergency_helpline"] == "112"
    assert "busy, well-lit" in data["reply"]
    assert len(data["suggested_actions"]) > 0


@pytest.mark.asyncio
async def test_chatbot_api_kannada(client: AsyncClient):
    req_body = {
        "message": "ಯಾರಾದರೂ ನನ್ನನ್ನು ಹಿಂಬಾಲಿಸಿದರೆ",
        "language": "kn",
    }
    response = await client.post("/api/v1/chatbot/message", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "kn"
    assert data["key_topic"] == "followed"
