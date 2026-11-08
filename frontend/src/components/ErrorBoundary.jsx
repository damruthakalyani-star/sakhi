import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an unhandled error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          background: "linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%)",
          textAlign: "center",
          fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
          <div style={{
            background: "#ffffff",
            padding: "2.5rem",
            borderRadius: "16px",
            boxShadow: "0 10px 25px rgba(233, 30, 99, 0.15)",
            maxWidth: "480px",
            width: "100%"
          }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🛡️</div>
            <h2 style={{ color: "#880E4F", marginBottom: "0.75rem", fontSize: "1.5rem" }}>
              Something went wrong
            </h2>
            <p style={{ color: "#666", marginBottom: "1.5rem", fontSize: "0.95rem", lineHeight: 1.5 }}>
              We encountered an unexpected issue, but your safety is our priority.
              Please reload or return to the main dashboard.
            </p>
            <button
              onClick={this.handleReset}
              style={{
                backgroundColor: "#E91E63",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                padding: "0.75rem 1.75rem",
                fontSize: "1rem",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: "0 4px 12px rgba(233, 30, 99, 0.3)",
                transition: "background-color 0.2s"
              }}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "#C2185B")}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "#E91E63")}
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
