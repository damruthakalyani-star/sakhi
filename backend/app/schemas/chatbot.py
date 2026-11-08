"""Pydantic schemas for the AI Safety Chatbot."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatbotMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    language: Literal["en", "kn"] = "en"


class ChatbotMessageResponse(BaseModel):
    reply: str
    language: Literal["en", "kn"]
    key_topic: str
    emergency_helpline: str = "112"
    suggested_actions: list[str] = []
    created_at: datetime
