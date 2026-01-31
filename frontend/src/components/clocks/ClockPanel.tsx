import { useClock } from "../../hooks/useClock";
import {
  formatDateLocal,
  formatDateUTC,
  formatTime,
  formatTimeUTC,
} from "../../lib/formatters";
import { useStore } from "../../store";
import WidgetCard from "../layout/WidgetCard";
import ClockDisplay from "./ClockDisplay";

export default function ClockPanel() {
  const now = useClock();
  const config = useStore((s) => s.stationConfig);

  return (
    <WidgetCard title="Clocks">
      <div className="clock-panel">
        {config?.callsign && (
          <div className="callsign-header">{config.callsign}</div>
        )}
        <ClockDisplay
          time={formatTimeUTC(now)}
          date={formatDateUTC(now)}
          label="UTC"
        />
        <ClockDisplay
          time={formatTime(now)}
          date={formatDateLocal(now)}
          label="Local"
        />
      </div>
    </WidgetCard>
  );
}
