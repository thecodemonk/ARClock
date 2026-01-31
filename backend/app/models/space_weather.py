from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SFIData(BaseModel):
    value: float
    time_tag: str
    history: list[dict] = []


class KpData(BaseModel):
    value: float
    time_tag: str
    history: list[dict] = []


class XRayData(BaseModel):
    flux: float
    flare_class: str
    time_tag: str


class SSNData(BaseModel):
    value: int
    time_tag: str
    history: list[dict] = []


class SpaceWeatherAll(BaseModel):
    sfi: Optional[SFIData] = None
    kp: Optional[KpData] = None
    xray: Optional[XRayData] = None
    ssn: Optional[SSNData] = None
    updated_at: Optional[str] = None
