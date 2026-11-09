import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/Auth.css";

const MIN_PASSWORD_LENGTH = 8;

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setServerError("");
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.password) {
      newErrors.password = "Please enter a new password.";
    } else if (formData.password.length < MIN_PASSWORD_LENGTH) {
      newErrors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your new password.";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match.";
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token) {
      setServerError("Reset token is missing from the URL. Please use the link sent to your email.");
      return;
    }

    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setIsSubmitting(true);
    setServerError("");

    try {
      const res = await api.post("/auth/reset-password", {
        token,
        new_password: formData.password,
      });
      setSuccessMessage(res.message || "Password has been successfully reset! You can now log in.");
    } catch (err) {
      setServerError(err.message || "Failed to reset password. The link may have expired.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <Link to="/login" className="auth-back-link">
          <span aria-hidden="true">&larr;</span> Back to Login
        </Link>

        <header className="auth-header">
          <div className="auth-brand">
            <svg
              className="auth-logo"
              width="44"
              height="44"
              viewBox="0 0 48 48"
              role="img"
              aria-label="SAKHISAHAY logo"
            >
              <circle cx="24" cy="24" r="24" fill="#B8A5D6" />
              <path
                d="M24 10l12 4.5v9.2c0 7.2-4.9 12.6-12 14.8-7.1-2.2-12-7.6-12-14.8v-9.2L24 10z"
                fill="#FFFAFC"
              />
              <path
                d="M24 31.5c-4.2-2.9-6.5-5.1-6.5-7.9 0-1.9 1.4-3.3 3.2-3.3 1.3 0 2.5.7 3.3 1.8.8-1.1 2-1.8 3.3-1.8 1.8 0 3.2 1.4 3.2 3.3 0 2.8-2.3 5-6.5 7.9z"
                fill="#C77D98"
              />
            </svg>
            <span className="auth-brand-name">SAKHISAHAY</span>
          </div>
          <h1 className="auth-title">Set New Password</h1>
          <p className="auth-subtitle">
            Enter your new password below to regain access to your safety account.
          </p>
        </header>

        {serverError && (
          <div
            className="auth-notice"
            role="alert"
            style={{
              backgroundColor: "#FFEBEE",
              borderColor: "#EF9A9A",
              color: "#C62828",
            }}
          >
            <strong>Error:</strong> {serverError}
          </div>
        )}

        {successMessage ? (
          <div style={{ textAlign: "center", padding: "1.5rem 0" }}>
            <div
              style={{
                backgroundColor: "#E8F5E9",
                color: "#2E7D32",
                padding: "1rem",
                borderRadius: "8px",
                marginBottom: "1.5rem",
                fontWeight: 500,
              }}
            >
              {successMessage}
            </div>
            <button
              type="button"
              className="auth-submit"
              onClick={() => navigate("/login")}
            >
              Go to Login
            </button>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            {!token && (
              <div
                style={{
                  backgroundColor: "#FFF3E0",
                  color: "#E65100",
                  padding: "0.75rem",
                  borderRadius: "6px",
                  fontSize: "0.85rem",
                  marginBottom: "1rem",
                }}
              >
                No token found in link. If you received a link by email, please make sure the full URL is copied.
              </div>
            )}

            <div className="auth-field">
              <label htmlFor="reset-password">New Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="reset-password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="At least 8 characters"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  className={errors.password ? "has-error" : ""}
                />
                <button
                  type="button"
                  className="auth-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  disabled={isSubmitting}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
              {errors.password && (
                <p className="auth-error" role="alert">
                  {errors.password}
                </p>
              )}
            </div>

            <div className="auth-field">
              <label htmlFor="reset-confirm-password">Confirm New Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="reset-confirm-password"
                  name="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  autoComplete="new-password"
                  placeholder="Re-enter your new password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  className={errors.confirmPassword ? "has-error" : ""}
                />
                <button
                  type="button"
                  className="auth-toggle"
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                  disabled={isSubmitting}
                >
                  {showConfirmPassword ? "Hide" : "Show"}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="auth-error" role="alert">
                  {errors.confirmPassword}
                </p>
              )}
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={isSubmitting || !token}
              style={{
                opacity: isSubmitting || !token ? 0.75 : 1,
                cursor: isSubmitting ? "wait" : !token ? "not-allowed" : "pointer",
              }}
            >
              {isSubmitting ? "Resetting Password..." : "Update Password"}
            </button>
          </form>
        )}

        <p className="auth-switch">
          Remember your password? <Link to="/login">Log in</Link>
        </p>
      </div>
    </main>
  );
}
