import { useXRay } from "../../hooks/useSpaceWeather";
import { timeAgo } from "../../lib/formatters";
import WidgetCard from "../layout/WidgetCard";

function flareColor(flareClass: string): string {
  const letter = flareClass?.[0]?.toUpperCase();
  switch (letter) {
    case "A":
    case "B":
      return "var(--accent-green)";
    case "C":
      return "var(--accent-yellow)";
    case "M":
      return "var(--accent-amber)";
    case "X":
      return "var(--accent-red)";
    default:
      return "var(--text-primary)";
  }
}

export default function XrayWidget() {
  const { data, isLoading, isError } = useXRay();
  const d = data as any;

  return (
    <WidgetCard title="X-Ray Flux">
      {isLoading && <div className="loading-text">Loading...</div>}
      {isError && <div className="error-text">No data</div>}
      {d && (
        <>
          <div
            className="weather-value"
            style={{ color: flareColor(d.flare_class ?? "") }}
          >
            {d.flare_class}
          </div>
          <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
            {d.flux?.toExponential(2)} W/m²
          </div>
          {d.time_tag && (
            <div className="weather-updated">{timeAgo(d.time_tag)}</div>
          )}
        </>
      )}
    </WidgetCard>
  );
}
