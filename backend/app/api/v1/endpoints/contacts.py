"""Emergency contact management endpoints."""

from typing import Any

from backend.app.api.deps import get_contact_service, get_current_user
from backend.app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from backend.app.services.contact_service import ContactService
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

router = APIRouter()


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int


@router.get(
    "",
    response_model=ContactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List emergency contacts for current user",
)
async def list_contacts(
    current_user: dict[str, Any] = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
) -> ContactListResponse:
    contacts = await contact_service.list_contacts(current_user["id"])
    return ContactListResponse(
        items=[ContactResponse(**c) for c in contacts],
        total=len(contacts),
    )


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new emergency contact",
)
async def create_contact(
    data: ContactCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    contact = await contact_service.create_contact(current_user["id"], data)
    return ContactResponse(**contact)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing emergency contact",
)
async def update_contact(
    contact_id: str,
    data: ContactUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
) -> ContactResponse:
    contact = await contact_service.update_contact(contact_id, current_user["id"], data)
    return ContactResponse(**contact)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an emergency contact",
)
async def delete_contact(
    contact_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    contact_service: ContactService = Depends(get_contact_service),
) -> Response:
    await contact_service.delete_contact(contact_id, current_user["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
