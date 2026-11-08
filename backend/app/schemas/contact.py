"""Pydantic schemas for emergency contact management."""

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RelationshipType = Literal["Family", "Friend", "Guardian", "Other"]


class ContactBase(BaseModel):
    name: str = Field(
        min_length=2, max_length=100, description="Full name of emergency contact"
    )
    phone: str = Field(description="10-digit Indian mobile number")
    relationship: RelationshipType = Field(description="Relationship to contact")

    @field_validator("phone")
    @classmethod
    def validate_indian_mobile(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError(
                "Phone number must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9."
            )
        return cleaned


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = None
    relationship: RelationshipType | None = None

    @field_validator("phone")
    @classmethod
    def validate_indian_mobile(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = re.sub(r"\D", "", v)
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError(
                "Phone number must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9."
            )
        return cleaned


class ContactResponse(ContactBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
