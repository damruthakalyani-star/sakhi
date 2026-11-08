"""Idempotent database index definitions and creation on startup."""

from backend.app.core.logging import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Creates all required indexes idempotently."""
    logger.info("Ensuring database indexes...")

    try:
        # 1. users indexes
        await db.users.create_indexes(
            [
                IndexModel(
                    [("email", ASCENDING)], unique=True, name="idx_users_email_unique"
                ),
                IndexModel(
                    [("is_active", ASCENDING), ("role", ASCENDING)],
                    name="idx_users_active_role",
                ),
            ]
        )

        # 2. refresh_tokens indexes
        await db.refresh_tokens.create_indexes(
            [
                IndexModel(
                    [("token_hash", ASCENDING)],
                    unique=True,
                    name="idx_refresh_tokens_hash_unique",
                ),
                IndexModel([("user_id", ASCENDING)], name="idx_refresh_tokens_user"),
                IndexModel(
                    [("family_id", ASCENDING)], name="idx_refresh_tokens_family"
                ),
                IndexModel(
                    [("expires_at", ASCENDING)],
                    expireAfterSeconds=0,
                    name="idx_refresh_tokens_ttl",
                ),
            ]
        )

        # 3. password_resets indexes
        await db.password_resets.create_indexes(
            [
                IndexModel(
                    [("token_hash", ASCENDING)],
                    unique=True,
                    name="idx_password_resets_hash_unique",
                ),
                IndexModel([("user_id", ASCENDING)], name="idx_password_resets_user"),
                IndexModel(
                    [("expires_at", ASCENDING)],
                    expireAfterSeconds=0,
                    name="idx_password_resets_ttl",
                ),
            ]
        )

        # 4. emergency_contacts indexes
        await db.emergency_contacts.create_indexes(
            [
                IndexModel(
                    [("user_id", ASCENDING), ("is_deleted", ASCENDING)],
                    name="idx_contacts_user_active",
                ),
                IndexModel(
                    [
                        ("user_id", ASCENDING),
                        ("phone", ASCENDING),
                        ("is_deleted", ASCENDING),
                    ],
                    name="idx_contacts_user_phone",
                ),
            ]
        )

        # 5. sos_alerts indexes
        await db.sos_alerts.create_indexes(
            [
                IndexModel(
                    [("user_id", ASCENDING), ("status", ASCENDING)],
                    name="idx_sos_user_status",
                ),
                IndexModel(
                    [("triggered_at", DESCENDING)], name="idx_sos_triggered_desc"
                ),
            ]
        )

        # 6. location_shares indexes
        await db.location_shares.create_indexes(
            [
                IndexModel(
                    [("share_token", ASCENDING)],
                    unique=True,
                    name="idx_loc_share_token_unique",
                ),
                IndexModel(
                    [("user_id", ASCENDING), ("is_active", ASCENDING)],
                    name="idx_loc_share_user",
                ),
                IndexModel(
                    [("expires_at", ASCENDING)],
                    expireAfterSeconds=0,
                    name="idx_loc_share_ttl",
                ),
            ]
        )

        # 7. incident_reports indexes
        await db.incident_reports.create_indexes(
            [
                IndexModel(
                    [
                        ("user_id", ASCENDING),
                        ("incident_date", DESCENDING),
                        ("is_deleted", ASCENDING),
                    ],
                    name="idx_reports_user_date",
                ),
                IndexModel(
                    [("notes", TEXT), ("location_summary", TEXT)],
                    name="idx_reports_text_search",
                ),
            ]
        )

        # 8. audit_logs indexes
        await db.audit_logs.create_indexes(
            [
                IndexModel(
                    [("action", ASCENDING), ("timestamp", DESCENDING)],
                    name="idx_audit_action_time",
                ),
                IndexModel(
                    [("actor_id", ASCENDING), ("timestamp", DESCENDING)],
                    name="idx_audit_actor_time",
                ),
                IndexModel(
                    [("resource", ASCENDING), ("resource_id", ASCENDING)],
                    name="idx_audit_resource",
                ),
            ]
        )

        logger.info("All database indexes created successfully.")
    except Exception as e:
        logger.warning(
            f"Index creation encountered an issue (may occur on in-memory mocks): {e}"
        )
