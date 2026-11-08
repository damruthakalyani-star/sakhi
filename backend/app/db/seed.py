"""Database seed script for default admin and development sample data."""

import asyncio
from datetime import UTC, datetime

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.security import hash_password
from backend.app.db.indexes import create_indexes
from backend.app.db.mongo import db_manager
from motor.motor_asyncio import AsyncIOMotorDatabase


async def seed_admin(db: AsyncIOMotorDatabase) -> None:
    """Seeds the initial administrator account idempotently from environment variables."""
    admin_email = settings.FIRST_ADMIN_EMAIL.strip().lower()
    existing = await db.users.find_one({"email": admin_email})
    if existing:
        logger.info(f"Admin user '{admin_email}' already exists. Skipping admin seed.")
        return

    admin_doc = {
        "email": admin_email,
        "full_name": settings.FIRST_ADMIN_NAME,
        "password_hash": hash_password(settings.FIRST_ADMIN_PASSWORD),
        "role": "admin",
        "is_active": True,
        "is_verified": True,
        "avatar_url": None,
        "failed_login_attempts": 0,
        "locked_until": None,
        "last_login_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "is_deleted": False,
    }
    res = await db.users.insert_one(admin_doc)
    logger.info(f"Admin user seeded with ID: {res.inserted_id}")


async def seed_dev_data(db: AsyncIOMotorDatabase, force: bool = False) -> None:
    """Seeds sample development data for testing all screens. Refuses in production."""
    if settings.APP_ENV == "production" and not force:
        logger.warning(
            "Development sample seeding is disabled in production environment."
        )
        return

    demo_email = "demo@sakhisahay.example"
    existing_demo = await db.users.find_one({"email": demo_email})
    if existing_demo:
        demo_user_id = str(existing_demo["_id"])
    else:
        demo_user = {
            "email": demo_email,
            "full_name": "Pooja Sharma",
            "password_hash": hash_password("DemoPassword123!"),
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "avatar_url": None,
            "failed_login_attempts": 0,
            "locked_until": None,
            "last_login_at": None,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "is_deleted": False,
        }
        res = await db.users.insert_one(demo_user)
        demo_user_id = str(res.inserted_id)
        logger.info(f"Demo user seeded: {demo_email}")

    # Seed sample emergency contacts
    contacts_count = await db.emergency_contacts.count_documents(
        {"user_id": demo_user_id, "is_deleted": {"$ne": True}}
    )
    if contacts_count == 0:
        sample_contacts = [
            {
                "user_id": demo_user_id,
                "name": "Anjali Sharma",
                "phone": "9876543210",
                "relationship": "Family",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "is_deleted": False,
            },
            {
                "user_id": demo_user_id,
                "name": "Priya Patel",
                "phone": "9123456780",
                "relationship": "Friend",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "is_deleted": False,
            },
            {
                "user_id": demo_user_id,
                "name": "Dr. Sunita Rao",
                "phone": "9988776655",
                "relationship": "Guardian",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "is_deleted": False,
            },
        ]
        await db.emergency_contacts.insert_many(sample_contacts)
        logger.info("Sample emergency contacts seeded.")

    # Seed sample incident report
    reports_count = await db.incident_reports.count_documents(
        {"user_id": demo_user_id, "is_deleted": {"$ne": True}}
    )
    if reports_count == 0:
        sample_report = {
            "user_id": demo_user_id,
            "category": "stalking",
            "incident_date": datetime.now(UTC),
            "location_summary": "Near Metro Station Gate 2",
            "notes": "Observed repeated following on the evening walk back from work. Documented vehicle registration and stayed on a call with a trusted contact.",
            "witnesses": "Security guard at metro entrance",
            "evidence_files": [],
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "is_deleted": False,
        }
        await db.incident_reports.insert_one(sample_report)
        logger.info("Sample incident report seeded.")


async def run_seed() -> None:
    await db_manager.connect()
    db = db_manager.get_db()
    await create_indexes(db)
    await seed_admin(db)
    await seed_dev_data(db)
    await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(run_seed())
