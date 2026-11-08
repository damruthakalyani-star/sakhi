"""Base asynchronous repository for MongoDB operations."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase


class BaseRepository:
    """Base generic repository encapsulating Motor MongoDB collection queries."""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str) -> None:
        self.db = db
        self.collection_name = collection_name
        self.collection: AsyncIOMotorCollection = db[collection_name]

    @staticmethod
    def to_object_id(id_str: str) -> ObjectId:
        """Converts string ID to BSON ObjectId safely."""
        try:
            return ObjectId(id_str)
        except Exception as e:
            raise ValueError(f"Invalid ObjectId format: {id_str}") from e

    @staticmethod
    def map_id(doc: dict[str, Any] | None) -> dict[str, Any] | None:
        """Converts MongoDB BSON _id to string id in document dictionaries."""
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def get_by_id(self, id_str: str) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(id_str)
        except ValueError:
            return None
        doc = await self.collection.find_one({"_id": oid, "is_deleted": {"$ne": True}})
        return self.map_id(doc)

    async def list(
        self,
        filter_query: dict[str, Any] | None = None,
        sort: list[tuple] | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        query = filter_query or {}
        if "is_deleted" not in query:
            query["is_deleted"] = {"$ne": True}

        cursor = self.collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)

        docs = await cursor.to_list(length=limit)
        return [self.map_id(d) for d in docs if d is not None]

    async def count(self, filter_query: dict[str, Any] | None = None) -> int:
        query = filter_query or {}
        if "is_deleted" not in query:
            query["is_deleted"] = {"$ne": True}
        return await self.collection.count_documents(query)

    async def create(self, doc_data: dict[str, Any]) -> dict[str, Any]:
        data = dict(doc_data)
        now = datetime.now(UTC)
        if "created_at" not in data:
            data["created_at"] = now
        if "updated_at" not in data:
            data["updated_at"] = now
        if "is_deleted" not in data:
            data["is_deleted"] = False

        result = await self.collection.insert_one(data)
        data["id"] = str(result.inserted_id)
        if "_id" in data:
            del data["_id"]
        return data

    async def update(
        self, id_str: str, update_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            oid = self.to_object_id(id_str)
        except ValueError:
            return None

        data = dict(update_data)
        data["updated_at"] = datetime.now(UTC)

        await self.collection.update_one({"_id": oid}, {"$set": data})
        doc = await self.collection.find_one({"_id": oid})
        return self.map_id(doc)

    async def soft_delete(self, id_str: str) -> bool:
        try:
            oid = self.to_object_id(id_str)
        except ValueError:
            return False

        res = await self.collection.update_one(
            {"_id": oid},
            {"$set": {"is_deleted": True, "deleted_at": datetime.now(UTC)}},
        )
        return res.modified_count > 0
