"""AI Safety Chatbot API endpoints."""

from backend.app.schemas.chatbot import ChatbotMessageRequest, ChatbotMessageResponse
from backend.app.services.chatbot_service import ChatbotService
from fastapi import APIRouter, status

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
