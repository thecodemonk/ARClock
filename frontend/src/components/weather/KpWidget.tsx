import { useKp } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";
import { KpBarChart } from "./MiniChart";

function kpColor(value: number): string {
  if (value < 4) return "var(--kp-low)";
  if (value < 6) return "var(--kp-moderate)";
  if (value < 8) return "var(--kp-high)";
  return "var(--kp-severe)";
}

export default function KpWidget() {
  const { data, isLoading, isError } = useKp();
  const d = data as any;

  return (
    <WidgetCard title="Kp Index">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div
            className="weather-value"
            style={{ color: kpColor(d.value ?? 0) }}
          >
            {d.value?.toFixed(1)}
          </div>
          <KpBarChart
            data={d.history?.map((h: any) => ({ value: h.value })) ?? []}
          />
          {d.time_tag && (
            <div className="weather-updated">{timeAgo(d.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
