# ARClock - Amateur Radio Dashboard

A HamClock-inspired amateur radio dashboard built with Python/FastAPI and React/TypeScript.

## Architecture

- **Backend:** Python 3.12 + FastAPI, served by Uvicorn
- **Frontend:** React 18 + TypeScript, built with Vite, served as static files by FastAPI
- **Map:** MapLibre GL JS with CartoCDN Dark Matter tiles
- **Real-time:** WebSocket push from backend to frontend via React Query
- **Scheduling:** APScheduler polls NOAA SWPC APIs at configurable intervals
- **Astronomy:** Skyfield + DE421 ephemeris for subsolar point / grey line

## Project Structure

```
backend/app/
  main.py              # FastAPI app, lifespan, static mount, CORS
  config.py            # Pydantic settings + YAML overlay
  routers/             # REST + WebSocket endpoints
  services/            # NOAA fetching, greyline, solar, grid square, geodesic
  core/                # WebSocket manager, in-memory cache
  models/              # Pydantic response models
  data/de421.bsp       # Skyfield ephemeris (gitignored, downloaded at build)

frontend/src/
  App.tsx              # Root component, WebSocket hook, station config load
  store.ts             # Zustand state (WS status, DX location, station config)
  hooks/               # useClock, useWebSocket, useSpaceWeather
  components/
    layout/            # Dashboard (CSS Grid), WidgetCard
    clocks/            # UTC + local clocks with requestAnimationFrame
    map/               # MapLibre view, grey line GeoJSON layer, station marker
    station/           # DE info, DX info, setup modal
    weather/           # SFI, Kp, X-ray, SSN widgets with Recharts mini-charts
  lib/                 # API fetch wrapper, grid square math, formatters
```

## Data Sources

| Data | NOAA Endpoint | Refresh |
|------|--------------|---------|
| Solar Flux (SFI) | `f107_cm_flux.json` | 15 min |
| Kp Index | `planetary_k_index_1m.json` | 5 min |
| X-ray Flux | `goes/primary/xrays-6-hour.json` | 1 min |
| Sunspot Number | `solar-cycle/sunspots.json` | 1 hr |
| Grey Line | Computed via Skyfield | 1 min |

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python -c "from skyfield.api import Loader; Loader('app/data')('de421.bsp')"
uvicorn app.main:app --port 8000

# Frontend dev (proxies API to :8000)
cd frontend
npm install
npm run dev

# Production via Docker
docker compose up --build
# Open http://localhost:8000
```

## Configuration

Station config is stored in `config/arclock.yaml` and can be set via the UI setup modal or environment variables with `ARCLOCK_` prefix.

```yaml
de_callsign: "W1AW"
de_grid: "FN31pr"
de_latitude: 41.7147
de_longitude: -72.7272
de_timezone: "America/New_York"
```

## API Endpoints

- `GET /api/v1/health` — health check
- `GET /api/v1/space-weather/{sfi,kp,xray,ssn,all}` — space weather data
- `GET /api/v1/greyline` — terminator GeoJSON + subsolar point
- `GET /api/v1/station/de` — station config
- `PUT /api/v1/station/de` — update station config
- `GET /api/v1/location/info?lat=&lon=` — grid square, bearing, distance from DE
- `WS /api/v1/ws` — real-time updates (sends snapshot on connect)

## Key Dependencies

Backend: fastapi, uvicorn, httpx, skyfield, apscheduler, numpy, pyyaml, pydantic-settings
Frontend: react, react-dom, maplibre-gl, react-map-gl, recharts, @tanstack/react-query, zustand
