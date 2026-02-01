import ClockPanel from "../clocks/ClockPanel";
import MapView from "../map/MapView";
import MapStyleSwitcher from "../map/MapStyleSwitcher";
import DEInfoPanel from "../station/DEInfoPanel";
import DXInfoPanel from "../station/DXInfoPanel";
import PropagationPanel from "../station/PropagationPanel";
import SpaceWeatherPanel from "../weather/SpaceWeatherPanel";
import { useStore } from "../../store";

export default function Dashboard() {
  const wsStatus = useStore((s) => s.wsStatus);

  return (
    <div className="dashboard">
      <div className="dashboard-clocks">
        <ClockPanel />
      </div>
      <div className="dashboard-map">
        <MapView />
        <div className="map-overlay-bottom-left">
          <div className="ws-status">
            <span
              className={`ws-dot ${wsStatus}`}
            />
            <span>
              {wsStatus === "connected"
                ? "Live"
                : wsStatus === "connecting"
                ? "Connecting..."
                : "Disconnected"}
            </span>
          </div>
        </div>
        <div className="map-overlay-top-left">
          <MapStyleSwitcher />
        </div>
      </div>
      <div className="dashboard-station">
        <DEInfoPanel />
        <DXInfoPanel />
        <PropagationPanel />
      </div>
      <div className="dashboard-weather">
        <SpaceWeatherPanel />
      </div>
    </div>
  );
}
