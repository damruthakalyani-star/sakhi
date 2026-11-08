# Data Model: SAKHISAHAY MongoDB Architecture

**Database Engine:** MongoDB 7.x  
**ODM/Driver:** Motor (Async Python Driver) + Pydantic v2 document models  
**Date/Time Standard:** UTC ISO 8601 timestamps stored as native BSON `Date` objects  
**Primary Keys:** MongoDB `ObjectId` internally, mapped to string `id` in all API schemas

---

## 1. Design Principles & Relationships

1. **Embedded vs. Referenced Rationale:**
   - **Embedded:** Fast read access for bounded child documents that are lifecycle-dependent on the parent (e.g., GPS coordinates `{ latitude, longitude, accuracy }` inside `sos_alerts` and `location_shares`; snapshot of contacts alerted at the moment of SOS trigger).
   - **Referenced:** Relationships that grow unbounded or require independent querying, security ownership, and soft deletion (e.g., `emergency_contacts` referenced by `user_id`, `sos_alerts` referenced by `user_id`, `audit_logs` referencing `actor_id`).
2. **Standard Document Fields:**
   - Every entity document includes:
     - `_id`: `ObjectId`
     - `created_at`: `datetime` (UTC)
     - `updated_at`: `datetime` (UTC)
     - `is_deleted`: `bool` (default `False`, for soft delete where applicable)
3. **Data Integrity & Privacy:**
   - Zero credentials or tokens stored in plaintext. Password hashes stored via Argon2id / Bcrypt (cost 12+).
   - Refresh tokens and password reset tokens are cryptographically hashed (`SHA-256`) prior to DB storage.

---

## 2. Collections & Schema Definitions

### 2.1 `users`
Stores user profile, authentication credentials, and security lockout states.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `email` | `String` | Yes | Lowercase, trimmed, unique email address |
| `full_name` | `String` | Yes | User's full display name |
| `password_hash` | `String` | Yes | Bcrypt / Argon2id salted hash |
| `role` | `String` | Yes | `"user"` or `"admin"` (default `"user"`) |
| `is_active` | `Boolean` | Yes | Default `True` |
| `is_verified` | `Boolean` | Yes | Default `False` (email verified status) |
| `avatar_url` | `String` | No | Optional URL to user's profile picture |
| `failed_login_attempts` | `Integer` | Yes | Consecutive failed logins (resets on success) |
| `locked_until` | `DateTime` | No | Timestamp until which account is locked if threshold exceeded |
| `last_login_at` | `DateTime` | No | Timestamp of most recent successful login |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |
| `updated_at` | `DateTime` | Yes | UTC last update timestamp |
| `is_deleted` | `Boolean` | Yes | Default `False` |

**Indexes:**
- Unique index: `{"email": 1}`
- Compound index: `{"is_active": 1, "role": 1}`

**Example Document:**
```json
{
  "_id": {"$oid": "672e12a4f1a23b45c6789def"},
  "email": "pooja@example.com",
  "full_name": "Pooja Sharma",
  "password_hash": "$2b$12$e8YJq5N0V1a...XYZ",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "avatar_url": null,
  "failed_login_attempts": 0,
  "locked_until": null,
  "last_login_at": {"$date": "2026-11-08T09:30:00Z"},
  "created_at": {"$date": "2026-11-08T09:30:00Z"},
  "updated_at": {"$date": "2026-11-08T09:30:00Z"},
  "is_deleted": false
}
```

---

### 2.2 `refresh_tokens`
Stores hashed refresh tokens supporting single-use rotation and reuse detection.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to `users._id` |
| `token_hash` | `String` | Yes | SHA-256 hash of issued refresh token |
| `family_id` | `String` | Yes | UUID tracking token generation family |
| `expires_at` | `DateTime` | Yes | Expiration timestamp |
| `revoked` | `Boolean` | Yes | Default `False` |
| `user_agent` | `String` | No | Request client header |
| `ip` | `String` | No | Request IP address |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |

**Indexes:**
- Unique index: `{"token_hash": 1}`
- Foreign key index: `{"user_id": 1}`
- Family index: `{"family_id": 1}`
- TTL Index: `{"expires_at": 1}` with `expireAfterSeconds: 0` (automated garbage collection)

---

### 2.3 `password_resets`
Stores single-use password recovery tokens.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to `users._id` |
| `token_hash` | `String` | Yes | SHA-256 hash of reset token |
| `expires_at` | `DateTime` | Yes | Expiration timestamp (e.g. 15 minutes) |
| `used` | `Boolean` | Yes | Default `False` |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |

**Indexes:**
- Unique index: `{"token_hash": 1}`
- Foreign key index: `{"user_id": 1}`
- TTL Index: `{"expires_at": 1}` with `expireAfterSeconds: 0`

---

### 2.4 `emergency_contacts`
Stores trusted contacts configured per user for SOS and notifications.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to owning `users._id` |
| `name` | `String` | Yes | Contact's full name (2-100 characters) |
| `phone` | `String` | Yes | 10-digit Indian phone number (`^[6-9]\d{9}$`) |
| `relationship` | `String` | Yes | Enum: `"Family"`, `"Friend"`, `"Guardian"`, `"Other"` |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |
| `updated_at` | `DateTime` | Yes | UTC last update timestamp |
| `is_deleted` | `Boolean` | Yes | Default `False` (soft deletion) |

**Indexes:**
- Compound Index: `{"user_id": 1, "is_deleted": 1}`
- Unique constraint per active user contact: `{"user_id": 1, "phone": 1, "is_deleted": 1}`

**Example Document:**
```json
{
  "_id": {"$oid": "672e1310f1a23b45c6789df1"},
  "user_id": {"$oid": "672e12a4f1a23b45c6789def"},
  "name": "Anjali Sharma",
  "phone": "9876543210",
  "relationship": "Family",
  "created_at": {"$date": "2026-11-08T09:35:00Z"},
  "updated_at": {"$date": "2026-11-08T09:35:00Z"},
  "is_deleted": false
}
```

---

### 2.5 `sos_alerts`
Tracks triggered emergency SOS events, coordinates snapshot, and notification dispatches.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to `users._id` |
| `status` | `String` | Yes | `"ACTIVE"`, `"RESOLVED"`, or `"CANCELLED"` |
| `location` | `Object` | Yes | Embedded `{ latitude: Float, longitude: Float, accuracy: Float }` |
| `message` | `String` | No | Custom emergency text or default template |
| `contacts_snapshot` | `Array` | Yes | Embedded snapshot of contacts alerted at trigger moment |
| `triggered_at` | `DateTime` | Yes | UTC trigger timestamp |
| `resolved_at` | `DateTime` | No | UTC resolution timestamp |
| `resolution_note` | `String` | No | User/admin closing comment |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |
| `updated_at` | `DateTime` | Yes | UTC last update timestamp |

**Indexes:**
- Compound Query Index: `{"user_id": 1, "status": 1}`
- Temporal sorting Index: `{"triggered_at": -1}`
- Geospatial index: `{"location.coordinates": "2dsphere"}` (for spatial aggregation if required)

**Example Document:**
```json
{
  "_id": {"$oid": "672e13a0f1a23b45c6789df5"},
  "user_id": {"$oid": "672e12a4f1a23b45c6789def"},
  "status": "ACTIVE",
  "location": {
    "latitude": 12.971598,
    "longitude": 77.594566,
    "accuracy": 15.5
  },
  "message": "I need help. Please contact me as soon as possible.",
  "contacts_snapshot": [
    {
      "name": "Anjali Sharma",
      "phone": "9876543210",
      "relationship": "Family",
      "dispatched_at": {"$date": "2026-11-08T09:40:01Z"},
      "dispatch_status": "SENT"
    }
  ],
  "triggered_at": {"$date": "2026-11-08T09:40:00Z"},
  "resolved_at": null,
  "resolution_note": null,
  "created_at": {"$date": "2026-11-08T09:40:00Z"},
  "updated_at": {"$date": "2026-11-08T09:40:00Z"}
}
```

---

### 2.6 `location_shares`
Stores time-limited, shareable live location sessions.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to `users._id` |
| `share_token` | `String` | Yes | High-entropy random alphanumeric token |
| `latitude` | `Float` | Yes | WGS84 Latitude |
| `longitude` | `Float` | Yes | WGS84 Longitude |
| `accuracy` | `Float` | No | Accuracy radius in meters |
| `is_active` | `Boolean` | Yes | Default `True` |
| `expires_at` | `DateTime` | Yes | Expiration timestamp |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |
| `updated_at` | `DateTime` | Yes | UTC last update timestamp |

**Indexes:**
- Unique Index: `{"share_token": 1}`
- Foreign key: `{"user_id": 1, "is_active": 1}`
- TTL Index: `{"expires_at": 1}` with `expireAfterSeconds: 0`

---

### 2.7 `incident_reports`
Stores self-paced harassment documentation entries.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `user_id` | `ObjectId` | Yes | Reference to `users._id` |
| `category` | `String` | Yes | `"online"`, `"stalking"`, `"verbal"`, `"physical"`, `"other"` |
| `incident_date` | `DateTime` | Yes | Timestamp when incident occurred |
| `location_summary` | `String` | No | Plain text location notes |
| `notes` | `String` | Yes | Detailed narrative of what happened |
| `witnesses` | `String` | No | Optional names or descriptions of witnesses |
| `evidence_files` | `Array` | Yes | List of attached media metadata `[{ filename, file_url, mime_type, size }]` |
| `created_at` | `DateTime` | Yes | UTC creation timestamp |
| `updated_at` | `DateTime` | Yes | UTC last update timestamp |
| `is_deleted` | `Boolean` | Yes | Default `False` |

**Indexes:**
- Compound Index: `{"user_id": 1, "incident_date": -1, "is_deleted": 1}`
- Text Index on narrative fields: `{"notes": "text", "location_summary": "text"}`

---

### 2.8 `audit_logs`
Immutable record of security events, administrative actions, and authorization changes.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `_id` | `ObjectId` | Yes | Primary document ID |
| `actor_id` | `ObjectId` | No | `users._id` or `null` for unauthenticated actions |
| `action` | `String` | Yes | Action code (`"AUTH_LOGIN"`, `"SOS_TRIGGERED"`, `"CONTACT_CREATED"`, etc.) |
| `resource` | `String` | Yes | Target resource (`"users"`, `"contacts"`, `"sos_alerts"`) |
| `resource_id` | `String` | No | Target identifier |
| `ip` | `String` | Yes | Client IP address |
| `user_agent` | `String` | No | Client User Agent |
| `timestamp` | `DateTime` | Yes | UTC event timestamp |
| `metadata` | `Object` | No | Structured contextual details (non-sensitive) |

**Indexes:**
- Compound Index: `{"action": 1, "timestamp": -1}`
- Foreign key: `{"actor_id": 1, "timestamp": -1}`
- Resource index: `{"resource": 1, "resource_id": 1}`

