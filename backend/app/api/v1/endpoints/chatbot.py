"""AI Safety Chatbot API endpoints."""

from typing import Literal

from backend.app.schemas.chatbot import (
    ChatbotFaqItem,
    ChatbotMessageRequest,
    ChatbotMessageResponse,
)
from backend.app.services.chatbot_service import ChatbotService
from fastapi import APIRouter, Query, status

router = APIRouter()
chatbot_service = ChatbotService()


@router.post(
    "/message",
    response_model=ChatbotMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Query the SAKHISAHAY safety companion",
)
async def chat_message(
    data: ChatbotMessageRequest,
) -> ChatbotMessageResponse:
    return chatbot_service.generate_response(data)


@router.get(
    "/faq",
    response_model=list[ChatbotFaqItem],
    status_code=status.HTTP_200_OK,
    summary="Get safety FAQ suggestions",
)
async def get_faqs(
    language: Literal["en", "kn"] = Query(default="en"),
) -> list[ChatbotFaqItem]:
    return chatbot_service.get_faqs(language)
