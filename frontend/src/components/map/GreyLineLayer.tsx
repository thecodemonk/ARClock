import { useEffect } from "react";
import { useMap } from "react-map-gl/maplibre";
import { useGreyLine } from "../../hooks/useSpaceWeather";

export default function GreyLineLayer() {
  const { current: map } = useMap();
  const { data } = useGreyLine();
  const greyline = data as any;

  useEffect(() => {
    if (!map || !greyline?.geojson) return;

    const m = map.getMap();

    // Wait for map style to be loaded
    const applyLayers = () => {
      const sourceId = "greyline-source";

      if (m.getSource(sourceId)) {
        (m.getSource(sourceId) as any).setData(greyline.geojson);
        return;
      }

      m.addSource(sourceId, {
        type: "geojson",
        data: greyline.geojson,
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

    if (m.isStyleLoaded()) {
      applyLayers();
    } else {
      m.on("style.load", applyLayers);
      return () => {
        m.off("style.load", applyLayers);
      };
    }
  }, [map, greyline]);

  return null;
}
