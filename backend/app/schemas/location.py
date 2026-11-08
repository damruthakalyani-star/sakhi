"""Pydantic schemas for live location sharing."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocationShareRequest(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    accuracy: float | None = Field(None, ge=0.0)
    duration_minutes: int = Field(default=60, ge=5, le=1440)


class LocationShareResponse(BaseModel):
    share_token: str
    share_url: str
    expires_at: datetime
    latitude: float
    longitude: float
    accuracy: float | None = None

    model_config = ConfigDict(from_attributes=True)


class PublicSharedLocationView(BaseModel):
    user_name: str
    latitude: float
    longitude: float
    accuracy: float | None = None
    updated_at: datetime
    expires_at: datetime
    is_active: bool
