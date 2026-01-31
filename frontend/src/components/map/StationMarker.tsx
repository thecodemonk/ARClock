import { Marker } from "react-map-gl/maplibre";
import { useStore } from "../../store";

export default function StationMarker() {
  const config = useStore((s) => s.stationConfig);

  if (!config || (config.latitude === 0 && config.longitude === 0)) {
    return null;
  }

  return (
    <Marker latitude={config.latitude} longitude={config.longitude}>
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: "var(--accent-amber)",
          border: "2px solid var(--bg-primary)",
          boxShadow: "0 0 8px rgba(240, 160, 32, 0.6)",
        }}
        title={config.callsign || "DE Station"}
      />
    </Marker>
  );
}
