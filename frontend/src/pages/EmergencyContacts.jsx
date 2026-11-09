import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/EmergencyContacts.css";

const RELATIONSHIPS = ["Family", "Friend", "Guardian", "Other"];
const EMPTY_FORM = { name: "", phone: "", relationship: "" };

/* ---------- Inline SVG icons ---------- */

function LogoIcon() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">
      <path
        d="M12 2.5 4.5 5.4v5.7c0 4.6 3.1 8.7 7.5 10.4 4.4-1.7 7.5-5.8 7.5-10.4V5.4L12 2.5Z"
        fill="currentColor"
      />
      <path
        d="M12 15.6s-3.2-2-3.2-4.2a1.8 1.8 0 0 1 3.2-1.1 1.8 1.8 0 0 1 3.2 1.1c0 2.2-3.2 4.2-3.2 4.2Z"
        fill="#fff"
      />
    </svg>
  );
}

function RelationshipIcon({ type }) {
  const common = {
    viewBox: "0 0 24 24",
    width: 26,
    height: 26,
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": "true",
    focusable: "false",
  };

  switch (type) {
    case "Family":
      return (
        <svg {...common}>
          <path d="M3 11.5 12 4l9 7.5" />
          <path d="M5.5 10v9.5h13V10" />
          <path d="M10 19.5v-5h4v5" />
        </svg>
      );
    case "Friend":
      return (
        <svg {...common}>
          <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z" />
        </svg>
      );
    case "Guardian":
      return (
        <svg {...common}>
          <path d="M12 3 5 5.8v5.4c0 4.3 2.9 8.1 7 9.8 4.1-1.7 7-5.5 7-9.8V5.8L12 3Z" />
          <path d="m9 12 2.2 2.2L15.2 10" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <circle cx="12" cy="8.5" r="3.5" />
          <path d="M5 20c.8-3.6 3.6-5.5 7-5.5s6.2 1.9 7 5.5" />
        </svg>
      );
  }
}

function PhoneIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1Z" />
    </svg>
  );
}

function BackIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      <path d="M15 5 8 12l7 7" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8h.01" />
    </svg>
  );
}

/* ---------- Page component ---------- */

function EmergencyContacts() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  const nameInputRef = useRef(null);
  const isEditing = editingId !== null;

  const loadContacts = async () => {
    try {
      setLoading(true);
      const data = await api.get("/contacts");
      const list = Array.isArray(data) ? data : (data?.items || []);
      setContacts(list);
      setServerError("");
    } catch (err) {
      setServerError("Failed to load contacts: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, []);

  /* ----- Form handlers ----- */

  const handleChange = (event) => {
    const { name, value } = event.target;
    const cleanedValue = name === "phone" ? value.replace(/\D/g, "").slice(0, 10) : value;

    setFormData((prev) => ({ ...prev, [name]: cleanedValue }));
    setServerError("");

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const validate = () => {
    const newErrors = {};
    const name = formData.name.trim();
    const phone = formData.phone.trim();

    if (!name) {
      newErrors.name = "Please enter the contact's full name.";
    } else if (name.length < 2) {
      newErrors.name = "Name must be at least 2 characters long.";
    }

    if (!phone) {
      newErrors.phone = "Please enter a phone number.";
    } else if (!/^\d{10}$/.test(phone)) {
      newErrors.phone = "Phone number must contain exactly 10 digits.";
    } else if (!/^[6-9]/.test(phone)) {
      newErrors.phone = "Indian mobile numbers start with 6, 7, 8 or 9.";
    } else if (contacts.some((c) => c.phone_number === phone && c.id !== editingId)) {
      newErrors.phone = "This phone number is already saved as an emergency contact.";
    }

    if (!formData.relationship) {
      newErrors.relationship = "Please choose a relationship.";
    }

    return newErrors;
  };

  const resetForm = () => {
    setFormData(EMPTY_FORM);
    setErrors({});
    setEditingId(null);
    setServerError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSaving(true);
    setServerError("");

    const payload = {
      name: formData.name.trim(),
      phone: formData.phone.trim(),
      phone_number: formData.phone.trim(),
      relationship: formData.relationship,
      is_primary: contacts.length === 0,
    };

    try {
      if (isEditing) {
        const updated = await api.put(`/contacts/${editingId}`, payload);
        setContacts((prev) => prev.map((c) => (c.id === editingId ? updated : c)));
        setStatusMessage(`${updated.name} was updated successfully.`);
      } else {
        const created = await api.post("/contacts", payload);
        setContacts((prev) => [...prev, created]);
        setStatusMessage(`${created.name} was added to your emergency contacts.`);
      }
      resetForm();
    } catch (err) {
      setServerError(err.message || "Failed to save contact.");
    } finally {
      setIsSaving(false);
    }
  };

  /* ----- Edit / delete handlers ----- */

  const handleEdit = (contact) => {
    setEditingId(contact.id);
    setFormData({
      name: contact.name,
      phone: contact.phone || contact.phone_number || "",
      relationship: contact.relationship,
    });
    setErrors({});
    setConfirmDeleteId(null);
    setStatusMessage("");
    setServerError("");

    if (nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  const handleConfirmDelete = async (contact) => {
    try {
      await api.delete(`/contacts/${contact.id}`);
      setContacts((prev) => prev.filter((c) => c.id !== contact.id));
      setConfirmDeleteId(null);
      setStatusMessage(`${contact.name} was removed from your emergency contacts.`);

      if (editingId === contact.id) {
        resetForm();
      }
    } catch (err) {
      setServerError("Failed to delete contact: " + err.message);
    }
  };

  /* ----- Render ----- */

  return (
    <div className="ec-page">
      <header className="ec-topbar">
        <div className="ec-brand">
          <span className="ec-brand-icon">
            <LogoIcon />
          </span>
          <span className="ec-brand-name">SAKHISAHAY</span>
        </div>

        <Link to="/dashboard" className="ec-back-link">
          <BackIcon />
          <span>Back to Dashboard</span>
        </Link>
      </header>

      <main className="ec-main">
        <section className="ec-hero">
          <h1 className="ec-title">Emergency Contacts</h1>
          <p className="ec-subtitle">
            Add the trusted people who should be alerted when you need help. Keep
            their details up to date so support is always one step away.
          </p>
          <p className="ec-notice" role="note">
            <InfoIcon />
            <span>
              All contacts are encrypted and securely stored. Up to 10 trusted contacts can be registered.
            </span>
          </p>
        </section>

        {serverError && (
          <div
            className="ec-notice"
            role="alert"
            style={{
              backgroundColor: "#FFEBEE",
              borderColor: "#EF9A9A",
              color: "#C62828",
              marginBottom: "1.5rem",
            }}
          >
            <strong>Error:</strong> {serverError}
          </div>
        )}

        {statusMessage && (
          <div
            className="ec-notice"
            role="status"
            style={{
              backgroundColor: "#E8F5E9",
              borderColor: "#A5D6A7",
              color: "#2E7D32",
              marginBottom: "1.5rem",
            }}
          >
            {statusMessage}
          </div>
        )}

        <div className="ec-layout">
          {/* ----- Add / edit form ----- */}
          <section className="ec-card ec-form-card" aria-labelledby="ec-form-heading">
            <h2 id="ec-form-heading" className="ec-card-title">
              {isEditing ? "Edit contact" : "Add a contact"}
            </h2>

            <form onSubmit={handleSubmit} noValidate>
              <div className="ec-field">
                <label htmlFor="ec-name">Full name</label>
                <input
                  ref={nameInputRef}
                  id="ec-name"
                  name="name"
                  type="text"
                  autoComplete="off"
                  placeholder="e.g. Anjali Sharma"
                  value={formData.name}
                  onChange={handleChange}
                  disabled={isSaving}
                  aria-invalid={Boolean(errors.name)}
                  aria-describedby={errors.name ? "ec-name-error" : undefined}
                  className={errors.name ? "ec-input ec-input-error" : "ec-input"}
                />
                {errors.name && (
                  <p id="ec-name-error" className="ec-error" role="alert">
                    {errors.name}
                  </p>
                )}
              </div>

              <div className="ec-field">
                <label htmlFor="ec-phone">Phone number</label>
                <input
                  id="ec-phone"
                  name="phone"
                  type="tel"
                  inputMode="numeric"
                  autoComplete="off"
                  placeholder="10-digit mobile number"
                  maxLength={10}
                  value={formData.phone}
                  onChange={handleChange}
                  disabled={isSaving}
                  aria-invalid={Boolean(errors.phone)}
                  aria-describedby={errors.phone ? "ec-phone-error" : undefined}
                  className={errors.phone ? "ec-input ec-input-error" : "ec-input"}
                />
                {errors.phone && (
                  <p id="ec-phone-error" className="ec-error" role="alert">
                    {errors.phone}
                  </p>
                )}
              </div>

              <div className="ec-field">
                <label htmlFor="ec-relationship">Relationship</label>
                <select
                  id="ec-relationship"
                  name="relationship"
                  value={formData.relationship}
                  onChange={handleChange}
                  disabled={isSaving}
                  aria-invalid={Boolean(errors.relationship)}
                  aria-describedby={errors.relationship ? "ec-rel-error" : undefined}
                  className={errors.relationship ? "ec-select ec-select-error" : "ec-select"}
                >
                  <option value="">Select relationship</option>
                  {RELATIONSHIPS.map((rel) => (
                    <option key={rel} value={rel}>
                      {rel}
                    </option>
                  ))}
                </select>
                {errors.relationship && (
                  <p id="ec-rel-error" className="ec-error" role="alert">
                    {errors.relationship}
                  </p>
                )}
              </div>

              <div className="ec-form-actions">
                <button
                  type="submit"
                  className="ec-btn ec-btn-primary"
                  disabled={isSaving || (!isEditing && contacts.length >= 10)}
                >
                  {isSaving ? "Saving..." : isEditing ? "Save changes" : "Add contact"}
                </button>
                {isEditing && (
                  <button
                    type="button"
                    className="ec-btn ec-btn-ghost"
                    onClick={resetForm}
                    disabled={isSaving}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </section>

          {/* ----- Contacts list ----- */}
          <section className="ec-card ec-list-card" aria-labelledby="ec-list-heading">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 id="ec-list-heading" className="ec-card-title">
                Saved contacts ({contacts.length}/10)
              </h2>
            </div>

            {loading ? (
              <div style={{ padding: "2rem", textAlign: "center", color: "#666" }}>
                Loading contacts from database...
              </div>
            ) : contacts.length === 0 ? (
              <div className="ec-empty">
                <p>No emergency contacts saved yet.</p>
                <p className="ec-empty-sub">
                  Fill in the form on the left to add your first trusted contact.
                </p>
              </div>
            ) : (
              <ul className="ec-list">
                {contacts.map((contact) => (
                  <li key={contact.id} className="ec-item">
                    <div className="ec-item-avatar" aria-hidden="true">
                      <RelationshipIcon type={contact.relationship} />
                    </div>

                    <div className="ec-item-body">
                      <div className="ec-item-header">
                        <h3 className="ec-item-name">{contact.name}</h3>
                        <span className="ec-item-rel">{contact.relationship}</span>
                      </div>
                      <p className="ec-item-phone">
                        <PhoneIcon />
                        <span>+91 {contact.phone || contact.phone_number}</span>
                      </p>
                    </div>

                    <div className="ec-item-actions">
                      <button
                        type="button"
                        className="ec-btn ec-btn-small ec-btn-ghost"
                        onClick={() => handleEdit(contact)}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="ec-btn ec-btn-small ec-btn-danger"
                        onClick={() => setConfirmDeleteId(contact.id)}
                      >
                        Delete
                      </button>
                    </div>

                    {confirmDeleteId === contact.id && (
                      <div className="ec-confirm-overlay">
                        <p>Remove {contact.name} from emergency contacts?</p>
                        <div className="ec-confirm-actions">
                          <button
                            type="button"
                            className="ec-btn ec-btn-small ec-btn-danger"
                            onClick={() => handleConfirmDelete(contact)}
                          >
                            Yes, remove
                          </button>
                          <button
                            type="button"
                            className="ec-btn ec-btn-small ec-btn-ghost"
                            onClick={() => setConfirmDeleteId(null)}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default EmergencyContacts;
