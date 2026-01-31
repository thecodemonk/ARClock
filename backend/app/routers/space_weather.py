from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.cache import cache

router = APIRouter(tags=["space-weather"])


_METRICS = ("sfi", "kp", "xray", "ssn", "ap", "signal_noise", "muf")


@router.get("/space-weather/{metric}")
async def get_space_weather(metric: str):
    if metric == "all":
        all_data = {}
        for key in _METRICS:
            entry = cache.get(key)
            if entry:
                all_data[key] = entry["data"]
                all_data.setdefault("updated_at", entry["updated_at"])
        return all_data

    if metric not in _METRICS:
        raise HTTPException(status_code=404, detail=f"Unknown metric: {metric}")

    entry = cache.get(metric)
    if not entry:
        raise HTTPException(status_code=503, detail=f"No data available for {metric}")
    return entry["data"]
