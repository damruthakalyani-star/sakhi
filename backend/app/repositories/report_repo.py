"""Incident reporting repository."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class ReportRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "incident_reports")

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find({"user_id": user_id, "is_deleted": {"$ne": True}})
            .sort("incident_date", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self.map_id(d) for d in docs if d is not None]

    async def count_by_user(self, user_id: str) -> int:
        return await self.collection.count_documents(
            {"user_id": user_id, "is_deleted": {"$ne": True}}
        )

    async def get_by_id_and_user(
        self, report_id: str, user_id: str
    ) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(report_id)
        except ValueError:
            return None
        doc = await self.collection.find_one(
            {"_id": oid, "user_id": user_id, "is_deleted": {"$ne": True}}
        )
        return self.map_id(doc)

    async def update_by_user(
        self, report_id: str, user_id: str, update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(report_id)
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

    async def delete_by_user(self, report_id: str, user_id: str) -> bool:
        try:
            oid = self.to_object_id(report_id)
        except ValueError:
            return False
        res = await self.collection.update_one(
            {"_id": oid, "user_id": user_id},
            {"$set": {"is_deleted": True, "deleted_at": datetime.now(UTC)}},
        )
        return res.modified_count > 0
