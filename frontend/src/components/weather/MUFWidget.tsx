import { useMUF } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";
import { Sparkline } from "./MiniChart";

export default function MUFWidget() {
  const { data, isLoading, isError } = useMUF();
  const d = data as any;

  return (
    <WidgetCard title="MUF (3000)">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div
            className="weather-value"
            style={{ color: "var(--accent-amber)" }}
          >
            {d.muf?.toFixed(1)} <span style={{ fontSize: 12 }}>MHz</span>
          </div>
          {d.fof2 != null && (
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
              foF2: {d.fof2.toFixed(1)} MHz
            </div>
          )}
          <Sparkline
            data={d.history?.map((h: any) => ({ value: h.value })) ?? []}
            color="#f0a020"
          />
          {d.station_name && (
            <div style={{ fontSize: 9, color: "var(--text-muted)" }}>
              {d.station_name} ({d.station_code})
            </div>
          )}
          {d.time_tag && (
            <div className="weather-updated">{timeAgo(d.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
