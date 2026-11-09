import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Auth.css";

export default function NotFound() {
  const { isAuthenticated } = useAuth();

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        textAlign: "center",
        backgroundColor: "#FAF7FA",
      }}
    >
      <div
        style={{
          maxWidth: "480px",
          backgroundColor: "#fff",
          padding: "3rem 2rem",
          borderRadius: "16px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
          border: "1px solid #FFE4E1",
        }}
      >
        <span
          style={{
            display: "inline-block",
            fontSize: "3.5rem",
            marginBottom: "1rem",
          }}
        >
          🌸
        </span>
        <h1 style={{ color: "#880E4F", fontSize: "2rem", marginBottom: "0.5rem" }}>
          404 - Page Not Found
        </h1>
        <p style={{ color: "#666", fontSize: "1rem", lineHeight: 1.6, marginBottom: "2rem" }}>
          The page you are looking for does not exist or may have moved. If you are in danger or need immediate help, dial <strong>112</strong>.
        </p>
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
          <Link
            to={isAuthenticated ? "/dashboard" : "/"}
            style={{
              backgroundColor: "#E91E63",
              color: "#fff",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            {isAuthenticated ? "Go to Dashboard" : "Return Home"}
          </Link>
          <a
            href="tel:112"
            style={{
              backgroundColor: "#D32F2F",
              color: "#fff",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            Emergency 112
          </a>
        </div>
      </div>
    </div>
  );
}
