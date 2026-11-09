import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import "../styles/Dashboard.css";
import "../styles/Auth.css";

export default function Profile() {
  const { user } = useAuth();

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [errors, setErrors] = useState({});
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
    setPasswordError("");
    setPasswordSuccess("");
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validatePasswordForm = () => {
    const newErrors = {};
    if (!passwordData.currentPassword) {
      newErrors.currentPassword = "Enter your current password.";
    }
    if (!passwordData.newPassword) {
      newErrors.newPassword = "Enter a new password.";
    } else if (passwordData.newPassword.length < 8) {
      newErrors.newPassword = "New password must be at least 8 characters.";
    }
    if (!passwordData.confirmPassword) {
      newErrors.confirmPassword = "Confirm your new password.";
    } else if (passwordData.newPassword !== passwordData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match.";
    }
    return newErrors;
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validatePasswordForm();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    setPasswordError("");
    setPasswordSuccess("");

    try {
      const res = await api.post("/auth/change-password", {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      setPasswordSuccess(res.message || "Password changed successfully!");
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (err) {
      setPasswordError(err.message || "Failed to change password. Verify your current password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayName = user?.full_name || "User";
  const userInitial = displayName.charAt(0).toUpperCase();

  return (
    <div className="db-page">
      <header className="db-header">
        <div className="db-container db-header__inner">
          <Link to="/dashboard" className="db-brand" aria-label="SAKHISAHAY dashboard">
            <span className="db-brand__name">SAKHISAHAY</span>
          </Link>
          <Link
            to="/dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              color: "#880E4F",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: "0.95rem",
            }}
          >
            &larr; Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="db-container" style={{ padding: "2rem 1rem", maxWidth: "800px", margin: "0 auto" }}>
        <h1 style={{ color: "#3A2D3E", fontSize: "1.8rem", marginBottom: "1.5rem" }}>
          Account &amp; Security Settings
        </h1>

        {/* User Profile Card */}
        <section
          style={{
            backgroundColor: "#fff",
            borderRadius: "12px",
            padding: "1.5rem",
            boxShadow: "0 2px 10px rgba(0,0,0,0.06)",
            border: "1px solid #FFE4E1",
            marginBottom: "2rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "1.2rem", marginBottom: "1.5rem" }}>
            <span
              style={{
                width: "60px",
                height: "60px",
                borderRadius: "50%",
                backgroundColor: "#880E4F",
                color: "#fff",
                fontSize: "1.8rem",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {userInitial}
            </span>
            <div>
              <h2 style={{ margin: "0 0 0.2rem 0", color: "#3A2D3E", fontSize: "1.3rem" }}>
                {displayName}
              </h2>
              <p style={{ margin: 0, color: "#666", fontSize: "0.95rem" }}>
                {user?.email}
              </p>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1rem",
              paddingTop: "1rem",
              borderTop: "1px solid #f0f0f0",
            }}
          >
            <div>
              <span style={{ display: "block", fontSize: "0.85rem", color: "#777" }}>Registered Mobile</span>
              <strong style={{ color: "#333", fontSize: "0.95rem" }}>
                {user?.phone_number ? `+91 ${user.phone_number}` : "Not registered"}
              </strong>
            </div>
            <div>
              <span style={{ display: "block", fontSize: "0.85rem", color: "#777" }}>Account Role</span>
              <strong style={{ color: "#333", fontSize: "0.95rem", textTransform: "capitalize" }}>
                {user?.role || "User"}
              </strong>
            </div>
            <div>
              <span style={{ display: "block", fontSize: "0.85rem", color: "#777" }}>Emergency Contacts</span>
              <strong style={{ color: "#880E4F", fontSize: "0.95rem" }}>
                {user?.emergency_contacts_count ?? 0} saved
              </strong>
            </div>
          </div>
        </section>

        {/* Change Password Card */}
        <section
          style={{
            backgroundColor: "#fff",
            borderRadius: "12px",
            padding: "1.5rem",
            boxShadow: "0 2px 10px rgba(0,0,0,0.06)",
            border: "1px solid #FFE4E1",
          }}
        >
          <h2 style={{ color: "#880E4F", fontSize: "1.2rem", marginBottom: "0.5rem" }}>
            Change Password
          </h2>
          <p style={{ color: "#666", fontSize: "0.9rem", marginBottom: "1.2rem" }}>
            Protect your safety account by using a strong, unique password.
          </p>

          {passwordSuccess && (
            <div
              style={{
                backgroundColor: "#E8F5E9",
                color: "#2E7D32",
                padding: "0.75rem",
                borderRadius: "6px",
                marginBottom: "1rem",
                fontSize: "0.9rem",
              }}
            >
              {passwordSuccess}
            </div>
          )}

          {passwordError && (
            <div
              style={{
                backgroundColor: "#FFEBEE",
                color: "#C62828",
                padding: "0.75rem",
                borderRadius: "6px",
                marginBottom: "1rem",
                fontSize: "0.9rem",
              }}
            >
              {passwordError}
            </div>
          )}

          <form onSubmit={handlePasswordSubmit} style={{ maxWidth: "450px" }} noValidate>
            <div className="auth-field">
              <label htmlFor="currentPassword">Current Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="currentPassword"
                  name="currentPassword"
                  type={showCurrent ? "text" : "password"}
                  value={passwordData.currentPassword}
                  onChange={handlePasswordChange}
                  disabled={isSubmitting}
                  className={errors.currentPassword ? "has-error" : ""}
                />
                <button
                  type="button"
                  className="auth-toggle"
                  onClick={() => setShowCurrent((p) => !p)}
                  aria-label={showCurrent ? "Hide password" : "Show password"}
                  disabled={isSubmitting}
                >
                  {showCurrent ? "Hide" : "Show"}
                </button>
              </div>
              {errors.currentPassword && (
                <p className="auth-error" role="alert">{errors.currentPassword}</p>
              )}
            </div>

            <div className="auth-field">
              <label htmlFor="newPassword">New Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="newPassword"
                  name="newPassword"
                  type={showNew ? "text" : "password"}
                  value={passwordData.newPassword}
                  onChange={handlePasswordChange}
                  disabled={isSubmitting}
                  className={errors.newPassword ? "has-error" : ""}
                />
                <button
                  type="button"
                  className="auth-toggle"
                  onClick={() => setShowNew((p) => !p)}
                  aria-label={showNew ? "Hide password" : "Show password"}
                  disabled={isSubmitting}
                >
                  {showNew ? "Hide" : "Show"}
                </button>
              </div>
              {errors.newPassword && (
                <p className="auth-error" role="alert">{errors.newPassword}</p>
              )}
            </div>

            <div className="auth-field">
              <label htmlFor="confirmPassword">Confirm New Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirm ? "text" : "password"}
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  disabled={isSubmitting}
                  className={errors.confirmPassword ? "has-error" : ""}
                />
                <button
                  type="button"
                  className="auth-toggle"
                  onClick={() => setShowConfirm((p) => !p)}
                  aria-label={showConfirm ? "Hide password" : "Show password"}
                  disabled={isSubmitting}
                >
                  {showConfirm ? "Hide" : "Show"}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="auth-error" role="alert">{errors.confirmPassword}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                backgroundColor: "#E91E63",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                padding: "0.75rem 1.5rem",
                fontWeight: 600,
                cursor: isSubmitting ? "wait" : "pointer",
                marginTop: "0.5rem",
              }}
            >
              {isSubmitting ? "Saving..." : "Change Password"}
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}
