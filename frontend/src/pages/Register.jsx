import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Auth.css";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const MIN_PASSWORD_LENGTH = 8;

const INITIAL_FORM = {
  fullName: "",
  email: "",
  phoneNumber: "",
  password: "",
  confirmPassword: "",
};

function validate({ fullName, email, phoneNumber, password, confirmPassword }) {
  const errors = {};

  if (!fullName.trim()) {
    errors.fullName = "Please enter your full name.";
  }

  if (!email.trim()) {
    errors.email = "Please enter your email address.";
  } else if (!EMAIL_PATTERN.test(email.trim())) {
    errors.email = "Please enter a valid email address, e.g. name@example.com.";
  }

  if (phoneNumber && !/^\d{10}$/.test(phoneNumber.replace(/\D/g, ""))) {
    errors.phoneNumber = "Phone number must be 10 digits if provided.";
  }

  if (!password) {
    errors.password = "Please create a password.";
  } else if (password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`;
  }

  if (!confirmPassword) {
    errors.confirmPassword = "Please confirm your password.";
  } else if (password !== confirmPassword) {
    errors.confirmPassword = "Passwords do not match. Please try again.";
  }

  return errors;
}

function Register() {
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [serverError, setServerError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (event) => {
    const { name, value } = event.target;
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

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationErrors = validate(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      const firstInvalid = Object.keys(validationErrors)[0];
      document.getElementById(`register-${firstInvalid}`)?.focus();
      return;
    }

    setIsSubmitting(true);
    setServerError("");

    try {
      await register({
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        confirm_password: formData.confirmPassword,
        full_name: formData.fullName.trim(),
        phone_number: formData.phoneNumber.trim() || null,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setServerError(err.message || "Registration failed. Please check your information.");
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-back-link">
          <span aria-hidden="true">←</span> Back to Home
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
          <h1 className="auth-title">Create Your Account</h1>
          <p className="auth-subtitle">
            Join SAKHISAHAY to get started with your safety support.
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
            <strong>Registration failed:</strong> {serverError}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-field">
            <label htmlFor="register-fullName">Full name</label>
            <input
              id="register-fullName"
              name="fullName"
              type="text"
              autoComplete="name"
              placeholder="Your full name"
              value={formData.fullName}
              onChange={handleChange}
              disabled={isSubmitting}
              aria-invalid={errors.fullName ? "true" : "false"}
              aria-describedby={
                errors.fullName ? "register-fullName-error" : undefined
              }
              className={errors.fullName ? "has-error" : ""}
            />
            {errors.fullName && (
              <p id="register-fullName-error" className="auth-error" role="alert">
                {errors.fullName}
              </p>
            )}
          </div>

          <div className="auth-field">
            <label htmlFor="register-email">Email address</label>
            <input
              id="register-email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              disabled={isSubmitting}
              aria-invalid={errors.email ? "true" : "false"}
              aria-describedby={errors.email ? "register-email-error" : undefined}
              className={errors.email ? "has-error" : ""}
            />
            {errors.email && (
              <p id="register-email-error" className="auth-error" role="alert">
                {errors.email}
              </p>
            )}
          </div>

          <div className="auth-field">
            <label htmlFor="register-phoneNumber">Phone number (optional)</label>
            <input
              id="register-phoneNumber"
              name="phoneNumber"
              type="tel"
              autoComplete="tel"
              placeholder="10-digit mobile number"
              value={formData.phoneNumber}
              onChange={handleChange}
              disabled={isSubmitting}
              aria-invalid={errors.phoneNumber ? "true" : "false"}
              aria-describedby={errors.phoneNumber ? "register-phoneNumber-error" : undefined}
              className={errors.phoneNumber ? "has-error" : ""}
            />
            {errors.phoneNumber && (
              <p id="register-phoneNumber-error" className="auth-error" role="alert">
                {errors.phoneNumber}
              </p>
            )}
          </div>

          <div className="auth-field">
            <label htmlFor="register-password">Password</label>
            <div className="auth-password-wrapper">
              <input
                id="register-password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={formData.password}
                onChange={handleChange}
                disabled={isSubmitting}
                aria-invalid={errors.password ? "true" : "false"}
                aria-describedby={
                  errors.password
                    ? "register-password-hint register-password-error"
                    : "register-password-hint"
                }
                className={errors.password ? "has-error" : ""}
              />
              <button
                type="button"
                className="auth-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-pressed={showPassword}
                aria-label={showPassword ? "Hide password" : "Show password"}
                disabled={isSubmitting}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
            <p id="register-password-hint" className="auth-hint">
              Use at least {MIN_PASSWORD_LENGTH} characters.
            </p>
            {errors.password && (
              <p id="register-password-error" className="auth-error" role="alert">
                {errors.password}
              </p>
            )}
          </div>

          <div className="auth-field">
            <label htmlFor="register-confirmPassword">Confirm password</label>
            <div className="auth-password-wrapper">
              <input
                id="register-confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Re-enter your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={isSubmitting}
                aria-invalid={errors.confirmPassword ? "true" : "false"}
                aria-describedby={
                  errors.confirmPassword
                    ? "register-confirmPassword-error"
                    : undefined
                }
                className={errors.confirmPassword ? "has-error" : ""}
              />
              <button
                type="button"
                className="auth-toggle"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                aria-pressed={showConfirmPassword}
                aria-label={
                  showConfirmPassword
                    ? "Hide confirm password"
                    : "Show confirm password"
                }
                disabled={isSubmitting}
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
            {errors.confirmPassword && (
              <p
                id="register-confirmPassword-error"
                className="auth-error"
                role="alert"
              >
                {errors.confirmPassword}
              </p>
            )}
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
            style={{ opacity: isSubmitting ? 0.75 : 1, cursor: isSubmitting ? "wait" : "pointer" }}
          >
            {isSubmitting ? "Creating Account..." : "Register"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </main>
  );
}

export default Register;
