from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NOAA_BASE = "https://services.swpc.noaa.gov/json"
TIMEOUT = 15.0


async def fetch_sfi() -> Optional[dict[str, Any]]:
    """Fetch Solar Flux Index (10.7 cm) from NOAA SWPC."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_BASE}/f107_cm_flux.json")
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            latest = data[-1]
            history = [
                {"time_tag": r.get("time_tag", ""), "value": float(r.get("flux", 0))}
                for r in data[-30:]
            ]
            return {
                "value": float(latest.get("flux", 0)),
                "time_tag": latest.get("time_tag", ""),
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
                {"time_tag": r.get("time_tag", ""), "value": float(r.get("estimated_kp", 0))}
                for r in sampled
            ]
            return {
                "value": float(latest.get("estimated_kp", 0)),
                "time_tag": latest.get("time_tag", ""),
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
                "time_tag": latest.get("time_tag", ""),
            }
    except Exception as e:
        logger.error("Failed to fetch X-ray: %s", e)
        return None


async def fetch_ssn() -> Optional[dict[str, Any]]:
    """Fetch monthly sunspot number from NOAA SWPC solar cycle data."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(f"{NOAA_BASE}/solar-cycle/sunspots.json")
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            latest = data[-1]
            history = [
                {"time_tag": r.get("time-tag", ""), "value": float(r.get("ssn", 0))}
                for r in data[-30:]
            ]
            return {
                "value": round(float(latest.get("ssn", 0))),
                "time_tag": latest.get("time-tag", ""),
                "history": history,
            }
    except Exception as e:
        logger.error("Failed to fetch SSN: %s", e)
        return None
