# ARClock

An amateur radio dashboard inspired by [HamClock](https://www.clearskyinstitute.com/ham/HamClock/), built with a Python backend and React frontend. Displays real-time space weather data, a world map with grey line terminator overlay, and station information — all in a dark, ham-shack-friendly interface.

![Python](https://img.shields.io/badge/python-3.12+-blue)
![React](https://img.shields.io/badge/react-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Live Space Weather** — Solar Flux Index (SFI), Kp/Ap Index, X-ray flux with flare classification, Sunspot Number, Signal Noise (HamQSL), and MUF from nearest GIRO ionosonde — all with automatic refresh
- **Grey Line Map** — World map with real-time day/night terminator overlay computed from Skyfield ephemeris data. Night regions are shaded to look like nighttime
- **Multiple Map Styles** — Five built-in tile sets (Dark, Dark Clean, Light, Voyager, Liberty) switchable on the fly
- **Station Info** — Configure your home station (DE) callsign, grid square, and coordinates. Click anywhere on the map to see the DX grid square, bearing, and distance
- **Real-Time Updates** — WebSocket connection pushes new data to the browser as it arrives. No polling, no page refresh
- **Mini Charts** — Sparkline history charts for SFI, SSN, and MUF; colored bar chart for Kp index
- **Responsive Layout** — CSS Grid adapts from 7" RPi touchscreen (single column) to full desktop (three-column layout)
- **Frontend Configuration** — All settings managed through the UI and persisted to YAML. No need to edit config files by hand
- **Docker Ready** — Single-container deployment with config volume mount for persistence across rebuilds

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/thecodemonk/ARClock.git
cd ARClock
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000). On first run, a setup modal appears to configure your station.

Configuration is stored in `./config/arclock.yaml` on the host, mounted into the container. It persists across `docker compose down` and image rebuilds.

### Local Development

**Backend** (requires Python 3.12+):

```bash
cd backend
pip install -r requirements.txt
python -c "from skyfield.api import Loader; Loader('app/data')('de421.bsp')"
uvicorn app.main:app --port 8000
```

**Frontend** (requires Node 14+):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on port 5173 and proxies `/api` requests to the backend on port 8000.

## Screenshots

The dashboard adapts to three screen sizes:

| Layout | Screen | Description |
|--------|--------|-------------|
| **Small** | < 1024px | Single column: clocks → map → station → weather |
| **Medium** | 1024–1439px | Sidebar (clocks + station) + map + weather below |
| **Large** | 1440px+ | Three columns: clocks/station \| map \| weather |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Docker Container (or local)                            │
│                                                         │
│  FastAPI (Uvicorn) on :8000                             │
│  ├── /api/v1/space-weather/*  ← REST, from cache       │
│  ├── /api/v1/greyline         ← REST, computed          │
│  ├── /api/v1/station/de       ← REST, reads/writes YAML │
│  ├── /api/v1/location/info    ← REST, grid/bearing/dist │
│  ├── /api/v1/ws               ← WebSocket, real-time    │
│  ├── APScheduler              ← background NOAA polling  │
│  └── Static files at /        ← built React SPA         │
│                                                         │
│  Browser → localhost:8000                               │
│  ├── React SPA served from static mount                 │
│  ├── REST calls to /api/v1/*                            │
│  └── WebSocket to /api/v1/ws                            │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **APScheduler** fires a job on its interval (e.g., SFI every 15 minutes)
2. **Service layer** fetches from NOAA SWPC, parses, stores in an in-memory **DataCache**
3. **WebSocket Manager** broadcasts `{type: "sfi", data: {...}}` to all connected clients
4. **Frontend `useWebSocket` hook** receives the message and writes it into the **React Query** cache
5. **Widget component** (e.g., `SFIWidget`) subscribes via `useQuery` and re-renders automatically

On initial WebSocket connect, the backend sends a snapshot of all cached data so the client doesn't wait for the next poll cycle.

## Data Sources

Space weather data is sourced from NOAA SWPC, HamQSL, and GIRO ionosondes.

| Data | Source | Endpoint | Refresh |
|------|--------|----------|---------|
| Solar Flux Index (SFI) | [NOAA SWPC](https://www.swpc.noaa.gov/) | `text/daily-solar-indices.txt` | 15 min |
| Kp Index | NOAA SWPC | `json/planetary_k_index_1m.json` | 5 min |
| X-ray Flux | NOAA SWPC | `json/goes/primary/xrays-6-hour.json` | 1 min |
| Sunspot Number (SSN) | NOAA SWPC | `text/daily-solar-indices.txt` | 1 hr |
| Ap Index | NOAA SWPC | `text/daily-geomagnetic-indices.txt` | 1 hr |
| Signal Noise | [HamQSL](https://www.hamqsl.com/) | `solarxml.php` (XML) | 15 min |
| MUF (3000 km) | [GIRO](https://giro.uml.edu/) | Nearest ionosonde via `lgdc.uml.edu` | 15 min |
| Grey Line | Local | Computed via Skyfield + DE421 ephemeris | 1 min |

## Map Styles

Five free tile sets are included, all requiring no API key:

| Style | Source | Best For |
|-------|--------|----------|
| **Dark** (default) | CartoCDN Dark Matter | Ham shack use, low-light |
| **Dark (clean)** | CartoCDN Dark Matter No Labels | Minimal distraction |
| **Light** | CartoCDN Positron | Daytime readability |
| **Voyager** | CartoCDN Voyager | Colorful, detailed |
| **Liberty** | OpenFreeMap | OSM-based alternative |

Switch styles by clicking the style button on the map or selecting from the dropdown in Station Setup. The choice persists to the config file.

## Configuration

All configuration is managed through the frontend Station Setup modal (click `[setup]` on the DE Station panel). Settings are persisted to `config/arclock.yaml`:

```yaml
de_callsign: "W1AW"
de_grid: "FN31pr"
de_latitude: 41.7147
de_longitude: -72.7272
de_timezone: "America/New_York"
map_style: "dark-matter"
```

### Environment Variables

Every setting can be overridden with an `ARCLOCK_` prefixed environment variable:

| Variable | Default | Description |
|----------|---------|-------------|
| `ARCLOCK_DE_CALLSIGN` | `""` | Station callsign |
| `ARCLOCK_DE_GRID` | `""` | Maidenhead grid square |
| `ARCLOCK_DE_LATITUDE` | `0.0` | Station latitude |
| `ARCLOCK_DE_LONGITUDE` | `0.0` | Station longitude |
| `ARCLOCK_DE_TIMEZONE` | `UTC` | Station timezone (IANA format) |
| `ARCLOCK_MAP_STYLE` | `dark-matter` | Default map tile style |
| `ARCLOCK_SFI_INTERVAL` | `900` | SFI fetch interval (seconds) |
| `ARCLOCK_KP_INTERVAL` | `300` | Kp fetch interval (seconds) |
| `ARCLOCK_XRAY_INTERVAL` | `60` | X-ray fetch interval (seconds) |
| `ARCLOCK_SSN_INTERVAL` | `3600` | SSN fetch interval (seconds) |
| `ARCLOCK_AP_INTERVAL` | `3600` | Ap fetch interval (seconds) |
| `ARCLOCK_SIGNAL_NOISE_INTERVAL` | `900` | Signal noise fetch interval (seconds) |
| `ARCLOCK_MUF_INTERVAL` | `900` | MUF fetch interval (seconds) |
| `ARCLOCK_GREYLINE_INTERVAL` | `60` | Grey line recompute interval (seconds) |
| `ARCLOCK_CONFIG` | *(auto-detected)* | Path to YAML config file |

### Docker Persistence

The `docker-compose.yml` mounts `./config:/app/config`, so the YAML config lives on the host filesystem. Changes made through the UI persist across container rebuilds and restarts. No data is stored inside the container.

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Returns `{"status": "ok"}` |
| `GET` | `/api/v1/space-weather/sfi` | Solar Flux Index (current + 30-day history) |
| `GET` | `/api/v1/space-weather/kp` | Kp Index (current + 24-point history) |
| `GET` | `/api/v1/space-weather/xray` | X-ray flux + flare classification |
| `GET` | `/api/v1/space-weather/ssn` | Sunspot Number (current + 30-day history) |
| `GET` | `/api/v1/space-weather/ap` | Ap Index (current + 30-day history) |
| `GET` | `/api/v1/space-weather/signal_noise` | Signal noise level + A/K indices (HamQSL) |
| `GET` | `/api/v1/space-weather/muf` | MUF + foF2 from nearest GIRO ionosonde |
| `GET` | `/api/v1/space-weather/all` | All seven metrics in one response |
| `GET` | `/api/v1/greyline` | Terminator GeoJSON + subsolar point |
| `GET` | `/api/v1/station/de` | Station configuration |
| `PUT` | `/api/v1/station/de` | Update station config (persists to YAML) |
| `GET` | `/api/v1/location/info?lat=&lon=` | Grid square, bearing, and distance from DE |
| `WS` | `/api/v1/ws` | Real-time updates (snapshot on connect) |

## Project Structure

```
ARClock/
├── Dockerfile                          # Multi-stage build (Node 20 + Python 3.12)
├── docker-compose.yml                  # Single service with config volume
├── config/
│   ├── arclock.example.yaml            # Example configuration
│   └── arclock.yaml                    # User config (gitignored)
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                     # FastAPI app, lifespan, static mount
│       ├── config.py                   # Settings + YAML loader + config path
│       ├── routers/
│       │   ├── space_weather.py        # /space-weather/* endpoints
│       │   ├── greyline.py             # /greyline endpoint
│       │   ├── station.py              # /station/de GET/PUT
│       │   ├── location.py             # /location/info endpoint
│       │   └── ws.py                   # WebSocket endpoint
│       ├── services/
│       │   ├── space_weather.py        # NOAA SWPC + HamQSL data fetching
│       │   ├── muf.py                  # GIRO ionosonde MUF fetcher
│       │   ├── greyline.py             # Terminator polygon computation
│       │   ├── solar.py                # Subsolar point via Skyfield
│       │   ├── grid_square.py          # Maidenhead grid conversions
│       │   ├── geodesic.py             # Haversine bearing/distance
│       │   └── scheduler.py            # APScheduler + WebSocket broadcast
│       ├── core/
│       │   ├── websocket_manager.py    # Connection tracking + broadcast
│       │   └── cache.py                # Thread-safe in-memory cache
│       ├── models/                     # Pydantic response models
│       └── data/
│           └── de421.bsp               # Skyfield ephemeris (gitignored)
└── frontend/
    ├── package.json
    ├── vite.config.ts                  # Dev proxy to backend
    ├── index.html
    └── src/
        ├── App.tsx                     # Root: config load, WebSocket, setup modal
        ├── main.tsx                    # React entry, QueryClient
        ├── store.ts                    # Zustand (WS status, DX, config, map style)
        ├── styles/globals.css          # Dark theme, CSS Grid, all styles
        ├── hooks/
        │   ├── useClock.ts             # requestAnimationFrame tick
        │   ├── useWebSocket.ts         # WS connect/reconnect + React Query
        │   └── useSpaceWeather.ts      # Query hooks for all data
        ├── components/
        │   ├── layout/
        │   │   ├── Dashboard.tsx       # CSS Grid with named areas
        │   │   └── WidgetCard.tsx      # Dark card wrapper
        │   ├── clocks/
        │   │   ├── ClockPanel.tsx      # Callsign + UTC/local clocks
        │   │   └── ClockDisplay.tsx    # Single clock display
        │   ├── map/
        │   │   ├── MapView.tsx         # MapLibre GL JS
        │   │   ├── GreyLineLayer.tsx   # Night fill + terminator line
        │   │   ├── StationMarker.tsx   # DE station pin
        │   │   └── MapStyleSwitcher.tsx# Style cycle button
        │   ├── station/
        │   │   ├── DEInfoPanel.tsx     # Home station display
        │   │   ├── DXInfoPanel.tsx     # Clicked location info
        │   │   └── StationSetup.tsx    # Config modal
        │   └── weather/
        │       ├── SpaceWeatherPanel.tsx# 3x2 widget grid
        │       ├── SFIWidget.tsx       # Solar flux + sparkline
        │       ├── KpApWidget.tsx      # Kp + Ap index + bar chart
        │       ├── XrayWidget.tsx      # Flare class + color
        │       ├── SSNWidget.tsx       # Sunspot number + sparkline
        │       ├── SignalNoiseWidget.tsx# S-level noise + A/K indices
        │       ├── MUFWidget.tsx       # MUF + foF2 + ionosonde info
        │       └── MiniChart.tsx       # Recharts sparkline/bar
        └── lib/
            ├── api.ts                  # Fetch wrappers
            ├── gridSquare.ts           # Client-side Maidenhead
            └── formatters.ts           # Time/date/timeAgo
```

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Python 3.12, FastAPI, Uvicorn | Serves API + static SPA |
| Frontend | React 18, TypeScript, Vite 2 | Dark-themed responsive dashboard |
| Map | MapLibre GL JS, react-map-gl | Vector tiles, no API key needed |
| Tiles | CartoCDN, OpenFreeMap | Five free styles included |
| Charts | Recharts | Sparklines and bar charts |
| Server State | TanStack React Query 5 | Manages API + WebSocket data |
| Client State | Zustand 4 | UI state (DX location, settings) |
| Real-time | WebSocket (FastAPI native) | Push updates to browser |
| Scheduling | APScheduler | Background NOAA polling |
| Astronomy | Skyfield + DE421 | Subsolar point for grey line |

## License

MIT
