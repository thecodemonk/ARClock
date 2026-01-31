import { useAp, useKp } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";
import { KpBarChart } from "./MiniChart";

function kpColor(value: number): string {
  if (value < 4) return "var(--kp-low)";
  if (value < 6) return "var(--kp-moderate)";
  if (value < 8) return "var(--kp-high)";
  return "var(--kp-severe)";
}

function apColor(value: number): string {
  if (value < 8) return "var(--accent-green)";
  if (value < 32) return "var(--accent-yellow)";
  if (value < 100) return "var(--kp-high)";
  return "var(--accent-red)";
}

export default function KpApWidget() {
  const { data: kpData, isLoading: kpLoading, isError: kpError } = useKp();
  const { data: apData } = useAp();
  const kp = kpData as any;
  const ap = apData as any;

  return (
    <WidgetCard title="Kp / Ap Index">
      {kpLoading && <div className="loading-text">Loading...</div>}
      {kpError && <div className="error-text">No data</div>}
      {kp && (
        <>
          <div className="kp-ap-values">
            <div
              className="weather-value"
              style={{ color: kpColor(kp.value ?? 0) }}
            >
              {kp.value?.toFixed(2)}
            </div>
            {ap && (
              <div
                className="weather-value-secondary"
                style={{ color: apColor(ap.value ?? 0) }}
              >
                Ap {ap.value}
              </div>
            )}
          </div>
          <KpBarChart
            data={kp.history?.map((h: any) => ({ value: h.value })) ?? []}
          />
          {kp.time_tag && (
            <div className="weather-updated">{timeAgo(kp.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
