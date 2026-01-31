import { FormEvent, useState } from "react";
import { putJson } from "../../lib/api";
import { useStore } from "../../store";

export default function StationSetup() {
  const showSetup = useStore((s) => s.showSetup);
  const setShowSetup = useStore((s) => s.setShowSetup);
  const config = useStore((s) => s.stationConfig);
  const setStationConfig = useStore((s) => s.setStationConfig);

  const [callsign, setCallsign] = useState(config?.callsign ?? "");
  const [grid, setGrid] = useState(config?.grid ?? "");
  const [lat, setLat] = useState(config?.latitude?.toString() ?? "");
  const [lon, setLon] = useState(config?.longitude?.toString() ?? "");
  const [tz, setTz] = useState(config?.timezone ?? "UTC");
  const [saving, setSaving] = useState(false);

  if (!showSetup) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const body = {
        callsign: callsign.toUpperCase(),
        grid,
        latitude: parseFloat(lat) || 0,
        longitude: parseFloat(lon) || 0,
        timezone: tz,
      };
      await putJson("/station/de", body);
      setStationConfig(body);
      setShowSetup(false);
    } catch {
      // show error inline
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => setShowSetup(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-title">Station Setup</div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Callsign</label>
            <input
              className="form-input"
              value={callsign}
              onChange={(e) => setCallsign(e.target.value)}
              placeholder="W1AW"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Grid Square</label>
            <input
              className="form-input"
              value={grid}
              onChange={(e) => setGrid(e.target.value)}
              placeholder="FN31pr"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Latitude</label>
            <input
              className="form-input"
              type="number"
              step="any"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder="41.7147"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Longitude</label>
            <input
              className="form-input"
              type="number"
              step="any"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              placeholder="-72.7272"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Timezone</label>
            <input
              className="form-input"
              value={tz}
              onChange={(e) => setTz(e.target.value)}
              placeholder="America/New_York"
            />
          </div>
          <button className="btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Configuration"}
          </button>
        </form>
      </div>
    </div>
  );
}
