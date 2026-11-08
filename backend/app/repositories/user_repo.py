"""User repository for MongoDB operations."""

from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "users")

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        normalized = email.strip().lower()
        doc = await self.collection.find_one(
            {"email": normalized, "is_deleted": {"$ne": True}}
        )
        return self.map_id(doc)

    async def increment_failed_login(
        self, user_id: str, lock_threshold: int = 5, lock_minutes: int = 15
    ) -> dict[str, Any]:
        oid = self.to_object_id(user_id)
        user = await self.collection.find_one({"_id": oid})
        if not user:
            raise ValueError("User not found")

        attempts = user.get("failed_login_attempts", 0) + 1
        update_set: dict[str, Any] = {
            "failed_login_attempts": attempts,
            "updated_at": datetime.now(UTC),
        }

        if attempts >= lock_threshold:
            update_set["locked_until"] = datetime.now(UTC) + timedelta(
                minutes=lock_minutes
            )

        await self.collection.update_one({"_id": oid}, {"$set": update_set})
        updated = await self.collection.find_one({"_id": oid})
        return self.map_id(updated) or {}

    async def reset_failed_login(self, user_id: str) -> None:
        oid = self.to_object_id(user_id)
        await self.collection.update_one(
            {"_id": oid},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "locked_until": None,
                    "last_login_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                }
            },
        )

    async def update_password(self, user_id: str, password_hash: str) -> bool:
        oid = self.to_object_id(user_id)
        res = await self.collection.update_one(
            {"_id": oid},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(UTC),
                }
            },
        )
        return res.modified_count > 0
