#!/usr/bin/env python3
"""Database Migration Script for SAKHISAHAY.

Provides an idempotent, versioned migration runner for MongoDB schema & indexes.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.db.indexes import create_indexes
from app.db.mongo import get_database, mongo_manager

MIGRATIONS = [
    {
        "version": "001_initial_indexes",
        "description": "Create unique, compound, and TTL indexes on core collections",
        "handler": create_indexes,
    },
    {
        "version": "002_user_lockout_fields",
        "description": "Ensure failed_login_attempts and locked_until exist on users",
        "handler": None,  # Handled dynamically below
    },
]


async def migration_002_user_fields(db) -> None:
    """Backfill missing security fields for older user records."""
    result = await db["users"].update_many(
        {"failed_login_attempts": {"$exists": False}},
        {"$set": {"failed_login_attempts": 0, "locked_until": None}},
    )
    print(f"  [002] Backfilled {result.modified_count} user records.")


MIGRATIONS[1]["handler"] = migration_002_user_fields


async def run_migrations() -> None:
    print(f"[*] Connecting to MongoDB at {settings.MONGODB_URI}...")
    await mongo_manager.connect()
    db = get_database()

    migrations_coll = db["_schema_migrations"]

    print("[*] Checking applied migrations...")
    for migration in MIGRATIONS:
        v = migration["version"]
        desc = migration["description"]
        existing = await migrations_coll.find_one({"version": v})

        if existing:
            print(f"  [-] Already applied: {v} ({desc})")
            continue

        print(f"  [>] Applying migration {v}: {desc}...")
        try:
            handler = migration["handler"]
            if handler:
                if handler == create_indexes:
                    await handler()
                else:
                    await handler(db)

            await migrations_coll.insert_one(
                {
                    "version": v,
                    "description": desc,
                    "applied_at": datetime.now(timezone.utc),
                    "status": "success",
                }
            )
            print(f"  [✓] Migration {v} applied successfully.")
        except Exception as e:
            print(f"  [✗] Migration {v} failed: {e}")
            await migrations_coll.insert_one(
                {
                    "version": v,
                    "description": desc,
                    "applied_at": datetime.now(timezone.utc),
                    "status": "failed",
                    "error": str(e),
                }
            )
            raise

    print("[*] All migrations evaluated.")
    await mongo_manager.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
