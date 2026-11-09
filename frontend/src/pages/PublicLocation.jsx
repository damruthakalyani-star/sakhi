import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/Location.css";

function PublicLocation() {
  const { shareToken } = useParams();
  const [status, setStatus] = useState("loading");
  const [share, setShare] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadShare() {
      try {
        const data = await api.get(`/location/shared/${shareToken}`);
        if (!mounted) return;
        setShare(data);
        setStatus("success");
      } catch (err) {
        if (!mounted) return;
        setError(
          err.message ||
            "This location link is invalid, expired, or has been stopped."
        );
        setStatus("error");
      }
    }

    loadShare();
    const timer = setInterval(loadShare, 30000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, [shareToken]);

  const mapUrl = share
    ? `https://www.openstreetmap.org/?mlat=${share.latitude}&mlon=${share.longitude}#map=17/${share.latitude}/${share.longitude}`
    : "";

  return (
    <div className="loc-page">
      <header className="loc-topbar">
        <div className="loc-brand">
          <span className="loc-brand-icon">S</span>
          <span className="loc-brand-name">SAKHISAHAY</span>
        </div>
        <Link to="/" className="loc-back-link">
          Home
        </Link>
      </header>

      <main className="loc-main">
        <section className="loc-hero">
          <h1 className="loc-title">Shared Live Location</h1>
          <p className="loc-subtitle">
            This secure link shows the latest location shared with you by a
            SAKHISAHAY user. It refreshes automatically every 30 seconds.
          </p>
        </section>

        <section className="loc-card loc-result-card" aria-live="polite">
          {status === "loading" && (
            <div className="loc-placeholder">
              <p>Loading shared location...</p>
            </div>
          )}

          {status === "error" && (
            <div className="loc-alert" role="alert">
              <div>
                <h3>Location link unavailable</h3>
                <p>{error}</p>
              </div>
            </div>
          )}

          {status === "success" && share && (
            <>
              <h2 className="loc-card-title">{share.user_name}'s location</h2>
              <dl className="loc-coords">
                <div className="loc-coord">
                  <dt>Latitude</dt>
                  <dd>{share.latitude.toFixed(6)}</dd>
                </div>
                <div className="loc-coord">
                  <dt>Longitude</dt>
                  <dd>{share.longitude.toFixed(6)}</dd>
                </div>
              </dl>
              {typeof share.accuracy === "number" && (
                <p className="loc-accuracy">
                  Accurate to within about {Math.round(share.accuracy)} metres.
                </p>
              )}
              <p className="loc-accuracy">
                Last updated {new Date(share.updated_at).toLocaleString()}.
                Expires {new Date(share.expires_at).toLocaleString()}.
              </p>
              <div className="loc-result-actions">
                <a
                  href={mapUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="loc-btn loc-btn-primary"
                >
                  Open in Map
                </a>
                <a href="tel:112" className="loc-btn loc-btn-outline">
                  Call 112
                </a>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default PublicLocation;
