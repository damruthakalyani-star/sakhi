"""Audit logging repository for immutable security logs."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class AuditRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "audit_logs")

    async def log_action(
        self,
        action: str,
        resource: str,
        actor_id: str | None = None,
        resource_id: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = {
            "actor_id": actor_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "ip": ip or "0.0.0.0",
            "user_agent": user_agent or "unknown",
            "timestamp": datetime.now(UTC),
            "metadata": metadata or {},
        }
        res = await self.collection.insert_one(data)
        data["id"] = str(res.inserted_id)
        if "_id" in data:
            del data["_id"]
        return data

    async def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.map_id(d) for d in docs if d is not None]
