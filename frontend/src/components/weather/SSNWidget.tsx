import { useSSN } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";
import { Sparkline } from "./MiniChart";

export default function SSNWidget() {
  const { data, isLoading, isError } = useSSN();
  const d = data as any;

  return (
    <WidgetCard title="Sunspot Number">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div className="weather-value" style={{ color: "var(--accent-blue)" }}>
            {d.value}
          </div>
          <Sparkline
            data={d.history?.map((h: any) => ({ value: h.value })) ?? []}
            color="#40a0e0"
          />
          {d.time_tag && (
            <div className="weather-updated">{timeAgo(d.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
