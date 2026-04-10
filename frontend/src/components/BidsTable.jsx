import { useState } from "react";

function buildPageNumbers(currentPage, totalPages) {
  const pages = new Set([1, totalPages, currentPage, currentPage - 1, currentPage + 1]);
  return [...pages].filter((page) => page >= 1 && page <= totalPages).sort((left, right) => left - right);
}

function getBidDraft(bid) {
  return {
    platform: bid.platform,
    profile: bid.profile,
    job_link: bid.job_link,
    connects: bid.connects,
    status: bid.status,
  };
}

function BidsTable({
  bids,
  loading,
  user,
  filters,
  onFilterChange,
  users,
  page,
  pageSize,
  totalCount,
  bidOptions,
  onUpdateBid,
  onDeleteBid,
  onPageChange,
  onPageSizeChange,
}) {
  const [editingBidId, setEditingBidId] = useState(null);
  const [draft, setDraft] = useState(null);
  const [savingBidId, setSavingBidId] = useState(null);
  const [deletingBidId, setDeletingBidId] = useState(null);
  const [actionError, setActionError] = useState("");
  const totalPages = Math.max(1, Math.ceil((totalCount || 0) / pageSize));
  const pageNumbers = buildPageNumbers(page, totalPages);
  const startItem = totalCount ? (page - 1) * pageSize + 1 : 0;
  const endItem = totalCount ? Math.min(page * pageSize, totalCount) : 0;

  const startEditing = (bid) => {
    setActionError("");
    setEditingBidId(bid.id);
    setDraft(getBidDraft(bid));
  };

  const cancelEditing = () => {
    setEditingBidId(null);
    setDraft(null);
    setActionError("");
  };

  const handleDraftChange = (event) => {
    const { name, value } = event.target;
    setDraft((current) => ({
      ...current,
      [name]: name === "connects" ? Number(value) : value,
    }));
  };

  const handleSave = async (bidId) => {
    setSavingBidId(bidId);
    setActionError("");
    try {
      await onUpdateBid(bidId, draft);
      cancelEditing();
    } catch (error) {
      setActionError("Unable to update bid. Please check the fields and try again.");
    } finally {
      setSavingBidId(null);
    }
  };

  const handleDelete = async (bidId) => {
    const confirmed = window.confirm("Delete this bid entry? This cannot be undone.");
    if (!confirmed) {
      return;
    }

    setDeletingBidId(bidId);
    setActionError("");
    try {
      await onDeleteBid(bidId);
      if (editingBidId === bidId) {
        cancelEditing();
      }
    } catch (error) {
      setActionError("Unable to delete bid. Please try again.");
    } finally {
      setDeletingBidId(null);
    }
  };

  return (
    <div className="premium-table-shell">
      {user.role === "admin" ? (
        <div className="bid-filters">
          <label>
            User
            <select name="user_id" value={filters.user_id} onChange={onFilterChange}>
              <option value="">All users</option>
              {users.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Platform
            <select name="platform" value={filters.platform} onChange={onFilterChange}>
              <option value="">All platforms</option>
              {bidOptions.platforms.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Status
            <select name="status" value={filters.status} onChange={onFilterChange}>
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="reply">Reply</option>
              <option value="call">Call</option>
              <option value="closed">Closed</option>
            </select>
          </label>
          <label>
            Start date
            <input type="date" name="start_date" value={filters.start_date} onChange={onFilterChange} />
          </label>
          <label>
            End date
            <input type="date" name="end_date" value={filters.end_date} onChange={onFilterChange} />
          </label>
        </div>
      ) : null}

      <div className="table-toolbar">
        <p className="muted">
          Showing {startItem}-{endItem} of {totalCount} bids
        </p>
        <label className="page-size-control">
          Page size
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </label>
      </div>

      {actionError ? <div className="error-panel">{actionError}</div> : null}

      {loading ? (
        <div className="table-skeleton">
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-line" />
          <div className="skeleton-line" />
          <div className="skeleton-line skeleton-short" />
        </div>
      ) : null}
      {!loading && !bids.length ? (
        <div className="empty-state">
          <strong>No bids found</strong>
          <p>Try widening your filters or add a fresh bid to start building your pipeline view.</p>
        </div>
      ) : null}

      {bids.length ? (
        <div className="table-wrap premium-table-wrap">
          <table className="premium-table">
            <thead>
              <tr>
                <th>Platform</th>
                <th>Profile</th>
                <th>Status</th>
                <th>Connects</th>
                <th>User</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((bid, index) => {
                const isEditing = editingBidId === bid.id;
                return (
                  <tr key={bid.id} className={index % 2 ? "zebra-row" : ""}>
                    <td>
                      {isEditing ? (
                        <select className="table-input" name="platform" value={draft.platform} onChange={handleDraftChange}>
                          {bidOptions.platforms.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.name}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className="pill">{bidOptions.platforms.find((option) => option.value === bid.platform)?.name || bid.platform}</span>
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <select className="table-input" name="profile" value={draft.profile} onChange={handleDraftChange}>
                          {bidOptions.profiles.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.name}
                            </option>
                          ))}
                        </select>
                      ) : (
                        bidOptions.profiles.find((option) => option.value === bid.profile)?.name || bid.profile
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <select className="table-input" name="status" value={draft.status} onChange={handleDraftChange}>
                          <option value="pending">Pending</option>
                          <option value="reply">Reply</option>
                          <option value="call">Call</option>
                          <option value="closed">Closed</option>
                        </select>
                      ) : (
                        <span className={`status-chip status-${bid.status}`}>{bid.status}</span>
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <input className="table-input compact-table-input" name="connects" type="number" min="0" value={draft.connects} onChange={handleDraftChange} />
                      ) : (
                        bid.connects
                      )}
                    </td>
                    <td>{bid.user_name || "-"}</td>
                    <td>{new Date(bid.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="table-actions">
                        {isEditing ? (
                          <>
                            <button type="button" className="mini-button" onClick={() => handleSave(bid.id)} disabled={savingBidId === bid.id}>
                              {savingBidId === bid.id ? "Saving" : "Save"}
                            </button>
                            <button type="button" className="mini-button secondary-button" onClick={cancelEditing}>
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button type="button" className="mini-button secondary-button" onClick={() => startEditing(bid)}>
                              Edit
                            </button>
                            <button type="button" className="mini-button danger-button" onClick={() => handleDelete(bid.id)} disabled={deletingBidId === bid.id}>
                              {deletingBidId === bid.id ? "Deleting" : "Delete"}
                            </button>
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

      <div className="pagination-bar">
        <div className="pagination-actions">
          <button type="button" className="pager-button secondary-button" onClick={() => onPageChange(1)} disabled={page === 1}>
            First
          </button>
          <button type="button" className="pager-button secondary-button" onClick={() => onPageChange(page - 1)} disabled={page === 1}>
            Previous
          </button>
        </div>

        <div className="page-number-list">
          {pageNumbers.map((pageNumber) => (
            <button
              type="button"
              key={pageNumber}
              className={`page-number ${pageNumber === page ? "active" : ""}`}
              onClick={() => onPageChange(pageNumber)}
            >
              {pageNumber}
            </button>
          ))}
        </div>

        <div className="pagination-actions">
          <label className="jump-input">
            Jump to
            <input
              type="number"
              min="1"
              max={totalPages}
              defaultValue={page}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  const nextPage = Number(event.currentTarget.value);
                  if (nextPage >= 1 && nextPage <= totalPages) {
                    onPageChange(nextPage);
                  }
                }
              }}
            />
          </label>
          <button type="button" className="pager-button secondary-button" onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}>
            Next
          </button>
          <button type="button" className="pager-button secondary-button" onClick={() => onPageChange(totalPages)} disabled={page >= totalPages}>
            Last
          </button>
        </div>
      </div>
    </div>
  );
}

export default BidsTable;
