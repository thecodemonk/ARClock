from __future__ import annotations

import logging
from pathlib import Path

from skyfield.api import Loader, wgs84

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_load = Loader(str(DATA_DIR))
_ts = _load.timescale()
_eph = _load("de421.bsp")


def get_subsolar_point() -> tuple[float, float]:
    """Return (latitude, longitude) of the subsolar point at the current time."""
    t = _ts.now()
    sun = _eph["earth"].at(t).observe(_eph["sun"]).apparent()
    lat, lon = wgs84.latlon_of(sun)
    return lat.degrees, lon.degrees
