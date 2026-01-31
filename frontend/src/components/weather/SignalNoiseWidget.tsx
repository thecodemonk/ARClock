import { useSignalNoise } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";

function noiseColor(value: string): string {
  if (!value) return "var(--text-primary)";
  // Extract the highest S-level number from values like "S0", "S0-S1", "S4-S5"
  const match = value.match(/S(\d+)/g);
  if (!match) return "var(--text-primary)";
  const levels = match.map((s) => parseInt(s.slice(1), 10));
  const max = Math.max(...levels);
  if (max <= 1) return "var(--accent-green)";
  if (max <= 3) return "var(--accent-yellow)";
  if (max <= 5) return "var(--accent-amber)";
  return "var(--accent-red)";
}

export default function SignalNoiseWidget() {
  const { data, isLoading, isError } = useSignalNoise();
  const d = data as any;

  return (
    <WidgetCard title="Signal Noise">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div
            className="weather-value"
            style={{ color: noiseColor(d.value ?? "") }}
          >
            {d.value}
          </div>
          {(d.aindex != null || d.kindex != null) && (
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
              {d.aindex != null && <>A={d.aindex}</>}
              {d.aindex != null && d.kindex != null && " "}
              {d.kindex != null && <>K={d.kindex}</>}
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
