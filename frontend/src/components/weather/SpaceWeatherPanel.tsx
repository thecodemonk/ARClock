import KpWidget from "./KpWidget";
import SFIWidget from "./SFIWidget";
import SSNWidget from "./SSNWidget";
import XrayWidget from "./XrayWidget";

export default function SpaceWeatherPanel() {
  return (
    <div className="weather-grid">
      <SFIWidget />
      <KpWidget />
      <XrayWidget />
      <SSNWidget />
    </div>
  );
}
