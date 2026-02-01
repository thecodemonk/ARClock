import { usePropagation } from "../../hooks/usePropagation";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";

const STATUS_COLORS: Record<string, string> = {
  GOOD: "var(--accent-green)",
  FAIR: "var(--accent-yellow)",
  POOR: "var(--kp-high)",
  CLOSED: "var(--text-muted)",
};

export default function PropagationPanel() {
  const { data, isLoading, isError } = usePropagation();
  const d = data as any;

  const title =
    d?.mode === "path" ? "HF Propagation (DE\u2192DX)" : "HF Propagation";

  return (
    <WidgetCard title={title}>
      {isLoading && <div className="loading-text">Computing...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div
            className="weather-value"
            style={{ color: "var(--accent-amber)" }}
          >
            {d.muf?.toFixed(1)}{" "}
            <span style={{ fontSize: 12 }}>MHz MUF</span>
          </div>
          <div className="prop-band-grid">
            {d.bands?.map((b: any) => (
              <div
                key={b.band}
                className="prop-badge"
                style={{
                  borderColor: STATUS_COLORS[b.status] || STATUS_COLORS.CLOSED,
                  color: STATUS_COLORS[b.status] || STATUS_COLORS.CLOSED,
                }}
                title={
                  b.reliability != null
                    ? `${(b.reliability * 100).toFixed(0)}% reliability`
                    : b.status
                }
              >
                <span className="prop-badge-band">{b.band}</span>
                <span className="prop-badge-status">{b.status}</span>
              </div>
            ))}
          </div>
          <div className="prop-legend">
            {Object.entries(STATUS_COLORS).map(([label, color]) => (
              <span key={label} className="prop-legend-item">
                <span
                  className="prop-legend-dot"
                  style={{ background: color }}
                />
                {label}
              </span>
            ))}
          </div>
          <div className="weather-updated">
            SSN {d.ssn} &middot; {d.utc_hour?.toFixed(1)}h UTC
            {d.computed_at && <> &middot; {timeAgo(d.computed_at)}</>}
          </div>
        </>
      )}
    </WidgetCard>
  );
}
