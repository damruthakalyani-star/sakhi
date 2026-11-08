"""MongoDB connection manager using Motor (async driver)."""

from backend.app.core.config import settings
from backend.app.core.logging import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoManager:
    """Manages MongoDB client and database connections."""

    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None
        self._is_mock: bool = False

    async def connect(self, uri: str | None = None, db_name: str | None = None) -> None:
        """Connects to MongoDB and tests connection."""
        if self.client is not None and self._is_mock:
            return

        mongo_uri = uri or settings.MONGODB_URI
        target_db = db_name or settings.MONGODB_DB_NAME

        if mongo_uri.startswith("mock") or mongo_uri.startswith("mongomock"):
            import mongomock_motor

            self.client = mongomock_motor.AsyncMongoMockClient()
            self.db = self.client[target_db]
            self._is_mock = True
            logger.info("Using in-memory mock MongoDB (mongomock-motor).")
            return

        try:
            self.client = AsyncIOMotorClient(
                mongo_uri,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=1000,
            )
            self.db = self.client[target_db]
            # Verify connectivity with short timeout
            await self.client.admin.command("ping")
            self._is_mock = False
            logger.info(f"Connected to MongoDB at {target_db}")
        except Exception as e:
            logger.warning(f"Standard MongoDB connection failed: {e}")
            if settings.APP_ENV != "production":
                try:
                    import mongomock_motor

                    self.client = mongomock_motor.AsyncMongoMockClient()
                    self.db = self.client[target_db]
                    self._is_mock = True
                    logger.warning(
                        "Using in-memory mock MongoDB (mongomock-motor) for offline development/testing."
                    )
                except ImportError:
                    logger.error("mongomock-motor not available.")
                    raise e from None
            else:
                raise e from None

    async def disconnect(self) -> None:
        """Closes all MongoDB connection pools."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed.")

    async def ping(self) -> bool:
        """Checks if MongoDB is healthy and reachable."""
        if not self.client or not self.db:
            return False
        try:
            if self._is_mock:
                return True
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping check failed: {e}")
            return False

    def get_db(self) -> AsyncIOMotorDatabase:
        """Returns the active database instance."""
        if self.db is None:
            raise RuntimeError(
                "Database not initialized. Ensure app lifespan has connected to MongoDB."
            )
        return self.db


db_manager = MongoManager()


def get_database() -> AsyncIOMotorDatabase:
    """Convenience helper to retrieve database instance."""
    return db_manager.get_db()
