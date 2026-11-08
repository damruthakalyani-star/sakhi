# API Contract: SAKHISAHAY RESTful Backend API

**Base URL:** `http://localhost:8000/api/v1` (Dev) / `https://api.sakhisahay.example/api/v1` (Prod)  
**Version:** 1.0.0  
**Authentication Scheme:** Bearer JWT in `Authorization` header (`Bearer <token>`) AND/OR httpOnly secure SameSite cookie `access_token` with CSRF protection.  
**Standard Response Formats:**
- **Success:** Direct JSON resource or paginated envelope:
  ```json
  {
    "items": [...],
    "total": 42,
    "page": 1,
    "page_size": 20,
    "pages": 3
  }
  ```
- **Error Envelope (Strict Standard across all endpoints):**
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Human readable explanation",
      "details": [
        {
          "field": "phone",
          "issue": "Phone number must contain exactly 10 digits"
        }
      ],
      "request_id": "req-e35b71c2-901b-4cf7-9a88-251f28b2a304"
    }
  }
  ```

---

## 1. Authentication & User Management

### 1.1 User Signup
- **Method & Path:** `POST /api/v1/auth/signup`
- **Auth Required:** No (Public)
- **Rate Limit:** 5 requests / minute
- **UI Source:** `src/pages/Register.jsx`
- **Request Body (`application/json`):**
  ```json
  {
    "full_name": "Pooja Sharma",
    "email": "pooja@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }
  ```
- **Success Response:** `201 Created`
  ```json
  {
    "user": {
      "id": "672e12a4f1a23b45c6789def",
      "email": "pooja@example.com",
      "full_name": "Pooja Sharma",
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-11-08T09:30:00Z"
    },
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 900
  }
  ```
- **Error Responses:**
  - `400 Bad Request` (`PASSWORDS_DO_NOT_MATCH`)
  - `409 Conflict` (`EMAIL_ALREADY_EXISTS`)
  - `422 Unprocessable Entity` (`VALIDATION_ERROR`)

---

### 1.2 User Login
- **Method & Path:** `POST /api/v1/auth/login`
- **Auth Required:** No (Public)
- **Rate Limit:** 5 requests / minute
- **UI Source:** `src/pages/Login.jsx`
- **Request Body (`application/json`):**
  ```json
  {
    "email": "pooja@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Success Response:** `200 OK` (Sets httpOnly cookie `refresh_token` and returns token response)
  ```json
  {
    "user": {
      "id": "672e12a4f1a23b45c6789def",
      "email": "pooja@example.com",
      "full_name": "Pooja Sharma",
      "role": "user",
      "is_active": true,
      "is_verified": true,
      "avatar_url": null,
      "created_at": "2026-11-08T09:30:00Z"
    },
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 900
  }
  ```
- **Error Responses:**
  - `401 Unauthorized` (`INVALID_CREDENTIALS` - generic message preventing account enumeration)
  - `403 Forbidden` (`ACCOUNT_LOCKED` - 5 failed attempts locked for 15 minutes)
  - `429 Too Many Requests` (`RATE_LIMIT_EXCEEDED`)

---

### 1.3 Refresh Access Token
- **Method & Path:** `POST /api/v1/auth/refresh`
- **Auth Required:** No (Reads httpOnly `refresh_token` cookie or Bearer `refresh_token` in body)
- **Rate Limit:** 20 requests / minute
- **UI Source:** Axios/Fetch interceptor in `src/lib/api.js`
- **Request Body (Optional if cookie is present):**
  ```json
  {
    "refresh_token": "d7a8e9f0..."
  }
  ```
- **Success Response:** `200 OK` (Rotates refresh token; returns new access token)
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 900
  }
  ```
- **Error Responses:**
  - `401 Unauthorized` (`TOKEN_EXPIRED` or `TOKEN_REVOKED` - if reused, family is invalidated)

---

### 1.4 User Logout
- **Method & Path:** `POST /api/v1/auth/logout`
- **Auth Required:** Yes
- **UI Source:** `src/pages/Dashboard.jsx` (Logout button)
- **Request Body:** None
- **Success Response:** `204 No Content` (Clears cookies; revokes active refresh token)

---

### 1.5 Get Current User Profile ("Me")
- **Method & Path:** `GET /api/v1/auth/me`
- **Auth Required:** Yes
- **UI Source:** `src/pages/Dashboard.jsx` (Welcome banner and profile avatar)
- **Success Response:** `200 OK`
  ```json
  {
    "id": "672e12a4f1a23b45c6789def",
    "email": "pooja@example.com",
    "full_name": "Pooja Sharma",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "avatar_url": null,
    "emergency_contacts_count": 3,
    "has_active_sos": false,
    "created_at": "2026-11-08T09:30:00Z"
  }
  ```
- **Error Responses:** `401 Unauthorized`

---

### 1.6 Forgot & Reset Password
- **Path:** `POST /api/v1/auth/forgot-password`
  - **Body:** `{"email": "pooja@example.com"}`
  - **Response:** `200 OK` `{"message": "If the account exists, a password reset link has been sent."}` (Prevents email harvesting)
- **Path:** `POST /api/v1/auth/reset-password`
  - **Body:** `{"token": "reset-token-str", "new_password": "NewSecurePassword123!"}`
  - **Response:** `200 OK` `{"message": "Password has been successfully reset. Please log in with your new password."}`

---

## 2. Emergency Contacts (`/api/v1/contacts`)

### 2.1 List Emergency Contacts
- **Method & Path:** `GET /api/v1/contacts`
- **Auth Required:** Yes
- **UI Source:** `src/pages/EmergencyContacts.jsx`, `src/pages/Dashboard.jsx`, `src/pages/SOS.jsx`
- **Query Params:** None (contacts per user typically bounded <= 10)
- **Success Response:** `200 OK`
  ```json
  {
    "items": [
      {
        "id": "672e1310f1a23b45c6789df1",
        "name": "Anjali Sharma",
        "phone": "9876543210",
        "relationship": "Family",
        "created_at": "2026-11-08T09:35:00Z",
        "updated_at": "2026-11-08T09:35:00Z"
      }
    ],
    "total": 1
  }
  ```

---

### 2.2 Create Emergency Contact
- **Method & Path:** `POST /api/v1/contacts`
- **Auth Required:** Yes
- **UI Source:** `src/pages/EmergencyContacts.jsx` (Add Contact form)
- **Request Body (`application/json`):**
  ```json
  {
    "name": "Anjali Sharma",
    "phone": "9876543210",
    "relationship": "Family"
  }
  ```
- **Validation Rules:**
  - `name`: string, min 2 chars, max 100 chars, stripped.
  - `phone`: string, exactly 10 digits, regex `^[6-9]\d{9}$`.
  - `relationship`: enum `["Family", "Friend", "Guardian", "Other"]`.
  - Max contacts per user limit: 10 contacts maximum.
- **Success Response:** `201 Created`
  ```json
  {
    "id": "672e1310f1a23b45c6789df1",
    "name": "Anjali Sharma",
    "phone": "9876543210",
    "relationship": "Family",
    "created_at": "2026-11-08T09:35:00Z",
    "updated_at": "2026-11-08T09:35:00Z"
  }
  ```
- **Error Responses:**
  - `400 Bad Request` (`DUPLICATE_PHONE_NUMBER` or `CONTACTS_LIMIT_REACHED`)
  - `422 Unprocessable Entity` (`VALIDATION_ERROR`)

---

### 2.3 Update Emergency Contact
- **Method & Path:** `PUT /api/v1/contacts/{contact_id}`
- **Auth Required:** Yes (Ownership verified; IDOR prevented)
- **UI Source:** `src/pages/EmergencyContacts.jsx` (Edit Contact mode)
- **Request Body (`application/json`):**
  ```json
  {
    "name": "Anjali Sharma",
    "phone": "9876543211",
    "relationship": "Family"
  }
  ```
- **Success Response:** `200 OK` (Returns updated contact object)
- **Error Responses:**
  - `404 Not Found` (`CONTACT_NOT_FOUND`)
  - `403 Forbidden` (`FORBIDDEN_RESOURCE`)

---

### 2.4 Delete Emergency Contact
- **Method & Path:** `DELETE /api/v1/contacts/{contact_id}`
- **Auth Required:** Yes (Ownership verified)
- **UI Source:** `src/pages/EmergencyContacts.jsx` (Confirm delete dialog)
- **Success Response:** `204 No Content`
- **Error Responses:**
  - `404 Not Found` (`CONTACT_NOT_FOUND`)
  - `403 Forbidden` (`FORBIDDEN_RESOURCE`)

---

## 3. Emergency SOS Assistance (`/api/v1/sos`)

### 3.1 Trigger SOS Alert
- **Method & Path:** `POST /api/v1/sos/trigger`
- **Auth Required:** Yes
- **Rate Limit:** 10 requests / minute
- **UI Source:** `src/pages/SOS.jsx` (SOS Confirmation Modal), `src/pages/Dashboard.jsx` (SOS Ring)
- **Request Body (`application/json`):**
  ```json
  {
    "latitude": 12.971598,
    "longitude": 77.594566,
    "accuracy": 15.5,
    "message": "I need help. Please contact me as soon as possible."
  }
  ```
- **Success Response:** `201 Created`
  ```json
  {
    "sos_id": "672e13a0f1a23b45c6789df5",
    "status": "ACTIVE",
    "triggered_at": "2026-11-08T09:40:00Z",
    "location": {
      "latitude": 12.971598,
      "longitude": 77.594566,
      "accuracy": 15.5
    },
    "contacts_notified": [
      {
        "name": "Anjali Sharma",
        "phone": "9876543210",
        "dispatch_status": "SENT"
      }
    ],
    "message": "SOS alert recorded and dispatched to trusted contacts."
  }
  ```
- **Error Responses:**
  - `400 Bad Request` (`NO_CONTACTS_CONFIGURED`)

---

### 3.2 Get Active SOS Status
- **Method & Path:** `GET /api/v1/sos/active`
- **Auth Required:** Yes
- **UI Source:** `src/pages/SOS.jsx`, `src/pages/Dashboard.jsx`
- **Success Response:** `200 OK`
  ```json
  {
    "has_active_sos": true,
    "sos": {
      "id": "672e13a0f1a23b45c6789df5",
      "status": "ACTIVE",
      "triggered_at": "2026-11-08T09:40:00Z",
      "latitude": 12.971598,
      "longitude": 77.594566,
      "accuracy": 15.5
    }
  }
  ```

---

### 3.3 Resolve / Cancel Active SOS Alert
- **Method & Path:** `POST /api/v1/sos/resolve`
- **Auth Required:** Yes
- **UI Source:** `src/pages/SOS.jsx` (Reset button)
- **Request Body (`application/json`):**
  ```json
  {
    "resolution_note": "User confirmed safe"
  }
  ```
- **Success Response:** `200 OK`
  ```json
  {
    "sos_id": "672e13a0f1a23b45c6789df5",
    "status": "RESOLVED",
    "resolved_at": "2026-11-08T09:45:00Z"
  }
  ```

---

## 4. Live Location Sharing (`/api/v1/location`)

### 4.1 Create or Update Live Location Share Session
- **Method & Path:** `POST /api/v1/location/share`
- **Auth Required:** Yes
- **UI Source:** `src/pages/Location.jsx` ("Detect My Location" & Share)
- **Request Body (`application/json`):**
  ```json
  {
    "latitude": 12.971598,
    "longitude": 77.594566,
    "accuracy": 15.5,
    "duration_minutes": 60
  }
  ```
- **Success Response:** `201 Created`
  ```json
  {
    "share_token": "shr_9a2b4c6e8f012345",
    "share_url": "https://sakhisahay.example/track/shr_9a2b4c6e8f012345",
    "expires_at": "2026-11-08T10:40:00Z",
    "latitude": 12.971598,
    "longitude": 77.594566,
    "accuracy": 15.5
  }
  ```

---

### 4.2 View Shared Location (Public Gated Endpoint)
- **Method & Path:** `GET /api/v1/location/shared/{share_token}`
- **Auth Required:** No (Token in path provides temporary read capability)
- **Success Response:** `200 OK`
  ```json
  {
    "user_name": "Pooja S.",
    "latitude": 12.971598,
    "longitude": 77.594566,
    "accuracy": 15.5,
    "updated_at": "2026-11-08T09:40:00Z",
    "expires_at": "2026-11-08T10:40:00Z",
    "is_active": true
  }
  ```
- **Error Responses:**
  - `404 Not Found` (`SHARED_LOCATION_NOT_FOUND_OR_EXPIRED`)

---

## 5. AI Safety Chatbot (`/api/v1/chatbot`)

### 5.1 Send Message to AI Safety Companion
- **Method & Path:** `POST /api/v1/chatbot/message`
- **Auth Required:** Optional (Allows logged-in users to persist history; anonymous users can chat)
- **Rate Limit:** 30 requests / minute
- **UI Source:** `src/pages/Chatbot.jsx`
- **Request Body (`application/json`):**
  ```json
  {
    "message": "What should I do if someone follows me?",
    "language": "en"
  }
  ```
- **Validation Rules:**
  - `message`: string, min 1 char, max 500 chars.
  - `language`: enum `["en", "kn"]` (English or Kannada).
- **Success Response:** `200 OK`
  ```json
  {
    "reply": "If you think someone is following you:\n• Stay calm and move towards a busy, well-lit place such as a shop, petrol pump or bus stop.\n• Do not go home directly, as the person may learn where you live.\n• Call a trusted person, or call 112 if you feel unsafe.\n• Note down what the person looks like and any vehicle details if it is safe to do so.\n• Ask shop staff, security guards or the police for help.",
    "language": "en",
    "key_topic": "followed",
    "emergency_helpline": "112",
    "suggested_actions": [
      "Move to a public place",
      "Call emergency 112",
      "Share live location"
    ],
    "created_at": "2026-11-08T09:42:00Z"
  }
  ```

---

## 6. Incident Reporting Diary (`/api/v1/reports/incidents`)

### 6.1 List Recorded Incidents
- **Method & Path:** `GET /api/v1/reports/incidents`
- **Auth Required:** Yes (Ownership check)
- **UI Source:** `src/pages/Reporting.jsx`
- **Query Params:** `page` (default 1), `page_size` (default 20, max 100)
- **Success Response:** `200 OK`
  ```json
  {
    "items": [
      {
        "id": "672e1440f1a23b45c6789e02",
        "category": "stalking",
        "incident_date": "2026-11-08T08:15:00Z",
        "location_summary": "Near Metro Station Gate 2",
        "notes": "Person repeatedly following across bus stop",
        "witnesses": "Shopkeeper nearby",
        "evidence_count": 2,
        "created_at": "2026-11-08T09:45:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "pages": 1
  }
  ```

---

### 6.2 Record New Incident Diary Entry
- **Method & Path:** `POST /api/v1/reports/incidents`
- **Auth Required:** Yes
- **UI Source:** `src/pages/Reporting.jsx`
- **Request Body (`application/json`):**
  ```json
  {
    "category": "stalking",
    "incident_date": "2026-11-08T08:15:00Z",
    "location_summary": "Near Metro Station Gate 2",
    "notes": "Person repeatedly following across bus stop",
    "witnesses": "Shopkeeper nearby"
  }
  ```
- **Success Response:** `201 Created`
  ```json
  {
    "id": "672e1440f1a23b45c6789e02",
    "category": "stalking",
    "incident_date": "2026-11-08T08:15:00Z",
    "location_summary": "Near Metro Station Gate 2",
    "notes": "Person repeatedly following across bus stop",
    "witnesses": "Shopkeeper nearby",
    "created_at": "2026-11-08T09:45:00Z"
  }
  ```

---

## 7. Safety Resources & System Operations

### 7.1 Safety Resources Directory
- **Method & Path:** `GET /api/v1/safety-resources`
- **Auth Required:** No (Public)
- **UI Source:** `src/pages/SafetyInformation.jsx`, `src/pages/Reporting.jsx`
- **Success Response:** `200 OK` (Provides verified national helplines, online portals, tips)

### 7.2 Health & Readiness
- `GET /health`: Liveness probe (`{"status": "ok", "service": "sakhisahay-backend"}`)
- `GET /ready`: Readiness probe (`{"status": "ready", "database": "connected"}`)
- `GET /version`: Git commit SHA and version tag

