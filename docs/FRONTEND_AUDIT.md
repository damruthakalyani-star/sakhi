# Frontend Audit: SAKHISAHAY Women's Safety Platform

**Date:** November 2026  
**Auditor:** Senior Full-Stack Engineer, DevOps & QA Lead  
**Application Name:** SAKHISAHAY (Women's Safety and Emergency Assistance Companion)  
**Repository Path:** `frontend/`

---

## 1. Technology Inventory

| Attribute | Detected Value | Notes / Verification |
| :--- | :--- | :--- |
| **Framework** | React 19.3.1 (`^19.3.1`) | Functional components with React Hooks (`useState`, `useEffect`, `useRef`). |
| **DOM Renderer** | React DOM 19.3.1 (`^19.3.1`) | Mounted with React 19 `createRoot` in `src/main.jsx`. |
| **Routing** | React Router DOM 7.18.5 (`^7.18.5`) | Client-side routing with `BrowserRouter`, `Routes`, `Route`, `Link`, `Navigate`, `useLocation`. |
| **Build Tool** | Vite 8.3.5 (`^8.3.5`) | `@vitejs/plugin-react` 6.1.2 using Oxc/SWC compiler. |
| **Package Manager** | npm (`package-lock.json` present) | Node.js runtime v24.13.0 verified. |
| **Code Linter** | Oxlint 1.89.0 (`oxlint`) | Configured in `.oxlintrc.json`. |
| **Styling** | Pure CSS (BEM / modular stylesheets) | Individual stylesheets in `src/styles/` (`Auth.css`, `Dashboard.css`, `EmergencyContacts.css`, `Location.css`, `Chatbot.css`, `Reporting.css`, `SafetyInformation.css`, `SOS.css`) + `App.css` and `index.css`. |
| **State Management** | Local React Component State | Local `useState`, `useRef`. No global state manager (Redux/Zustand) currently configured. |
| **API Client** | None | No Axios, Fetch wrapper, React Query, or SWR installed yet. Static/demo states only. |
| **Environment Vars** | None present | Needs `VITE_API_BASE_URL` and `VITE_APP_NAME` in `.env.example`. |

---

## 2. Page-by-Page Audit & Inventory

### 2.1 Landing Page (`/` -> `HomePage` in `src/App.jsx`)
- **Purpose:** Public landing page introducing SAKHISAHAY's mission, core pillars, key safety features, emergency SOS overview, and direct calls to action.
- **Sections:**
  - `Navbar`: Sticky navigation bar with brand icon ("shield"), smooth scroll links (`#home`, `#about`, `#features`, `#contact`), Login CTA, and Get Started CTA. Responsive mobile toggle menu with keyboard trap on `Escape`.
  - `Hero`: Hero headline, mission copy, "Get Started" (`/register`), "Explore Features" (`#features`), trust badges ("Quick to reach", "Easy to use", "Built with care"), and SVG hero illustration with interactive floating status badges ("SOS ready", "Location shared").
  - `About`: Three pillars: *Safety*, *Accessibility*, *Emergency Assistance*.
  - `Features`: 6 feature cards: Emergency SOS (`/sos`), Emergency Contacts (`/emergency-contacts`), Live Location Sharing (`/location`), AI Safety Chatbot (`/chatbot`), Harassment Reporting (`/reporting`), and Safety Information (`/safety-information`).
  - `Emergency`: Prominent SOS teaser card with large SOS button leading to `/sos`, process steps, and statutory 112 emergency advice for India.
  - `Footer`: Quick links, safety tool navigation, verified contact information (`support@sakhisahay.example`, `+91 00000 00000`), copyright notice, and 112 reminder.
- **Components Used:** `Navbar`, `Button`, `SectionHeading`, `Icon`, `HeroIllustration`, `Hero`, `About`, `Features`, `FeatureCard`, `Emergency`, `Footer`.
- **Form / User Input:** None.
- **API Interactions Needed:** None (static promotional content); public system health ping or statistics may optionally be shown.

---

### 2.2 Login Page (`/login` -> `src/pages/Login.jsx`)
- **Purpose:** User authentication portal for returning users.
- **Form Fields:**
  - `email`: Type `email`, autocomplete `email`, required, validated against email regex (`/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/`).
  - `password`: Type `password` with show/hide toggle (`showPassword` state), required.
- **Submit Handler:**
  - Client-side validation: sets error state per field; autofocuses first invalid element.
  - Currently mocks completion by clearing password and displaying informational banner: *"Login is not available yet. Your details look valid, but authentication will be available after backend integration."*
- **Auth UI Elements:**
  - Brand header and back link to `/`.
  - "Forgot password?" placeholder button marked `aria-disabled="true"` with badge *"Unavailable for now"*.
  - Link to `/register`: *"New to SAKHISAHAY? Create an account"*.
- **API Interactions Needed:**
  - `POST /api/v1/auth/login` (request: email, password; response: user details, accessToken, refreshToken in httpOnly cookie or Authorization response).
  - `POST /api/v1/auth/forgot-password` (request: email).

---

### 2.3 Registration Page (`/register` -> `src/pages/Register.jsx`)
- **Purpose:** New user onboarding and account creation.
- **Form Fields:**
  - `fullName`: Type `text`, autocomplete `name`, required (minimum 1 character trimmed).
  - `email`: Type `email`, autocomplete `email`, required, regex validated.
  - `password`: Type `password` with show/hide toggle, required, minimum 8 characters.
  - `confirmPassword`: Type `password` with show/hide toggle, required, must strictly match `password`.
- **Submit Handler:**
  - Client-side validation: validates all 4 fields, displays inline error messages under each field, autofocuses first invalid field.
  - Currently displays placeholder status notice: *"Registration is not available yet. Your details look valid, but account creation will be available after backend integration."*
- **Auth UI Elements:**
  - Brand header and back link to `/`.
  - Link to `/login`: *"Already have an account? Log in"*.
- **API Interactions Needed:**
  - `POST /api/v1/auth/signup` (request: fullName, email, password, confirmPassword; response: user profile, token/cookie, initial verification state).

---

### 2.4 User Dashboard (`/dashboard` -> `src/pages/Dashboard.jsx`)
- **Purpose:** Central command center for authenticated users.
- **Sections:**
  - `DashboardNav`: Top navigation bar with brand icon, links to `/dashboard`, `/sos`, `/emergency-contacts`, `/location`, `/chatbot`, `/reporting`, user avatar chip (initial letter), user display name, and Logout button leading to `/login`.
  - `WelcomeSection`: Personalized welcome card: *"Welcome back! Hello, {USER_NAME}."* Currently hardcoded to `"User"`.
  - `SosSection`: Emergency SOS activation card with pulsating SOS action button leading to `/sos` and warning that preview version is not connected to real police dispatch.
  - `QuickAccessSection`: 5 quick navigation cards linking to Contacts, Location, Chatbot, Reporting, and Safety Information.
  - `ContactOverview`: Preview of saved emergency contacts. Currently displays hardcoded empty state: *"No emergency contacts added yet"*, with "Add Contact" button linking to `/emergency-contacts`.
  - `SafetyReminder`: Curated safety advice card (charging phone, sharing itinerary, sticking to well-lit routes).
- **API Interactions Needed:**
  - `GET /api/v1/auth/me`: Retrieve authenticated user profile (name, email, role, avatar).
  - `GET /api/v1/contacts`: Retrieve user's emergency contacts count and top contacts for quick display.
  - `GET /api/v1/sos/active`: Check if user currently has an active SOS emergency session.
  - `POST /api/v1/auth/logout`: Invalidate session and revoke refresh tokens.

---

### 2.5 Emergency Contacts (`/emergency-contacts` -> `src/pages/EmergencyContacts.jsx`)
- **Purpose:** Full CRUD management of trusted individuals alerted during emergencies.
- **Form Fields:**
  - `name`: Full name, required, length >= 2 chars.
  - `phone`: Mobile number, required, exactly 10 digits, starts with 6, 7, 8, or 9 (Indian mobile format), duplicate phone number check across existing contacts.
  - `relationship`: Dropdown selection, required: `Family`, `Friend`, `Guardian`, `Other`.
- **Interactions & State:**
  - Contact creation (Add Contact).
  - Contact update (inline form prefill, Save changes / Cancel).
  - Contact deletion with inline modal confirmation: *"Delete {contact.name}? This cannot be undone."*
  - Live count indicator (`X contacts`).
  - Empty state with illustration when list is empty.
  - Live screen reader announcer (`aria-live="polite"` status message).
  - Notice currently states: *"Contacts are kept temporarily on this page and are not permanently saved until backend integration is added."*
- **API Interactions Needed:**
  - `GET /api/v1/contacts`: Fetch all emergency contacts for current user.
  - `POST /api/v1/contacts`: Create new emergency contact document.
  - `PUT /api/v1/contacts/{contact_id}`: Update existing contact details.
  - `DELETE /api/v1/contacts/{contact_id}`: Remove contact from database.

---

### 2.6 Emergency SOS Assistance (`/sos` -> `src/pages/SOS.jsx`)
- **Purpose:** Emergency activation hub to trigger alert and broadcast current coordinates to trusted contacts.
- **Sections & Features:**
  - Emergency Notice: Prominent callout to call `112` directly with immediate dialer link `tel:112`.
  - Large SOS Trigger Button:
    - Triggers accessible confirmation dialog: *"Start SOS demonstration? / No emergency alert will be sent / No contacts notified / Call 112 if in danger."*
    - On confirmation: activates SOS status banner with confirmation message and "Reset" button.
  - Emergency Contacts Summary Widget:
    - Lists registered contacts to be notified. Currently reads from empty local constant `emergencyContacts = []`.
  - Live Location Fetcher:
    - "Get My Current Location" button using `navigator.geolocation.getCurrentPosition`.
    - High accuracy GPS coordinates (`latitude`, `longitude`, `accuracy` in meters).
    - Friendly error message handling (permission denied, position unavailable, timeout).
  - Emergency Message Preview:
    - Shows message template with placeholder: *"I need help. Please contact me as soon as possible. My location: [location will be inserted here]"*.
- **API Interactions Needed:**
  - `GET /api/v1/contacts`: Fetch registered emergency contacts for SOS display.
  - `POST /api/v1/sos/trigger`: Initiate emergency SOS alert (latitude, longitude, accuracy, timestamp); dispatches async SMS/Email notifications to contacts.
  - `POST /api/v1/sos/resolve`: Cancel or resolve active SOS alert.
  - `GET /api/v1/sos/active`: Get status of any active alert session.

---

### 2.7 Live Location Sharing (`/location` -> `src/pages/Location.jsx`)
- **Purpose:** On-demand GPS location detection, coordinate inspection, clipboard copying, and OpenStreetMap navigation.
- **Features:**
  - "Detect My Location" button with spinner loading state.
  - GPS Coordinate display: latitude and longitude to 6 decimal places, accuracy radius in meters.
  - "Open in OpenStreetMap" dynamic external link: `https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=17/{lat}/{lng}`.
  - "Copy Coordinates" button with clipboard write API and temporary feedback banner ("Coordinates copied to your clipboard").
  - Geolocation error handling with explanatory troubleshooting tips (browser permission, device GPS, timeout).
  - Educational privacy cards: "You are in control" and "Privacy notice".
- **API Interactions Needed:**
  - `POST /api/v1/location/share`: Create shareable live location session with expiry (15m, 1h, 4h).
  - `GET /api/v1/location/shared/{share_token}`: Public token-gated endpoint allowing trusted contacts to view live location without login.

---

### 2.8 AI Safety Chatbot (`/chatbot` -> `src/pages/Chatbot.jsx`)
- **Purpose:** Interactive conversational assistant providing calm, practical guidance for safety queries in English and Kannada.
- **Features:**
  - Bilingual toggle: English (`en`) and Kannada (`kn`).
  - Emergency notice banner: Call 112 if in immediate danger.
  - Chat window: chat history log with user and bot message bubbles.
  - Animated typing indicator dots (`chatbot-typing`) with realistic delay (600ms).
  - Suggested question chips:
    - Followed: *"What should I do if someone follows me?"* / *"ಯಾರಾದರೂ ನನ್ನನ್ನು ಹಿಂಬಾಲಿಸಿದರೆ ನಾನು ಏನು ಮಾಡಬೇಕು?"*
    - Harassment: *"How can I report harassment?"* / *"ಕಿರುಕುಳದ ಬಗ್ಗೆ ನಾನು ಹೇಗೆ ದೂರು ನೀಡಬಹುದು?"*
    - Travel: *"How can I stay safe while travelling alone?"* / *"ಒಂಟಿಯಾಗಿ ಪ್ರಯಾಣಿಸುವಾಗ ನಾನು ಹೇಗೆ ಸುರಕ್ಷಿತವಾಗಿರಬಹುದು?"*
    - Emergency: *"What should I do in an emergency?"* / *"ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?"*
  - Form input: Text input with character counter (`0/500 characters`), submit button, enter key support, input length enforcement.
  - Current implementation: Keyword matching against static text table `DEMO_RESPONSES`.
- **API Interactions Needed:**
  - `POST /api/v1/chatbot/message`: Accepts message prompt, user language (`en` or `kn`), conversation context; returns structured safety response, source references, and emergency helplines.
  - `GET /api/v1/chatbot/history`: Retrieves user past chat session logs.

---

### 2.9 Harassment Reporting (`/reporting` -> `src/pages/Reporting.jsx`)
- **Purpose:** Comprehensive informational and self-paced incident documentation guidance.
- **Sections:**
  - Emergency 112 Card with click-to-call link.
  - Types of Harassment (Expandable accordions): Online harassment, Stalking, Verbal harassment, Physical harassment, with examples and actionable suggestions.
  - 6-Step Reporting Guide: Safety first, preserve evidence, note incident details, identify channel, seek support, follow up.
  - Evidence Preservation: Detailed guidance for Screenshots, Messages/Emails, Call logs, Photographs, Witness details.
  - Help and Support in India: 112, Women Helpline 181, Cyber Crime 1930 / `cybercrime.gov.in`, NCW 14490 / `ncw.gov.in`.
  - Privacy and Safety Notice.
- **API Interactions Needed:**
  - `POST /api/v1/reports/incidents`: Secure, private incident diary entry (date, time, location description, category, incident notes, evidence attachments metadata).
  - `GET /api/v1/reports/incidents`: Private listing of user's documented incidents.
  - `DELETE /api/v1/reports/incidents/{incident_id}`: Option to delete private diary entries.

---

### 2.10 Safety Information & Guidance (`/safety-information` -> `src/pages/SafetyInformation.jsx`)
- **Purpose:** Curated safety tips, practical awareness advice, and directory of verified Indian helplines.
- **Sections:**
  - Emergency 112 Card.
  - Accordion sections with single-open toggle state:
    - Personal Safety: public alertness, boundaries, informing contacts.
    - Online and Cyber Safety: account privacy, 2FA, phishing awareness.
    - Travel Safety: planning routes, sharing itinerary, cab verification.
    - Emergency Preparedness: saving contacts, knowing numbers, de-escalation.
    - Important Helplines: 112 ERSS, 181 Women Helpline, 1930 Cyber Crime Helpline, `cybercrime.gov.in`.
- **API Interactions Needed:**
  - `GET /api/v1/safety-resources`: Public directory of helplines, safety tips, and state emergency numbers.

---

## 3. Reusable Component Inventory

| Component | Source File | Used By Pages / Components | Purpose |
| :--- | :--- | :--- | :--- |
| `Icon` | `src/App.jsx` | `HomePage`, `Navbar`, `Footer`, `FeatureCard`, `Hero` | 24x24 SVG icons (shield, bell, users, pin, chat, report, info, etc.) |
| `Button` | `src/App.jsx` | `HomePage`, `Navbar`, `Hero`, `PlaceholderPage` | Polymorphic button/link component supporting variants & sizes |
| `SectionHeading` | `src/App.jsx` | `HomePage` (`About`, `Features`) | Consistent typography & alignment for headings |
| `Navbar` | `src/App.jsx` | `HomePage` | Public navigation header with mobile toggle |
| `HeroIllustration`| `src/App.jsx` | `HomePage` | Custom SVG graphic with animated floating cards |
| `Footer` | `src/App.jsx` | `HomePage` | Global footer with contact details and statutory disclaimers |
| `DashboardNav` | `src/pages/Dashboard.jsx` | `Dashboard` | Authenticated top bar with navigation links, profile chip, logout |
| `QuickAccessCard`| `src/pages/Dashboard.jsx` | `Dashboard` | Feature navigation card on dashboard |
| `Expandable` | `src/pages/Reporting.jsx` | `Reporting` | Accessible accordion with keyboard controls and ARIA attributes |
| `SafetyAccordionItem` | `src/pages/SafetyInformation.jsx` | `SafetyInformation` | Interactive accordion panel for safety tips & helpline cards |
| Page Icons | `EmergencyContacts`, `SOS`, `Location`, `SafetyInformation` | Local pages | Inline lightweight SVGs for buttons and visual markers |

---

## 4. Current State Management & Data Flow

- **Global Store:** Currently **NONE**.
- **User Session:**
  - Login & Register only have local component state. They do not persist tokens or user objects in localStorage, cookies, or Context.
  - `Dashboard.jsx` hardcodes `const USER_NAME = "User";`.
- **CRUD Operations:**
  - `EmergencyContacts.jsx` maintains an in-memory array (`contacts` state) initialized to `[]`. State is lost on page refresh.
  - `SOS.jsx` references an empty array `const emergencyContacts = [];`.
- **AI / Query Flow:**
  - `Chatbot.jsx` executes deterministic string searches against hardcoded dictionaries. No remote API call exists.
- **Location Flow:**
  - Direct browser API call `navigator.geolocation.getCurrentPosition`. Coordinates are stored in local page state only.

---

## 5. Security & Accessibility Audit

### Accessibility Strengths
- Good use of ARIA attributes (`aria-expanded`, `aria-controls`, `aria-label`, `aria-invalid`, `aria-describedby`, `aria-live="polite"`).
- Keyboard support: `Escape` key closes mobile navigation and SOS confirmation dialog.
- Semantic HTML tags used: `<main>`, `<header>`, `<footer>`, `<section>`, `<article>`, `<nav>`, `<aside>`, `<dl>`, `<ol>`, `<ul>`.
- Form labels properly linked via `htmlFor` and `id`.

### Accessibility Gaps
- `ScrollToTop` uses instant scroll rather than smooth or reduced-motion aware behavior.
- Color contrast on some muted text elements (`#666` or opacity `0.55`) requires verification under WCAG AA guidelines.
- Missing keyboard focus rings on several custom buttons in dark/accent styles.

### Security Findings
- No tokens are stored insecurely yet (because no backend exists).
- When integrating authentication, tokens must **never** be placed raw in `localStorage` vulnerable to XSS. We will use secure, httpOnly, SameSite cookies with CSRF protection, plus an Authorization header fallback.
- Client-side phone number validation enforces 10-digit Indian numbers (`/^[6-9]\d{9}$/`), but this must be rigorously mirrored on the backend.
- Password validation on client requires >= 8 characters, but server must also enforce complexity, prevent common passwords, and check password hash integrity with bcrypt/argon2.

