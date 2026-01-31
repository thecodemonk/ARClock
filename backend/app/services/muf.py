from __future__ import annotations

import logging
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GIRO_STATION_LIST_URL = "https://lgdc.uml.edu/common/DIDBFastStationList"
GIRO_VALUES_URL = "https://lgdc.uml.edu/common/DIDBGetValues"
TIMEOUT = 20.0

# Module-level cache for station list (fetched once per app lifecycle)
_station_cache: list[dict[str, Any]] | None = None
_nearest_cache: dict[str, Any] | None = None


def invalidate_station_cache() -> None:
    """Clear nearest-station cache when user location changes."""
    global _nearest_cache
    _nearest_cache = None


async def _fetch_station_list() -> list[dict[str, Any]]:
    """Fetch GIRO ionosonde station list. Cached for app lifetime."""
    global _station_cache
    if _station_cache is not None:
        return _station_cache

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(GIRO_STATION_LIST_URL)
        resp.raise_for_status()

    stations: list[dict[str, Any]] = []
    # Parse HTML table rows with station data.
    # Each row has: URSI code, name, lat, lon (0-360 East), ...
    row_pattern = re.compile(
        r"<tr[^>]*>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>"
        r"\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>",
        re.IGNORECASE,
    )
    for m in row_pattern.finditer(resp.text):
        code = m.group(1).strip()
        name = m.group(2).strip()
        try:
            lat = float(m.group(3).strip())
            # GIRO uses 0-360 East longitude; convert to -180/+180
            lon_raw = float(m.group(4).strip())
            lon = lon_raw if lon_raw <= 180 else lon_raw - 360
        except ValueError:
            continue
        stations.append({"code": code, "name": name, "lat": lat, "lon": lon})

    if stations:
        _station_cache = stations
        logger.info("Loaded %d GIRO ionosonde stations", len(stations))
    return stations


def _angular_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Simple angular distance in degrees (good enough for nearest-station)."""
    dlat = lat1 - lat2
    dlon = lon1 - lon2
    return math.sqrt(dlat * dlat + dlon * dlon)


def _find_nearest_station(
    lat: float, lon: float, stations: list[dict[str, Any]]
) -> Optional[dict[str, Any]]:
    """Find the nearest ionosonde station to the given coordinates."""
    if not stations:
        return None
    best = None
    best_dist = float("inf")
    for s in stations:
        d = _angular_distance(lat, lon, s["lat"], s["lon"])
        if d < best_dist:
            best_dist = d
            best = s
    return best


async def fetch_muf() -> Optional[dict[str, Any]]:
    """Fetch MUF data from GIRO for the nearest ionosonde to the user's station."""
    global _nearest_cache
    try:
        lat = settings.de_latitude
        lon = settings.de_longitude
        if lat == 0.0 and lon == 0.0:
            return None

        stations = await _fetch_station_list()
        if not stations:
            logger.warning("No GIRO stations available")
            return None

        if _nearest_cache is None:
            _nearest_cache = _find_nearest_station(lat, lon, stations)
        nearest = _nearest_cache
        if nearest is None:
            return None

        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=1)).strftime("%Y.%m.%d")
        to_date = (now + timedelta(days=1)).strftime("%Y.%m.%d")

        params = {
            "ursiCode": nearest["code"],
            "charName": "foF2,MUFD",
            "DMUF": "3000",
            "fromDate": from_date,
            "toDate": to_date,
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(GIRO_VALUES_URL, params=params)
            resp.raise_for_status()

        muf_values: list[dict[str, Any]] = []
        fof2_latest: float | None = None

        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                char_name = parts[0]
                time_str = parts[1]
                value = float(parts[2])
                if value <= 0:
                    continue
                if char_name == "MUFD":
                    muf_values.append({"time_tag": time_str, "value": value})
                elif char_name == "foF2":
                    fof2_latest = value
            except (ValueError, IndexError):
                continue

        if not muf_values:
            return None

        latest = muf_values[-1]
        history = [{"time_tag": v["time_tag"], "value": v["value"]} for v in muf_values[-24:]]

        return {
            "muf": latest["value"],
            "fof2": fof2_latest,
            "station_code": nearest["code"],
            "station_name": nearest["name"],
            "time_tag": latest["time_tag"],
            "history": history,
        }

    except Exception as e:
        logger.error("Failed to fetch MUF: %s", e)
        return None
