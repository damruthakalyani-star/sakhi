"""Common reusable Pydantic schemas and types."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    pages: int = Field(default=1, ge=0)


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None
