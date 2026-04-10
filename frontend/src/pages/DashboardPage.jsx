import { useEffect, useState } from "react";

import { api } from "../api";
import AdminReport from "../components/AdminReport";
import BidForm from "../components/BidForm";
import KPISection from "../components/KPISection";
import BidsTable from "../components/BidsTable";
import ChatModule from "../chat/ChatModule";
import LeadStatusReport from "../components/LeadStatusReport";

const emptyBidOptions = {
  platforms: [],
  profiles: [],
};

const BASE_NAV_ITEMS = [
  { id: "overview", label: "Dashboard", icon: "DB" },
  { id: "bids", label: "Bids", icon: "BD" },
  { id: "leads", label: "Leads", icon: "LD" },
  { id: "chat", label: "Chat", icon: "CH" },
];

function DashboardPage({ user, onLogout, theme, onToggleTheme }) {
  const [kpi, setKpi] = useState(null);
  const [bids, setBids] = useState([]);
  const [bidUsers, setBidUsers] = useState([]);
  const [bidOptions, setBidOptions] = useState(emptyBidOptions);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    user_id: "",
    platform: "",
    status: "",
    start_date: "",
    end_date: "",
  });
  const [workspaceQuery, setWorkspaceQuery] = useState("");
  const [activeSection, setActiveSection] = useState("overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });

      const requests = [api.get("/kpi/"), api.get(`/bids/my/?${params.toString()}`), api.get("/bid-options/")];
      if (user.role === "admin") {
        requests.push(api.get("/users/"));
      }

      const responses = await Promise.all(requests);
      const kpiData = responses[0].data;
      const bidsData = responses[1].data;
      const bidOptionsData = responses[2].data;
      setKpi(kpiData);
      setBids(bidsData.results || []);
      setTotalCount(bidsData.count || 0);
      setBidOptions({
        platforms: bidOptionsData.platforms || [],
        profiles: bidOptionsData.profiles || [],
      });
      if (user.role === "admin") {
        setBidUsers(responses[3].data);
      }
    } catch (requestError) {
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [page, pageSize, user.role, filters.user_id, filters.platform, filters.status, filters.start_date, filters.end_date]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setPage(1);
    setFilters((current) => ({ ...current, [name]: value }));
  };

  const handleUpdateBid = async (bidId, payload) => {
    await api.patch(`/bids/${bidId}/`, payload);
    await loadDashboard();
  };

  const handleDeleteBid = async (bidId) => {
    await api.delete(`/bids/${bidId}/`);
    await loadDashboard();
  };

  const navItems = user.role === "admin" ? [...BASE_NAV_ITEMS.slice(0, 3), { id: "reports", label: "Reports", icon: "RP" }, BASE_NAV_ITEMS[3]] : BASE_NAV_ITEMS;

  const handleNavigate = (sectionId) => {
    setActiveSection(sectionId);
    document.getElementById(`section-${sectionId}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleSearchKeyDown = (event) => {
    if (event.key !== "Enter") {
      return;
    }

    const match = navItems.find((item) => item.label.toLowerCase().includes(workspaceQuery.trim().toLowerCase()));
    if (match) {
      handleNavigate(match.id);
    }
  };

  const openPipelineCount = Math.max(
    0,
    (kpi?.total_bids ?? 0) - (kpi?.replies ?? 0) - (kpi?.calls ?? 0) - (kpi?.closed ?? 0),
  );

  return (
    <div className={`workspace-shell ${sidebarCollapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="workspace-sidebar">
        <div className="sidebar-brand-row">
          <div className="sidebar-brand">
            <img src="/sales-crm.png" alt="Sales CRM" className="brand-logo sidebar-logo" />
            <div className="sidebar-brand-copy">
              <strong>Sales CRM</strong>
              <span>{user.role === "admin" ? "Control center" : "Team workspace"}</span>
            </div>
          </div>
          <button
            type="button"
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed((current) => !current)}
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? ">" : "<"}
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              type="button"
              key={item.id}
              className={`sidebar-link ${activeSection === item.id ? "active" : ""}`}
              onClick={() => handleNavigate(item.id)}
              title={item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-card">
          <span className="surface-tag">Live pipeline</span>
          <strong>{openPipelineCount}</strong>
          <p>Open opportunities still in motion across your current reporting view.</p>
        </div>
      </aside>

      <div className="workspace-main">
        <header className="topbar">
          <div className="topbar-search">
            <input
              type="search"
              placeholder="Search sections like Dashboard, Bids, Leads, Reports, or Chat"
              value={workspaceQuery}
              onChange={(event) => setWorkspaceQuery(event.target.value)}
              onKeyDown={handleSearchKeyDown}
            />
          </div>

          <div className="topbar-actions">
            <div className="notification-chip">
              <span className="notification-dot" />
              Replies {kpi?.replies ?? 0}
            </div>
            <button type="button" className="ghost-button" onClick={onToggleTheme}>
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <div className="profile-pill">
              <img src="/sales-crm.png" alt="Sales CRM" className="brand-logo profile-mark" />
              <div>
                <strong>{user.name}</strong>
                <span>{user.role}</span>
              </div>
            </div>
            <button className="secondary-button" onClick={onLogout}>Logout</button>
          </div>
        </header>

        <main className="dashboard-shell">
          <section className="hero-strip" id="section-overview">
            <div>
              <p className="eyebrow">Workspace overview</p>
              <h1>Operate your sales pipeline with clarity.</h1>
              <p className="muted">
                Monitor performance, add bids, review analytics, and collaborate in real time from one premium workspace.
              </p>
            </div>
            <div className="hero-metrics">
              <article className="hero-metric-card">
                <span>Open pipeline</span>
                <strong>{loading ? "..." : openPipelineCount}</strong>
              </article>
              <article className="hero-metric-card">
                <span>Total tracked bids</span>
                <strong>{loading ? "..." : totalCount}</strong>
              </article>
            </div>
          </section>

          {error ? <div className="panel error-panel">{error}</div> : null}

          <section className="dashboard-section" id="section-dashboard">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Performance</p>
                <h2>Dashboard snapshot</h2>
              </div>
            </div>
            <KPISection kpi={kpi} loading={loading} />
          </section>

          <section className="dashboard-grid" id="section-bids">
            <div className="panel form-panel">
              <div className="panel-heading">
                <p className="eyebrow">Capture activity</p>
                <h2>Add Bid</h2>
                <p className="muted">Track each proposal with platform, profile, connects, and status.</p>
              </div>
              <BidForm onCreated={loadDashboard} bidOptions={bidOptions} />
            </div>
            <div className="panel">
              <div className="panel-heading">
                <p className="eyebrow">Pipeline log</p>
                <h2>Bid Activity</h2>
                <p className="muted">
                  {user.role === "admin" ? "Admin view shows all bids." : "Team members see only their own bids."}
                </p>
              </div>
              <BidsTable
                bids={bids}
                loading={loading}
                user={user}
                filters={filters}
                onFilterChange={handleFilterChange}
                users={bidUsers}
                page={page}
                pageSize={pageSize}
                totalCount={totalCount}
                bidOptions={bidOptions}
                onUpdateBid={handleUpdateBid}
                onDeleteBid={handleDeleteBid}
                onPageChange={setPage}
                onPageSizeChange={(nextSize) => {
                  setPage(1);
                  setPageSize(nextSize);
                }}
              />
            </div>
          </section>

          {user.role === "admin" ? (
            <section className="dashboard-section" id="section-reports">
              <AdminReport />
            </section>
          ) : null}

          <section className="dashboard-section" id="section-leads">
            <LeadStatusReport bidOptions={bidOptions} />
          </section>

          <section className="dashboard-section" id="section-chat">
            <ChatModule user={user} />
          </section>
        </main>
      </div>
    </div>
  );
}

export default DashboardPage;
