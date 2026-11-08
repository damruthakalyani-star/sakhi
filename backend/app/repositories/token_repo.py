"""Token repository for refresh token families and password reset tokens."""

from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


class TokenRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "refresh_tokens")
        self.resets_collection = db["password_resets"]

    async def save_refresh_token(
        self,
        user_id: str,
        token_hash: str,
        family_id: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> dict[str, Any]:
        data = {
            "user_id": user_id,
            "token_hash": token_hash,
            "family_id": family_id,
            "expires_at": expires_at,
            "revoked": False,
            "user_agent": user_agent,
            "ip": ip,
            "created_at": datetime.now(UTC),
        }
        res = await self.collection.insert_one(data)
        data["id"] = str(res.inserted_id)
        if "_id" in data:
            del data["_id"]
        return data

    async def get_refresh_token(self, token_hash: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"token_hash": token_hash})
        return self.map_id(doc)

    async def revoke_refresh_token(self, token_hash: str) -> None:
        await self.collection.update_one(
            {"token_hash": token_hash}, {"$set": {"revoked": True}}
        )

    async def revoke_token_family(self, family_id: str) -> None:
        """Revokes all tokens in a family upon detecting token reuse."""
        await self.collection.update_many(
            {"family_id": family_id}, {"$set": {"revoked": True}}
        )

    async def save_password_reset(
        self, user_id: str, token_hash: str, expires_at: datetime
    ) -> dict[str, Any]:
        data = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(UTC),
        }
        res = await self.resets_collection.insert_one(data)
        data["id"] = str(res.inserted_id)
        if "_id" in data:
            del data["_id"]
        return data

    async def get_valid_password_reset(self, token_hash: str) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        doc = await self.resets_collection.find_one(
            {
                "token_hash": token_hash,
                "used": False,
                "expires_at": {"$gt": now},
            }
        )
        return self.map_id(doc)

    async def mark_password_reset_used(self, token_hash: str) -> None:
        await self.resets_collection.update_one(
            {"token_hash": token_hash}, {"$set": {"used": True}}
        )
