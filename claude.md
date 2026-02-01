# ARClock - Amateur Radio Dashboard

A HamClock-inspired amateur radio dashboard built with Python/FastAPI and React/TypeScript.

## Architecture

- **Backend:** Python 3.12 + FastAPI, served by Uvicorn
- **Frontend:** React 18 + TypeScript, built with Vite 2, served as static files by FastAPI
- **Map:** MapLibre GL JS with multiple tile providers (Carto, OpenFreeMap)
- **Real-time:** WebSocket push from backend to frontend via React Query
- **Scheduling:** APScheduler polls NOAA SWPC APIs at configurable intervals
- **Astronomy:** Skyfield + DE421 ephemeris for subsolar point / grey line
- **Deployment:** Docker multi-stage build (Node 20 for frontend, Python 3.12 for backend)

## Project Structure

```
backend/app/
  main.py              # FastAPI app, lifespan, static mount, CORS
  config.py            # Pydantic settings + YAML overlay + config path resolution
  routers/
    space_weather.py   # GET /api/v1/space-weather/{sfi,kp,xray,ssn,all}
    greyline.py        # GET /api/v1/greyline
    station.py         # GET/PUT /api/v1/station/de (persists to YAML)
    location.py        # GET /api/v1/location/info?lat=&lon=
    ws.py              # WebSocket /api/v1/ws (snapshot on connect)
  services/
    space_weather.py   # NOAA SWPC fetchers (SFI, Kp, X-ray, SSN, Ap) + HamQSL signal noise
    muf.py             # GIRO ionosonde MUF fetcher (station list, nearest finder, data query)
    greyline.py        # Terminator polygon via spherical geometry
    solar.py           # Subsolar point via Skyfield + DE421
    grid_square.py     # Maidenhead grid <-> lat/lon conversions
    geodesic.py        # Haversine bearing/distance calculations
    scheduler.py       # APScheduler jobs + WebSocket broadcast
  core/
    websocket_manager.py  # WS connection tracking + broadcast
    cache.py              # Thread-safe in-memory data cache
  models/              # Pydantic response models (station, space_weather incl. Ap/SignalNoise/MUF, greyline)
  data/de421.bsp       # Skyfield ephemeris (gitignored, downloaded at build)

frontend/src/
  App.tsx              # Root: loads station config, opens setup on first run
  main.tsx             # React entry point, QueryClient setup
  store.ts             # Zustand state (WS status, DX location, station config, map style)
  hooks/
    useClock.ts        # requestAnimationFrame clock tick
    useWebSocket.ts    # WS connect/reconnect, pushes into React Query cache
    useSpaceWeather.ts # React Query hooks for SFI, Kp, X-ray, SSN, greyline
  components/
    layout/
      Dashboard.tsx    # CSS Grid container with named areas + map overlays
      WidgetCard.tsx   # Reusable dark card wrapper
    clocks/
      ClockPanel.tsx   # Callsign header + UTC/local clocks
      ClockDisplay.tsx # Single digital clock
    map/
      MapView.tsx          # MapLibre GL JS, style from store, click handler
      GreyLineLayer.tsx    # GeoJSON night fill + terminator line, survives style swaps
      StationMarker.tsx    # DE station pin
      MapStyleSwitcher.tsx # Cycle button + style URL registry
    station/
      DEInfoPanel.tsx  # Home station info with [setup] button
      DXInfoPanel.tsx  # Clicked location info (grid, bearing, distance)
      StationSetup.tsx # Config modal (callsign, grid, lat/lon, timezone dropdown, map style); grid auto-fills lat/lon/timezone
    weather/
      SpaceWeatherPanel.tsx  # 3x2 grid of weather widgets
      SFIWidget.tsx    # Current value + sparkline
      KpApWidget.tsx   # Kp (primary) + Ap (secondary) + colored bar chart
      XrayWidget.tsx   # Flare class + flux with color coding
      SSNWidget.tsx    # Current value + sparkline
      SignalNoiseWidget.tsx  # S-level noise value + A/K indices
      MUFWidget.tsx    # MUF in MHz + foF2 + sparkline + ionosonde station
      MiniChart.tsx    # Reusable Recharts sparkline and bar chart
  lib/
    api.ts             # fetchJson / putJson wrappers
    gridSquare.ts      # Client-side Maidenhead conversion (latLonToGrid + gridToLatLon)
    formatters.ts      # Time/date formatting, timeAgo
  styles/
    globals.css        # Dark theme, CSS Grid (3 breakpoints), all component styles
```

## Data Sources

| Data | Source | Endpoint | Refresh |
|------|--------|----------|---------|
| Solar Flux (SFI) | NOAA SWPC | `text/daily-solar-indices.txt` | 15 min |
| Kp Index | NOAA SWPC | `planetary_k_index_1m.json` | 5 min |
| X-ray Flux | NOAA SWPC | `goes/primary/xrays-6-hour.json` | 1 min |
| Sunspot Number | NOAA SWPC | `text/daily-solar-indices.txt` | 1 hr |
| Ap Index | NOAA SWPC | `text/daily-geomagnetic-indices.txt` | 1 hr |
| Signal Noise | HamQSL | `solarxml.php` (XML) | 15 min |
| MUF (3000) | GIRO | `lgdc.uml.edu/common/DIDBGetValues` (nearest ionosonde) | 15 min |
| Grey Line | Local | Computed via Skyfield (subsolar point -> terminator polygon) | 1 min |

## Map Styles

Five built-in styles, switchable via button on the map or dropdown in setup modal. Selection persists to config.

| Key | Label | Source |
|-----|-------|--------|
| `dark-matter` | Dark | CartoCDN Dark Matter |
| `dark-matter-nolabels` | Dark (clean) | CartoCDN Dark Matter No Labels |
| `positron` | Light | CartoCDN Positron |
| `voyager` | Voyager | CartoCDN Voyager |
| `osm-liberty` | Liberty | OpenFreeMap Liberty |

Style URLs are defined in `frontend/src/components/map/MapStyleSwitcher.tsx`.

## Configuration

All configuration is managed through the frontend UI (Station Setup modal) and persisted to `config/arclock.yaml`. On first run with no config, the setup modal appears automatically.

Entering a valid Maidenhead grid square (4 or 6 characters) automatically populates the latitude, longitude, and timezone fields. Coordinates are set to the center of the grid square. Timezone is guessed from the coordinates using longitude-based offset matching with geographic region preference, and can be overridden via the timezone dropdown (populated from `Intl.supportedValuesOf("timeZone")`).

```yaml
de_callsign: "W1AW"
de_grid: "FN31pr"
de_latitude: 41.7147
de_longitude: -72.7272
de_timezone: "America/New_York"
map_style: "dark-matter"
```

Environment variable overrides are supported with the `ARCLOCK_` prefix (e.g., `ARCLOCK_DE_CALLSIGN`).

### Docker Persistence

The `docker-compose.yml` mounts `./config:/app/config` so the YAML file lives on the host filesystem. Config changes made through the UI survive container rebuilds and restarts.

## Running Locally

```bash
# Backend (requires Python 3.12+)
cd backend
pip install -r requirements.txt
python -c "from skyfield.api import Loader; Loader('app/data')('de421.bsp')"
uvicorn app.main:app --port 8000

# Frontend dev (proxies /api to :8000)
cd frontend
npm install
npm run dev

# Production via Docker
docker compose up --build
# Open http://localhost:8000
```

Note: Local frontend dev requires Node 14+ (Vite 2). Docker build uses Node 20.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/space-weather/{sfi,kp,xray,ssn,ap,signal_noise,muf,all}` | Space weather data from cache |
| GET | `/api/v1/greyline` | Terminator GeoJSON + subsolar point |
| GET | `/api/v1/station/de` | Station config (includes map_style) |
| PUT | `/api/v1/station/de` | Update station config, persists to YAML |
| GET | `/api/v1/location/info?lat=&lon=` | Grid square, bearing, distance from DE |
| WS | `/api/v1/ws` | Real-time updates (snapshot on connect, then push) |

## Real-Time Data Flow

1. APScheduler fires a job (e.g., fetch SFI every 15 min)
2. Service fetches from NOAA, parses, stores in DataCache
3. WebSocket Manager broadcasts `{type: "sfi", data: {...}}` to all clients
4. Frontend `useWebSocket` hook receives message, calls `queryClient.setQueryData`
5. Widget using `useQuery` automatically re-renders with new data

On initial connect, the backend sends a snapshot of all cached data.

## Responsive Layout

Three CSS Grid breakpoints:

- **Small (< 1024px):** Single column stack (clocks, map, station, weather)
- **Medium (1024-1439px):** Left sidebar (clocks + station) + map center + weather bottom
- **Large (1440px+):** Three columns (clocks/station | map | weather)

## Key Dependencies

**Backend:** fastapi, uvicorn, httpx, skyfield, apscheduler, numpy, pyyaml, pydantic-settings (xml.etree.ElementTree from stdlib for HamQSL XML parsing)

**Frontend:** react, react-dom, maplibre-gl, react-map-gl, recharts, @tanstack/react-query, zustand
