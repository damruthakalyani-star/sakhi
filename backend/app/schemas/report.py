"""Pydantic schemas for harassment reporting and incident diary."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

IncidentCategory = Literal["online", "stalking", "verbal", "physical", "other"]


class IncidentCreate(BaseModel):
    category: IncidentCategory
    incident_date: datetime
    location_summary: str | None = Field(None, max_length=200)
    notes: str = Field(min_length=5, max_length=5000)
    witnesses: str | None = Field(None, max_length=500)


class IncidentUpdate(BaseModel):
    category: IncidentCategory | None = None
    incident_date: datetime | None = None
    location_summary: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, min_length=5, max_length=5000)
    witnesses: str | None = Field(None, max_length=500)


class IncidentResponse(BaseModel):
    id: str
    user_id: str
    category: str
    incident_date: datetime
    location_summary: str | None = None
    notes: str
    witnesses: str | None = None
    evidence_files: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
