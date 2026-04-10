import { useEffect, useState } from "react";

import { api } from "../api";

const emptyForm = {
  client_name: "",
  current_status: "",
  chat_room_link: "",
  profile: "",
};

function getDraft(lead) {
  return {
    client_name: lead.client_name,
    current_status: lead.current_status,
    chat_room_link: lead.chat_room_link || "",
    profile: lead.profile || "",
  };
}

function LeadStatusReport({ bidOptions }) {
  const [leads, setLeads] = useState([]);
  const [formData, setFormData] = useState(emptyForm);
  const [editingLeadId, setEditingLeadId] = useState(null);
  const [draft, setDraft] = useState(null);
  const [includeArchived, setIncludeArchived] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const profiles = bidOptions.profiles || [];

  const loadLeads = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get(`/leads/status/?include_archived=${includeArchived}`);
      setLeads(data);
    } catch (requestError) {
      setError("Unable to load lead status report.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, [includeArchived]);

  useEffect(() => {
    setFormData((current) => ({
      ...current,
      profile: current.profile || profiles[0]?.value || "",
    }));
  }, [profiles]);

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleDraftChange = (event) => {
    const { name, value } = event.target;
    setDraft((current) => ({ ...current, [name]: value }));
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/leads/status/", formData);
      setFormData({ ...emptyForm, profile: profiles[0]?.value || "" });
      await loadLeads();
    } catch (requestError) {
      setError("Unable to create lead status. Please check the form.");
    } finally {
      setSaving(false);
    }
  };

  const startEditing = (lead) => {
    setEditingLeadId(lead.id);
    setDraft(getDraft(lead));
    setError("");
  };

  const cancelEditing = () => {
    setEditingLeadId(null);
    setDraft(null);
  };

  const handleSave = async (leadId) => {
    setSaving(true);
    setError("");
    try {
      await api.patch(`/leads/status/${leadId}/`, draft);
      cancelEditing();
      await loadLeads();
    } catch (requestError) {
      setError("Unable to update lead status. Please check the row.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (leadId) => {
    const confirmed = window.confirm("Delete this lead status row? This cannot be undone.");
    if (!confirmed) {
      return;
    }
    setSaving(true);
    setError("");
    try {
      await api.delete(`/leads/status/${leadId}/`);
      await loadLeads();
    } catch (requestError) {
      setError("Unable to delete lead status.");
    } finally {
      setSaving(false);
    }
  };

  const handleArchiveToggle = async (lead) => {
    setSaving(true);
    setError("");
    try {
      const action = lead.is_archived ? "unarchive" : "archive";
      await api.patch(`/leads/status/${lead.id}/${action}/`);
      await loadLeads();
    } catch (requestError) {
      setError("Unable to update archive status.");
    } finally {
      setSaving(false);
    }
  };

  const hasProfiles = Boolean(profiles.length);

  return (
    <section className="panel lead-report-panel">
      <div className="panel-heading report-header">
        <div>
          <p className="eyebrow">Shared tracker</p>
          <h2>Lead Status Report</h2>
          <p className="muted">Every team member can update the sheet. Lead Check always shows the last person who edited that lead.</p>
        </div>
        <label className="archive-toggle">
          <input type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} />
          Show archived
        </label>
      </div>

      {error ? <div className="error-panel">{error}</div> : null}

      <form className="lead-status-form" onSubmit={handleCreate}>
        <label>
          Client Name
          <input name="client_name" value={formData.client_name} onChange={handleFormChange} required />
        </label>
        <label>
          Current Status
          <input name="current_status" value={formData.current_status} onChange={handleFormChange} required />
        </label>
        <label>
          Chat Room Link
          <input name="chat_room_link" type="url" value={formData.chat_room_link} onChange={handleFormChange} />
        </label>
        <label>
          Profile
          <select name="profile" value={formData.profile} onChange={handleFormChange} disabled={!hasProfiles}>
            {profiles.map((profile) => (
              <option key={profile.value} value={profile.value}>
                {profile.name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={saving || !hasProfiles}>{saving ? "Saving..." : "Add Lead"}</button>
      </form>

      {!hasProfiles ? <p className="error-text">Ask an admin to add at least one active bid profile first.</p> : null}

      {loading ? (
        <div className="table-skeleton">
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-line" />
          <div className="skeleton-line skeleton-short" />
        </div>
      ) : null}

      {!loading && !leads.length ? (
        <div className="empty-state">
          <strong>No lead status rows yet</strong>
          <p>Add your first lead to begin tracking shared follow-up ownership.</p>
        </div>
      ) : null}

      {leads.length ? (
        <div className="table-wrap premium-table-wrap lead-table-wrap">
          <table className="premium-table lead-status-table">
            <thead>
              <tr>
                <th>Last Updated</th>
                <th>Client Name</th>
                <th>Current Status of the Project</th>
                <th>Lead Check</th>
                <th>Chat Room Link</th>
                <th>Profile</th>
                <th>Archive</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead, index) => {
                const isEditing = editingLeadId === lead.id;
                return (
                  <tr key={lead.id} className={`${index % 2 ? "zebra-row" : ""} ${lead.is_archived ? "archived-row" : ""}`}>
                    <td>{new Date(lead.last_updated).toLocaleString()}</td>
                    <td>
                      {isEditing ? (
                        <input className="table-input" name="client_name" value={draft.client_name} onChange={handleDraftChange} />
                      ) : (
                        lead.client_name
                      )}
                    </td>
                    <td className="lead-status-cell">
                      {isEditing ? (
                        <textarea className="table-input lead-status-input" name="current_status" value={draft.current_status} onChange={handleDraftChange} />
                      ) : (
                        lead.current_status
                      )}
                    </td>
                    <td><span className="pill">{lead.lead_check || "-"}</span></td>
                    <td>
                      {isEditing ? (
                        <input className="table-input" name="chat_room_link" value={draft.chat_room_link} onChange={handleDraftChange} />
                      ) : lead.chat_room_link ? (
                        <a href={lead.chat_room_link} target="_blank" rel="noreferrer">Open chat</a>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <select className="table-input" name="profile" value={draft.profile} onChange={handleDraftChange}>
                          {profiles.map((profile) => (
                            <option key={profile.value} value={profile.value}>
                              {profile.name}
                            </option>
                          ))}
                        </select>
                      ) : (
                        profiles.find((profile) => profile.value === lead.profile)?.name || lead.profile || "-"
                      )}
                    </td>
                    <td>
                      <span className={`status-chip ${lead.is_archived ? "status-pending" : "status-closed"}`}>
                        {lead.is_archived ? "Archived" : "Active"}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions">
                        {isEditing ? (
                          <>
                            <button type="button" className="mini-button" onClick={() => handleSave(lead.id)} disabled={saving}>Save</button>
                            <button type="button" className="mini-button secondary-button" onClick={cancelEditing}>Cancel</button>
                          </>
                        ) : (
                          <>
                            <button type="button" className="mini-button secondary-button" onClick={() => startEditing(lead)}>Edit</button>
                            <button type="button" className="mini-button secondary-button" onClick={() => handleArchiveToggle(lead)}>
                              {lead.is_archived ? "Unarchive" : "Archive"}
                            </button>
                            <button type="button" className="mini-button danger-button" onClick={() => handleDelete(lead.id)}>Delete</button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

export default LeadStatusReport;
