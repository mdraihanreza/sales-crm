const cards = [
  { key: "total_bids", label: "Total Bids", icon: "TB", tone: "blue", note: "All tracked outreach" },
  { key: "total_connects", label: "Connects Used", icon: "CN", tone: "cyan", note: "Spend across bids" },
  { key: "replies", label: "Replies", icon: "RE", tone: "green", note: "Positive responses" },
  { key: "calls", label: "Calls", icon: "CL", tone: "amber", note: "Qualified conversations" },
  { key: "closed", label: "Closed", icon: "WD", tone: "violet", note: "Won outcomes" },
];

function KPISection({ kpi, loading }) {
  return (
    <section className="kpi-grid">
      {cards.map((card) => (
        <article className={`panel kpi-card kpi-${card.tone}`} key={card.key}>
          <div className="kpi-card-top">
            <span className="metric-icon">{card.icon}</span>
            <span className="muted">{card.label}</span>
          </div>
          {loading || !kpi ? <div className="skeleton-line skeleton-value" /> : <h2>{kpi[card.key]}</h2>}
          <p className="kpi-note">{card.note}</p>
        </article>
      ))}
    </section>
  );
}

export default KPISection;
