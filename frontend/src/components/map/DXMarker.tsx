import { Marker } from "react-map-gl/maplibre";
import { useStore } from "../../store";

export default function DXMarker() {
  const dx = useStore((s) => s.dxLocation);

  if (!dx) {
    return null;
  }

  return (
    <Marker latitude={dx.latitude} longitude={dx.longitude}>
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: "var(--accent-blue)",
          border: "2px solid var(--bg-primary)",
          boxShadow: "0 0 8px rgba(64, 160, 224, 0.6)",
        }}
        title={`DX: ${dx.grid}`}
      />
    </Marker>
  );
}
