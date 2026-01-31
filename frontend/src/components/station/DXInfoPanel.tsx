import { useStore } from "../../store";
import WidgetCard from "../layout/WidgetCard";

export default function DXInfoPanel() {
  const dx = useStore((s) => s.dxLocation);

  return (
    <WidgetCard title="DX Location">
      {!dx ? (
        <div className="loading-text" style={{ color: "var(--text-muted)" }}>
          Click map to select
        </div>
      ) : (
        <div className="station-info">
          <div className="station-row">
            <span className="station-label">Grid</span>
            <span className="station-value">{dx.grid}</span>
          </div>
          <div className="station-row">
            <span className="station-label">Lat</span>
            <span className="station-value">{dx.latitude.toFixed(4)}</span>
          </div>
          <div className="station-row">
            <span className="station-label">Lon</span>
            <span className="station-value">{dx.longitude.toFixed(4)}</span>
          </div>
          {dx.bearing != null && (
            <div className="station-row">
              <span className="station-label">Bearing</span>
              <span className="station-value">{dx.bearing.toFixed(1)}&deg;</span>
            </div>
          )}
          {dx.distance_km != null && (
            <div className="station-row">
              <span className="station-label">Distance</span>
              <span className="station-value">
                {dx.distance_km.toFixed(0)} km / {dx.distance_mi?.toFixed(0)} mi
              </span>
            </div>
          )}
        </div>
      )}
    </WidgetCard>
  );
}
