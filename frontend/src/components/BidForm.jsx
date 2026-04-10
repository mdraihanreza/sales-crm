import { useEffect, useState } from "react";

import { api } from "../api";

const initialState = {
  platform: "upwork",
  profile: "Profile1",
  job_link: "",
  connects: 0,
  status: "pending",
};

function BidForm({ onCreated, bidOptions }) {
  const [formData, setFormData] = useState(initialState);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const hasBidOptions = Boolean(bidOptions.platforms.length && bidOptions.profiles.length);

  useEffect(() => {
    const firstPlatform = bidOptions.platforms[0]?.value;
    const firstProfile = bidOptions.profiles[0]?.value;

    setFormData((current) => ({
      ...current,
      platform: firstPlatform || current.platform,
      profile: firstProfile || current.profile,
    }));
  }, [bidOptions]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: name === "connects" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage("");
    try {
      await api.post("/bids/", formData);
      setFormData({
        ...initialState,
        platform: bidOptions.platforms[0]?.value || initialState.platform,
        profile: bidOptions.profiles[0]?.value || initialState.profile,
      });
      setMessage("Bid saved successfully.");
      onCreated();
    } catch (error) {
      setMessage("Unable to save bid.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-grid">
      <label>
        Platform
        <select name="platform" value={formData.platform} onChange={handleChange} disabled={!bidOptions.platforms.length}>
          {bidOptions.platforms.map((option) => (
            <option key={option.value} value={option.value}>
              {option.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Profile
        <select name="profile" value={formData.profile} onChange={handleChange} disabled={!bidOptions.profiles.length}>
          {bidOptions.profiles.map((option) => (
            <option key={option.value} value={option.value}>
              {option.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Job Link
        <input name="job_link" type="url" value={formData.job_link} onChange={handleChange} required />
      </label>
      <label>
        Connects
        <input name="connects" type="number" min="0" value={formData.connects} onChange={handleChange} required />
      </label>
      <label>
        Status
        <select name="status" value={formData.status} onChange={handleChange}>
          <option value="pending">Pending</option>
          <option value="reply">Reply</option>
          <option value="call">Call</option>
          <option value="closed">Closed</option>
        </select>
      </label>
      {!hasBidOptions ? <p className="error-text">Ask an admin to add at least one active platform and profile.</p> : null}
      {message ? <p className={`form-message ${message.includes("Unable") ? "error-text" : "success-text"}`}>{message}</p> : null}
      <button type="submit" disabled={submitting || !hasBidOptions}>
        {submitting ? "Saving..." : "Add Bid"}
      </button>
    </form>
  );
}

export default BidForm;
