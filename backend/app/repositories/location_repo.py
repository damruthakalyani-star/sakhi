"""Location share repository."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class LocationRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "location_shares")

    async def create_or_update_share(
        self,
        user_id: str,
        share_token: str,
        latitude: float,
        longitude: float,
        accuracy: float | None,
        expires_at: datetime,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        # Deactivate any previous shares for this user
        await self.collection.update_many(
            {"user_id": user_id, "is_active": True}, {"$set": {"is_active": False}}
        )

        data = {
            "user_id": user_id,
            "share_token": share_token,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
            "is_active": True,
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
        }
        res = await self.collection.insert_one(data)
        data["id"] = str(res.inserted_id)
        if "_id" in data:
            del data["_id"]
        return data

    async def get_by_token(self, share_token: str) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        doc = await self.collection.find_one(
            {
                "share_token": share_token,
                "is_active": True,
                "expires_at": {"$gt": now},
            }
        )
        return self.map_id(doc)

    async def deactivate_share(self, user_id: str) -> bool:
        res = await self.collection.update_many(
            {"user_id": user_id, "is_active": True}, {"$set": {"is_active": False}}
        )
        return res.modified_count > 0
