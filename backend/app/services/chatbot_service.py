"""AI Safety Chatbot service providing bilingual safety guidance."""

from datetime import UTC, datetime
from typing import Any

from backend.app.schemas.chatbot import ChatbotMessageRequest, ChatbotMessageResponse

SAFETY_KNOWLEDGE: dict[str, dict[str, dict[str, Any]]] = {
    "en": {
        "emergency": {
            "reply": "🚨 IN IMMEDIATE DANGER? CALL 112 FIRST.\n\nSteps to take right now:\n• Call 112 immediately. This is India's national emergency number for police, medical, and fire assistance.\n• Move quickly into a safe, populated, and well-lit area.\n• Alert people around you clearly that you need assistance.\n• Once secure, contact a trusted family member or friend.",
            "actions": [
                "Call 112 immediately",
                "Move to a crowded place",
                "Trigger Emergency SOS in SAKHISAHAY",
            ],
            "helpline": "112",
        },
        "followed": {
            "reply": "If you suspect someone is following you:\n• Stay calm and head directly toward a busy, well-lit public place (e.g., open shop, petrol station, metro station, bus stop).\n• DO NOT go straight home or into secluded alleys—prevent them from identifying your residence.\n• Call a trusted contact or emergency services (112) and stay on the line.\n• If safe, take mental note of their appearance or vehicle number.\n• Approach security guards, police personnel, or store employees and ask for shelter/help.",
            "actions": [
                "Head to a brightly lit shop/station",
                "Call 112 or a trusted contact",
                "Share your live location in SAKHISAHAY",
            ],
            "helpline": "112",
        },
        "harassment": {
            "reply": "To report harassment and protect yourself:\n• If you are currently in danger, dial 112 immediately.\n• For support and counseling, call the 24x7 Women Helpline at 181 or the police helpline at 1091.\n• You can register a formal complaint or FIR at the nearest police station. Police are legally mandated to register FIRs for cognizable offenses.\n• Preserve all evidence: keep original screenshots, call logs, text messages, photos, and witness names.\n• Have a trusted person or legal counselor accompany you for support.",
            "actions": [
                "Call Women Helpline 181",
                "Preserve screenshots and call logs",
                "Document details in SAKHISAHAY Reporting Diary",
            ],
            "helpline": "181",
        },
        "travel": {
            "reply": "Tips for safe travel alone:\n• Share your live trip location with a trusted contact before boarding any vehicle.\n• Use verified, licensed cabs and confirm vehicle registration numbers and driver details before entering.\n• Sit near the driver or near other female passengers in public buses or trains.\n• Keep your mobile phone charged and emergency numbers on speed dial.\n• Trust your instincts: if a driver takes an unfamiliar route or acts suspiciously, ask them to stop at a busy spot and call 112.",
            "actions": [
                "Share Live Location in SAKHISAHAY",
                "Verify vehicle registration number",
                "Keep phone charged",
            ],
            "helpline": "112",
        },
        "cyber": {
            "reply": "For online harassment and cyber safety:\n• Never delete abusive messages, profiles, or emails—they serve as crucial evidence.\n• Take full-screen screenshots displaying dates, timestamps, and usernames before blocking the harasser.\n• File a cyber complaint via the National Cyber Crime Portal at cybercrime.gov.in or call helpline 1930.\n• Change your passwords immediately and turn on two-factor authentication (2FA).\n• Review your social media privacy settings and restrict public visibility.",
            "actions": [
                "Report on cybercrime.gov.in",
                "Call Cyber Helpline 1930",
                "Enable Two-Factor Authentication",
            ],
            "helpline": "1930",
        },
        "fallback": {
            "reply": "I am your SAKHISAHAY Safety Companion. I can help guide you through:\n• Being followed or watched\n• Reporting harassment and preserving evidence\n• Travelling safely alone\n• Online cyber harassment\n• Emergency procedures\n\nIf you are in immediate danger anywhere in India, please call 112 immediately.",
            "actions": [
                "Ask about being followed",
                "Ask how to report harassment",
                "Call emergency 112",
            ],
            "helpline": "112",
        },
    },
    "kn": {
        "emergency": {
            "reply": "🚨 ತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದರೆ ಮೊದಲು 112 ಗೆ ಕರೆ ಮಾಡಿ.\n\nತಕ್ಷಣ ತೆಗೆದುಕೊಳ್ಳಬೇಕಾದ ಕ್ರಮಗಳು:\n• ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ. ಇದು ಪೊಲೀಸ್, ವೈದ್ಯಕೀಯ ಮತ್ತು ಅಗ್ನಿಶಾಮಕ ಸೇವೆಗಳ ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಂಖ್ಯೆ.\n• ಸುರಕ್ಷಿತ, ಜನನಿಬಿಡ ಮತ್ತು ಚೆನ್ನಾಗಿ ಬೆಳಕಿರುವ ಸ್ಥಳಕ್ಕೆ ಬೇಗನೆ ಹೋಗಿ.\n• ನಿಮ್ಮ ಸುತ್ತಲಿನ ಜನರಿಗೆ ನಿಮಗೆ ಸಹಾಯ ಬೇಕೆಂದು ಸ್ಪಷ್ಟವಾಗಿ ತಿಳಿಸಿ.\n• ಸುರಕ್ಷಿತರಾದ ನಂತರ ನಂಬಿಕಸ್ಥ ವ್ಯಕ್ತಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            "actions": [
                "ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ",
                "ಜನನಿಬಿಡ ಸ್ಥಳಕ್ಕೆ ಹೋಗಿ",
                "SAKHISAHAY ನಲ್ಲಿ SOS ಬಳಸಿ",
            ],
            "helpline": "112",
        },
        "followed": {
            "reply": "ಯಾರಾದರೂ ನಿಮ್ಮನ್ನು ಹಿಂಬಾಲಿಸುತ್ತಿದ್ದಾರೆ ಎಂದು ಅನಿಸಿದರೆ:\n• ಶಾಂತವಾಗಿರಿ ಮತ್ತು ಅಂಗಡಿ, ಪೆಟ್ರೋಲ್ ಬಂಕ್ ಅಥವಾ ಬಸ್ ನಿಲ್ದಾಣದಂತಹ ಜನನಿಬಿಡ, ಬೆಳಕಿರುವ ಸ್ಥಳದ ಕಡೆಗೆ ಹೋಗಿ.\n• ನೇರವಾಗಿ ಮನೆಗೆ ಹೋಗಬೇಡಿ—ನಿಮ್ಮ ಮನೆಯ ವಿಳಾಸ ಅವರಿಗೆ ತಿಳಿಯಬಾರದು.\n• ನಂಬಿಕಸ್ಥ ವ್ಯಕ್ತಿಗೆ ಅಥವಾ ತುರ್ತು ಸಂಖ್ಯೆ 112 ಗೆ ಕರೆ ಮಾಡಿ.\n• ಸುರಕ್ಷಿತವಾಗಿದ್ದರೆ, ಅವರ ರೂಪ ಅಥವಾ ವಾಹನದ ಸಂಖ್ಯೆಯನ್ನು ನೆನಪಿನಲ್ಲಿಡಿ.\n• ಅಂಗಡಿ ಸಿಬ್ಬಂದಿ, ಭದ್ರತಾ ಸಿಬ್ಬಂದಿ ಅಥವಾ ಪೊಲೀಸರ ಸಹಾಯ ಕೇಳಿ.",
            "actions": [
                "ಬೆಳಕಿರುವ ಅಂಗಡಿಗೆ ಹೋಗಿ",
                "112 ಗೆ ಕರೆ ಮಾಡಿ",
                "ಲೈವ್ ಲೊಕೇಶನ್ ಹಂಚಿಕೊಳ್ಳಿ",
            ],
            "helpline": "112",
        },
        "harassment": {
            "reply": "ಕಿರುಕುಳದ ಬಗ್ಗೆ ದೂರು ನೀಡಲು:\n• ನೀವು ಈಗಲೇ ಅಪಾಯದಲ್ಲಿದ್ದರೆ 112 ಗೆ ಕರೆ ಮಾಡಿ.\n• ಮಹಿಳಾ ಸಹಾಯವಾಣಿ 181 ಮತ್ತು ಪೊಲೀಸ್ ಸಹಾಯವಾಣಿ 1091 ಗೆ ಕರೆ ಮಾಡಿ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ.\n• ಹತ್ತಿರದ ಪೊಲೀಸ್ ಠಾಣೆಯಲ್ಲಿ ದೂರು ಅಥವಾ ಎಫ್‌ಐಆರ್ ದಾಖಲಿಸಿ.\n• ಸಾಕ್ಷ್ಯಗಳನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ: ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ಗಳು, ಕರೆ ವಿವರಗಳು, ಫೋಟೋಗಳು ಮತ್ತು ಸಾಕ್ಷಿಗಳ ವಿವರಗಳನ್ನು ಉಳಿಸಿ.\n• ನಿಮ್ಮ ನಂಬಿಕಸ್ಥ ವ್ಯಕ್ತಿಯ ಸಹಾಯದೊಂದಿಗೆ ಮುಂದುವರಿಯಿರಿ.",
            "actions": [
                "ಮಹಿಳಾ ಸಹಾಯವಾಣಿ 181 ಗೆ ಕರೆ ಮಾಡಿ",
                "ಸಾಕ್ಷ್ಯಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ",
                "SAKHISAHAY ನಲ್ಲಿ ದಾಖಲಿಸಿ",
            ],
            "helpline": "181",
        },
        "travel": {
            "reply": "ಒಂಟಿಯಾಗಿ ಪ್ರಯಾಣಿಸುವಾಗ ಸುರಕ್ಷತಾ ಸಲಹೆಗಳು:\n• ಪ್ರಯಾಣ ಪ್ರಾರಂಭಿಸುವ ಮೊದಲು ನಿಮ್ಮ ಲೈವ್ ಲೊಕೇಶನ್ ಅನ್ನು ನಂಬಿಕಸ್ಥ ವ್ಯಕ್ತಿಯೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಿ.\n• ಪರವಾನಗಿ ಪಡೆದ ಕ್ಯಾಬ್‌ಗಳನ್ನು ಬಳಸಿ ಮತ್ತು ವಾಹನದ ಸಂಖ್ಯೆಯನ್ನು ಪರಿಶೀಲಿಸಿ.\n• ಸಾರ್ವಜನಿಕ ವಾಹನಗಳಲ್ಲಿ ಮಹಿಳಾ ಪ್ರಯಾಣಿಕರ ಬಳಿ ಕುಳಿತುಕೊಳ್ಳಿ.\n• ಮೊಬೈಲ್ ಫೋನ್ ಚಾರ್ಜ್ ಇರಲಿ ಮತ್ತು ತುರ್ತು ಸಂಖ್ಯೆಗಳು ಸುಲಭವಾಗಿ ಸಿಗುವಂತಿರಲಿ.\n• ಸಂಶಯಾಸ್ಪದ ಮಾರ್ಗದಲ್ಲಿ ಹೋದರೆ ತಕ್ಷಣ ವಾಹನ ನಿಲ್ಲಿಸಿ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
            "actions": [
                "ಲೈವ್ ಲೊಕೇಶನ್ ಹಂಚಿಕೊಳ್ಳಿ",
                "ವಾಹನ ಸಂಖ್ಯೆ ಪರಿಶೀಲಿಸಿ",
                "ಫೋನ್ ಚಾರ್ಜ್ ಇರಲಿ",
            ],
            "helpline": "112",
        },
        "cyber": {
            "reply": "ಆನ್‌ಲೈನ್ ಕಿರುಕುಳ ಮತ್ತು ಸೈಬರ್ ಸುರಕ್ಷತೆಗಾಗಿ:\n• ಸಂದೇಶಗಳು ಅಥವಾ ಇಮೇಲ್‌ಗಳನ್ನು ಅಳಿಸಬೇಡಿ—ಅವು ಮುಖ್ಯ ಸಾಕ್ಷಿಗಳಾಗಿವೆ.\n• ನಿರ್ಬಂಧಿಸುವ (ಬ್ಲಾಕ್) ಮೊದಲು ದಿನಾಂಕ, ಸಮಯ ಮತ್ತು ಬಳಕೆದಾರ ಹೆಸರಿನೊಂದಿಗೆ ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.\n• cybercrime.gov.in ನಲ್ಲಿ ಅಥವಾ ಸಹಾಯವಾಣಿ 1930 ಗೆ ದೂರು ದಾಖಲಿಸಿ.\n• ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್‌ಗಳನ್ನು ಬದಲಾಯಿಸಿ ಮತ್ತು 2FA ಸಕ್ರಿಯಗೊಳಿಸಿ.\n• ಸಾಮಾಜಿಕ ಮಾಧ್ಯಮದ ಗೌಪ್ಯತಾ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಬಿಗಿಗೊಳಿಸಿ.",
            "actions": [
                "cybercrime.gov.in ಗೆ ಭೇಟಿ ನೀಡಿ",
                "1930 ಗೆ ಕರೆ ಮಾಡಿ",
                "ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಿ",
            ],
            "helpline": "1930",
        },
        "fallback": {
            "reply": "ನಾನು ನಿಮ್ಮ SAKHISAHAY ಸುರಕ್ಷತಾ ಸಂಗಾತಿ. ಈ ವಿಷಯಗಳಲ್ಲಿ ನಾನು ನಿಮಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡಬಲ್ಲೆ:\n• ಯಾರಾದರೂ ಹಿಂಬಾಲಿಸುವುದು\n• ಕಿರುಕುಳದ ದೂರು ಮತ್ತು ಸಾಕ್ಷ್ಯ ಸಂರಕ್ಷಣೆ\n• ಒಂಟಿ ಪ್ರಯಾಣದ ಸುರಕ್ಷತೆ\n• ಆನ್‌ಲೈನ್ ಸೈಬರ್ ಕಿರುಕುಳ\n• ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳು\n\nತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದರೆ ದಯವಿಟ್ಟು 112 ಗೆ ಕರೆ ಮಾಡಿ.",
            "actions": [
                "ಹಿಂಬಾಲಿಸುವ ಬಗ್ಗೆ ಕೇಳಿ",
                "ಕಿರುಕುಳ ವರದಿ ಬಗ್ಗೆ ಕೇಳಿ",
                "112 ಗೆ ಕರೆ ಮಾಡಿ",
            ],
            "helpline": "112",
        },
    },
}

TOPIC_KEYWORDS = [
    (
        "followed",
        [
            "follow",
            "stalk",
            "chasing",
            "watching me",
            "behind me",
            "creepy guy",
            "ಹಿಂಬಾಲ",
            "ನೋಡುತ್ತಿದ್ದಾರೆ",
        ],
    ),
    (
        "harassment",
        [
            "harass",
            "report",
            "complaint",
            "fir",
            "abuse",
            "grop",
            "touch",
            "assault",
            "ಕಿರುಕುಳ",
            "ದೂರು",
            "ಎಫ್‌ಐಆರ್",
        ],
    ),
    (
        "travel",
        [
            "travel",
            "trip",
            "cab",
            "taxi",
            "uber",
            "ola",
            "auto",
            "alone",
            "journey",
            "bus",
            "train",
            "night",
            "ಪ್ರಯಾಣ",
            "ಒಂಟಿ",
            "ಕ್ಯಾಬ್",
            "ಬಸ್",
        ],
    ),
    (
        "cyber",
        [
            "cyber",
            "online",
            "hacked",
            "leak",
            "photo",
            "blackmail",
            "otp",
            "fake account",
            "whatsapp",
            "instagram",
            "ಸೈಬರ್",
            "ಖಾತೆ",
        ],
    ),
    (
        "emergency",
        [
            "emergency",
            "danger",
            "help me",
            "attack",
            "112",
            "police",
            "urgent",
            "save me",
            "ತುರ್ತು",
            "ಅಪಾಯ",
            "ಸಹಾಯ",
        ],
    ),
]


class ChatbotService:
    def classify_topic(self, text: str) -> str:
        lower = text.lower()
        for topic, keywords in TOPIC_KEYWORDS:
            if any(kw in lower for kw in keywords):
                return topic
        return "fallback"

    def generate_response(
        self, request: ChatbotMessageRequest
    ) -> ChatbotMessageResponse:
        lang = request.language if request.language in ("en", "kn") else "en"
        topic = self.classify_topic(request.message)

        lang_data = SAFETY_KNOWLEDGE.get(lang, SAFETY_KNOWLEDGE["en"])
        topic_data = lang_data.get(topic, lang_data["fallback"])

        return ChatbotMessageResponse(
            reply=topic_data["reply"],
            language=lang,
            key_topic=topic,
            emergency_helpline=topic_data.get("helpline", "112"),
            suggested_actions=topic_data.get("actions", []),
            created_at=datetime.now(UTC),
        )
