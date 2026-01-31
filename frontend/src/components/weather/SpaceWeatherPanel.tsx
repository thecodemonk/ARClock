import KpApWidget from "./KpApWidget";
import MUFWidget from "./MUFWidget";
import SFIWidget from "./SFIWidget";
import SignalNoiseWidget from "./SignalNoiseWidget";
import SSNWidget from "./SSNWidget";
import XrayWidget from "./XrayWidget";

export default function SpaceWeatherPanel() {
  return (
    <div className="weather-grid">
      <SFIWidget />
      <KpApWidget />
      <XrayWidget />
      <SSNWidget />
      <SignalNoiseWidget />
      <MUFWidget />
    </div>
  );
}
