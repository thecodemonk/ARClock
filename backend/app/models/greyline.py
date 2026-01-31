from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GreyLineData(BaseModel):
    geojson: dict[str, Any]
    subsolar_lat: float
    subsolar_lon: float
    computed_at: str
