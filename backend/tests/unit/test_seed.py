"""Unit tests for database seeding logic."""

import pytest
from backend.app.db.indexes import create_indexes
from backend.app.db.seed import seed_admin, seed_dev_data


@pytest.mark.asyncio
async def test_seed_admin_and_dev_data(test_db):
    await create_indexes(test_db)
    # First run: seeds admin & dev data
    await seed_admin(test_db)
    admin = await test_db.users.find_one({"role": "admin"})
    assert admin is not None
    assert admin["role"] == "admin"

    await seed_dev_data(test_db, force=True)
    demo = await test_db.users.find_one({"email": "demo@sakhisahay.example"})
    assert demo is not None

    contacts = await test_db.emergency_contacts.count_documents({})
    assert contacts >= 3

    reports = await test_db.incident_reports.count_documents({})
    assert reports >= 1

    # Second run: idempotent (does not duplicate records)
    await seed_admin(test_db)
    admins_count = await test_db.users.count_documents({"role": "admin"})
    assert admins_count == 1
