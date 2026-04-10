import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "../api";

function toDateInputValue(date) {
  const timezoneOffset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - timezoneOffset).toISOString().slice(0, 10);
}

function getInitialFilters() {
  const today = toDateInputValue(new Date());

  return {
    user_id: "",
    start_date: today,
    end_date: today,
    group_by: "day",
  };
}

const emptySummary = {
  total_bids: 0,
  total_connects: 0,
  replies: 0,
  calls: 0,
  closed: 0,
};

const REPORT_PAGE_SIZES = [10, 20, 50];

function buildPageNumbers(currentPage, totalPages) {
  const pages = new Set([1, totalPages, currentPage, currentPage - 1, currentPage + 1]);
  return [...pages].filter((page) => page >= 1 && page <= totalPages).sort((left, right) => left - right);
}

function AdminReport() {
  const [filters, setFilters] = useState(getInitialFilters);
  const [users, setUsers] = useState([]);
  const [report, setReport] = useState({ summary: emptySummary, data: [], user: null, filters: getInitialFilters() });
  const [tablePage, setTablePage] = useState(1);
  const [tablePageSize, setTablePageSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.user_id) {
      params.append("user_id", filters.user_id);
    }
    if (filters.start_date) {
      params.append("start_date", filters.start_date);
    }
    if (filters.end_date) {
      params.append("end_date", filters.end_date);
    }
    params.append("group_by", filters.group_by);
    return params;
  }, [filters]);

  const loadUsers = async () => {
    const { data } = await api.get("/users/");
    setUsers(data);
  };

  const loadReport = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get(`/admin/report/?${queryParams.toString()}`);
      setReport(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load admin report.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const todayFilters = getInitialFilters();
    setFilters(todayFilters);
    setReport((current) => ({ ...current, filters: todayFilters }));
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await loadUsers();
        await loadReport();
      } catch (requestError) {
        setError("Unable to initialize reporting tools.");
        setLoading(false);
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    if (!users.length && filters.user_id) {
      return;
    }
    loadReport();
  }, [queryParams]);

  useEffect(() => {
    setTablePage(1);
  }, [report.data.length, filters.user_id, filters.start_date, filters.end_date, filters.group_by]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  };

  const totalRows = report.data?.length ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalRows / tablePageSize));
  const currentPage = Math.min(tablePage, totalPages);
  const startIndex = totalRows ? (currentPage - 1) * tablePageSize : 0;
  const endIndex = Math.min(startIndex + tablePageSize, totalRows);
  const visibleRows = report.data.slice(startIndex, endIndex);
  const pageNumbers = buildPageNumbers(currentPage, totalPages);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const response = await api.get(`/admin/report/pdf/?${queryParams.toString()}`, {
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "sales-crm-report.pdf";
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      setError("Unable to download PDF report.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <section className="panel admin-report-panel">
      <div className="panel-heading report-header">
        <div>
          <p className="eyebrow">Analytics</p>
          <h2>Admin Reporting</h2>
          <p className="muted">Analyze any team member or all users across daily, weekly, and monthly performance windows.</p>
        </div>
        <button onClick={handleDownload} disabled={downloading}>
          {downloading ? "Preparing PDF..." : "Download PDF"}
        </button>
      </div>

      <div className="report-filters">
        <label>
          User
          <select name="user_id" value={filters.user_id} onChange={handleChange}>
            <option value="">All users</option>
            {users.map((reportUser) => (
              <option value={reportUser.id} key={reportUser.id}>
                {reportUser.name} ({reportUser.email})
              </option>
            ))}
          </select>
        </label>
        <label>
          Start date
          <input type="date" name="start_date" value={filters.start_date} onChange={handleChange} />
        </label>
        <label>
          End date
          <input type="date" name="end_date" value={filters.end_date} onChange={handleChange} />
        </label>
        <label>
          Group by
          <select name="group_by" value={filters.group_by} onChange={handleChange}>
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
        </label>
      </div>

      {error ? <div className="error-panel">{error}</div> : null}

      <div className="kpi-grid report-kpi-grid">
        {[
          ["Total Bids", report.summary?.total_bids ?? 0],
          ["Total Connects", report.summary?.total_connects ?? 0],
          ["Replies", report.summary?.replies ?? 0],
          ["Calls", report.summary?.calls ?? 0],
          ["Closed", report.summary?.closed ?? 0],
        ].map(([label, value]) => (
          <article className="panel kpi-card report-card" key={label}>
            <p className="muted">{label}</p>
            {loading ? <div className="skeleton-line skeleton-value" /> : <h2>{value}</h2>}
          </article>
        ))}
      </div>

      <div className="report-chart-grid">
        <div className="panel chart-panel">
          <div className="panel-heading">
            <h3>Bids Over Time</h3>
            <p className="muted">Selected user: {report.user?.name || "All users"}</p>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={report.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="period" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="total_bids" stroke="#2563eb" strokeWidth={3} name="Bids" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel chart-panel">
          <div className="panel-heading">
            <h3>Outcome Mix</h3>
            <p className="muted">Connect consumption against replies and closures by period.</p>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={report.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="period" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_connects" fill="#0f766e" name="Connects" />
                <Bar dataKey="replies" fill="#f97316" name="Replies" />
                <Bar dataKey="closed" fill="#7c3aed" name="Closed" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="panel report-table-panel">
        <div className="panel-heading">
          <h3>Report Table</h3>
          <p className="muted">Period-level analytics for export-ready review.</p>
        </div>
        <div className="premium-table-shell">
          <div className="table-toolbar">
            <p className="muted">
              Showing {totalRows ? startIndex + 1 : 0}-{totalRows ? endIndex : 0} of {totalRows} periods
            </p>
            <label className="page-size-control">
              Page size
              <select value={tablePageSize} onChange={(event) => {
                setTablePageSize(Number(event.target.value));
                setTablePage(1);
              }}>
                {REPORT_PAGE_SIZES.map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="table-wrap premium-table-wrap">
            <table className="premium-table">
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Bids</th>
                  <th>Connects</th>
                  <th>Replies</th>
                  <th>Calls</th>
                  <th>Closed</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.length ? (
                  visibleRows.map((row, index) => (
                    <tr key={row.period} className={index % 2 ? "zebra-row" : ""}>
                      <td>{row.period}</td>
                      <td>{row.total_bids}</td>
                      <td>{row.total_connects}</td>
                      <td>{row.replies}</td>
                      <td>{row.calls}</td>
                      <td>{row.closed}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6">{loading ? "Loading report..." : "No report data for the selected filters."}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pagination-bar">
            <div className="pagination-actions">
              <button
                type="button"
                className="pager-button secondary-button"
                onClick={() => setTablePage(1)}
                disabled={currentPage === 1}
              >
                First
              </button>
              <button
                type="button"
                className="pager-button secondary-button"
                onClick={() => setTablePage((page) => Math.max(1, page - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
            </div>

            <div className="page-number-list">
              {pageNumbers.map((pageNumber) => (
                <button
                  type="button"
                  key={pageNumber}
                  className={`page-number ${pageNumber === currentPage ? "active" : ""}`}
                  onClick={() => setTablePage(pageNumber)}
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
                  defaultValue={currentPage}
                  onKeyDown={(event) => {
                    if (event.key !== "Enter") {
                      return;
                    }
                    const nextPage = Number(event.currentTarget.value);
                    if (nextPage >= 1 && nextPage <= totalPages) {
                      setTablePage(nextPage);
                    }
                  }}
                />
              </label>
              <button
                type="button"
                className="pager-button secondary-button"
                onClick={() => setTablePage((page) => Math.min(totalPages, page + 1))}
                disabled={currentPage >= totalPages}
              >
                Next
              </button>
              <button
                type="button"
                className="pager-button secondary-button"
                onClick={() => setTablePage(totalPages)}
                disabled={currentPage >= totalPages}
              >
                Last
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default AdminReport;
