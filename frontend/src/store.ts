import { create } from "zustand";

export type WsStatus = "connecting" | "connected" | "disconnected";

interface DXLocation {
  latitude: number;
  longitude: number;
  grid: string;
  bearing: number | null;
  distance_km: number | null;
  distance_mi: number | null;
}

interface StationConfig {
  callsign: string;
  grid: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

interface AppState {
  wsStatus: WsStatus;
  setWsStatus: (status: WsStatus) => void;

  dxLocation: DXLocation | null;
  setDxLocation: (loc: DXLocation | null) => void;

  stationConfig: StationConfig | null;
  setStationConfig: (config: StationConfig) => void;

  showSetup: boolean;
  setShowSetup: (show: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  wsStatus: "disconnected",
  setWsStatus: (status) => set({ wsStatus: status }),

  dxLocation: null,
  setDxLocation: (loc) => set({ dxLocation: loc }),

  stationConfig: null,
  setStationConfig: (config) => set({ stationConfig: config }),

  showSetup: false,
  setShowSetup: (show) => set({ showSetup: show }),
}));
