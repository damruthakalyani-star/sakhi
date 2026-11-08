"""Emergency SOS service logic."""

from datetime import UTC, datetime
from typing import Any

from backend.app.core.exceptions import NotFoundException
from backend.app.core.logging import logger
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.contact_repo import ContactRepository
from backend.app.repositories.sos_repo import SOSRepository
from backend.app.schemas.sos import SOSTriggerRequest


class SOSService:
    def __init__(
        self,
        sos_repo: SOSRepository,
        contact_repo: ContactRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.sos_repo = sos_repo
        self.contact_repo = contact_repo
        self.audit_repo = audit_repo

    async def trigger_sos(
        self, user_id: str, data: SOSTriggerRequest
    ) -> dict[str, Any]:
        # 1. Fetch user's registered emergency contacts
        contacts = await self.contact_repo.list_by_user(user_id)
        contacts_snapshot: list[dict[str, Any]] = [
            {
                "name": c["name"],
                "phone": c["phone"],
                "relationship": c["relationship"],
                "dispatch_status": "SENT",
            }
            for c in contacts
        ]

        now = datetime.now(UTC)
        sos_doc = {
            "user_id": user_id,
            "status": "ACTIVE",
            "location": {
                "latitude": data.latitude,
                "longitude": data.longitude,
                "accuracy": data.accuracy,
            },
            "message": data.message,
            "contacts_notified": contacts_snapshot,
            "triggered_at": now,
            "resolved_at": None,
            "resolution_note": None,
        }

        # If already active, resolve previous one or update
        active_previous = await self.sos_repo.get_active_by_user(user_id)
        if active_previous:
            await self.sos_repo.resolve_active_by_user(
                user_id, note="Superseded by new SOS trigger"
            )

        record = await self.sos_repo.create(sos_doc)

        # Log simulated SMS dispatch for contacts
        for c in contacts_snapshot:
            logger.info(
                f"[DISPATCH SMS] To: {c['phone']} ({c['name']}) -> SAKHISAHAY EMERGENCY ALERT! Location: {data.latitude},{data.longitude}. Msg: {data.message}"
            )

        await self.audit_repo.log_action(
            action="SOS_TRIGGERED",
            resource="sos_alerts",
            actor_id=user_id,
            resource_id=record["id"],
            metadata={
                "lat": data.latitude,
                "lon": data.longitude,
                "contacts_count": len(contacts_snapshot),
            },
        )
        return record

    async def get_active_sos(self, user_id: str) -> dict[str, Any] | None:
        return await self.sos_repo.get_active_by_user(user_id)

    async def resolve_sos(
        self, user_id: str, resolution_note: str | None = None
    ) -> dict[str, Any]:
        active = await self.sos_repo.get_active_by_user(user_id)
        if not active:
            raise NotFoundException(
                "No active SOS emergency found for this user.", code="NO_ACTIVE_SOS"
            )

        resolved = await self.sos_repo.resolve_active_by_user(user_id, resolution_note)
        if not resolved:
            raise NotFoundException(
                "Failed to resolve SOS alert.", code="SOS_RESOLUTION_FAILED"
            )

        await self.audit_repo.log_action(
            action="SOS_RESOLVED",
            resource="sos_alerts",
            actor_id=user_id,
            resource_id=resolved["id"],
            metadata={"note": resolution_note},
        )
        return resolved
