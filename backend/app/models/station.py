from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StationConfig(BaseModel):
    callsign: str = ""
    grid: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = "UTC"
    map_style: str = "dark-matter"


class LocationInfo(BaseModel):
    latitude: float
    longitude: float
    grid: str
    bearing: Optional[float] = None
    distance_km: Optional[float] = None
    distance_mi: Optional[float] = None
