import ClockPanel from "../clocks/ClockPanel";
import MapView from "../map/MapView";
import DEInfoPanel from "../station/DEInfoPanel";
import DXInfoPanel from "../station/DXInfoPanel";
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
        <div
          style={{
            position: "absolute",
            bottom: 8,
            left: 8,
            zIndex: 10,
          }}
        >
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
      </div>
      <div className="dashboard-station">
        <DEInfoPanel />
        <DXInfoPanel />
      </div>
      <div className="dashboard-weather">
        <SpaceWeatherPanel />
      </div>
    </div>
  );
}
