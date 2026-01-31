import { useEffect, useRef } from "react";
import { useMap } from "react-map-gl/maplibre";
import { useGreyLine } from "../../hooks/useSpaceWeather";
import { useStore } from "../../store";

const SOURCE_ID = "greyline-source";
const NIGHT_LAYER = "night-fill";
const TERMINATOR_LAYER = "terminator-line";

export default function GreyLineLayer() {
  const { current: map } = useMap();
  const { data } = useGreyLine();
  const greyline = data as any;
  const dataRef = useRef(greyline);
  dataRef.current = greyline;
  const mapStyle = useStore((s) => s.mapStyle);

  useEffect(() => {
    if (!map) return;
    const m = map.getMap();

    const addSourceAndLayers = () => {
      const geojson = dataRef.current?.geojson;
      if (!geojson) return;

      // If source already exists, just update data
      if (m.getSource(SOURCE_ID)) {
        (m.getSource(SOURCE_ID) as any).setData(geojson);
        return;
      }

      m.addSource(SOURCE_ID, { type: "geojson", data: geojson });

      // Determine if we're on a dark or light base map for fill tuning
      const isLight =
        mapStyle === "positron" || mapStyle === "voyager";

      m.addLayer({
        id: NIGHT_LAYER,
        type: "fill",
        source: SOURCE_ID,
        filter: ["==", ["get", "name"], "night"],
        paint: {
          "fill-color": isLight ? "#0a1128" : "#000010",
          "fill-opacity": isLight ? 0.30 : 0.45,
        },
      });

      m.addLayer({
        id: TERMINATOR_LAYER,
        type: "line",
        source: SOURCE_ID,
        filter: ["==", ["get", "name"], "terminator"],
        paint: {
          "line-color": "#f0a020",
          "line-width": 2,
          "line-opacity": 0.85,
        },
      });
    };

    // Use 'styledata' which fires after every style load/diff
    const onStyleData = () => {
      // Small delay to let react-map-gl finish its own diffing
      setTimeout(addSourceAndLayers, 50);
    };

    if (m.isStyleLoaded()) {
      addSourceAndLayers();
    }
    m.on("styledata", onStyleData);
    return () => {
      m.off("styledata", onStyleData);
    };
  }, [map, mapStyle]);

  // Update data when greyline changes
  useEffect(() => {
    if (!map || !greyline?.geojson) return;
    const m = map.getMap();
    if (!m.isStyleLoaded()) return;
    const src = m.getSource(SOURCE_ID);
    if (src) {
      (src as any).setData(greyline.geojson);
    }
  }, [map, greyline]);

  return null;
}
