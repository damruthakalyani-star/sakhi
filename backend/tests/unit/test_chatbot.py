"""Unit tests for the AI Safety Chatbot service."""

from backend.app.schemas.chatbot import ChatbotMessageRequest
from backend.app.services.chatbot_service import ChatbotService


def test_chatbot_classification():
    service = ChatbotService()
    assert service.classify_topic("Someone is following me home!") == "followed"
    assert (
        service.classify_topic("I need to report harassment to police") == "harassment"
    )
    assert service.classify_topic("Tips for travelling alone at night") == "travel"
    assert service.classify_topic("Immediate danger help 112") == "emergency"
    assert service.classify_topic("Someone leaked my photos online") == "cyber"
    assert service.classify_topic("What is the weather today?") == "fallback"


def test_chatbot_bilingual_response():
    service = ChatbotService()

    # English
    req_en = ChatbotMessageRequest(message="What if I am followed?", language="en")
    res_en = service.generate_response(req_en)
    assert res_en.language == "en"
    assert res_en.key_topic == "followed"
    assert "busy, well-lit" in res_en.reply
    assert len(res_en.suggested_actions) > 0

    # Kannada
    req_kn = ChatbotMessageRequest(message="ಯಾರಾದರೂ ಹಿಂಬಾಲಿಸಿದರೆ", language="kn")
    res_kn = service.generate_response(req_kn)
    assert res_kn.language == "kn"
    assert res_kn.key_topic == "followed"
    assert "ಶಾಂತವಾಗಿರಿ" in res_kn.reply
