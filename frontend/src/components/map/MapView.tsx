import { useCallback } from "react";
import Map, { MapLayerMouseEvent, NavigationControl } from "react-map-gl/maplibre";
import { fetchJson } from "../../lib/api";
import { useStore } from "../../store";
import GreyLineLayer from "./GreyLineLayer";
import { MAP_STYLES } from "./MapStyleSwitcher";
import StationMarker from "./StationMarker";

export default function MapView() {
  const setDxLocation = useStore((s) => s.setDxLocation);
  const mapStyle = useStore((s) => s.mapStyle);

  const styleUrl =
    MAP_STYLES[mapStyle]?.url || MAP_STYLES["dark-matter"].url;

  const handleClick = useCallback(
    async (e: MapLayerMouseEvent) => {
      const { lat, lng } = e.lngLat;
      try {
        const info = await fetchJson<any>(
          `/location/info?lat=${lat.toFixed(4)}&lon=${lng.toFixed(4)}`
        );
        setDxLocation(info);
      } catch {
        // fail silently
      }
    },
    [setDxLocation]
  );

  return (
    <div className="map-container">
      <Map
        initialViewState={{
          longitude: 0,
          latitude: 30,
          zoom: 1.5,
        }}
        style={{ width: "100%", height: "100%" }}
        mapStyle={styleUrl}
        onClick={handleClick}
        attributionControl={false}
      >
        <NavigationControl position="top-right" />
        <GreyLineLayer />
        <StationMarker />
      </Map>
    </div>
  );
}
