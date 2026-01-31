import { useEffect, useRef } from "react";
import { useMap } from "react-map-gl/maplibre";
import { useGreyLine } from "../../hooks/useSpaceWeather";

export default function GreyLineLayer() {
  const { current: map } = useMap();
  const { data } = useGreyLine();
  const greyline = data as any;
  const dataRef = useRef(greyline);
  dataRef.current = greyline;

  useEffect(() => {
    if (!map) return;
    const m = map.getMap();

    const applyLayers = () => {
      const geojson = dataRef.current?.geojson;
      if (!geojson) return;

      const sourceId = "greyline-source";

      if (m.getSource(sourceId)) {
        (m.getSource(sourceId) as any).setData(geojson);
        return;
      }

      m.addSource(sourceId, {
        type: "geojson",
        data: geojson,
      });

      m.addLayer({
        id: "night-fill",
        type: "fill",
        source: sourceId,
        filter: ["==", ["get", "name"], "night"],
        paint: {
          "fill-color": "#000000",
          "fill-opacity": 0.35,
        },
      });

      m.addLayer({
        id: "terminator-line",
        type: "line",
        source: sourceId,
        filter: ["==", ["get", "name"], "terminator"],
        paint: {
          "line-color": "#f0a020",
          "line-width": 2,
          "line-opacity": 0.8,
        },
      });
    };

    // Apply now if style is ready, and re-apply after every style change
    if (m.isStyleLoaded()) {
      applyLayers();
    }
    m.on("style.load", applyLayers);
    return () => {
      m.off("style.load", applyLayers);
    };
  }, [map]);

  // Update data when greyline changes (without re-registering the event)
  useEffect(() => {
    if (!map || !greyline?.geojson) return;
    const m = map.getMap();
    if (!m.isStyleLoaded()) return;
    const src = m.getSource("greyline-source");
    if (src) {
      (src as any).setData(greyline.geojson);
    }
  }, [map, greyline]);

  return null;
}
