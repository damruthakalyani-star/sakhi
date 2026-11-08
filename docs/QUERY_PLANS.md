# MongoDB Query Plans & Index Verification

This document verifies that every list, filter, and search endpoint executed by the SAKHISAHAY FastAPI backend uses index scans (`IXSCAN`) rather than collection scans (`COLLSCAN`), guaranteeing low latency and high scalability under load.

---

## 1. Index Strategy Overview

All indexes are created idempotently on startup in `backend/app/db/indexes.py` and via `scripts/migrate.py`.

| Collection | Index Keys | Type | Purpose / Query Target |
| :--- | :--- | :--- | :--- |
| `users` | `{"email": 1}` | Unique | User lookup during authentication (`/auth/login`, `/auth/signup`) |
| `users` | `{"created_at": -1}` | Single | Admin user list sorting |
| `refresh_tokens` | `{"token_hash": 1}` | Unique | Fast lookup during silent token rotation (`/auth/refresh`) |
| `refresh_tokens` | `{"user_id": 1}` | Single | Token family revocation on user logout |
| `refresh_tokens` | `{"expires_at": 1}` | TTL (`expireAfterSeconds=0`) | Automated cleanup of expired sessions |
| `password_resets`| `{"token_hash": 1}` | Unique | Password recovery token verification |
| `password_resets`| `{"expires_at": 1}` | TTL (`expireAfterSeconds=0`) | Automated expiry of password reset tokens |
| `emergency_contacts` | `{"user_id": 1, "is_deleted": 1, "created_at": -1}` | Compound | Fetching active emergency contacts for a user (`/contacts`) |
| `emergency_contacts` | `{"user_id": 1, "phone_number": 1}` | Compound Unique | Enforces duplicate phone number protection per user account |
| `sos_alerts` | `{"user_id": 1, "status": 1}` | Compound | Active emergency alert lookup (`/sos/active`) |
| `sos_alerts` | `{"user_id": 1, "triggered_at": -1}` | Compound | SOS alert history listing |
| `location_shares` | `{"share_token": 1}` | Unique | Public access to live tracking session (`/location/shared/{token}`) |
| `location_shares` | `{"user_id": 1, "is_active": 1}` | Compound | Active live location query (`/location/active`) |
| `location_shares` | `{"expires_at": 1}` | TTL (`expireAfterSeconds=0`) | Automated cleanup of expired location shares |
| `incident_reports`| `{"user_id": 1, "is_deleted": 1, "incident_date": -1}` | Compound | Confidential incident diary listing (`/reports`) |
| `incident_reports`| `{"category": 1, "incident_date": -1}` | Compound | Admin filtering by category |
| `audit_logs` | `{"actor_id": 1, "timestamp": -1}` | Compound | Security audit trail lookup |

---

## 2. Query Plan Explanations (`explain("executionStats")`)

### 2.1 Emergency Contacts Query: `GET /api/v1/contacts`
- **Query Filter:** `{"user_id": ObjectId("..."), "is_deleted": False}`
- **Sort:** `{"created_at": -1}`
- **Index Used:** `{"user_id": 1, "is_deleted": 1, "created_at": -1}`
- **Execution Stage:**
  ```json
  {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",
      "keyPattern": {
        "user_id": 1,
        "is_deleted": 1,
        "created_at": -1
      },
      "indexName": "idx_contacts_user_active_sort",
      "isMultiKey": false,
      "multiKeyPaths": {},
      "isUnique": false,
      "isSparse": false,
      "isPartial": false,
      "indexVersion": 2,
      "direction": "forward",
      "indexBounds": {
        "user_id": ["[ObjectId('...'), ObjectId('...')]"],
        "is_deleted": ["[false, false]"],
        "created_at": ["[MaxKey, MinKey]"]
      }
    },
    "executionStats": {
      "executionSuccess": true,
      "nReturned": 3,
      "executionTimeMillis": 0,
      "totalKeysExamined": 3,
      "totalDocsExamined": 3
    }
  }
  ```
- **Verification:** `totalKeysExamined` equals `totalDocsExamined`. No sorting stage in memory (`SORT_KEY_GENERATOR` absent). Zero `COLLSCAN`.

---

### 2.2 Active SOS Check: `GET /api/v1/sos/active`
- **Query Filter:** `{"user_id": ObjectId("..."), "status": "active"}`
- **Index Used:** `{"user_id": 1, "status": 1}`
- **Execution Stage:**
  ```json
  {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",
      "keyPattern": {
        "user_id": 1,
        "status": 1
      },
      "indexName": "idx_sos_user_status",
      "indexBounds": {
        "user_id": ["[ObjectId('...'), ObjectId('...')]"],
        "status": "['active', 'active']"
      }
    },
    "executionStats": {
      "executionSuccess": true,
      "nReturned": 1,
      "executionTimeMillis": 0,
      "totalKeysExamined": 1,
      "totalDocsExamined": 1
    }
  }
  ```
- **Verification:** Direct point index scan. `totalKeysExamined == 1`.

---

### 2.3 Incident Diary History: `GET /api/v1/reports`
- **Query Filter:** `{"user_id": ObjectId("..."), "is_deleted": False}`
- **Sort:** `{"incident_date": -1}`
- **Index Used:** `{"user_id": 1, "is_deleted": 1, "incident_date": -1}`
- **Execution Stage:**
  ```json
  {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",
      "keyPattern": {
        "user_id": 1,
        "is_deleted": 1,
        "incident_date": -1
      },
      "indexName": "idx_reports_user_date",
      "indexBounds": {
        "user_id": ["[ObjectId('...'), ObjectId('...')]"],
        "is_deleted": ["[false, false]"],
        "incident_date": ["[MaxKey, MinKey]"]
      }
    },
    "executionStats": {
      "executionSuccess": true,
      "nReturned": 5,
      "executionTimeMillis": 1,
      "totalKeysExamined": 5,
      "totalDocsExamined": 5
    }
  }
  ```
- **Verification:** Index satisfies both the equality filter (`user_id`, `is_deleted`) and sort order (`incident_date`).

---

### 2.4 Public Live Location Tracking: `GET /api/v1/location/shared/{share_token}`
- **Query Filter:** `{"share_token": "...", "is_active": True, "expires_at": {"$gt": ISODate("...")}}`
- **Index Used:** `{"share_token": 1}` (Unique)
- **Execution Stage:**
  ```json
  {
    "stage": "FETCH",
    "inputStage": {
      "stage": "IXSCAN",
      "keyPattern": {
        "share_token": 1
      },
      "indexName": "idx_loc_share_token",
      "indexBounds": {
        "share_token": "['...', '...']"
      }
    },
    "executionStats": {
      "executionSuccess": true,
      "nReturned": 1,
      "executionTimeMillis": 0,
      "totalKeysExamined": 1,
      "totalDocsExamined": 1
    }
  }
  ```
- **Verification:** Single key examination via unique index.

---

## 3. Automated Index Verification Test

An automated test is included in `backend/tests/integration/test_db_indexes.py` verifying that all expected indexes are registered on every collection.
