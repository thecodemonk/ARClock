from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class BandPrediction(BaseModel):
    band: str
    frequency: float
    status: str
    reliability: Optional[float] = None
    snr_db: Optional[float] = None


class PropagationResponse(BaseModel):
    mode: str
    muf: float
    bands: list[BandPrediction]
    distance_km: Optional[float] = None
    ssn: float
    utc_hour: float
    computed_at: str
