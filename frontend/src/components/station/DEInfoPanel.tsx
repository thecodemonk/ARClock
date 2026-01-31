import { useStore } from "../../store";
import WidgetCard from "../layout/WidgetCard";

export default function DEInfoPanel() {
  const config = useStore((s) => s.stationConfig);
  const setShowSetup = useStore((s) => s.setShowSetup);

  return (
    <WidgetCard
      title="DE Station"
      rightHeader={
        <button
          onClick={() => setShowSetup(true)}
          style={{
            background: "none",
            border: "none",
            color: "var(--text-muted)",
            cursor: "pointer",
            fontFamily: "var(--font-mono)",
            fontSize: 10,
          }}
        >
          [setup]
        </button>
      }
    >
      <div className="station-info">
        <div className="station-row">
          <span className="station-label">Call</span>
          <span className="station-value">
            {config?.callsign || "Not set"}
          </span>
        </div>
        <div className="station-row">
          <span className="station-label">Grid</span>
          <span className="station-value">{config?.grid || "---"}</span>
        </div>
        <div className="station-row">
          <span className="station-label">Lat</span>
          <span className="station-value">
            {config?.latitude?.toFixed(4) ?? "---"}
          </span>
        </div>
        <div className="station-row">
          <span className="station-label">Lon</span>
          <span className="station-value">
            {config?.longitude?.toFixed(4) ?? "---"}
          </span>
        </div>
      </div>
    </WidgetCard>
  );
}
