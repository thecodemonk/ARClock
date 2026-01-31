from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NOAA_BASE = "https://services.swpc.noaa.gov/json"
NOAA_TEXT_BASE = "https://services.swpc.noaa.gov/text"
HAMQSL_URL = "https://www.hamqsl.com/solarxml.php"
TIMEOUT = 15.0


def _utc_tag(tag: str) -> str:
    """Ensure NOAA timestamp has a UTC 'Z' suffix.

    NOAA SWPC timestamps are UTC but omit the trailing Z, which causes
    JavaScript's Date parser to treat them as local time.
    """
    if tag and not tag.endswith("Z") and "+" not in tag:
        return tag + "Z"
    return tag


async def _fetch_daily_solar_indices() -> Optional[list[dict[str, Any]]]:
    """Fetch and parse NOAA Daily Solar Data (DSD) text file.

    Returns a list of rows, each with keys: time_tag, sfi, ssn.
    Both SFI and SSN fetchers share this to avoid duplicate requests.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_TEXT_BASE}/daily-solar-indices.txt")
            resp.raise_for_status()
            rows: list[dict[str, Any]] = []
            for line in resp.text.splitlines():
                line = line.strip()
                if not line or line.startswith(("#", ":")):
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    sfi = int(parts[3])
                    ssn = int(parts[4])
                    tag = f"{year:04d}-{month:02d}-{day:02d}T00:00:00Z"
                    rows.append({"time_tag": tag, "sfi": sfi, "ssn": ssn})
                except (ValueError, IndexError):
                    continue
            return rows if rows else None
    except Exception as e:
        logger.error("Failed to fetch daily solar indices: %s", e)
        return None


async def fetch_sfi() -> Optional[dict[str, Any]]:
    """Fetch daily Solar Flux Index (10.7 cm) from NOAA SWPC."""
    try:
        rows = await _fetch_daily_solar_indices()
        if not rows:
            return None
        latest = rows[-1]
        history = [
            {"time_tag": r["time_tag"], "value": r["sfi"]}
            for r in rows[-30:]
        ]
        return {
            "value": latest["sfi"],
            "time_tag": latest["time_tag"],
            "history": history,
        }
    except Exception as e:
        logger.error("Failed to fetch SFI: %s", e)
        return None


async def fetch_kp() -> Optional[dict[str, Any]]:
    """Fetch planetary Kp index from NOAA SWPC."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_BASE}/planetary_k_index_1m.json")
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            latest = data[-1]
            # Sample every ~60 entries (1 per minute -> ~1 per hour) for last 24 points
            step = max(1, len(data) // 24)
            sampled = data[::step][-24:]
            history = [
                {"time_tag": _utc_tag(r.get("time_tag", "")), "value": float(r.get("estimated_kp", 0))}
                for r in sampled
            ]
            return {
                "value": float(latest.get("estimated_kp", 0)),
                "time_tag": _utc_tag(latest.get("time_tag", "")),
                "history": history,
            }
    except Exception as e:
        logger.error("Failed to fetch Kp: %s", e)
        return None


def _classify_xray(flux: float) -> str:
    """Classify X-ray flux into solar flare class."""
    if flux <= 0:
        return "A0.0"
    if flux < 1e-7:
        return "A0.0"
    elif flux < 1e-6:
        decade = flux / 1e-7
        return f"B{decade:.1f}"
    elif flux < 1e-5:
        decade = flux / 1e-6
        return f"C{decade:.1f}"
    elif flux < 1e-4:
        decade = flux / 1e-5
        return f"M{decade:.1f}"
    else:
        decade = flux / 1e-4
        return f"X{decade:.1f}"


async def fetch_xray() -> Optional[dict[str, Any]]:
    """Fetch X-ray flux from NOAA SWPC."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_BASE}/goes/primary/xrays-6-hour.json")
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            latest = data[-1]
            flux = float(latest.get("flux", 0))
            return {
                "flux": flux,
                "flare_class": _classify_xray(flux),
                "time_tag": _utc_tag(latest.get("time_tag", "")),
            }
    except Exception as e:
        logger.error("Failed to fetch X-ray: %s", e)
        return None


async def fetch_ssn() -> Optional[dict[str, Any]]:
    """Fetch daily sunspot number from NOAA SWPC Daily Solar Data."""
    try:
        rows = await _fetch_daily_solar_indices()
        if not rows:
            return None
        latest = rows[-1]
        history = [
            {"time_tag": r["time_tag"], "value": r["ssn"]}
            for r in rows[-30:]
        ]
        return {
            "value": latest["ssn"],
            "time_tag": latest["time_tag"],
            "history": history,
        }
    except Exception as e:
        logger.error("Failed to fetch SSN: %s", e)
        return None


async def fetch_ap() -> Optional[dict[str, Any]]:
    """Fetch planetary A-index from NOAA SWPC daily geomagnetic indices.

    Parses the DGD text file. Each data line contains station blocks ending
    with the planetary values. The planetary A-index is extracted from the
    rightmost group of values.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_TEXT_BASE}/daily-geomagnetic-indices.txt")
            resp.raise_for_status()
            rows: list[dict[str, Any]] = []
            for line in resp.text.splitlines():
                line = line.strip()
                if not line or line.startswith(("#", ":")):
                    continue
                parts = line.split()
                if len(parts) < 12:
                    continue
                try:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    # The planetary A-index is the last value before the final
                    # Kp values in the line. In the DGD format the A-index
                    # for the planetary row is at parts[-9] (first of last 9 cols).
                    ap = int(parts[-9])
                    tag = f"{year:04d}-{month:02d}-{day:02d}T00:00:00Z"
                    rows.append({"time_tag": tag, "value": ap})
                except (ValueError, IndexError):
                    continue
            if not rows:
                return None
            latest = rows[-1]
            history = [{"time_tag": r["time_tag"], "value": r["value"]} for r in rows[-30:]]
            return {
                "value": latest["value"],
                "time_tag": latest["time_tag"],
                "history": history,
            }
    except Exception as e:
        logger.error("Failed to fetch Ap: %s", e)
        return None


def _parse_hamqsl_time(raw: str) -> str:
    """Convert HamQSL time format to ISO 8601.

    Input example: '31 Jan 2026 2022 GMT'
    Output: '2026-01-31T20:22:00Z'
    """
    try:
        dt = datetime.strptime(raw.strip(), "%d %b %Y %H%M %Z")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, AttributeError):
        return raw


async def fetch_signal_noise() -> Optional[dict[str, Any]]:
    """Fetch signal noise and solar data from HamQSL XML feed."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(HAMQSL_URL)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            solar = root.find(".//solardata")
            if solar is None:
                return None

            def _text(tag: str) -> Optional[str]:
                el = solar.find(tag)
                return el.text.strip() if el is not None and el.text else None

            def _int(tag: str) -> Optional[int]:
                v = _text(tag)
                if v is None:
                    return None
                try:
                    return int(v)
                except ValueError:
                    return None

            value = _text("signalnoise") or "N/A"
            updated_raw = _text("updated") or ""
            time_tag = _parse_hamqsl_time(updated_raw) if updated_raw else ""

            return {
                "value": value,
                "time_tag": time_tag,
                "aindex": _int("aindex"),
                "kindex": _int("kindex"),
                "solarflux": _int("solarflux"),
            }
    except Exception as e:
        logger.error("Failed to fetch signal noise: %s", e)
        return None
