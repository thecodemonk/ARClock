from __future__ import annotations

import logging
import math
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.cache import cache

logger = logging.getLogger(__name__)

BANDS = [
    ("160m", 1.9),
    ("80m", 3.6),
    ("40m", 7.15),
    ("30m", 10.125),
    ("20m", 14.15),
    ("17m", 18.1),
    ("15m", 21.2),
    ("12m", 24.95),
    ("10m", 28.4),
]

_engine_lock = threading.Lock()
_fourier_maps = None
_geomag_calc = None
_solar_calc = None


def _get_ssn() -> float:
    """Get SSN from cache, estimate from SFI, or use default."""
    entry = cache.get("ssn")
    if entry and entry.get("data"):
        try:
            return float(entry["data"]["value"])
        except (KeyError, TypeError, ValueError):
            pass
    entry = cache.get("sfi")
    if entry and entry.get("data"):
        try:
            sfi = float(entry["data"]["value"])
            return max(0, sfi / 0.7 - 60)
        except (KeyError, TypeError, ValueError):
            pass
    return 50.0


def _classify_band(reliability: Optional[float], freq: float, muf: float) -> str:
    """Classify band status from reliability or MUF ratio."""
    if reliability is not None:
        if reliability >= 0.50:
            return "GOOD"
        if reliability >= 0.25:
            return "FAIR"
        if reliability >= 0.10:
            return "POOR"
        return "CLOSED"
    ratio = freq / muf if muf > 0 else 999
    if ratio < 0.8:
        return "GOOD"
    if ratio < 1.0:
        return "FAIR"
    if ratio < 1.2:
        return "POOR"
    return "CLOSED"


def _ensure_maps():
    """Lazily initialize FourierMaps singleton."""
    global _fourier_maps, _geomag_calc, _solar_calc
    if _fourier_maps is None:
        from dvoacap import FourierMaps
        from dvoacap.geomagnetic import GeomagneticCalculator
        from dvoacap.solar import SolarCalculator
        _fourier_maps = FourierMaps()
        _geomag_calc = GeomagneticCalculator()
        _solar_calc = SolarCalculator()


def _predict_path(
    tx_lat: float, tx_lon: float,
    rx_lat: float, rx_lon: float,
    ssn: float,
    now: datetime,
) -> dict[str, Any]:
    """Full DE-to-DX path prediction using PredictionEngine."""
    from dvoacap.path_geometry import GeoPoint
    from dvoacap.prediction_engine import PredictionEngine

    month = now.month
    utc_fraction = (now.hour + now.minute / 60.0) / 24.0

    engine = PredictionEngine()
    engine.params.ssn = ssn
    engine.params.month = month
    engine.params.tx_power = 100
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)

    rx = GeoPoint.from_degrees(rx_lat, rx_lon)
    freqs = [b[1] for b in BANDS]

    engine.predict(rx_location=rx, utc_time=utc_fraction, frequencies=freqs)

    # Extract circuit MUF (set by predict())
    muf = 0.0
    if engine.circuit_muf is not None:
        muf = float(engine.circuit_muf.muf)

    bands = []
    for i, (band_name, freq) in enumerate(BANDS):
        reliability = None
        snr_db = None
        if i < len(engine.predictions):
            pred = engine.predictions[i]
            if hasattr(pred, "signal") and pred.signal is not None:
                # muf_day is the probability the MUF exceeds this frequency
                # (i.e. probability the band is open), which is the right
                # metric for "band open" classification.
                muf_day = float(pred.signal.muf_day)
                snr_val = float(pred.signal.snr_db)
                # If the engine found usable modes (non-zero muf_day),
                # use muf_day for classification. Otherwise fall back
                # to MUF ratio (reliability=None triggers ratio mode).
                if muf_day > 0:
                    reliability = muf_day
                    snr_db = snr_val
        status = _classify_band(reliability, freq, muf)
        bands.append({
            "band": band_name,
            "frequency": freq,
            "status": status,
            "reliability": round(reliability, 3) if reliability is not None else None,
            "snr_db": round(snr_db, 1) if snr_db is not None else None,
        })

    distance_km = engine.path.get_distance_km() if hasattr(engine.path, "get_distance_km") else None

    return {
        "mode": "path",
        "muf": round(muf, 1),
        "bands": bands,
        "distance_km": round(distance_km, 1) if distance_km is not None else None,
        "ssn": round(ssn, 1),
        "utc_hour": round(now.hour + now.minute / 60.0, 1),
        "computed_at": now.isoformat(),
    }


def _predict_local(
    lat: float, lon: float,
    ssn: float,
    now: datetime,
) -> dict[str, Any]:
    """Local ionospheric conditions at DE using FourierMaps."""
    from dvoacap import (
        ControlPoint, compute_iono_params, compute_zenith_angle, compute_local_time,
    )
    from dvoacap.layer_parameters import GeographicPoint

    _ensure_maps()

    month = now.month
    utc_fraction = (now.hour + now.minute / 60.0) / 24.0

    _fourier_maps.set_conditions(month=month, ssn=ssn, utc_fraction=utc_fraction)

    location = GeographicPoint.from_degrees(lat, lon)

    # Solar parameters (module-level functions use float utc_fraction)
    zen_angle = compute_zenith_angle(location, utc_fraction, month)
    local_time = compute_local_time(utc_fraction, math.radians(lon))

    # Geomagnetic parameters
    geo_params = _geomag_calc.calculate_parameters(location)

    zen_max = _fourier_maps.compute_zen_max(geo_params.magnetic_dip)

    pnt = ControlPoint(
        location=location,
        east_lon=math.radians(lon),
        distance_rad=0.0,
        local_time=local_time,
        zen_angle=zen_angle,
        zen_max=zen_max,
        mag_lat=geo_params.magnetic_latitude,
        mag_dip=geo_params.magnetic_dip,
        gyro_freq=geo_params.gyrofrequency,
    )

    compute_iono_params(pnt, _fourier_maps)

    # Estimate MUF from foF2 and M(3000)F2 factor
    fof2 = pnt.f2.fo if pnt.f2 and pnt.f2.fo else 0.0
    m3000 = pnt.f2m3 if hasattr(pnt, "f2m3") and pnt.f2m3 else 3.0
    muf = fof2 * m3000

    bands = []
    for band_name, freq in BANDS:
        status = _classify_band(None, freq, muf)
        bands.append({
            "band": band_name,
            "frequency": freq,
            "status": status,
            "reliability": None,
            "snr_db": None,
        })

    return {
        "mode": "local",
        "muf": round(muf, 1),
        "bands": bands,
        "distance_km": None,
        "ssn": round(ssn, 1),
        "utc_hour": round(now.hour + now.minute / 60.0, 1),
        "computed_at": now.isoformat(),
    }


def compute_propagation(
    tx_lat: float,
    tx_lon: float,
    rx_lat: Optional[float] = None,
    rx_lon: Optional[float] = None,
) -> dict[str, Any]:
    """Compute HF propagation predictions. Thread-safe.

    If rx_lat/rx_lon provided, computes full path prediction.
    Otherwise computes local ionospheric conditions at tx location.
    """
    ssn = _get_ssn()
    now = datetime.now(timezone.utc)

    with _engine_lock:
        try:
            if rx_lat is not None and rx_lon is not None:
                return _predict_path(tx_lat, tx_lon, rx_lat, rx_lon, ssn, now)
            else:
                return _predict_local(tx_lat, tx_lon, ssn, now)
        except Exception as e:
            logger.error("Propagation prediction failed: %s", e, exc_info=True)
            return _fallback_response(ssn, now, rx_lat is not None)


def _fallback_response(ssn: float, now: datetime, is_path: bool) -> dict[str, Any]:
    """Return a minimal response when dvoacap fails."""
    bands = []
    for band_name, freq in BANDS:
        bands.append({
            "band": band_name,
            "frequency": freq,
            "status": "CLOSED",
            "reliability": None,
            "snr_db": None,
        })
    return {
        "mode": "path" if is_path else "local",
        "muf": 0.0,
        "bands": bands,
        "distance_km": None,
        "ssn": round(ssn, 1),
        "utc_hour": round(now.hour + now.minute / 60.0, 1),
        "computed_at": now.isoformat(),
    }
