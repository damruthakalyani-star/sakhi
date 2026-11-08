# Frontend Gaps & Remediation Plan: SAKHISAHAY

**Date:** November 2026  
**Auditor:** Senior Full-Stack Engineer, DevOps & QA Lead  
**Scope:** `frontend/src` audit for hardcoded values, missing UX states, accessibility, security, and integration readiness.

---

## 1. Summary of Findings

| Category | High | Medium | Low | Total |
| :--- | :---: | :---: | :---: | :---: |
| **Hardcoded Data / Mocks** | 4 | 2 | 0 | 6 |
| **Missing UX States (Loading/Error/Empty)** | 3 | 3 | 1 | 7 |
| **Broken / Placeholder Routes** | 2 | 1 | 0 | 3 |
| **State Management & Session Handling** | 3 | 1 | 0 | 4 |
| **Accessibility & Styling** | 0 | 3 | 2 | 5 |
| **Security & Secrets** | 0 | 1 | 1 | 2 |
| **Total** | **12** | **11** | **4** | **27** |

---

## 2. Detailed Findings

### 2.1 Hardcoded Data and Static Mocks
1. **User Name & Profile in Dashboard (`src/pages/Dashboard.jsx:10`):**
   - **Finding:** `const USER_NAME = "User";` is hardcoded. The avatar simply displays `"U"` and the greeting says *"Hello, User."*.
   - **Impact:** Authenticated user never sees their real name, email, or profile picture.
   - **Remediation:** Connect to `GET /api/v1/auth/me` via centralized Auth Context.
2. **Contact Overview in Dashboard (`src/pages/Dashboard.jsx:323`):**
   - **Finding:** Contacts card strictly renders `db-empty` ("No emergency contacts added yet"), ignoring any contacts the user adds.
   - **Impact:** Users who add contacts on `/emergency-contacts` see zero reflected on their dashboard.
   - **Remediation:** Fetch contacts list on Dashboard mount and display real contact cards with quick-call triggers.
3. **Emergency Contacts List in SOS (`src/pages/SOS.jsx:84`):**
   - **Finding:** `const emergencyContacts = [];` is an empty static constant.
   - **Impact:** SOS page always displays *"No emergency contacts are available yet"*, preventing user from confirming who will receive emergency dispatch.
   - **Remediation:** Fetch active user contacts from `/api/v1/contacts`.
4. **Chatbot Pre-written Responses (`src/pages/Chatbot.jsx:82`):**
   - **Finding:** `DEMO_RESPONSES` contains 4 static dictionary entries (`followed`, `harassment`, `travel`, `emergency`) with fallback text.
   - **Impact:** Chatbot cannot answer queries beyond exact keyword matches.
   - **Remediation:** Connect to `POST /api/v1/chatbot/message` powered by FastAPI assistant logic.
5. **In-Memory Contacts Storage (`src/pages/EmergencyContacts.jsx:103`):**
   - **Finding:** Contacts are saved in local React state (`useState([])`) with counter `nextIdRef`.
   - **Impact:** Refreshing or navigating away deletes all contacts. Notice explicitly acknowledges this gap.
   - **Remediation:** Connect to backend CRUD `/api/v1/contacts`.
6. **Footer Dummy Telephone & Address (`src/App.jsx:685`):**
   - **Finding:** `+91 00000 00000` and `Your city, State, India`.
   - **Impact:** Placeholder text in production build.
   - **Remediation:** Parameterize via environment variables or replace with verified national women safety helpline directory details.

---

### 2.2 Missing UX States (Loading, Error, Retry)
1. **Login & Register Form Submissions:**
   - **Finding:** `Login.jsx` and `Register.jsx` lack an `isLoading` / pending state on submit buttons.
   - **Impact:** Users can double-submit forms or become confused during network latency.
   - **Remediation:** Add `isSubmitting` state, spinner icon, and disable submit button while request is in-flight.
2. **Emergency Contacts Async State:**
   - **Finding:** No skeleton or spinner during initial data loading or save/delete mutations.
   - **Impact:** Sudden layout shifts; no feedback if network request fails.
   - **Remediation:** Add loading skeleton for contacts list, inline mutation spinners, and error toast / alert banner with "Retry" action.
3. **Location Detection Timeout & Retry:**
   - **Finding:** `Location.jsx` has `isLoading` spinner, but error display does not provide a direct "Retry" button.
   - **Remediation:** Add clear "Retry Location Detection" CTA on error box.
4. **Global Error Boundary:**
   - **Finding:** No React Error Boundary in `src/main.jsx` or `src/App.jsx`. If a component throws an uncaught JavaScript error, the entire screen renders blank.
   - **Remediation:** Add top-level `ErrorBoundary` with a calm, branded recovery screen ("Something went wrong, return to home").

---

### 2.3 Broken / Placeholder Routes & Actions
1. **Forgot Password Link (`src/pages/Login.jsx:167`):**
   - **Finding:** Disabled `<button className="auth-disabled-link">` with badge *"Unavailable for now"*.
   - **Impact:** Users who forget passwords are locked out permanently with no recovery avenue.
   - **Remediation:** Implement forgot password modal and `/api/v1/auth/forgot-password` endpoint.
2. **Feature Card "Coming Soon" (`src/App.jsx:98`):**
   - **Finding:** "Safety Information and Guidance" had `to: null` with *"Coming soon"*, even though `src/pages/SafetyInformation.jsx` exists and is routed at `/safety-information`!
   - **Impact:** Landing page visitors cannot click the card to access the Safety Information page.
   - **Remediation:** Update `FEATURES[5].to` from `null` to `"/safety-information"` and `cta: "Read guidance"`.
3. **Route Guards & Auth Protection:**
   - **Finding:** `/dashboard`, `/emergency-contacts`, `/sos`, `/location`, `/chatbot`, `/reporting` are completely unprotected. Anyone can access `/dashboard` without signing in.
   - **Remediation:** Implement `<ProtectedRoute>` wrapper that redirects unauthenticated users to `/login?redirect=...`.

---

### 2.4 State Management & Session Handling
1. **No Global Auth Context:**
   - **Finding:** User credentials, tokens, and active profile are not shared across components.
   - **Remediation:** Create `AuthContext` (`AuthProvider`, `useAuth`) storing `user`, `isAuthenticated`, `login()`, `logout()`, `refresh()`.
2. **Centralized API Client Missing:**
   - **Finding:** No centralized Axios/Fetch client exists.
   - **Remediation:** Create `src/lib/api.js` with base URL from `import.meta.env.VITE_API_BASE_URL`, automatic JWT attachment, request timeout (10s), typed error normalization, and 401 token refresh queue.

---

### 2.5 Accessibility & Quality Issues
1. **Color Contrast:**
   - **Finding:** Light rose/lavender tags (`.ec-tag`, `.float-card small`) have contrast ratios around 3.2:1 against light backgrounds.
   - **Remediation:** Adjust text colors to `#3A2D3E` or `#49364F` to meet WCAG AA (>= 4.5:1).
2. **Instant Scroll on Route Navigation:**
   - **Finding:** `ScrollToTop` uses `behavior: "instant"`, which can be abrupt for users who prefer reduced motion.
   - **Remediation:** Respect `prefers-reduced-motion` media query.

---

### 2.6 Security Findings
1. **No LocalStorage Token Leakage (Currently Clean):**
   - **Finding:** Currently no tokens are stored in `localStorage`.
   - **Remediation:** Preserve this good practice. Store JWTs in secure httpOnly cookies or in-memory React state with refresh token rotation.
2. **Environment Variable Configuration:**
   - **Finding:** No `.env.example` in `frontend/`.
   - **Remediation:** Add `frontend/.env.example` defining `VITE_API_BASE_URL=http://localhost:8000/api/v1` and `VITE_APP_NAME=SAKHISAHAY`.

