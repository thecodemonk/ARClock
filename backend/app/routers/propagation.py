from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.services.propagation import compute_propagation

router = APIRouter(tags=["propagation"])


@router.get("/propagation")
async def get_propagation(
    rx_lat: Optional[float] = Query(None, ge=-90, le=90),
    rx_lon: Optional[float] = Query(None, ge=-180, le=180),
):
    if settings.de_latitude == 0 and settings.de_longitude == 0:
        raise HTTPException(status_code=400, detail="Station not configured")

    if (rx_lat is None) != (rx_lon is None):
        raise HTTPException(status_code=400, detail="Provide both rx_lat and rx_lon or neither")

    result = await asyncio.to_thread(
        compute_propagation,
        settings.de_latitude,
        settings.de_longitude,
        rx_lat,
        rx_lon,
    )
    return result
