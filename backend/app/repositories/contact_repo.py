"""Emergency contacts repository."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class ContactRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "emergency_contacts")

    async def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        cursor = self.collection.find(
            {"user_id": user_id, "is_deleted": {"$ne": True}}
        ).sort("created_at", 1)
        docs = await cursor.to_list(length=100)
        return [self.map_id(d) for d in docs if d is not None]

    async def count_by_user(self, user_id: str) -> int:
        return await self.collection.count_documents(
            {"user_id": user_id, "is_deleted": {"$ne": True}}
        )

    async def get_by_id_and_user(
        self, contact_id: str, user_id: str
    ) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(contact_id)
        except ValueError:
            return None
        doc = await self.collection.find_one(
            {"_id": oid, "user_id": user_id, "is_deleted": {"$ne": True}}
        )
        return self.map_id(doc)

    async def get_by_phone_and_user(
        self, phone: str, user_id: str, exclude_id: str | None = None
    ) -> dict[str, Any] | None:
        query: dict[str, Any] = {
            "user_id": user_id,
            "phone": phone,
            "is_deleted": {"$ne": True},
        }
        if exclude_id:
            try:
                query["_id"] = {"$ne": self.to_object_id(exclude_id)}
            except ValueError:
                pass
        doc = await self.collection.find_one(query)
        return self.map_id(doc)

    async def update_by_user(
        self, contact_id: str, user_id: str, update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(contact_id)
        except ValueError:
            return None
        data = dict(update_data)
        data["updated_at"] = datetime.now(UTC)
        res = await self.collection.update_one(
            {"_id": oid, "user_id": user_id}, {"$set": data}
        )
        if res.matched_count == 0:
            return None
        doc = await self.collection.find_one({"_id": oid})
        return self.map_id(doc)

    async def delete_by_user(self, contact_id: str, user_id: str) -> bool:
        try:
            oid = self.to_object_id(contact_id)
        except ValueError:
            return False
        res = await self.collection.update_one(
            {"_id": oid, "user_id": user_id},
            {"$set": {"is_deleted": True, "deleted_at": datetime.now(UTC)}},
        )
        return res.modified_count > 0
