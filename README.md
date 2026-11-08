# SAKHISAHAY (सखी सहाय)

> **A Comprehensive, Deployment-Ready Women's Safety & Emergency Assistance Platform**  
> *Built with FastAPI (Python 3.12+), Motor AsyncIO, MongoDB 7.x, React 19, and Vite 8.*

[![CI Pipeline](https://github.com/sakhisahay/sakhisahay/actions/workflows/ci.yml/badge.svg)](https://github.com/sakhisahay/sakhisahay/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248.svg?logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Overview & Core Features

**SAKHISAHAY** is an emergency assistance web platform designed to provide women with immediate help, discreet safety tools, trusted contact management, live location sharing, and legal/safety guidance.

### Key Capabilities:
- 🚨 **Emergency SOS Assistance:** One-tap emergency broadcast with real-time GPS coordinate acquisition, alerting registered emergency contacts.
- 👥 **Emergency Contacts Management:** Secure storage and organization of up to 10 verified contacts with relationship classification and primary designation.
- 📍 **Live Location Sharing:** Temporary public tracking links with configurable expiration (30m, 1h, 2h, 8h) and one-click termination.
- 💬 **Bilingual Safety AI Assistant:** Intelligent safety guidance in English and Kannada with instant crisis helpline links (112, 181, 1091, 1930).
- 📝 **Confidential Incident Diary:** Private, encrypted documentation of harassment incidents, chronology, locations, and witness details for personal or legal reference.
- 🛡️ **Defensive Security:** JWT access tokens (15m) + secure httpOnly refresh tokens (7d) with cryptographic rotation, account lockout (5 attempts / 15m), and rate limiting.

---

## 2. Target Architecture

```
project-root/
├── frontend/                  # React 19 + Vite 8 SPA
│   ├── src/
│   │   ├── components/        # ProtectedRoute, ErrorBoundary
│   │   ├── context/           # AuthContext (JWT management & session sync)
│   │   ├── lib/api.js         # Fetch client with auto-refresh & timeout
│   │   ├── pages/             # Dashboard, SOS, Contacts, Location, Chatbot, etc.
│   │   └── styles/            # Scoped CSS stylesheets
│   ├── Dockerfile             # Multi-stage production container
│   └── nginx.conf             # SPA routing & caching
├── backend/                   # FastAPI Python Asynchronous Service
│   ├── app/
│   │   ├── main.py            # App factory & middleware pipeline
│   │   ├── core/              # Config, Security, Logging, Rate Limiting
│   │   ├── db/                # Motor client, Idempotent Indexes, Seeder
│   │   ├── models/            # Document schema representations
│   │   ├── schemas/           # Pydantic v2 input/output schemas
│   │   ├── repositories/      # Layered MongoDB queries (zero raw DB in services)
│   │   ├── services/          # Pure domain business logic
│   │   └── api/v1/endpoints/  # Auth, Contacts, SOS, Location, Chatbot, Reports
│   ├── tests/                 # Unit & integration test suite (100% pass)
│   ├── requirements.txt       # Pinned production dependencies
│   ├── requirements-dev.txt   # Quality & test dependencies
│   ├── pyproject.toml         # Ruff, Black, Mypy, Pytest configuration
│   └── Dockerfile             # Multi-stage non-root container
├── nginx/
│   └── nginx.conf             # Edge reverse proxy, SSL, rate-limiting & gzip
├── docker-compose.yml         # Local development environment
├── docker-compose.prod.yml    # Production container orchestration
├── .github/workflows/         # CI/CD pipelines (lint, test, build, deploy)
├── scripts/                   # backup.sh, restore.sh, migrate.py, healthcheck.py
├── docs/                      # Full architecture, security, and operational docs
└── Makefile                   # Developer shortcut commands
```

---

## 3. Quickstart: Local Development

### 3.1 Option A: Docker Compose (Recommended)

Start the full stack (MongoDB, FastAPI Backend, React Frontend):
```bash
docker compose up --build
```
- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
- Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 3.2 Option B: Native Local Setup

#### Prerequisites:
- Python 3.12+ (or 3.14+)
- Node.js 20+ & npm
- MongoDB running locally or a MongoDB Atlas URI

#### 1. Backend Setup:
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env

# Run database migrations
python ../scripts/migrate.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 4. Running Tests & Quality Checks

Run the automated test suite with coverage report:
```bash
cd backend
pytest tests -v --cov=app --cov-report=term-missing
```

Run code formatting and linting:
```bash
ruff check backend
black --check backend
```

Build the frontend:
```bash
cd frontend
npm run build
```

---

## 5. API Documentation

Interactive Swagger/OpenAPI documentation is available at `/docs` when the backend is running.
- Exported OpenAPI specification: [`docs/openapi.json`](docs/openapi.json)
- Postman Collection: [`docs/postman_collection.json`](docs/postman_collection.json)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/signup` | Create user account & receive JWT pair | No |
| `POST` | `/api/v1/auth/login` | Authenticate with email/password | No |
| `POST` | `/api/v1/auth/refresh` | Rotate access token via refresh token | No (Cookie) |
| `POST` | `/api/v1/auth/logout` | Invalidate token family & clear cookie | Yes |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes |
| `GET` | `/api/v1/contacts` | List user's emergency contacts | Yes |
| `POST` | `/api/v1/contacts` | Add new emergency contact (max 10) | Yes |
| `PUT` | `/api/v1/contacts/{id}`| Update existing contact | Yes |
| `DELETE`| `/api/v1/contacts/{id}`| Remove emergency contact | Yes |
| `POST` | `/api/v1/sos/trigger` | Trigger emergency SOS broadcast | Yes |
| `GET` | `/api/v1/sos/active` | Get currently active SOS alert | Yes |
| `POST` | `/api/v1/sos/resolve` | Mark SOS emergency as safe | Yes |
| `POST` | `/api/v1/location/share`| Generate live location share link | Yes |
| `GET` | `/api/v1/location/active`| Get user's active location share | Yes |
| `DELETE`| `/api/v1/location/share`| Stop active live location share | Yes |
| `GET` | `/api/v1/location/shared/{token}`| Public live location query | No |
| `POST` | `/api/v1/chatbot/message`| Safety guidance AI response | No |
| `GET` | `/api/v1/chatbot/faq` | Multilingual suggested safety FAQs | No |
| `GET` | `/api/v1/reports` | List confidential incident logs | Yes |
| `POST` | `/api/v1/reports` | Record incident in private diary | Yes |
| `DELETE`| `/api/v1/reports/{id}`| Delete incident log | Yes |
| `GET` | `/api/v1/health/live` | Container liveness check | No |
| `GET` | `/api/v1/health/ready` | Database readiness check & latency | No |

---

## 6. Detailed Documentation Index

For in-depth technical details, refer to the documentation in [`docs/`](docs/):
- [`docs/FRONTEND_AUDIT.md`](docs/FRONTEND_AUDIT.md): Initial audit of all pages, inputs, and components.
- [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md): Comprehensive REST contract with request/response schemas.
- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md): MongoDB collections, fields, and relationships.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): System architecture, layered design, and data flows.
- [`docs/SECURITY.md`](docs/SECURITY.md): Threat model, cryptography, lockout, and OWASP defenses.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): Production deployment guide (VPS, Docker, SSL, Atlas).
- [`docs/RUNBOOK.md`](docs/RUNBOOK.md): On-call incident response, logging, and disaster recovery.
- [`docs/PERFORMANCE.md`](docs/PERFORMANCE.md): Latency SLOs, connection pooling, and caching.
- [`docs/QUERY_PLANS.md`](docs/QUERY_PLANS.md): MongoDB index verification and IXSCAN execution plans.
- [`docs/GAPS.md`](docs/GAPS.md): Analysis and resolution of all initial frontend gaps.
- [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md): Documented technical and domain assumptions.

---

## 7. License

Distributed under the MIT License. See `LICENSE` for more information.
