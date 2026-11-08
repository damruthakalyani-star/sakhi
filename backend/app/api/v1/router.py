"""Main API v1 router mounting all resource endpoints."""

from backend.app.api.v1.endpoints import (
    auth,
    chatbot,
    contacts,
    health,
    location,
    reports,
    sos,
)
from fastapi import APIRouter

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(
    contacts.router, prefix="/contacts", tags=["Emergency Contacts"]
)
api_v1_router.include_router(sos.router, prefix="/sos", tags=["Emergency SOS"])
api_v1_router.include_router(
    location.router, prefix="/location", tags=["Live Location"]
)
api_v1_router.include_router(chatbot.router, prefix="/chatbot", tags=["AI Chatbot"])
api_v1_router.include_router(
    reports.router, prefix="/reports", tags=["Harassment Reporting"]
)
api_v1_router.include_router(health.router, tags=["Health & Resources"])
