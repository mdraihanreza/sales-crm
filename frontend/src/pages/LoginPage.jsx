import { useState } from "react";

import { api } from "../api";

function LoginPage({ onLogin, theme, onToggleTheme }) {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const { data } = await api.post("/login/", formData);
      onLogin(data.access, data.user);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Login failed. Please check your credentials.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app-shell auth-shell">
      <div className="auth-layout">
        <section className="auth-showcase panel">
          <div className="auth-topbar">
            <span className="surface-tag">Premium CRM Workspace</span>
            <button type="button" className="ghost-button" onClick={onToggleTheme}>
              {theme === "dark" ? "Light mode" : "Dark mode"}
            </button>
          </div>
          <div className="auth-brand-lockup">
            <img src="/sales-crm.png" alt="Sales CRM" className="brand-logo auth-brand-logo" />
            <div>
              <p className="eyebrow">Sales CRM</p>
              <h1>Pipeline visibility for teams who live on bids, connects, and follow-ups.</h1>
              <p className="muted">
                A refined workspace for revenue ops, sales teams, and admins who need instant reporting and internal collaboration.
              </p>
            </div>
          </div>
          <div className="auth-feature-grid">
            <article className="feature-card">
              <strong>Performance snapshots</strong>
              <span>Track bids, replies, calls, and closed deals from one surface.</span>
            </article>
            <article className="feature-card">
              <strong>Live collaboration</strong>
              <span>Stay synced with room-based chat, mentions, and unread alerts.</span>
            </article>
            <article className="feature-card">
              <strong>Admin clarity</strong>
              <span>Review export-ready reporting with filters, charts, and PDF output.</span>
            </article>
          </div>
        </section>

        <div className="auth-card">
          <div className="brand-hero">
            <img src="/sales-crm.png" alt="Sales CRM" className="brand-logo auth-brand-logo auth-brand-mark" />
          </div>
          <div>
            <p className="eyebrow">Secure access</p>
            <h2>Sign in to your workspace</h2>
            <p className="muted">JWT-protected access for admins and delivery teams.</p>
          </div>
          <form onSubmit={handleSubmit} className="form-grid">
            <label>
              Email
              <input type="email" name="email" value={formData.email} onChange={handleChange} required />
            </label>
            <label>
              Password
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </label>
            {error ? <p className="error-text">{error}</p> : null}
            <button type="submit" disabled={submitting}>
              {submitting ? "Signing in..." : "Enter workspace"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
