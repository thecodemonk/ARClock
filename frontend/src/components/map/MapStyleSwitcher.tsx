import { useCallback } from "react";
import { putJson } from "../../lib/api";
import { useStore } from "../../store";

export const MAP_STYLES: Record<string, { label: string; url: string }> = {
  "dark-matter": {
    label: "Dark",
    url: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
  },
  "dark-matter-nolabels": {
    label: "Dark (clean)",
    url: "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-style/style.json",
  },
  positron: {
    label: "Light",
    url: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  },
  voyager: {
    label: "Voyager",
    url: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
  },
  "osm-liberty": {
    label: "Liberty",
    url: "https://tiles.openfreemap.org/styles/liberty",
  },
};

export const STYLE_KEYS = Object.keys(MAP_STYLES);

export default function MapStyleSwitcher() {
  const mapStyle = useStore((s) => s.mapStyle);
  const setMapStyle = useStore((s) => s.setMapStyle);
  const config = useStore((s) => s.stationConfig);

  const handleCycle = useCallback(() => {
    const idx = STYLE_KEYS.indexOf(mapStyle);
    const next = STYLE_KEYS[(idx + 1) % STYLE_KEYS.length];
    setMapStyle(next);

    // Persist to backend
    if (config) {
      putJson("/station/de", { ...config, map_style: next }).catch(() => {});
    }
  }, [mapStyle, setMapStyle, config]);

  const current = MAP_STYLES[mapStyle] || MAP_STYLES["dark-matter"];

  return (
    <button
      onClick={handleCycle}
      className="map-style-btn"
      title="Switch map style"
    >
      {current.label}
    </button>
  );
}
