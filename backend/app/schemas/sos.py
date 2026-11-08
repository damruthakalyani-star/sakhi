"""Pydantic schemas for Emergency SOS Assistance."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GeoLocation(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    accuracy: float | None = Field(None, ge=0.0)


class SOSTriggerRequest(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    accuracy: float | None = Field(None, ge=0.0)
    message: str | None = Field(
        "I need help. Please contact me as soon as possible.", max_length=500
    )


class ContactAlertSnapshot(BaseModel):
    name: str
    phone: str
    relationship: str
    dispatch_status: str = "SENT"


class SOSResponse(BaseModel):
    id: str
    user_id: str
    status: Literal["ACTIVE", "RESOLVED", "CANCELLED"] = "ACTIVE"
    location: GeoLocation
    message: str | None = None
    contacts_notified: list[ContactAlertSnapshot] = []
    triggered_at: datetime
    resolved_at: datetime | None = None
    resolution_note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SOSResolveRequest(BaseModel):
    resolution_note: str | None = Field(
        default="Resolved safely by user", max_length=500
    )


class ActiveSOSStatus(BaseModel):
    has_active_sos: bool
    sos: SOSResponse | None = None
