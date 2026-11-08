# Architectural & Implementation Assumptions: SAKHISAHAY

**Date:** November 2026  
**Document Version:** 1.0.0  
**Scope:** Assumptions made during Phase 0 Frontend Audit and Technical Design

---

## 1. Domain & Business Assumptions

1. **Target Region & Emergency Services:**
   - **Assumption:** The primary operational context for SAKHISAHAY is India, as evidenced by Indian phone validation (`^[6-9]\d{9}$`), statutory emergency number `112` (ERSS), Women Helpline `181`, Cyber Crime Helpline `1930`, NCW `14490`, and Kannada (`kn`) language support.
   - **Choice:** All emergency dialer links, helpline directories, and phone validators default to the Indian standard (E.164 +91 / 10-digit mobile), while keeping phone input extensible.
2. **Emergency SOS Dispatch:**
   - **Assumption:** In a browser web application environment without direct native GSM modem hardware, emergency SOS triggers must notify registered emergency contacts via backend transactional SMS / Email dispatch and update live dashboard status, while advising the user to dial `112` directly.
   - **Choice:** Backend will record active SOS alerts with GPS coordinates, dispatch notifications via background tasks, and return immediate acknowledgment to the frontend.
3. **AI Chatbot Service:**
   - **Assumption:** The chatbot provides calm, non-judgmental, legally compliant safety guidance in English and Kannada. While a production LLM API (e.g. Gemini API) can be hooked via backend environment variable `GEMINI_API_KEY`, the backend must include a robust, rule-based fallback assistant covering verified safety guidance so the app operates deterministically even without third-party external API keys.
   - **Choice:** Implement an intelligent, multilingual assistant service in FastAPI with structured safety intent recognition and fallback to verified guidelines.

---

## 2. Authentication & Security Assumptions

1. **Token Delivery & Storage:**
   - **Assumption:** Web security best practice avoids storing long-lived tokens in browser `localStorage` due to XSS vulnerability.
   - **Choice:** Deliver access tokens in API response for memory store and refresh tokens in `httpOnly`, `Secure`, `SameSite=Lax` cookies. Maintain full compatibility with `Authorization: Bearer <token>` headers for REST testing and automated API clients.
2. **User Roles:**
   - **Assumption:** The platform has standard `user` accounts and `admin` accounts (for viewing audit logs, system health, and emergency statistics).
   - **Choice:** Implement role-based dependency `require_role(["admin"])` and default all user signups to role `"user"`.
3. **Contact Ownership & IDOR Protection:**
   - **Assumption:** A user may only view, edit, or delete emergency contacts and incident reports that belong to their own account.
   - **Choice:** Enforce repository-level scoping where queries always filter by `user_id == current_user.id` unless the caller has administrative override.

---

## 3. Infrastructure & Deployment Assumptions

1. **Local Development Environment:**
   - **Assumption:** Developers may run the system via Docker Compose or directly on a local Python 3.12 / Node.js workstation.
   - **Choice:** Provide full `docker-compose.yml` for containerized dev (Mongo, Backend, Frontend) and virtual environment instructions (`requirements.txt`).
2. **MongoDB Connectivity:**
   - **Assumption:** The database connects via standard MongoDB connection URI (`mongodb://localhost:27017` in local Docker, or MongoDB Atlas SRV connection string in staging/production).
   - **Choice:** Use Motor async driver with connection pooling (`maxPoolSize=50`, `minPoolSize=5`), lifespan health checking, and automatic idempotent index creation.

