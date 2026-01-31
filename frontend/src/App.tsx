import { useEffect } from "react";
import Dashboard from "./components/layout/Dashboard";
import StationSetup from "./components/station/StationSetup";
import { useWebSocket } from "./hooks/useWebSocket";
import { fetchJson } from "./lib/api";
import { useStore } from "./store";

export default function App() {
  useWebSocket();
  const setStationConfig = useStore((s) => s.setStationConfig);
  const setShowSetup = useStore((s) => s.setShowSetup);
  useEffect(() => {
    fetchJson<any>("/station/de")
      .then((config) => {
        setStationConfig(config);
        if (!config.callsign) {
          setShowSetup(true);
        }
      })
      .catch(() => {
        setShowSetup(true);
      });
  }, [setStationConfig, setShowSetup]);

  return (
    <>
      <Dashboard />
      <StationSetup />
    </>
  );
}
