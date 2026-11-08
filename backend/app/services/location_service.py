"""Location sharing service logic."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.core.exceptions import NotFoundException
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.location_repo import LocationRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.schemas.location import LocationShareRequest, PublicSharedLocationView


class LocationService:
    def __init__(
        self,
        location_repo: LocationRepository,
        user_repo: UserRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.location_repo = location_repo
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def share_location(
        self, user_id: str, data: LocationShareRequest
    ) -> dict[str, Any]:
        share_token = f"shr_{secrets.token_urlsafe(18)}"
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=data.duration_minutes)

        record = await self.location_repo.create_or_update_share(
            user_id=user_id,
            share_token=share_token,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy=data.accuracy,
            expires_at=expires_at,
        )

        share_url = f"/location/shared/{share_token}"
        record["share_url"] = share_url

        await self.audit_repo.log_action(
            action="LOCATION_SHARED",
            resource="location_shares",
            actor_id=user_id,
            resource_id=record["id"],
        )
        return record

    async def get_shared_location(self, share_token: str) -> PublicSharedLocationView:
        share = await self.location_repo.get_by_token(share_token)
        if not share:
            raise NotFoundException(
                "Shared location link is invalid, expired, or has been ended.",
                code="SHARED_LOCATION_NOT_FOUND",
            )

        user_name = "SAKHISAHAY User"
        user = await self.user_repo.get_by_id(share["user_id"])
        if user and "full_name" in user:
            # Mask last name for privacy: "Pooja Sharma" -> "Pooja S."
            parts = user["full_name"].strip().split()
            if len(parts) > 1:
                user_name = f"{parts[0]} {parts[-1][0]}."
            else:
                user_name = parts[0]

        return PublicSharedLocationView(
            user_name=user_name,
            latitude=share["latitude"],
            longitude=share["longitude"],
            accuracy=share.get("accuracy"),
            updated_at=share.get("updated_at", share["created_at"]),
            expires_at=share["expires_at"],
            is_active=share["is_active"],
        )

    async def stop_sharing(self, user_id: str) -> None:
        await self.location_repo.deactivate_share(user_id)
        await self.audit_repo.log_action(
            action="LOCATION_SHARE_STOPPED",
            resource="location_shares",
            actor_id=user_id,
        )
