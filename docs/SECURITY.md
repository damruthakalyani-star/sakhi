# SAKHISAHAY: Security Model & Hardening Guide

This document details the security architecture, threat model, cryptographic practices, and defensive countermeasures implemented across the SAKHISAHAY platform.

---

## 1. Threat Model & Countermeasures (OWASP Top 10)

| OWASP Risk | Platform Vulnerability Vectors | Implemented Countermeasure |
| :--- | :--- | :--- |
| **A01: Broken Access Control (IDOR)** | Unauthorized access to another user's contacts, SOS history, or incident diary. | All repository queries enforce tenancy: every query filters by `user_id == current_user.id`. Route dependencies reject ID tampering with `404 Not Found` (never `403` to prevent enumeration). |
| **A02: Cryptographic Failures** | Weak password hashing, cleartext token storage, leaked credentials. | Passwords hashed using Bcrypt (12 rounds). Refresh and password reset tokens stored strictly as SHA-256 hashes. TLS 1.3 enforced in production. JWTs signed with HMAC-SHA256 and unique cryptographic `jti` IDs. |
| **A03: Injection** | NoSQL injection, BSON manipulation. | Strict Pydantic v2 input schemas reject unexpected fields. Motor queries construct BSON filters using typed Python dictionaries without `eval()` or string concatenation. |
| **A04: Insecure Design** | Unlimited emergency contact creation, infinite SOS broadcasts, replay attacks. | Contact count hard-limited to 10 per account. Duplicate phone numbers rejected. Active SOS alerts enforce state transitions. Token rotation invalidates replay attempts. |
| **A05: Security Misconfiguration** | Default credentials in production, wildcard CORS, verbose stack traces. | Startup assertions in `config.py` halt execution if `SECRET_KEY` is default, `DEBUG=true` in production, or `CORS_ORIGINS` contains `*`. Uniform error envelopes suppress stack traces. |
| **A06: Vulnerable & Outdated Components** | Unpatched Python or Node libraries. | Dependencies pinned to exact patch versions. `pip check` and `npm audit` enforced in CI pipeline. |
| **A07: Identification & Auth Failures** | Brute force password guessing, credential stuffing, session hijacking. | Exponential lockout: account locked for 15 minutes after 5 consecutive failed attempts. Silent token rotation with family revocation invalidates all sessions if a used refresh token is replayed. |
| **A08: Software & Data Integrity Failures** | Code tampering, untrusted package downloads. | Multi-stage Docker builds run as non-root user (UID 10001). Node packages and wheels verified via checksums. |
| **A09: Security Logging & Monitoring** | Undetected intrusion attempts. | Structured JSON logging with unique correlation `request_id` per HTTP transaction. Security audit trail records auth failures, lockouts, and emergency alerts. |
| **A10: Server-Side Request Forgery (SSRF)** | Arbitrary outbound requests from backend services. | Backend makes no untrusted outbound URL requests. External links (OpenStreetMap, 112) rendered on the client browser. |

---

## 2. Authentication & Session Architecture

### 2.1 Password Hashing & Account Lockout
- **Algorithm:** Bcrypt with work factor (salt rounds) = 12.
- **Lockout Policy:**
  - `failed_login_attempts` counter incremented on every invalid password attempt.
  - Upon reaching 5 failed attempts, the account is locked: `locked_until` set to `now() + 15 minutes`.
  - Further authentication attempts return HTTP 403 Forbidden with exact unlock timestamp.
  - Successful authentication immediately resets `failed_login_attempts` to 0 and clears `locked_until`.

### 2.2 JWT Access Tokens
- **Lifespan:** 15 minutes.
- **Algorithm:** `HS256` signed using a minimum 64-character cryptographically random secret.
- **Claims:**
  - `sub`: User ID
  - `role`: Role (`user` or `admin`)
  - `type`: `access`
  - `iat`: Timestamp issued
  - `exp`: Timestamp expired
  - `jti`: Cryptographic UUIDv4 string preventing token collisions and enabling token revocation.

### 2.3 Refresh Tokens & Token Rotation
- **Lifespan:** 7 days.
- **Storage:** Refresh token is never stored in plaintext. The backend computes `sha256(token).hexdigest()` and stores only the hash in MongoDB.
- **Delivery:** Delivered via HTTP-only cookie (`httpOnly=True`, `secure=True` in production, `sameSite="lax"`).
- **Silent Rotation:** Every call to `/api/v1/auth/refresh` revokes the incoming token and issues a fresh token pair.
- **Token Family Reuse Detection:** If an already-revoked refresh token is presented, the system flags a replay attack and revokes all active refresh tokens for that user account immediately.

---

## 3. Rate Limiting Policy

Rate limiting is enforced at two distinct layers:
1. **Nginx Edge Layer:**
   - Auth endpoints (`/api/v1/auth/*`): 10 requests per minute with burst=5.
   - General endpoints (`/api/*`): 100 requests per minute with burst=20.
2. **FastAPI Application Layer (`slowapi`):**
   - In-memory or Redis-backed sliding window rate limiters protecting against application-level resource exhaustion.

---

## 4. HTTP Security Headers

The reverse proxy and backend middleware attach the following headers to all HTTP responses:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' http: https:;
```

---

## 5. Production Environment Validation

The backend application factory validates environment integrity in `backend/app/core/config.py`:
- Refuses to start if `APP_ENV == "production"` and `DEBUG == True`.
- Refuses to start if `SECRET_KEY` contains default dummy values or has fewer than 32 characters (64+ recommended).
- Refuses to start if `CORS_ORIGINS` contains wildcard `*` in production mode.
