# SAKHISAHAY: System Architecture & Technical Specification

## 1. Executive Summary & Mission

**SAKHISAHAY** is a mission-critical full-stack digital platform designed to provide women with rapid emergency assistance, trusted contact coordination, live GPS location sharing, verified legal and emergency guidance, and confidential incident documentation.

The architecture emphasizes:
1. **Zero Downtime & Fast Response:** Sub-100ms API response latency for critical SOS and emergency contact lookups.
2. **Defensive Security & Privacy:** Strict zero-trust authentication, cryptographic token rotation, account lockout defense, and data segregation.
3. **Layered Separation of Concerns:** Rigid architectural boundaries ensuring testability, maintainability, and clean code hygiene.

---

## 2. Target Architecture Diagram

```mermaid
flowchart TD
    Client["Browser / Mobile Web (React 19 + Vite)"]
    Nginx["Nginx Reverse Proxy & SSL Gateway (Port 80/443)"]
    
    subgraph BackendApp ["FastAPI Application (Uvicorn / Gunicorn)"]
        Middleware["Middleware Pipeline\n• Request ID Correlation\n• Security Headers\n• CORS Validation\n• Rate Limiting (SlowAPI)\n• JSON Access Logging"]
        Routers["API v1 Routers (/api/v1/)\n• /auth\n• /contacts\n• /sos\n• /location\n• /chatbot\n• /reports\n• /health"]
        Deps["Dependencies & Guards\n• Bearer Token Authentication\n• Role Verification\n• Pagination & Filter Bounds"]
        Services["Domain Services (Business Logic)\n• AuthService\n• ContactService\n• SosService\n• LocationService\n• ChatbotService\n• ReportService"]
        Repos["Data Repositories (Data Access Layer)\n• UserRepository\n• TokenRepository\n• ContactRepository\n• SosRepository\n• LocationRepository\n• ReportRepository\n• AuditRepository"]
    end

    subgraph DatabaseLayer ["Database & Storage"]
        MongoDB[("MongoDB 7.x Replica Set / Atlas\n• Users & Tokens\n• Emergency Contacts\n• SOS Incidents\n• Location Shares\n• Incident Diary\n• Audit Logs")]
    end

    Client -->|HTTPS / WSS| Nginx
    Nginx -->|Proxy HTTP /api/| Middleware
    Nginx -->|Static Assets /| Client
    Middleware --> Routers
    Routers --> Deps
    Deps --> Services
    Services --> Repos
    Repos -->|Motor AsyncIO| MongoDB
```

---

## 3. Layered Design & Architectural Rules

The backend strictly enforces a four-tier architecture. No layer is permitted to bypass another:

```
[ HTTP Endpoints / Routers ]
            │
            ▼
[ Domain Services (Business Logic) ]
            │
            ▼
[ Data Repositories (Database Access) ]
            │
            ▼
[ MongoDB Database (Motor Driver) ]
```

### 3.1 HTTP Endpoints / Routers (`backend/app/api/v1/endpoints/`)
- Sole responsibility: Parse HTTP requests, validate input via Pydantic schemas, invoke dependencies, call domain services, and return normalized responses with appropriate HTTP status codes.
- Prohibitions: No direct database access; no business calculation logic.

### 3.2 Domain Services (`backend/app/services/`)
- Sole responsibility: Implement business rules, enforce domain limits (e.g., maximum 10 emergency contacts per account, duplicate contact rejection, account lockout thresholds, multilingual keyword classification).
- Prohibitions: No HTTP request/response handling (headers, cookies, status codes are abstracted); no raw database queries.

### 3.3 Data Repositories (`backend/app/repositories/`)
- Sole responsibility: Encapsulate all database queries, projections, aggregations, and BSON/ObjectId transformations.
- Provides standard CRUD primitives (`get_by_id`, `find_one`, `find_many`, `create`, `update`, `delete`, `count`).

### 3.4 Schemas & Document Models (`backend/app/schemas/` & `backend/app/models/`)
- Strict Pydantic v2 models validate data ingress and egress.
- MongoDB internal `_id` is always mapped to clean string `id`. Sensitive attributes (`password_hash`, `token_hash`) are excluded by design from response schemas.

---

## 4. Key End-to-End Interaction Flows

### 4.1 Authentication & Silent Token Rotation

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Client
    participant API as FastAPI /auth
    participant Service as AuthService
    participant Repo as TokenRepo & UserRepo
    participant DB as MongoDB

    User->>Frontend: Enters Email & Password
    Frontend->>API: POST /api/v1/auth/login
    API->>Service: authenticate_user(email, password)
    Service->>Repo: get_by_email(email)
    Repo->>DB: Query users where email = target
    DB-->>Repo: User Document
    Service->>Service: Verify Bcrypt Hash & Check Lockout
    Service->>Repo: Create Refresh Token (SHA-256 hash stored)
    Repo->>DB: Insert refresh_token
    Service-->>API: Return access_token (15m) + set httpOnly refresh_token cookie (7d)
    API-->>Frontend: 200 OK + JWT Access Token

    Note over Frontend,API: Subsequent Request after Access Token Expires
    Frontend->>API: GET /api/v1/contacts (Token expired -> 401)
    Frontend->>API: POST /api/v1/auth/refresh (Sends httpOnly cookie)
    API->>Service: refresh_access_token(token)
    Service->>Repo: Validate token hash & check revocation
    Note over Service,Repo: Token Rotation: Old token revoked, New token generated
    Service-->>API: New access_token + Rotated cookie
    API-->>Frontend: 200 OK
    Frontend->>API: Retries original request with new token
```

### 4.2 Emergency SOS Trigger Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Client
    participant Geo as Browser Geolocation API
    participant API as FastAPI /sos
    participant Service as SosService
    participant ContactRepo as ContactRepository
    participant SosRepo as SosRepository
    participant DB as MongoDB

    User->>Frontend: Press SOS Emergency Button
    Frontend->>Geo: getCurrentPosition()
    Geo-->>Frontend: {latitude, longitude, accuracy}
    Frontend->>API: POST /api/v1/sos/trigger {coordinates, notes}
    API->>Service: trigger_sos(user_id, coordinates)
    Service->>ContactRepo: get_user_contacts(user_id)
    ContactRepo->>DB: Query active emergency contacts
    DB-->>ContactRepo: List of verified contacts
    Service->>SosRepo: create_sos_alert(status='active', contacts_notified=N)
    SosRepo->>DB: Insert sos_alerts record
    Service-->>API: Active SOS Alert Details
    API-->>Frontend: 201 Created {alert_id, status: 'active', contacts_notified}
    Frontend-->>User: Active Alert Banner & Confirmation
```

---

## 5. Technology Stack Summary

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React | 19.x | Declarative UI components and state management |
| **Frontend Tooling** | Vite | 8.x | High-performance bundling and development server |
| **Backend Framework** | FastAPI | 0.115.x | High-throughput asynchronous REST API framework |
| **Async Web Server** | Uvicorn / Gunicorn | Latest | ASGI server running multiple worker processes |
| **Database Driver** | Motor / PyMongo | 3.6.x / 4.9.x | Asynchronous non-blocking MongoDB client |
| **Data Validation** | Pydantic v2 | 2.10.x | Type checking, request parsing, and schema generation |
| **Cryptography** | Passlib / Bcrypt / PyJWT | 1.7.x / 4.2.x / 2.10.x | Password hashing and signed JWT authentication |
| **Rate Limiter** | SlowAPI | 0.1.9 | IP and user based request throttling |
| **Reverse Proxy** | Nginx | 1.27 Alpine | TLS termination, rate limiting, and static file delivery |
| **Database** | MongoDB | 7.0 | Document store for users, alerts, contacts, and reports |
