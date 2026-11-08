"""Emergency contacts management service."""

from typing import Any

from backend.app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.contact_repo import ContactRepository
from backend.app.schemas.contact import ContactCreate, ContactUpdate

MAX_CONTACTS_PER_USER = 10


class ContactService:
    def __init__(
        self, contact_repo: ContactRepository, audit_repo: AuditRepository
    ) -> None:
        self.contact_repo = contact_repo
        self.audit_repo = audit_repo

    async def list_contacts(self, user_id: str) -> list[dict[str, Any]]:
        return await self.contact_repo.list_by_user(user_id)

    async def create_contact(self, user_id: str, data: ContactCreate) -> dict[str, Any]:
        count = await self.contact_repo.count_by_user(user_id)
        if count >= MAX_CONTACTS_PER_USER:
            raise ValidationException(
                f"You have reached the maximum limit of {MAX_CONTACTS_PER_USER} emergency contacts.",
                code="CONTACTS_LIMIT_REACHED",
            )

        existing_phone = await self.contact_repo.get_by_phone_and_user(
            data.phone, user_id
        )
        if existing_phone:
            raise ConflictException(
                f"Phone number {data.phone} is already saved as an emergency contact.",
                code="DUPLICATE_PHONE_NUMBER",
            )

        doc_data = {
            "user_id": user_id,
            "name": data.name.strip(),
            "phone": data.phone,
            "relationship": data.relationship,
        }
        contact = await self.contact_repo.create(doc_data)
        await self.audit_repo.log_action(
            action="CONTACT_CREATED",
            resource="emergency_contacts",
            actor_id=user_id,
            resource_id=contact["id"],
        )
        return contact

    async def update_contact(
        self, contact_id: str, user_id: str, data: ContactUpdate
    ) -> dict[str, Any]:
        existing = await self.contact_repo.get_by_id_and_user(contact_id, user_id)
        if not existing:
            raise NotFoundException(
                "Emergency contact not found.", code="CONTACT_NOT_FOUND"
            )

        update_dict: dict[str, Any] = {}
        if data.name is not None:
            update_dict["name"] = data.name.strip()
        if data.relationship is not None:
            update_dict["relationship"] = data.relationship
        if data.phone is not None:
            duplicate = await self.contact_repo.get_by_phone_and_user(
                data.phone, user_id, exclude_id=contact_id
            )
            if duplicate:
                raise ConflictException(
                    f"Phone number {data.phone} is already saved for another contact.",
                    code="DUPLICATE_PHONE_NUMBER",
                )
            update_dict["phone"] = data.phone

        updated = await self.contact_repo.update_by_user(
            contact_id, user_id, update_dict
        )
        if not updated:
            raise NotFoundException(
                "Emergency contact not found.", code="CONTACT_NOT_FOUND"
            )

        await self.audit_repo.log_action(
            action="CONTACT_UPDATED",
            resource="emergency_contacts",
            actor_id=user_id,
            resource_id=contact_id,
        )
        return updated

    async def delete_contact(self, contact_id: str, user_id: str) -> None:
        existing = await self.contact_repo.get_by_id_and_user(contact_id, user_id)
        if not existing:
            raise NotFoundException(
                "Emergency contact not found.", code="CONTACT_NOT_FOUND"
            )

        success = await self.contact_repo.delete_by_user(contact_id, user_id)
        if not success:
            raise NotFoundException(
                "Emergency contact not found.", code="CONTACT_NOT_FOUND"
            )

        await self.audit_repo.log_action(
            action="CONTACT_DELETED",
            resource="emergency_contacts",
            actor_id=user_id,
            resource_id=contact_id,
        )
