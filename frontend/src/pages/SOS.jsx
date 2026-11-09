import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/SOS.css";

/* ---------- Inline SVG icons ---------- */

const svgBase = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true",
  focusable: "false",
};

const ShieldIcon = ({ size = 24 }) => (
  <svg {...svgBase} width={size} height={size}>
    <path d="M12 3l7 3v5c0 4.5-3 8.2-7 10-4-1.8-7-5.5-7-10V6l7-3z" />
    <path d="M9 12l2 2 4-4" />
  </svg>
);

const ArrowLeftIcon = () => (
  <svg {...svgBase} width="18" height="18" strokeWidth="2">
    <path d="M19 12H5" />
    <path d="M11 6l-6 6 6 6" />
  </svg>
);

const BellIcon = () => (
  <svg {...svgBase} width="24" height="24">
    <path d="M6 9a6 6 0 0112 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9z" />
    <path d="M10 20a2 2 0 004 0" />
  </svg>
);

const UsersIcon = () => (
  <svg {...svgBase} width="24" height="24">
    <circle cx="9" cy="8" r="3.5" />
    <path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6" />
    <path d="M16 4.7a3.5 3.5 0 010 6.6" />
    <path d="M18 14.3c2.3.6 3.5 2.5 3.5 5.7" />
  </svg>
);

const PinIcon = () => (
  <svg {...svgBase} width="24" height="24">
    <path d="M12 21s-7-6.2-7-11.5A7 7 0 0119 9.5C19 14.8 12 21 12 21z" />
    <circle cx="12" cy="9.5" r="2.5" />
  </svg>
);

const MessageIcon = () => (
  <svg {...svgBase} width="24" height="24">
    <path d="M4 5h16a1 1 0 011 1v10a1 1 0 01-1 1H9l-5 4V6a1 1 0 011-1z" />
    <path d="M8 10h8" />
    <path d="M8 13h5" />
  </svg>
);

const InfoIcon = () => (
  <svg {...svgBase} width="22" height="22">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5" />
    <path d="M12 7.5v.01" />
  </svg>
);

const CheckIcon = () => (
  <svg {...svgBase} width="26" height="26" strokeWidth="2.2">
    <circle cx="12" cy="12" r="9" />
    <path d="M8 12.5l2.7 2.7L16 9.8" />
  </svg>
);

const MESSAGE_PREVIEW =
  "I need urgent assistance. Please contact me immediately. My location has been sent.";

const getLocationErrorMessage = (error) => {
  switch (error.code) {
    case 1:
      return "Location permission was denied. You can allow location access in your browser settings.";
    case 2:
      return "Your location is currently unavailable. Please check your device settings.";
    case 3:
      return "Getting your location took too long.";
    default:
      return "Unable to detect precise coordinates.";
  }
};

/* ---------- Page Component ---------- */

function SOS() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [activeAlert, setActiveAlert] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  const [serverError, setServerError] = useState("");

  const [locationStatus, setLocationStatus] = useState("idle"); // idle | loading | success | error
  const [coordinates, setCoordinates] = useState(null);
  const [locationError, setLocationError] = useState("");

  const sosButtonRef = useRef(null);
  const cancelButtonRef = useRef(null);

  useEffect(() => {
    async function initSosPage() {
      try {
        setLoading(true);
        const [contactsRes, activeRes] = await Promise.allSettled([
          api.get("/contacts"),
          api.get("/sos/active"),
        ]);

        if (contactsRes.status === "fulfilled") {
          const list = Array.isArray(contactsRes.value) ? contactsRes.value : (contactsRes.value?.items || []);
          setContacts(list);
        }
        if (activeRes.status === "fulfilled" && activeRes.value) {
          setActiveAlert(activeRes.value);
        }
      } catch (err) {
        setServerError("Failed to initialize SOS status: " + err.message);
      } finally {
        setLoading(false);
      }
    }

    initSosPage();
  }, []);

  /* Dialog keyboard handling: focus Cancel on open, close on Escape. */
  useEffect(() => {
    if (!showConfirm) return undefined;
    cancelButtonRef.current?.focus();

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setShowConfirm(false);
        sosButtonRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [showConfirm]);

  const openConfirm = () => {
    setServerError("");
    // Attempt background geolocation detection before confirmation
    if ("geolocation" in navigator && !coordinates) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setCoordinates({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
          });
          setLocationStatus("success");
        },
        () => {},
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 60000 }
      );
    }
    setShowConfirm(true);
  };

  const cancelConfirm = () => {
    setShowConfirm(false);
    sosButtonRef.current?.focus();
  };

  const handleTriggerSOS = async () => {
    setIsTriggering(true);
    setServerError("");

    const payload = {
      coordinates: coordinates
        ? {
            latitude: coordinates.latitude,
            longitude: coordinates.longitude,
            accuracy: coordinates.accuracy,
          }
        : null,
      address: null,
      notes: "Emergency SOS triggered by user from web app.",
    };

    try {
      const alert = await api.post("/sos/trigger", payload);
      setActiveAlert(alert);
      setShowConfirm(false);
    } catch (err) {
      setServerError(err.message || "Failed to trigger emergency SOS alert.");
    } finally {
      setIsTriggering(false);
    }
  };

  const handleResolveSOS = async () => {
    if (!activeAlert) return;
    setIsResolving(true);
    setServerError("");

    try {
      await api.post("/sos/resolve", {
        alert_id: activeAlert.id,
        resolution_notes: "Alert resolved safely by user.",
      });
      setActiveAlert(null);
      setCoordinates(null);
      setLocationStatus("idle");
    } catch (err) {
      setServerError(err.message || "Failed to resolve SOS alert.");
    } finally {
      setIsResolving(false);
    }
  };

  const requestLocation = () => {
    if (!("geolocation" in navigator)) {
      setLocationStatus("error");
      setLocationError("Your browser does not support the Geolocation API.");
      return;
    }

    setLocationStatus("loading");
    setLocationError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoordinates({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
        });
        setLocationStatus("success");
      },
      (error) => {
        setCoordinates(null);
        setLocationError(getLocationErrorMessage(error));
        setLocationStatus("error");
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  };

  return (
    <div className="sos-page">
      <header className="sos-header">
        <div className="sos-header-inner">
          <div className="sos-brand">
            <span className="sos-brand-mark">
              <ShieldIcon />
            </span>
            <span className="sos-brand-name">SAKHISAHAY</span>
          </div>
          <Link to="/dashboard" className="sos-back-link">
            <ArrowLeftIcon />
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </header>

      <main className="sos-main">
        {/* Real emergency notice */}
        <div className="sos-notice" role="note">
          <span className="sos-notice-icon">
            <InfoIcon />
          </span>
          <p>
            <strong>In immediate life-threatening danger?</strong> Call national emergency services:{" "}
            <strong>112 directly</strong>.{" "}
            <a href="tel:112" className="sos-notice-link">
              Call 112
            </a>
          </p>
        </div>

        {serverError && (
          <div
            className="sos-notice"
            role="alert"
            style={{
              backgroundColor: "#FFEBEE",
              borderColor: "#EF9A9A",
              color: "#C62828",
              marginBottom: "1rem",
            }}
          >
            <strong>Error:</strong> {serverError}
          </div>
        )}

        {/* Emergency SOS section */}
        <section className="sos-hero" aria-labelledby="sos-title">
          <h1 id="sos-title" className="sos-title">
            Emergency SOS Assistance
          </h1>
          <p className="sos-lead">
            Pressing the SOS button instantly records an emergency alert, captures your location,
            and notifies all your registered emergency contacts.
          </p>

          <div className="sos-button-wrap">
            <button
              type="button"
              ref={sosButtonRef}
              className="sos-button"
              onClick={openConfirm}
              disabled={Boolean(activeAlert) || isTriggering}
              aria-haspopup="dialog"
              aria-label="SOS emergency button. Opens confirmation dialog."
              style={activeAlert ? { backgroundColor: "#B71C1C", animation: "pulse 1.5s infinite" } : {}}
            >
              <span className="sos-button-text">
                {activeAlert ? "ACTIVE" : isTriggering ? "SENDING" : "SOS"}
              </span>
              <span className="sos-button-sub">
                {activeAlert ? "Alerting" : "Emergency"}
              </span>
            </button>
          </div>

          <p className="sos-demo-note" style={{ color: activeAlert ? "#C62828" : "#666" }}>
            {activeAlert
              ? "SOS alert is active! Your emergency contacts have been notified."
              : contacts.length === 0
              ? "Warning: You haven't added any emergency contacts yet. Please add contacts from the Dashboard."
              : `${contacts.length} emergency contact(s) ready to be alerted.`}
          </p>
        </section>

        {/* SOS active status */}
        {activeAlert && (
          <section
            className="sos-status"
            role="status"
            aria-live="polite"
            aria-labelledby="sos-status-title"
            style={{ backgroundColor: "#FFEBEE", borderColor: "#EF9A9A" }}
          >
            <span className="sos-status-icon" style={{ color: "#C62828" }}>
              <CheckIcon />
            </span>
            <div className="sos-status-body">
              <h2 id="sos-status-title" className="sos-status-title" style={{ color: "#B71C1C" }}>
                Emergency SOS Alert is Active!
              </h2>
              <p>
                Triggered at {new Date(activeAlert.triggered_at).toLocaleTimeString()}.{" "}
                <strong>{activeAlert.contacts_notified}</strong> emergency contacts were dispatched notifications.
              </p>
              {activeAlert.location && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>
                  Dispatched coordinates: {activeAlert.location.latitude.toFixed(6)},{" "}
                  {activeAlert.location.longitude.toFixed(6)}
                </p>
              )}
            </div>
            <button
              type="button"
              className="sos-btn sos-btn-secondary"
              onClick={handleResolveSOS}
              disabled={isResolving}
              style={{ backgroundColor: "#2E7D32", color: "#fff", borderColor: "#2E7D32" }}
            >
              {isResolving ? "Resolving..." : "Mark as Safe"}
            </button>
          </section>
        )}

        <div className="sos-grid">
          {/* Emergency contacts */}
          <section className="sos-card" aria-labelledby="sos-contacts-title">
            <div className="sos-card-head">
              <span className="sos-card-icon">
                <UsersIcon />
              </span>
              <h2 id="sos-contacts-title" className="sos-card-title">
                Registered Contacts ({contacts.length})
              </h2>
            </div>
            <p className="sos-card-text">
              These verified contacts will receive your emergency broadcast when SOS is triggered.
            </p>

            {loading ? (
              <div className="sos-empty">Loading contacts...</div>
            ) : contacts.length === 0 ? (
              <div className="sos-empty">
                No emergency contacts registered yet.{" "}
                <Link to="/emergency-contacts" style={{ color: "#E91E63", fontWeight: 600 }}>
                  Add contacts now
                </Link>
              </div>
            ) : (
              <ul className="sos-contact-list">
                {contacts.map((contact) => (
                  <li key={contact.id} className="sos-contact">
                    <span className="sos-contact-name">{contact.name}</span>
                    <span className="sos-contact-meta">
                      {contact.relationship} • +91 {contact.phone || contact.phone_number}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Location details */}
          <section className="sos-card" aria-labelledby="sos-location-title">
            <div className="sos-card-head">
              <span className="sos-card-icon">
                <PinIcon />
              </span>
              <h2 id="sos-location-title" className="sos-card-title">
                Current Location
              </h2>
            </div>
            <p className="sos-card-text">
              Your device's coordinates will be attached to the emergency dispatch so responders can locate you.
            </p>

            {locationStatus === "success" && coordinates ? (
              <div className="sos-coords-box">
                <p>
                  <strong>Latitude:</strong> {coordinates.latitude.toFixed(6)}
                </p>
                <p>
                  <strong>Longitude:</strong> {coordinates.longitude.toFixed(6)}
                </p>
                {coordinates.accuracy && (
                  <p className="sos-coords-accuracy">
                    Accurate within ±{Math.round(coordinates.accuracy)} meters
                  </p>
                )}
              </div>
            ) : locationStatus === "loading" ? (
              <div className="sos-empty">Acquiring GPS fix...</div>
            ) : (
              <div className="sos-empty">
                {locationError || "Location not acquired yet."}
              </div>
            )}

            <button
              type="button"
              className="sos-btn sos-btn-secondary"
              onClick={requestLocation}
              disabled={locationStatus === "loading"}
              style={{ marginTop: "1rem" }}
            >
              {locationStatus === "loading" ? "Locating..." : "Test Location Access"}
            </button>
          </section>

          {/* Alert message preview */}
          <section className="sos-card" aria-labelledby="sos-msg-title">
            <div className="sos-card-head">
              <span className="sos-card-icon">
                <MessageIcon />
              </span>
              <h2 id="sos-msg-title" className="sos-card-title">
                Alert Message Template
              </h2>
            </div>
            <p className="sos-card-text">
              This message will be dispatched alongside your real-time GPS location:
            </p>
            <div className="sos-message-box">
              <code>{MESSAGE_PREVIEW}</code>
            </div>
          </section>
        </div>
      </main>

      {/* Confirmation Dialog */}
      {showConfirm && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-title"
          className="sos-dialog-overlay"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
        >
          <div
            className="sos-dialog"
            style={{
              backgroundColor: "#fff",
              padding: "2rem",
              borderRadius: "16px",
              maxWidth: "460px",
              width: "100%",
              boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🚨</div>
            <h2 id="confirm-title" style={{ color: "#B71C1C", marginBottom: "0.75rem", fontSize: "1.4rem" }}>
              Confirm Emergency SOS Trigger
            </h2>
            <p style={{ color: "#555", fontSize: "0.95rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
              Are you sure you want to trigger an Emergency SOS alert? This will immediately alert your{" "}
              <strong>{contacts.length}</strong> emergency contact(s) with your GPS coordinates.
            </p>
            <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
              <button
                type="button"
                ref={cancelButtonRef}
                className="sos-btn"
                onClick={cancelConfirm}
                style={{ padding: "0.75rem 1.5rem", backgroundColor: "#f5f5f5", border: "1px solid #ccc", borderRadius: "8px", cursor: "pointer" }}
              >
                Cancel
              </button>
              <button
                type="button"
                className="sos-btn"
                onClick={handleTriggerSOS}
                disabled={isTriggering}
                style={{
                  padding: "0.75rem 1.5rem",
                  backgroundColor: "#D32F2F",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  fontWeight: 600,
                  cursor: isTriggering ? "wait" : "pointer",
                }}
              >
                {isTriggering ? "Broadcasting..." : "Yes, Trigger SOS"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SOS;
