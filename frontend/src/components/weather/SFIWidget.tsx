import { useSFI } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";
import { Sparkline } from "./MiniChart";

export default function SFIWidget() {
  const { data, isLoading, isError } = useSFI();
  const d = data as any;

  return (
    <WidgetCard title="SFI (10.7cm)">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div className="weather-value" style={{ color: "var(--accent-amber)" }}>
            {d.value?.toFixed(1)}
          </div>
          <Sparkline
            data={d.history?.map((h: any) => ({ value: h.value })) ?? []}
            color="#f0a020"
          />
          {d.time_tag && (
            <div className="weather-updated">{timeAgo(d.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
