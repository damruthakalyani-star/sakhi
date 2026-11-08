"""Emergency SOS repository."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class SOSRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "sos_alerts")

    async def get_active_by_user(self, user_id: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"user_id": user_id, "status": "ACTIVE"})
        return self.map_id(doc)

    async def resolve_active_by_user(
        self, user_id: str, note: str | None = None
    ) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        res = await self.collection.update_one(
            {"user_id": user_id, "status": "ACTIVE"},
            {
                "$set": {
                    "status": "RESOLVED",
                    "resolved_at": now,
                    "resolution_note": note or "Resolved by user",
                    "updated_at": now,
                }
            },
        )
        if res.matched_count == 0:
            return None
        doc = await self.collection.find_one({"user_id": user_id, "resolved_at": now})
        return self.map_id(doc)

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("triggered_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self.map_id(d) for d in docs if d is not None]
